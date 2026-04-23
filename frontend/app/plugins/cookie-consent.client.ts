import { useCookieConsent } from "~/composables/useCookieConsent";

export default defineNuxtPlugin(() => {
  const { load } = useCookieConsent();
  load();
});
