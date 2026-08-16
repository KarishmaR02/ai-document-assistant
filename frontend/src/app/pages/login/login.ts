import { Component, signal, inject, OnInit } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { Graphql } from '../../services/graphql';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-login',
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './login.html',
  styleUrl: './login.scss'
})
export class Login implements OnInit {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly graphqlService = inject(Graphql);

  email = '';
  password = '';
  
  isLoading = signal(false);
  errorMessage = signal<string | null>(null);

  ngOnInit(): void {
    // Verify Frontend-to-Backend GraphQL handshake
    this.graphqlService.query<{ hello: string }>('query { hello }')
      .then((data) => {
        console.log('%c[GraphQL Connection] SUCCESS! Handshake response:', 'color: #10b981; font-weight: bold;', data.hello);
      })
      .catch((err) => {
        console.warn('[GraphQL Connection] FAILED! Ensure FastAPI backend is running:', err.message || err);
      });
  }

  async onSubmit() {
    this.errorMessage.set(null);

    if (!this.email || !this.password) {
      this.errorMessage.set('Please enter both email and password.');
      return;
    }

    this.isLoading.set(true);

    try {
      const success = await this.authService.login(this.email, this.password);
      if (success) {
        this.router.navigate(['/dashboard']);
      } else {
        this.errorMessage.set('Invalid email or password.');
      }
    } catch (e: any) {
      this.errorMessage.set(e.message || 'An error occurred during login.');
    } finally {
      this.isLoading.set(false);
    }
  }
}
