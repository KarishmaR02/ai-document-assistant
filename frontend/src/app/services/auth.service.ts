import { Injectable, signal } from '@angular/core';

export interface User {
  email: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly currentUserSignal = signal<User | null>(null);
  
  // Expose signal as readonly
  readonly currentUser = this.currentUserSignal.asReadonly();

  constructor() {
    // Check if token and email exists in localStorage to restore session
    const token = localStorage.getItem('mock_token');
    const email = localStorage.getItem('mock_email');
    if (token && email) {
      this.currentUserSignal.set({ email });
    }
  }

  register(email: string, password: string): Promise<boolean> {
    return new Promise((resolve) => {
      setTimeout(() => {
        // Mock registering: Store mock credentials
        const registeredUsers = JSON.parse(localStorage.getItem('registered_users') || '[]');
        if (registeredUsers.some((u: any) => u.email === email)) {
          resolve(false);
          return;
        }
        registeredUsers.push({ email, password });
        localStorage.setItem('registered_users', JSON.stringify(registeredUsers));
        resolve(true);
      }, 500);
    });
  }

  login(email: string, password: string): Promise<boolean> {
    return new Promise((resolve) => {
      setTimeout(() => {
        // Mock login check
        const registeredUsers = JSON.parse(localStorage.getItem('registered_users') || '[]');
        const user = registeredUsers.find((u: any) => u.email === email && u.password === password);
        
        // Let's also allow a fallback user for easier development testing
        if (user || (email === 'demo@example.com' && password === 'password')) {
          localStorage.setItem('mock_token', 'mock_jwt_token_for_' + email);
          localStorage.setItem('mock_email', email);
          this.currentUserSignal.set({ email });
          resolve(true);
        } else {
          resolve(false);
        }
      }, 500);
    });
  }

  logout(): void {
    localStorage.removeItem('mock_token');
    localStorage.removeItem('mock_email');
    this.currentUserSignal.set(null);
  }

  isAuthenticated(): boolean {
    return this.currentUserSignal() !== null;
  }
}
