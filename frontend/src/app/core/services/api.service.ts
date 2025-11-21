import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private http = inject(HttpClient);
  private baseUrl = environment.apiUrl || 'http://localhost:8000/api';

  private getHeaders(skipAuth: boolean = false): HttpHeaders {
    let headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });
    
    // Ne pas ajouter le token pour les endpoints d'authentification publics
    if (!skipAuth) {
      // Utiliser localStorage pour récupérer le token
      const token = localStorage.getItem('access_token');
      if (token) {
        headers = headers.set('Authorization', `Bearer ${token}`);
      }
    }
    
    return headers;
  }

  get<T>(endpoint: string, params?: any): Observable<T> {
    let httpParams = new HttpParams();
    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined) {
          httpParams = httpParams.set(key, params[key]);
        }
      });
    }
    
    return this.http.get<T>(`${this.baseUrl}/${endpoint}`, {
      headers: this.getHeaders(),
      params: httpParams
    });
  }

  post<T>(endpoint: string, data: any, skipAuth: boolean = false): Observable<T> {
    // Ne pas ajouter le token pour les endpoints d'authentification publics
    const isAuthEndpoint = endpoint.includes('/login/login/') || 
                          endpoint.includes('/login/register/') ||
                          endpoint.includes('/login/refresh/');
    
    return this.http.post<T>(`${this.baseUrl}/${endpoint}`, data, {
      headers: this.getHeaders(skipAuth || isAuthEndpoint)
    });
  }

  put<T>(endpoint: string, data: any): Observable<T> {
    return this.http.put<T>(`${this.baseUrl}/${endpoint}`, data, {
      headers: this.getHeaders()
    });
  }

  patch<T>(endpoint: string, data: any): Observable<T> {
    return this.http.patch<T>(`${this.baseUrl}/${endpoint}`, data, {
      headers: this.getHeaders()
    });
  }

  delete<T>(endpoint: string): Observable<T> {
    return this.http.delete<T>(`${this.baseUrl}/${endpoint}`, {
      headers: this.getHeaders()
    });
  }

  postFormData<T>(endpoint: string, formData: FormData, skipAuth: boolean = false): Observable<T> {
    let headers = new HttpHeaders();
    // Ne pas définir Content-Type, le navigateur le fera automatiquement avec le boundary pour FormData
    
    // Ne pas ajouter le token pour les endpoints d'authentification publics
    if (!skipAuth) {
      // Utiliser localStorage pour récupérer le token
      const token = localStorage.getItem('access_token');
      if (token) {
        headers = headers.set('Authorization', `Bearer ${token}`);
      }
    }
    
    return this.http.post<T>(`${this.baseUrl}/${endpoint}`, formData, {
      headers
    });
  }

  patchFormData<T>(endpoint: string, formData: FormData, skipAuth: boolean = false): Observable<T> {
    let headers = new HttpHeaders();
    
    // Ne pas ajouter le token pour les endpoints d'authentification publics
    if (!skipAuth) {
      // Utiliser localStorage pour récupérer le token
      const token = localStorage.getItem('access_token');
      if (token) {
        headers = headers.set('Authorization', `Bearer ${token}`);
      }
    }
    
    return this.http.patch<T>(`${this.baseUrl}/${endpoint}`, formData, {
      headers
    });
  }
}
