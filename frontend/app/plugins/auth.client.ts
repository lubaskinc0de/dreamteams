/**
 * Client-side plugin to initialize authentication on app start
 */
export default defineNuxtPlugin(async () => {
  const { checkAuthStatus } = useAuth();

  // Check authentication status when app loads
  await checkAuthStatus();
});
