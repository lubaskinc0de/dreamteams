import { useCookieConsent } from "~/composables/useCookieConsent";
import { useBlockedAccount } from "~/composables/useBlockedAccount";

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

  // Cookie consent gate: if the user explicitly declined, keep them on the
  // "cookies required" page until they accept. Legal pages stay reachable so
  // they can review the policy before deciding.
  const { isDeclined } = useCookieConsent();
  const cookieAllowed = to.path === "/cookies-required" || to.path.startsWith("/legal");
  if (isDeclined.value && !cookieAllowed) {
    return navigateTo("/cookies-required", { replace: true });
  }

  const { isAuthenticated, needsOnboarding, hasProfile, isLoading } = useAuth();
  const { isAccountBlocked } = useBlockedAccount();

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
  const protectedRoutes = ['/me', '/onboarding', '/admin', '/explore'];
  const isProtectedRoute = protectedRoutes.some(route => to.path.startsWith(route));

  const isHomeRoute = to.path === '/';
  const isOnboardingRoute = to.path === '/onboarding';
  const isAccountRestrictedRoute = to.path === "/account-restricted";
  const isAdminRoute = to.path.startsWith('/admin');
  const isExploreRoute = to.path.startsWith('/explore');
  const isSuperuserRegisterRoute = to.path.startsWith('/register-superuser');
  const isPublicInfoRoute = to.path.startsWith('/legal') || to.path === '/cookies-required';

  if (isAccountBlocked.value && !isAccountRestrictedRoute && !isPublicInfoRoute) {
    return navigateTo("/account-restricted", { replace: true });
  }

  if (!isAccountBlocked.value && isAccountRestrictedRoute) {
    return navigateTo(isAuthenticated.value && hasProfile.value ? "/me" : "/", { replace: true });
  }

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

  // /explore is participant-only (mirrors backend 403 for non-participants)
  if (isAuthenticated.value && isExploreRoute && !userStore.isParticipant) {
    throw createError({
      statusCode: 403,
      statusMessage: 'Forbidden',
      fatal: true,
    });
  }

  // Participants get a dedicated /explore browse page; redirect them away
  // from the generic anon /competitions preview to keep navigation coherent.
  if (isAuthenticated.value && userStore.isParticipant && to.path === '/competitions') {
    return navigateTo('/explore', { replace: true });
  }

  // If authenticated but needs onboarding, redirect to onboarding flow.
  // Admins are allowed to visit /admin even without a role (to issue themselves an invite first).
  if (isAuthenticated.value && needsOnboarding.value && !isOnboardingRoute && !isSuperuserRegisterRoute && !isPublicInfoRoute && !(isAdminRoute && userStore.isAdmin)) {
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
