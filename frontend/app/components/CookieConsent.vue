<script setup lang="ts">
import { useCookieConsent } from "~/composables/useCookieConsent";

const { t } = useI18n();
const { isUndecided, accept, decline } = useCookieConsent();
const route = useRoute();

// Don't show the banner on the dedicated "cookies required" page — the page
// itself provides the accept button and explanatory copy.
const shouldShow = computed(
  () => isUndecided.value && route.path !== "/cookies-required",
);

const onAccept = () => accept();

const onDecline = () => {
  decline();
  navigateTo("/cookies-required");
};
</script>

<template>
  <ClientOnly>
    <Teleport to="body">
      <div
        v-if="shouldShow"
        class="fixed inset-x-0 bottom-0 p-3 sm:p-4 pointer-events-none"
        style="z-index: 100"
        role="dialog"
        aria-live="polite"
        :aria-label="t('cookieBanner.title')"
      >
        <div
          class="pointer-events-auto mx-auto max-w-4xl rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 shadow-2xl p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center gap-4"
        >
          <div class="flex items-start gap-3 flex-1 min-w-0">
            <UIcon
              name="i-heroicons-cake"
              class="text-primary-500 text-2xl shrink-0 mt-0.5"
              aria-hidden="true"
            />
            <div class="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
              <p class="font-semibold text-gray-900 dark:text-white mb-1">
                {{ t("cookieBanner.title") }}
              </p>
              <p>
                {{ t("cookieBanner.description") }}
                <NuxtLink
                  to="/legal/cookie-policy"
                  class="text-primary-500 hover:text-primary-400 underline"
                >
                  {{ t("cookieBanner.learnMore") }}
                </NuxtLink>
              </p>
            </div>
          </div>

          <div class="flex flex-row gap-2 sm:flex-none shrink-0">
            <UButton
              color="neutral"
              variant="ghost"
              size="md"
              :label="t('cookieBanner.decline')"
              @click="onDecline"
            />
            <UButton
              color="primary"
              variant="solid"
              size="md"
              icon="i-heroicons-check"
              :label="t('cookieBanner.accept')"
              @click="onAccept"
            />
          </div>
        </div>
      </div>
    </Teleport>
  </ClientOnly>
</template>
