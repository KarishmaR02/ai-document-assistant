import { Injectable, signal, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { Graphql } from './graphql';
import { AuthService } from './auth.service';

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
  private readonly http = inject(HttpClient);
  private readonly graphqlService = inject(Graphql);
  private readonly authService = inject(AuthService);
  
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

      // Start status polling for any document loaded in a non-final processing state
      this.documentsSignal().forEach(doc => {
        if (doc.status === 'PROCESSING' || doc.status === 'UPLOADED') {
          this.pollDocumentStatus(doc.id);
        }
      });

    } catch (error) {
      console.warn('[GraphQL Service] Failed to load documents from backend, using local mock fallback:', error);
      
      // Fallback data if backend database offline
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
          uploadedAt: new Date(Date.now() - 60000)
        }
      ];
      this.documentsSignal.set(fallbackDocs);
    }
  }

  getDocuments(): DocumentMetadata[] {
    return this.documentsSignal();
  }

  getDocumentById(id: string): DocumentMetadata | undefined {
    return this.documentsSignal().find((doc) => doc.id === id);
  }

  async uploadDocument(file: File): Promise<DocumentMetadata> {
    // 1. Validation check sizes on client
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      throw new Error('File size exceeds the 10MB limit.');
    }

    // 2. Validation check PDF type
    if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
      throw new Error('Only PDF files are supported.');
    }

    // 3. Construct multi-part FormData payload
    const formData = new FormData();
    formData.append('file', file);

    // 4. Retrieve auth session token to attach as authorization header
    const token = await this.authService.getAccessToken();
    let headers: { [header: string]: string } = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    // 5. Send POST file upload request
    try {
      const response = await firstValueFrom(
        this.http.post<any>('http://localhost:8000/api/documents/upload', formData, { headers })
      );

      const newDoc: DocumentMetadata = {
        id: response.id,
        name: response.name,
        size: response.size,
        status: response.status,
        progress: response.progress,
        uploadedAt: new Date(response.uploadedAt)
      };

      // Add newly uploaded file to list signal
      this.documentsSignal.update((docs) => [newDoc, ...docs]);

      // Spin up active polling watcher to display real-time parser progress in dashboard UI
      this.pollDocumentStatus(newDoc.id);

      return newDoc;
    } catch (error: any) {
      console.error('File upload request failed:', error);
      throw new Error(error.error?.detail || 'Failed to upload document to server.');
    }
  }

  private pollDocumentStatus(id: string): void {
    const interval = setInterval(async () => {
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
        const docs = data.getDocuments;
        
        // Match document in response
        const target = docs.find(d => d.id === id);
        if (target) {
          this.documentsSignal.update(existingDocs => {
            return existingDocs.map(doc => {
              if (doc.id === id) {
                return {
                  ...doc,
                  status: target.status,
                  progress: target.progress,
                  errorMessage: target.errorMessage
                };
              }
              return doc;
            });
          });

          // Terminate polling interval once parsing finishes or fails
          if (target.status === 'PROCESSED' || target.status === 'FAILED') {
            clearInterval(interval);
          }
        }
      } catch (error) {
        console.error('Failed to poll document status:', error);
        clearInterval(interval);
      }
    }, 2000);
  }
}
