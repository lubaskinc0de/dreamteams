/**
 * Global middleware to manage user profile loading
 * Ensures profile is loaded once and cached across route navigation
 * Prevents redundant API calls when navigating between pages
 */
export default defineNuxtRouteMiddleware(async (to, from) => {
  const userStore = useUserStore();

  // Skip profile loading on client-side navigation if already loaded or loading
  if (import.meta.client) {
    // Don't fetch if we already have profile data or if a fetch is in progress
    if (userStore.profile || userStore.loading) {
      return;
    }

    // Fetch profile on client-side navigation
    try {
      await userStore.fetchProfile();
    } catch (error) {
      console.error("Failed to load user profile:", error);
      // Don't block navigation on profile fetch error
      // User will see error handling in the page component
    }
  }
});
