import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError, timer, filter, take, mergeMap } from 'rxjs';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';

// Variable globale pour éviter les boucles infinies de refresh
let isRefreshing = false;

export const jwtInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const router = inject(Router);
  
  const token = authService.getAccessToken();
  const isRefreshingToken = authService.isRefreshing();
  
  // Ignorer les requêtes d'authentification publiques pour éviter les boucles et les erreurs de token invalide
  if (req.url.includes('/login/login/') || 
      req.url.includes('/login/register/') || 
      req.url.includes('/login/refresh/')) {
    return next(req);
  }
  
  // Si un refresh est en cours et qu'on n'a pas de token, attendre un peu
  // Cela évite d'envoyer des requêtes avec un token expiré pendant le refresh
  if (isRefreshingToken && !token) {
    // Attendre que le refresh soit terminé (max 2 secondes, check toutes les 100ms)
    return timer(0, 100).pipe(
      take(20), // Maximum 2 secondes (20 * 100ms)
      filter(() => {
        const stillRefreshing = authService.isRefreshing();
        const hasToken = !!authService.getAccessToken();
        // Continuer tant que le refresh est en cours et qu'on n'a pas de token
        return !stillRefreshing || hasToken;
      }),
      take(1), // Prendre le premier qui correspond
      mergeMap(() => {
        const finalToken = authService.getAccessToken();
        let finalReq = req;
        
        if (finalToken) {
          finalReq = req.clone({
            setHeaders: {
              Authorization: `Bearer ${finalToken}`
            }
          });
        }
        
        return next(finalReq);
      }),
      catchError((error: HttpErrorResponse) => {
        return throwError(() => error);
      })
    );
  }
  
  // Ajouter le token JWT si disponible
  if (token) {
    req = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
  }

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      // Si erreur 401 (Unauthorized), essayer de rafraîchir le token
      if (error.status === 401 && (token || authService.getRefreshToken()) && !isRefreshingToken && !isRefreshing) {
        isRefreshing = true;
        authService.isRefreshing.set(true);
        
        return authService.refreshToken().pipe(
          switchMap((response) => {
            isRefreshing = false;
            authService.isRefreshing.set(false);
            // Réessayer la requête avec le nouveau token
            const clonedReq = req.clone({
              setHeaders: {
                Authorization: `Bearer ${response.access}`
              }
            });
            return next(clonedReq);
          }),
          catchError((refreshError) => {
            isRefreshing = false;
            authService.isRefreshing.set(false);
            // Si le refresh échoue, déconnecter l'utilisateur
            console.error('Token refresh failed:', refreshError);
            // Attendre un peu avant de déconnecter pour éviter les déconnexions multiples
            setTimeout(() => {
              authService.logout();
              // Ne naviguer que si on n'est pas déjà sur la page de login
              if (!router.url.includes('/login')) {
                router.navigate(['/login']);
              }
            }, 100);
            return throwError(() => refreshError);
          })
        );
      }
      
      // Si le refresh est en cours et qu'on a une erreur 401, ne pas déconnecter
      // Attendre que le refresh soit terminé
      if (error.status === 401 && (isRefreshingToken || isRefreshing)) {
        console.log('Refresh in progress, ignoring 401 error');
        // Ne pas traiter l'erreur comme fatale, le refresh devrait résoudre le problème
        return throwError(() => error);
      }
      
      return throwError(() => error);
    })
  );
};

