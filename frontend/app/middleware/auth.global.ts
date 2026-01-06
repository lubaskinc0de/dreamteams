/**
 * Global authentication middleware
 * Manages authentication flow and onboarding redirects
 * Note: auth.client.ts plugin ensures auth is checked before this runs
 */
export default defineNuxtRouteMiddleware(async (to) => {
  // Skip middleware on server-side
  if (import.meta.server) {
    return;
  }

  const { isAuthenticated, needsOnboarding, hasProfile, isLoading } = useAuth();

  // Wait for auth to finish loading before making any decisions
  if (isLoading.value) {
    await new Promise<void>((resolve) => {
      const unwatch = watch(isLoading, (loading) => {
        if (!loading) {
          unwatch();
          resolve();
        }
      });
    });
  }

  // Define protected routes that require authentication
  const protectedRoutes = ['/profile', '/onboarding', '/competitions'];
  const isProtectedRoute = protectedRoutes.some(route => to.path.startsWith(route));

  const isHomeRoute = to.path === '/';
  const isOnboardingRoute = to.path === '/onboarding';

  // If not authenticated and trying to access protected route, throw 401 error
  if (!isAuthenticated.value && isProtectedRoute) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Unauthorized',
      fatal: true,
    });
  }

  // If authenticated but needs onboarding, redirect to onboarding flow
  if (isAuthenticated.value && needsOnboarding.value && !isOnboardingRoute) {
    return navigateTo('/onboarding', { replace: true });
  }

  // If authenticated and has profile, redirect from home to profile
  if (isAuthenticated.value && hasProfile.value && isHomeRoute) {
    return navigateTo('/profile', { replace: true });
  }

  // If authenticated and has profile, prevent access to onboarding
  if (isAuthenticated.value && hasProfile.value && isOnboardingRoute) {
    return navigateTo('/profile', { replace: true });
  }
});
