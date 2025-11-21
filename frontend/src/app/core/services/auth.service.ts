import { Injectable, inject, signal, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { Router } from '@angular/router';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, tap, catchError, throwError } from 'rxjs';
import { ApiService } from './api.service';
import { User, LoginRequest, LoginResponse, TokenRefresh, TokenRefreshResponse } from '../models/user.model';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private api = inject(ApiService);
  private http = inject(HttpClient);
  private router = inject(Router);
  private platformId = inject(PLATFORM_ID);
  private apiBaseUrl = environment.apiUrl || 'http://localhost:8000/api';
  
  private readonly ACCESS_TOKEN_KEY = 'access_token';
  private readonly REFRESH_TOKEN_KEY = 'refresh_token';
  private readonly USER_KEY = 'current_user';

  currentUser = signal<User | null>(null);
  isAuthenticated = signal<boolean>(false);
  isRefreshing = signal<boolean>(false);

  private get storage(): Storage | null {
    // Utiliser localStorage pour que la session persiste après un rafraîchissement de page
    // localStorage persiste même après la fermeture de l'onglet (contrairement à sessionStorage)
    return isPlatformBrowser(this.platformId) ? localStorage : null;
  }

  constructor() {
    if (isPlatformBrowser(this.platformId)) {
      // Restaurer la session au démarrage
      try {
        this.loadUserFromStorage();
        console.log('AuthService initialized, isAuthenticated:', this.isAuthenticated());
      } catch (error) {
        console.error('Error initializing AuthService:', error);
      }
    }
  }

  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.api.post<LoginResponse>('login/login/', credentials).pipe(
      tap(response => {
        this.setTokens(response.access, response.refresh);
        this.setUser(response.user);
        this.isAuthenticated.set(true);
      }),
      catchError(error => {
        console.error('Login error:', error);
        return throwError(() => error);
      })
    );
  }

  register(userData: any): Observable<LoginResponse> {
    return this.api.post<LoginResponse>('login/register/', userData).pipe(
      tap(response => {
        this.setTokens(response.access, response.refresh);
        this.setUser(response.user);
        this.isAuthenticated.set(true);
      }),
      catchError(error => {
        console.error('Register error:', error);
        return throwError(() => error);
      })
    );
  }

  logout(): void {
    // Nettoyer le localStorage
    if (this.storage) {
      this.storage.removeItem(this.ACCESS_TOKEN_KEY);
      this.storage.removeItem(this.REFRESH_TOKEN_KEY);
      this.storage.removeItem(this.USER_KEY);
    }
    this.currentUser.set(null);
    this.isAuthenticated.set(false);
    this.router.navigate(['/login']);
  }

  refreshToken(): Observable<TokenRefreshResponse> {
    const refreshToken = this.storage?.getItem(this.REFRESH_TOKEN_KEY);
    if (!refreshToken) {
      return throwError(() => new Error('No refresh token'));
    }

    this.isRefreshing.set(true);
    // Utiliser HttpClient directement pour éviter de passer par l'interceptor
    // Cela évite les dépendances circulaires lors du refresh au démarrage
    const headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });
    
    return this.http.post<TokenRefreshResponse>(
      `${this.apiBaseUrl}/login/refresh/`,
      { refresh: refreshToken },
      { headers }
    ).pipe(
      tap(response => {
        if (this.storage) {
          this.storage.setItem(this.ACCESS_TOKEN_KEY, response.access);
        }
        this.isRefreshing.set(false);
        this.isAuthenticated.set(true);
      }),
      catchError(error => {
        this.isRefreshing.set(false);
        this.logout();
        return throwError(() => error);
      })
    );
  }

  getAccessToken(): string | null {
    return this.storage?.getItem(this.ACCESS_TOKEN_KEY) ?? null;
  }

  getRefreshToken(): string | null {
    return this.storage?.getItem(this.REFRESH_TOKEN_KEY) ?? null;
  }

  getUser(): Observable<User> {
    return this.api.get<User>('users/custom-users/me/').pipe(
      tap(user => {
        this.setUser(user);
      })
    );
  }

  updateUser(data: Omit<Partial<User>, 'profile_picture'> & { profile_picture?: File | null }): Observable<User> {
    const profilePicture: File | null | undefined = data.profile_picture;
    
    // Si une image est fournie (File), utiliser FormData
    if (profilePicture !== null && profilePicture !== undefined) {
      // Vérifier que c'est bien un File
      if (profilePicture instanceof File) {
        const formData = new FormData();
        Object.keys(data).forEach(key => {
          if (key === 'profile_picture' && profilePicture instanceof File) {
            formData.append(key, profilePicture);
          } else if (data[key as keyof typeof data] !== undefined && key !== 'profile_picture') {
            const value = data[key as keyof typeof data];
            if (value !== null && value !== undefined) {
              // Vérifier si c'est un objet (mais pas File)
              if (typeof value === 'object') {
                // Utiliser une vérification plus sûre pour File
                const isFile = (val: any): val is File => {
                  return val instanceof File || 
                         (typeof val === 'object' && 
                          val !== null && 
                          'constructor' in val && 
                          val.constructor?.name === 'File');
                };
                if (isFile(value)) {
                  formData.append(key, value);
                } else {
                  formData.append(key, JSON.stringify(value));
                }
              } else {
                formData.append(key, String(value));
              }
            }
          }
        });
        return this.api.patchFormData<User>('users/custom-users/me/', formData).pipe(
          tap(user => {
            this.setUser(user);
          })
        );
      }
    }
    
    // Pour supprimer la photo, envoyer null
    if (profilePicture === null) {
      return this.api.patch<User>('users/custom-users/me/', { profile_picture: null } as any).pipe(
        tap(user => {
          this.setUser(user);
        })
      );
    }
    
    // Sinon, utiliser PATCH normal (sans photo)
    const { profile_picture, ...dataWithoutPhoto } = data;
    return this.api.patch<User>('users/custom-users/me/', dataWithoutPhoto).pipe(
      tap(user => {
        this.setUser(user);
      })
    );
  }

  private setTokens(access: string, refresh: string): void {
    // Utiliser localStorage pour que la session persiste après un rafraîchissement de page
    if (this.storage) {
      this.storage.setItem(this.ACCESS_TOKEN_KEY, access);
      this.storage.setItem(this.REFRESH_TOKEN_KEY, refresh);
    }
  }

  private setUser(user: User): void {
    this.currentUser.set(user);
    // Utiliser localStorage pour que la session persiste après un rafraîchissement de page
    if (this.storage) {
      this.storage.setItem(this.USER_KEY, JSON.stringify(user));
    }
  }

  private loadUserFromStorage(): void {
    if (!this.storage) return;
    
    const token = this.storage.getItem(this.ACCESS_TOKEN_KEY);
    const refreshToken = this.storage.getItem(this.REFRESH_TOKEN_KEY);
    const userStr = this.storage.getItem(this.USER_KEY);

    // Restaurer la session si on a au moins un token (access ou refresh)
    // L'utilisateur peut être restauré même sans userStr (sera récupéré via API si nécessaire)
    if (token || refreshToken) {
      // Restaurer l'utilisateur si disponible
      if (userStr) {
        try {
          const user = JSON.parse(userStr);
          this.currentUser.set(user);
        } catch (error) {
          console.error('Error parsing user from storage:', error);
          // Ne pas déconnecter si le parsing échoue, on peut récupérer l'utilisateur via API
        }
      }
      
      // Vérifier si le token est valide ou si on a un refresh token
      if (token && !this.isTokenExpired(token)) {
        // Token valide, restaurer la session complète
        this.isAuthenticated.set(true);
        console.log('Token valid, session restored');
      } else if (refreshToken) {
        // Token expiré ou absent mais refresh token disponible
        // Considérer comme authentifié immédiatement
        this.isAuthenticated.set(true);
        
        if (token && this.isTokenExpired(token)) {
          console.log('Access token expired, refreshing immediately...');
          // Utiliser setTimeout pour retarder le refresh après l'initialisation complète
          // Cela évite les dépendances circulaires tout en rafraîchissant le token rapidement
          setTimeout(() => {
            this.refreshToken().subscribe({
              next: () => {
                console.log('Token refreshed successfully on startup');
              },
              error: (error) => {
                console.error('Failed to refresh token on startup:', error);
                // Ne pas déconnecter immédiatement, l'interceptor gérera ça
              }
            });
          }, 0);
        } else if (!token) {
          console.log('No access token, refreshing immediately...');
          // Utiliser setTimeout pour retarder le refresh après l'initialisation complète
          setTimeout(() => {
            this.refreshToken().subscribe({
              next: () => {
                console.log('Token refreshed successfully on startup');
              },
              error: (error) => {
                console.error('Failed to refresh token on startup:', error);
                // Ne pas déconnecter immédiatement, l'interceptor gérera ça
              }
            });
          }, 0);
        }
      } else {
        // Aucun token valide, nettoyer la session
        console.log('No valid tokens found, logging out');
        this.logout();
      }
    } else if (userStr) {
      // Si on a un utilisateur mais pas de token, nettoyer la session
      console.log('User found but no tokens, logging out');
      this.logout();
    }
  }

  /**
   * Vérifie si un token JWT est expiré
   */
  isTokenExpired(token: string | null): boolean {
    if (!token) return true;
    try {
      // Un JWT est composé de 3 parties séparées par des points : header.payload.signature
      const payload = JSON.parse(atob(token.split('.')[1]));
      const expirationTime = payload.exp * 1000; // Convertir en millisecondes
      const currentTime = Date.now();
      
      // Ajouter un buffer de 5 minutes pour rafraîchir avant l'expiration réelle
      const bufferTime = 5 * 60 * 1000; // 5 minutes en millisecondes
      
      return currentTime >= (expirationTime - bufferTime);
    } catch (error) {
      console.error('Error decoding token:', error);
      return true; // En cas d'erreur, considérer le token comme expiré
    }
  }

  checkAuth(): boolean {
    // Toujours lire directement depuis le storage pour être sûr que la session est à jour
    // Cela garantit que même si loadUserFromStorage() n'a pas fini dans le constructeur,
    // on vérifie toujours l'état actuel du localStorage
    if (!this.storage) {
      console.log('checkAuth: No storage available (SSR?)');
      return false;
    }
    
    const token = this.storage.getItem(this.ACCESS_TOKEN_KEY);
    const refreshToken = this.storage.getItem(this.REFRESH_TOKEN_KEY);
    const userStr = this.storage.getItem(this.USER_KEY);
    
    console.log('checkAuth: token exists:', !!token, 'refreshToken exists:', !!refreshToken, 'user exists:', !!userStr, 'isAuthenticated:', this.isAuthenticated());
    
    // Si on a au moins un token (access ou refresh), considérer comme authentifié
    if (token || refreshToken) {
      // Restaurer la session si ce n'est pas déjà fait ou si l'état n'est pas synchronisé
      if (!this.isAuthenticated() || !this.currentUser() || 
          (userStr && !this.currentUser())) {
        console.log('checkAuth: Restoring session from storage');
        this.loadUserFromStorage();
      }
      
      // Vérifier si le token est valide ou si un refresh est en cours
      const hasValidToken = token && !this.isTokenExpired(token);
      const isRefreshingToken = this.isRefreshing();
      
      // Si le token est valide OU un refresh est en cours OU on a un refresh token, autoriser l'accès
      if (hasValidToken || isRefreshingToken || refreshToken) {
        console.log('checkAuth: Has valid tokens or refresh in progress, returning true');
        return true;
      }
      
      // Si le token est expiré mais qu'on a un refresh token, autoriser quand même
      // Le refresh se fera via l'interceptor
      console.log('checkAuth: Token expired but has refresh token, returning true');
      return true;
    }
    
    // Si aucun token trouvé mais qu'on se considère comme authentifié, nettoyer
    if (this.isAuthenticated()) {
      console.log('checkAuth: No tokens found but isAuthenticated is true, cleaning up');
      this.logout();
    }
    
    console.log('checkAuth: No valid tokens found, returning false');
    return false;
  }
}

