import { Injectable, signal } from '@angular/core';

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
  private readonly documentsSignal = signal<DocumentMetadata[]>([
    {
      id: 'doc-1',
      name: 'employee_policy.pdf',
      size: 124000,
      status: 'PROCESSED',
      progress: 100,
      uploadedAt: new Date(Date.now() - 3600000 * 2) // 2 hours ago
    },
    {
      id: 'doc-2',
      name: 'project_guide.pdf',
      size: 450000,
      status: 'PROCESSING',
      progress: 45,
      uploadedAt: new Date(Date.now() - 600000) // 10 mins ago
    }
  ]);

  readonly documents = this.documentsSignal.asReadonly();

  constructor() {
    // Resume simulation for any document in processing status on startup
    this.documentsSignal().forEach(doc => {
      if (doc.status === 'PROCESSING') {
        this.simulateProcessing(doc.id);
      }
    });
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
              // Finish processing. Decide if it fails (10% chance) or succeeds (90%)
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
