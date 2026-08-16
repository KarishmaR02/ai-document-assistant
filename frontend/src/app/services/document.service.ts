import { Injectable, signal, inject } from '@angular/core';
import { Graphql } from './graphql';

export interface DocumentMetadata {
  id: string;
  name: string;
  size: number;
  status: 'UPLOADED' | 'PROCESSING' | 'PROCESSED' | 'FAILED';
  progress: number;
  uploadedAt: Date;
  errorMessage?: string;
}

@Injectable({
  providedIn: 'root'
})
export class DocumentService {
  private readonly graphqlService = inject(Graphql);
  private readonly documentsSignal = signal<DocumentMetadata[]>([]);

  readonly documents = this.documentsSignal.asReadonly();

  constructor() {
    this.loadInitialDocuments();
  }

  private async loadInitialDocuments(): Promise<void> {
    try {
      const queryStr = `
        query {
          getDocuments {
            id
            name
            size
            status
            progress
            uploadedAt
            errorMessage
          }
        }
      `;
      
      const data = await this.graphqlService.query<{ getDocuments: any[] }>(queryStr);
      
      const docs: DocumentMetadata[] = data.getDocuments.map((doc) => ({
        id: doc.id,
        name: doc.name,
        size: doc.size,
        status: doc.status as any,
        progress: doc.progress,
        uploadedAt: new Date(doc.uploadedAt),
        errorMessage: doc.errorMessage
      }));
      
      this.documentsSignal.set(docs);
      console.log('%c[GraphQL Service] SUCCESS! Fetched documents list from backend:', 'color: #10b981; font-weight: bold;', docs);

      // Start simulation for any document in processing status
      this.documentsSignal().forEach(doc => {
        if (doc.status === 'PROCESSING') {
          this.simulateProcessing(doc.id);
        }
      });

    } catch (error) {
      console.warn('[GraphQL Service] Failed to load documents from backend, using local mock fallback:', error);
      
      // Local fallback data
      const fallbackDocs: DocumentMetadata[] = [
        {
          id: 'doc-1',
          name: 'employee_policy_fallback.pdf',
          size: 124000,
          status: 'PROCESSED',
          progress: 100,
          uploadedAt: new Date(Date.now() - 3600000 * 2)
        },
        {
          id: 'doc-2',
          name: 'project_guide_fallback.pdf',
          size: 450000,
          status: 'PROCESSING',
          progress: 45,
          uploadedAt: new Date(Date.now() - 600000)
        }
      ];
      this.documentsSignal.set(fallbackDocs);
      this.simulateProcessing('doc-2');
    }
  }

  getDocuments(): DocumentMetadata[] {
    return this.documentsSignal();
  }

  getDocumentById(id: string): DocumentMetadata | undefined {
    return this.documentsSignal().find((doc) => doc.id === id);
  }

  uploadDocument(file: File): Promise<DocumentMetadata> {
    return new Promise((resolve, reject) => {
      // Security Validation: size limit 10MB
      const maxSize = 10 * 1024 * 1024;
      if (file.size > maxSize) {
        reject(new Error('File size exceeds the 10MB limit.'));
        return;
      }

      // Security Validation: PDF only
      if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
        reject(new Error('Only PDF files are supported.'));
        return;
      }

      setTimeout(() => {
        const newDoc: DocumentMetadata = {
          id: 'doc-' + Math.random().toString(36).substring(2, 9),
          name: file.name,
          size: file.size,
          status: 'UPLOADED',
          progress: 10,
          uploadedAt: new Date()
        };

        this.documentsSignal.update((docs) => [newDoc, ...docs]);
        this.simulateProcessing(newDoc.id);
        resolve(newDoc);
      }, 800);
    });
  }

  private simulateProcessing(id: string): void {
    let currentStep = 0;
    const interval = setInterval(() => {
      this.documentsSignal.update((docs) => {
        return docs.map((doc) => {
          if (doc.id !== id) return doc;

          if (doc.status === 'UPLOADED') {
            return { ...doc, status: 'PROCESSING', progress: 40 };
          }

          if (doc.status === 'PROCESSING') {
            if (doc.progress < 80) {
              return { ...doc, progress: doc.progress + 20 };
            } else {
              clearInterval(interval);
              const failed = Math.random() < 0.1;
              if (failed) {
                return {
                  ...doc,
                  status: 'FAILED',
                  progress: 100,
                  errorMessage: 'PDF extraction failed: File contains unreadable encrypted text.'
                };
              } else {
                return { ...doc, status: 'PROCESSED', progress: 100 };
              }
            }
          }

          return doc;
        });
      });
    }, 1500);
  }
}
