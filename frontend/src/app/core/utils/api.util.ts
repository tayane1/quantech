import { PaginatedResponse } from '../interfaces/api.interface';

/**
 * Type pour les réponses paginées flexibles (accepte différents formats)
 */
type AnyPaginatedResponse<T> = {
  results: T[];
  count?: number;
  next?: string | null;
  previous?: string | null;
} | PaginatedResponse<T>;

/**
 * Normalise une réponse API qui peut être soit paginée, soit un tableau direct
 * @param response Réponse de l'API (peut être paginée ou tableau direct)
 * @returns Tableau des éléments
 */
export function normalizeApiResponse<T>(
  response: AnyPaginatedResponse<T> | T[] | null | undefined
): T[] {
  if (!response) {
    return [];
  }

  // Si la réponse est directement un tableau
  if (Array.isArray(response)) {
    return response;
  }

  // Si la réponse est paginée avec results
  if (response && typeof response === 'object' && 'results' in response) {
    const results = (response as any).results;
    if (Array.isArray(results)) {
      return results;
    }
  }

  // Format inattendu - retourner un tableau vide et logger un avertissement
  console.warn('Unexpected response format:', response);
  return [];
}

