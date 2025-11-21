import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { firstValueFrom, timer, filter, take, timeout, catchError, of, race } from 'rxjs';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  // Toujours vérifier directement depuis le storage
  const token = authService.getAccessToken();
  const refreshToken = authService.getRefreshToken();
  
  // Si aucun token, rediriger vers login
  if (!token && !refreshToken) {
    if (!state.url.includes('/login')) {
      router.navigate(['/login'], { queryParams: { returnUrl: state.url } });
    }
    return false;
  }
  
  // Restaurer la session si nécessaire
  authService.checkAuth();
  
  // Vérifier si le token est expiré ou si un refresh est nécessaire
  const tokenExpired = authService.isTokenExpired(token);
  const isRefreshing = authService.isRefreshing();
  const needsRefresh = tokenExpired || !token;
  
  // Si un refresh est nécessaire ou en cours, attendre qu'il soit terminé
  if ((needsRefresh || isRefreshing) && refreshToken) {
    console.log('Guard: Token needs refresh, waiting...', { tokenExpired, isRefreshing, needsRefresh, hasToken: !!token });
    
    // Démarrer le refresh si pas déjà en cours
    // Le refresh pourrait ne pas être encore démarré car il utilise setTimeout(0) dans loadUserFromStorage
    if (!isRefreshing && needsRefresh) {
      console.log('Guard: Starting token refresh...');
      authService.refreshToken().subscribe({
        next: () => {
          console.log('Guard: Token refreshed successfully');
        },
        error: (error) => {
          console.error('Guard: Failed to refresh token:', error);
          if (!state.url.includes('/login')) {
            router.navigate(['/login'], { queryParams: { returnUrl: state.url } });
          }
        }
      });
    }
    
    // Attendre que le refresh soit terminé (max 2 secondes)
    // Utiliser race entre le timer et la condition de succès
    const checkCondition = () => {
      const stillRefreshing = authService.isRefreshing();
      const currentToken = authService.getAccessToken();
      const hasValidToken = !!currentToken && !authService.isTokenExpired(currentToken);
      console.log('Guard waiting:', { stillRefreshing, hasValidToken, hasToken: !!currentToken });
      return !stillRefreshing && hasValidToken;
    };
    
    return firstValueFrom(
      race(
        // Condition de succès : refresh terminé et token valide
        timer(0, 100).pipe(
          filter(() => checkCondition()),
          take(1)
        ),
        // Timeout après 2 secondes
        timer(2000).pipe(
          take(1),
          catchError(() => of(null))
        )
      )
    ).then(() => {
      console.log('Guard: Refresh check completed');
      // Vérifier à nouveau après l'attente
      const finalAuth = authService.checkAuth();
      const finalToken = authService.getAccessToken();
      const finalTokenValid = finalToken && !authService.isTokenExpired(finalToken);
      console.log('Guard: Final auth check:', { finalAuth, hasToken: !!finalToken, tokenValid: finalTokenValid });
      
      // Autoriser seulement si authentifié ET token valide OU si on a un refresh token (le refresh se fera via l'interceptor)
      if ((finalAuth && finalTokenValid) || refreshToken) {
        console.log('Guard: Allowing access');
        return true;
      }
      
      if (!state.url.includes('/login')) {
        console.log('Guard: Redirecting to login');
        router.navigate(['/login'], { queryParams: { returnUrl: state.url } });
      }
      return false;
    }).catch((error) => {
      console.log('Guard error:', error);
      // En cas d'erreur/timeout, vérifier quand même
      const finalAuth = authService.checkAuth();
      const finalToken = authService.getAccessToken();
      const finalTokenValid = finalToken && !authService.isTokenExpired(finalToken);
      const hasRefreshToken = !!authService.getRefreshToken();
      
      // Autoriser si authentifié ET token valide OU si on a un refresh token
      if ((finalAuth && finalTokenValid) || hasRefreshToken) {
        console.log('Guard: Allowing access after error');
        return true;
      }
      
      if (!state.url.includes('/login')) {
        router.navigate(['/login'], { queryParams: { returnUrl: state.url } });
      }
      return false;
    });
  }

  // Si le token est valide, autoriser immédiatement
  console.log('Guard: Token valid, allowing access');
  return true;
};

