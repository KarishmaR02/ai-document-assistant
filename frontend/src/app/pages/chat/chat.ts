import { Component, OnInit, inject, signal, effect, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { DocumentService, DocumentMetadata } from '../../services/document.service';
import { ChatService, ChatMessage } from '../../services/chat.service';

@Component({
  selector: 'app-chat',
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './chat.html',
  styleUrl: './chat.scss'
})
export class Chat implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly documentService = inject(DocumentService);
  private readonly chatService = inject(ChatService);

  @ViewChild('scrollContainer') private scrollContainer!: ElementRef;

  document = signal<DocumentMetadata | undefined>(undefined);
  messagesList = signal<ChatMessage[]>([]);
  
  queryText = '';
  isAiResponding = signal(false);
  activeCitation = signal<any | null>(null);

  constructor() {
    // Keep list of messages reactive to changes in ChatService
    effect(() => {
      const doc = this.document();
      if (doc) {
        this.messagesList.set(this.chatService.getMessagesByDocument(doc.id));
        this.scrollToBottom();
      }
    });
  }

  ngOnInit(): void {
    const docId = this.route.snapshot.paramMap.get('documentId');
    if (!docId) {
      this.router.navigate(['/dashboard']);
      return;
    }

    const doc = this.documentService.getDocumentById(docId);
    if (!doc || doc.status !== 'PROCESSED') {
      // Document must exist and be fully processed to chat
      this.router.navigate(['/dashboard']);
      return;
    }

    this.document.set(doc);
    this.messagesList.set(this.chatService.getMessagesByDocument(docId));
    this.scrollToBottom();
  }

  async sendQuery() {
    const query = this.queryText.trim();
    const doc = this.document();
    if (!query || !doc || this.isAiResponding()) return;

    this.queryText = '';
    this.isAiResponding.set(true);
    this.scrollToBottom();

    try {
      await this.chatService.sendMessage(doc.id, query);
    } catch (error) {
      console.error('Error sending query:', error);
    } finally {
      this.isAiResponding.set(false);
      this.scrollToBottom();
    }
  }

  toggleCitation(chunk: any): void {
    if (this.activeCitation() === chunk) {
      this.activeCitation.set(null);
    } else {
      this.activeCitation.set(chunk);
    }
  }

  private scrollToBottom(): void {
    setTimeout(() => {
      try {
        if (this.scrollContainer) {
          const el = this.scrollContainer.nativeElement;
          el.scrollTop = el.scrollHeight;
        }
      } catch (err) {
        // ignore
      }
    }, 50);
  }
}
