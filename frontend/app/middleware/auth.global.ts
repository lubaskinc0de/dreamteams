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
  const protectedRoutes = ['/me', '/onboarding', '/admin'];
  const isProtectedRoute = protectedRoutes.some(route => to.path.startsWith(route));

  const isHomeRoute = to.path === '/';
  const isOnboardingRoute = to.path === '/onboarding';
  const isAdminRoute = to.path.startsWith('/admin');
  const isSuperuserRegisterRoute = to.path.startsWith('/register-superuser');

  // If not authenticated and trying to access protected route, throw 401 error
  if (!isAuthenticated.value && isProtectedRoute) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Unauthorized',
      fatal: true,
    });
  }

  const userStore = useUserStore();

  // If authenticated but not admin, deny access to admin routes
  if (isAuthenticated.value && isAdminRoute && !userStore.isAdmin) {
    throw createError({
      statusCode: 403,
      statusMessage: 'Forbidden',
      fatal: true,
    });
  }

  // If authenticated but needs onboarding, redirect to onboarding flow.
  // Admins are allowed to visit /admin even without a role (to issue themselves an invite first).
  if (isAuthenticated.value && needsOnboarding.value && !isOnboardingRoute && !isSuperuserRegisterRoute && !(isAdminRoute && userStore.isAdmin)) {
    return navigateTo('/onboarding', { replace: true });
  }

  // If authenticated and has profile, redirect from home to profile
  if (isAuthenticated.value && hasProfile.value && isHomeRoute) {
    return navigateTo('/me', { replace: true });
  }

  // If authenticated and has profile, prevent access to onboarding
  if (isAuthenticated.value && hasProfile.value && isOnboardingRoute) {
    return navigateTo('/me', { replace: true });
  }
});
