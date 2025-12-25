/**
 * Composable for authentication management
 * Provides authentication state checking and login/logout functionality
 */
export const useAuth = () => {
  const isAuthenticated = useState<boolean>('auth-isAuthenticated', () => false);
  const needsOnboarding = useState<boolean>('auth-needsOnboarding', () => false);
  const hasProfile = useState<boolean>('auth-hasProfile', () => false);
  const isLoading = useState<boolean>('auth-isLoading', () => true);
  const config = useRuntimeConfig();
  const apiBase = config.public.apiBase;
  const api = useApi();
  const userStore = useUserStore();

  /**
   * Check authentication status via OAuth2 endpoint
   * If authenticated, fetch user profile to determine onboarding state
   */
  const checkAuthStatus = async () => {
    isLoading.value = true;
    try {
      // Step 1: Check OAuth2 authentication
      const authenticated = await api.checkAuth();
      isAuthenticated.value = authenticated;

      if (!authenticated) {
        needsOnboarding.value = false;
        hasProfile.value = false;
        return;
      }

      // Step 2: If authenticated, check if user has profile
      const { data, error } = await api.getUserProfile();

      if (error) {
        // 401 or 404 USER_HAS_NO_ROLE means user is in Keycloak but hasn't created profile
        if (error.code === 'UNAUTHORIZED' || error.code === 'USER_HAS_NO_ROLE') {
          needsOnboarding.value = true;
          hasProfile.value = false;
        } else {
          // Other errors - treat as not having profile
          needsOnboarding.value = true;
          hasProfile.value = false;
        }
      } else if (data) {
        // User has profile
        userStore.profile = data;
        needsOnboarding.value = false;
        hasProfile.value = true;
      }
    } catch (error: any) {
      console.error('Error checking auth status:', error);
      isAuthenticated.value = false;
      needsOnboarding.value = false;
      hasProfile.value = false;
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

  return {
    isAuthenticated,
    needsOnboarding,
    hasProfile,
    isLoading,
    checkAuthStatus,
    login,
    logout,
  };
};
