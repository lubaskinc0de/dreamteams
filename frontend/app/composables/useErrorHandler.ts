import type { ApiError } from "~/types/api";

/**
 * Composable for centralized error handling across the application
 * Maps API error codes to i18n translations
 */
export const useErrorHandler = () => {
  const { t } = useI18n();

  /**
   * Get user-friendly error message from API error object.
   * Looks up the error code in i18n (apiErrors.*),
   * falls back to the raw server message, then to a generic unknown error translation.
   */
  const getErrorMessage = (error: ApiError | null): string | null => {
    if (!error) return null;

    const key = `apiErrors.${error.code}`;
    const translated = t(key);

    // t() returns the key itself when there is no matching translation
    if (translated !== key) {
      return translated;
    }

    // Fall back to the server-provided message or a generic fallback
    return error.message || t("apiErrors.UNKNOWN_ERROR");
  };

  /**
   * Check if error code matches a specific code
   */
  const isErrorCode = (error: ApiError | null, code: string): boolean => {
    return error?.code === code;
  };

  /**
   * Get error metadata if available
   */
  const getErrorMeta = (error: ApiError | null): Record<string, any> | null => {
    return error?.meta || null;
  };

  return {
    getErrorMessage,
    isErrorCode,
    getErrorMeta,
  };
};
