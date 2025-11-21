import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { Router } from '@angular/router';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      let errorMessage = 'Une erreur est survenue';

      if (error.error instanceof ErrorEvent) {
        // Erreur côté client
        errorMessage = `Erreur: ${error.error.message}`;
      } else {
        // Erreur côté serveur
        switch (error.status) {
          case 400:
            errorMessage = error.error?.detail || 'Requête invalide';
            break;
          case 401:
            errorMessage = 'Non autorisé. Veuillez vous connecter.';
            break;
          case 403:
            errorMessage = 'Accès refusé. Vous n\'avez pas les permissions nécessaires.';
            break;
          case 404:
            errorMessage = 'Ressource non trouvée';
            break;
          case 500:
            errorMessage = 'Erreur serveur. Veuillez réessayer plus tard.';
            break;
          default:
            errorMessage = error.error?.detail || `Erreur ${error.status}: ${error.message}`;
        }
      }

      console.error('HTTP Error:', errorMessage, error);
      
      // Vous pouvez ajouter ici un service de notification pour afficher l'erreur
      // notificationService.showError(errorMessage);

      return throwError(() => error);
    })
  );
};

