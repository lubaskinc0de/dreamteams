import type { ApiError } from "~/types/api";

/**
 * Composable for centralized error handling across the application
 * Provides consistent error message mapping and formatting
 */
export const useErrorHandler = () => {
  /**
   * Map of error codes to user-friendly messages
   * These will be replaced with i18n keys once i18n is integrated
   */
  const ERROR_MESSAGES: Record<string, string> = {
    UNAUTHORIZED: "Пожалуйста, войдите в систему",
    USER_NOT_FOUND: "Пользователь не найден",
    AUTH_USER_ALREADY_EXISTS: "Вы уже зарегистрированы как арендодатель",
    VALIDATION_ERROR: "Проверьте правильность заполнения формы",
    ACCESS_DENIED: "Доступ запрещен",
    INTERNAL_SERVER_ERROR: "Внутренняя ошибка сервера. Попробуйте позже",
    NETWORK_ERROR: "Ошибка сети. Проверьте интернет-соединение",
    UNKNOWN_ERROR: "Произошла неизвестная ошибка",
  };

  /**
   * Get user-friendly error message from API error object
   * @param error - The API error object or null
   * @returns User-friendly error message or null if no error
   */
  const getErrorMessage = (error: ApiError | null): string | null => {
    if (!error) return null;

    const message =
      ERROR_MESSAGES[error.code] ||
      error.message ||
      ERROR_MESSAGES["UNKNOWN_ERROR"];
    return message || null;
  };

  /**
   * Check if error code indicates user should take specific action
   * @param error - The API error object
   * @param code - The error code to check
   * @returns True if error code matches
   */
  const isErrorCode = (error: ApiError | null, code: string): boolean => {
    return error?.code === code;
  };

  /**
   * Get error metadata if available
   * @param error - The API error object
   * @returns Error metadata or null
   */
  const getErrorMeta = (error: ApiError | null): Record<string, any> | null => {
    return error?.meta || null;
  };

  return {
    getErrorMessage,
    isErrorCode,
    getErrorMeta,
    ERROR_MESSAGES,
  };
};
