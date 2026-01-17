/**
 * Composable for managing onboarding flow
 * Handles onboarding completion
 */
export const useOnboarding = () => {
  const router = useRouter();
  const { checkAuthStatus } = useAuth();

  /**
   * Complete onboarding after successful registration
   * Re-checks auth status and redirects to profile
   */
  const completeOnboarding = async () => {
    await checkAuthStatus();
    router.push('/me');
  };

  return {
    completeOnboarding,
  };
};
