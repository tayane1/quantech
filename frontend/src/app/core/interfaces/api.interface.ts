/**
 * Interface commune pour les réponses paginées de l'API
 */
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

/**
 * Interface commune pour les réponses de l'API avec un seul résultat
 */
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

/**
 * Interface commune pour les erreurs de l'API
 */
export interface ApiError {
  detail?: string;
  message?: string;
  errors?: Record<string, string[]>;
  [key: string]: any;
}

