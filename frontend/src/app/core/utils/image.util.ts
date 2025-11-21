import { environment } from '../../../environments/environment';

/**
 * Construit l'URL complète d'une image depuis le backend
 * @param imageUrl URL relative ou absolue de l'image
 * @returns URL absolue de l'image
 */
export function getImageUrl(imageUrl: string | null | undefined): string | null {
  if (!imageUrl) {
    return null;
  }

  // Si l'URL est déjà absolue (commence par http:// ou https://), la retourner telle quelle
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
    return imageUrl;
  }

  // Construire l'URL de base du backend (sans /api)
  const apiBaseUrl = environment.apiUrl || 'http://localhost:8000/api';
  const backendBaseUrl = apiBaseUrl.replace('/api', '');

  // Si l'URL commence déjà par /media/, l'ajouter directement
  if (imageUrl.startsWith('/media/')) {
    return `${backendBaseUrl}${imageUrl}`;
  }

  // Si l'URL ne commence pas par /, l'ajouter
  const normalizedUrl = imageUrl.startsWith('/') ? imageUrl : `/${imageUrl}`;

  // Si l'URL ne commence pas par /media/, l'ajouter
  if (!normalizedUrl.startsWith('/media/')) {
    return `${backendBaseUrl}/media${normalizedUrl}`;
  }

  return `${backendBaseUrl}${normalizedUrl}`;
}

