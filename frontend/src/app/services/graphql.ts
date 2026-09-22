import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { AuthService } from './auth.service';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class Graphql {
  private readonly http = inject(HttpClient);
  private readonly authService = inject(AuthService);
  private readonly endpoint = `${environment.apiBaseUrl}/graphql`;

  async query<T>(query: string, variables: any = {}): Promise<T> {
    try {
      // 1. Get access token from Supabase Auth
      const token = await this.authService.getAccessToken();
      
      // 2. Set Authorization header if user is authenticated
      let headers = new HttpHeaders();
      if (token) {
        headers = headers.set('Authorization', `Bearer ${token}`);
      }

      // 3. Make POST request
      const response = await firstValueFrom(
        this.http.post<any>(this.endpoint, { query, variables }, { headers })
      );
      
      if (response && response.errors) {
        throw new Error(response.errors[0].message || 'GraphQL Query Error');
      }
      
      return response.data as T;
    } catch (error: any) {
      console.error('GraphQL HTTP request failed:', error);
      throw error;
    }
  }

  async mutate<T>(mutation: string, variables: any = {}): Promise<T> {
    return this.query<T>(mutation, variables);
  }
}
