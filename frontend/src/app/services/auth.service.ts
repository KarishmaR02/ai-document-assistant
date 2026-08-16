import { Injectable, signal } from '@angular/core';
import { supabase } from './supabase';
import { Session } from '@supabase/supabase-js';

export interface AppUser {
  email: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly currentUserSignal = signal<AppUser | null>(null);
  
  // Expose signal as readonly
  readonly currentUser = this.currentUserSignal.asReadonly();

  constructor() {
    // 1. Fetch initial session state on app load
    supabase.auth.getSession().then(({ data: { session } }) => {
      this.handleSession(session);
    });

    // 2. Listen dynamically to authentication changes (login, logout, token refreshes)
    supabase.auth.onAuthStateChange((_event, session) => {
      this.handleSession(session);
    });
  }

  private handleSession(session: Session | null): void {
    if (session && session.user) {
      const email = session.user.email || '';
      this.currentUserSignal.set({ email });
      // Keep local items for backwards-compatibility checks
      localStorage.setItem('mock_token', session.access_token);
      localStorage.setItem('mock_email', email);
    } else {
      this.currentUserSignal.set(null);
      localStorage.removeItem('mock_token');
      localStorage.removeItem('mock_email');
    }
  }

  async register(email: string, password: string): Promise<boolean> {
    const { data, error } = await supabase.auth.signUp({
      email,
      password
    });
    
    if (error) {
      throw new Error(error.message);
    }
    
    return data.user !== null;
  }

  async login(email: string, password: string): Promise<boolean> {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    });

    if (error) {
      throw new Error(error.message);
    }

    return data.session !== null;
  }

  async logout(): Promise<void> {
    const { error } = await supabase.auth.signOut();
    if (error) {
      throw new Error(error.message);
    }
  }

  isAuthenticated(): boolean {
    return this.currentUserSignal() !== null;
  }

  async getAccessToken(): Promise<string | null> {
    const { data: { session } } = await supabase.auth.getSession();
    return session?.access_token || null;
  }
}
