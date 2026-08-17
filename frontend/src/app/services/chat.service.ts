import { inject, Injectable, signal } from '@angular/core';
import { Graphql } from './graphql';

export interface RetrievedChunk {
  text: string;
  pageNumber: number;
  score: number;
}

export interface ChatMessage {
  id: string;
  documentId: string;
  sender: 'user' | 'ai';
  text: string;
  timestamp: Date;
  retrievedChunks?: RetrievedChunk[];
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private readonly graphqlService = inject(Graphql);
  
  // List signal containing conversation items
  private readonly messagesSignal = signal<ChatMessage[]>([]);
  readonly messages = this.messagesSignal.asReadonly();

  // Local cache mapping documentId to its active database sessionId
  private readonly documentSessions = new Map<string, string>();

  getMessagesByDocument(documentId: string): ChatMessage[] {
    return this.messagesSignal().filter((m) => m.documentId === documentId);
  }

  /**
   * Resolves or creates a database chat session for a given document.
   */
  private async getOrCreateSession(documentId: string): Promise<string> {
    if (this.documentSessions.has(documentId)) {
      return this.documentSessions.get(documentId)!;
    }

    try {
      const mutationStr = `
        mutation CreateSession($docId: String!) {
          createChatSession(documentId: $docId) {
            id
          }
        }
      `;
      
      const response = await this.graphqlService.mutate<{ createChatSession: { id: string } }>(
        mutationStr,
        { docId: documentId }
      );
      
      const sessionId = response.createChatSession.id;
      this.documentSessions.set(documentId, sessionId);
      return sessionId;
    } catch (error) {
      console.error('Failed to create chat session on database:', error);
      throw error;
    }
  }

  /**
   * Loads message logs from PostgreSQL for a document chat.
   */
  async loadMessagesForDocument(documentId: string): Promise<void> {
    try {
      const sessionId = await this.getOrCreateSession(documentId);

      const queryStr = `
        query GetMsgs($sessId: String!) {
          getChatMessages(sessionId: $sessId) {
            id
            sender
            text
            timestamp
            retrievedChunks {
              text
              pageNumber
              score
            }
          }
        }
      `;

      const response = await this.graphqlService.query<{ getChatMessages: any[] }>(
        queryStr,
        { sessId: sessionId }
      );

      const messages: ChatMessage[] = response.getChatMessages.map(msg => ({
        id: msg.id,
        documentId,
        sender: msg.sender as 'user' | 'ai',
        text: msg.text,
        timestamp: new Date(msg.timestamp),
        retrievedChunks: msg.retrievedChunks
      }));

      // Update the reactive signal
      this.messagesSignal.update(existingMsgs => {
        const otherDocsMsgs = existingMsgs.filter(m => m.documentId !== documentId);
        return [...otherDocsMsgs, ...messages];
      });

    } catch (error) {
      console.warn('Failed to load conversation history from server, using local list:', error);
    }
  }

  /**
   * Dispatches user message to the backend REST/GraphQL RAG search mutation.
   */
  async sendMessage(documentId: string, text: string): Promise<ChatMessage> {
    const sessionId = await this.getOrCreateSession(documentId);

    // 1. Append user's query locally for instant responsiveness in UI
    const userMsg: ChatMessage = {
      id: 'msg-usr-' + Math.random().toString(36).substring(2, 9),
      documentId,
      sender: 'user',
      text,
      timestamp: new Date()
    };
    this.messagesSignal.update((msgs) => [...msgs, userMsg]);

    // 2. Dispatch GraphQL Mutation to run pgvector search on FastAPI server
    const mutationStr = `
      mutation SendMsg($sessId: String!, $txt: String!) {
        sendMessage(sessionId: $sessId, text: $txt) {
          id
          sender
          text
          timestamp
          retrievedChunks {
            text
            pageNumber
            score
          }
        }
      }
    `;

    try {
      const response = await this.graphqlService.mutate<{ sendMessage: any }>(
        mutationStr,
        { sessId: sessionId, txt: text }
      );
      
      const reply = response.sendMessage;
      const aiMsg: ChatMessage = {
        id: reply.id,
        documentId,
        sender: 'ai',
        text: reply.text,
        timestamp: new Date(reply.timestamp),
        retrievedChunks: reply.retrievedChunks
      };

      // 3. Append AI response chunks to signal logs
      this.messagesSignal.update((msgs) => [...msgs, aiMsg]);
      return aiMsg;
    } catch (error) {
      console.error('Failed to transmit chat message to backend:', error);
      throw error;
    }
  }
}
