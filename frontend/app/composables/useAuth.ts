/**
 * Composable for authentication management
 * Provides authentication state checking and login/logout functionality
 */
export const useAuth = () => {
  const isAuthenticated = ref<boolean>(false);
  const isLoading = ref<boolean>(true);
  const config = useRuntimeConfig();
  const apiBase = config.public.apiBase;

  /**
   * Check authentication status by trying to fetch user profile
   * This approach avoids direct OAuth endpoint calls from frontend
   */
  const checkAuth = async () => {
    isLoading.value = true;
    try {
      await $fetch(`${apiBase}/users/me`, {
        method: 'GET',
      });

      isAuthenticated.value = true;
    } catch (error: any) {
      // 401 or any other error means not authenticated
      isAuthenticated.value = false;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * Redirect to login page
   * Uses the redirect parameter to return to current page after login
   */
  const login = () => {
    const currentPath = window.location.pathname || '/';
    window.location.href = `${apiBase}/oauth2/sign_in?rd=${encodeURIComponent(currentPath)}`;
  };

  /**
   * Redirect to logout page
   */
  const logout = () => {
    window.location.href = `${apiBase}/oauth2/sign_out?rd=/`;
  };

  // Check authentication on composable initialization
  onMounted(() => {
    checkAuth();
  });

  return {
    isAuthenticated: readonly(isAuthenticated),
    isLoading: readonly(isLoading),
    checkAuth,
    login,
    logout,
  };
};
