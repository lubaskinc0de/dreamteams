export type CookieConsentChoice = "accepted" | "declined";

const STORAGE_KEY = "dreamteams-cookie-consent";

export const useCookieConsent = () => {
  const choice = useState<CookieConsentChoice | null>("cookie-consent", () => null);

  const load = () => {
    if (!import.meta.client) return;
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (raw === "accepted" || raw === "declined") {
      choice.value = raw;
    } else {
      choice.value = null;
    }
  };

  const accept = () => {
    if (!import.meta.client) return;
    window.localStorage.setItem(STORAGE_KEY, "accepted");
    choice.value = "accepted";
  };

  const decline = () => {
    if (!import.meta.client) return;
    window.localStorage.setItem(STORAGE_KEY, "declined");
    choice.value = "declined";
  };

  const reset = () => {
    if (!import.meta.client) return;
    window.localStorage.removeItem(STORAGE_KEY);
    choice.value = null;
  };

  const isUndecided = computed(() => choice.value === null);
  const isAccepted = computed(() => choice.value === "accepted");
  const isDeclined = computed(() => choice.value === "declined");

  return { choice, load, accept, decline, reset, isUndecided, isAccepted, isDeclined };
};
