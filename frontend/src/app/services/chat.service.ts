import { Injectable, signal } from '@angular/core';

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
  private readonly messagesSignal = signal<ChatMessage[]>([
    {
      id: 'msg-1',
      documentId: 'doc-1',
      sender: 'user',
      text: 'How many casual leaves can I take?',
      timestamp: new Date(Date.now() - 600000)
    },
    {
      id: 'msg-2',
      documentId: 'doc-1',
      sender: 'ai',
      text: 'According to the Employee Leave Policy (Section 3.2), full-time employees are entitled to **12 casual leaves** per year, which accrue on a monthly pro-rata basis.',
      timestamp: new Date(Date.now() - 590000),
      retrievedChunks: [
        {
          text: 'Casual Leave Policy: Full-time employees are entitled to 12 casual leaves per calendar year. These leaves are credited at the beginning of the year and accrue on a monthly pro-rata basis of 1 day per month.',
          pageNumber: 2,
          score: 0.92
        }
      ]
    }
  ]);

  readonly messages = this.messagesSignal.asReadonly();

  getMessagesByDocument(documentId: string): ChatMessage[] {
    return this.messagesSignal().filter((m) => m.documentId === documentId);
  }

  sendMessage(documentId: string, text: string): Promise<ChatMessage> {
    const userMsg: ChatMessage = {
      id: 'msg-' + Math.random().toString(36).substring(2, 9),
      documentId,
      sender: 'user',
      text,
      timestamp: new Date()
    };

    this.messagesSignal.update((msgs) => [...msgs, userMsg]);

    return new Promise((resolve) => {
      // Simulate network request to Strawberry/FastAPI + LLM typing delay
      setTimeout(() => {
        const replyText = this.generateMockReply(text);
        const aiMsg: ChatMessage = {
          id: 'msg-' + Math.random().toString(36).substring(2, 9),
          documentId,
          sender: 'ai',
          text: replyText.answer,
          timestamp: new Date(),
          retrievedChunks: replyText.chunks
        };

        this.messagesSignal.update((msgs) => [...msgs, aiMsg]);
        resolve(aiMsg);
      }, 1500); // 1.5s typing simulation
    });
  }

  private generateMockReply(query: string): { answer: string; chunks: RetrievedChunk[] } {
    const lower = query.toLowerCase();

    if (lower.includes('leave') || lower.includes('vacation') || lower.includes('casual')) {
      return {
        answer: 'Employees are entitled to 12 casual leaves per calendar year, which accrue on a monthly pro-rata basis of 1 day per month.',
        chunks: [
          {
            text: 'Section 4.1: Employees are entitled to 12 casual leaves per year. Casual leaves cannot be carried forward to the next calendar year.',
            pageNumber: 3,
            score: 0.89
          }
        ]
      };
    }

    if (lower.includes('working') || lower.includes('hours') || lower.includes('time')) {
      return {
        answer: 'Standard working hours are from 9:00 AM to 6:00 PM, Monday through Friday, including a one-hour lunch break.',
        chunks: [
          {
            text: 'Section 1.2: Working Hours. The standard working hours are 9:00 AM to 6:00 PM, Monday to Friday. A mandatory 1-hour lunch break is scheduled from 1:00 PM to 2:00 PM.',
            pageNumber: 1,
            score: 0.85
          }
        ]
      };
    }

    // Default reply
    return {
      answer: `I found some information in the document, but it may not address all aspects of your question. Based on the retrieved segments:

"The primary guidelines are outlined in the onboarding manual."

Please let me know if you would like me to retrieve specific pages or clarify other details.`,
      chunks: [
        {
          text: 'Document Onboarding Manual Intro: All guidelines must be read carefully and acknowledged by signing the training checklist within 30 days of joining.',
          pageNumber: 1,
          score: 0.65
        }
      ]
    };
  }
}
