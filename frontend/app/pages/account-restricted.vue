<script setup lang="ts">
import { useBlockedAccount } from "~/composables/useBlockedAccount";

definePageMeta({ layout: false });

const { t, locale } = useI18n();
const { blockedAccount } = useBlockedAccount();
const { logout } = useAuth();
const appealEmail = "structnull@yandex.ru";

useHead({ title: () => t("accountRestricted.title") });

const fallback = computed(() => t("accountRestricted.notProvided"));

const formatBlockedAt = (value: string | null | undefined): string | null => {
  if (!value) {
    return null;
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat(locale.value, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
};

const details = computed(() => [
  {
    label: t("accountRestricted.reason"),
    value: blockedAccount.value?.reason ?? fallback.value,
  },
  {
    label: t("accountRestricted.blockedAt"),
    value: formatBlockedAt(blockedAccount.value?.blocked_at) ?? fallback.value,
  },
]);
</script>

<template>
  <div class="min-h-screen bg-white dark:bg-gray-900">
    <UContainer class="py-12 sm:py-16">
      <div class="mx-auto max-w-3xl">
        <div class="mb-8 flex size-14 items-center justify-center rounded-full bg-error-500/10 text-error-500">
          <UIcon name="i-heroicons-no-symbol" class="size-8" />
        </div>

        <p class="mb-3 text-xs font-semibold uppercase tracking-[0.2em] text-error-500">
          {{ t("accountRestricted.headline") }}
        </p>

        <h1 class="text-3xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-5xl">
          {{ t("accountRestricted.title") }}
        </h1>

        <p class="mt-5 max-w-2xl text-base leading-7 text-gray-600 dark:text-gray-300 sm:text-lg">
          {{ t("accountRestricted.description") }}
        </p>

        <dl class="mt-10 divide-y divide-gray-200 rounded-lg border border-gray-200 bg-white dark:divide-gray-800 dark:border-gray-800 dark:bg-gray-900">
          <div
            v-for="detail in details"
            :key="detail.label"
            class="grid grid-cols-1 gap-2 px-5 py-4 sm:grid-cols-[12rem_1fr] sm:px-6"
          >
            <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
              {{ detail.label }}
            </dt>
            <dd class="break-words text-sm font-semibold text-gray-900 dark:text-white">
              {{ detail.value }}
            </dd>
          </div>
        </dl>

        <UAlert
          class="mt-6"
          color="neutral"
          variant="soft"
          icon="i-heroicons-envelope"
          :title="t('accountRestricted.appealTitle')"
        >
          <template #description>
            <p class="text-sm text-gray-600 dark:text-gray-300">
              {{ t("accountRestricted.appealDescription") }}
            </p>
            <a
              :href="`mailto:${appealEmail}`"
              class="mt-2 inline-flex font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400 dark:hover:text-primary-300"
            >
              {{ appealEmail }}
            </a>
          </template>
        </UAlert>

        <div class="mt-8 flex flex-col gap-3 sm:flex-row">
          <UButton
            to="/legal/terms-of-service"
            color="primary"
            variant="solid"
            size="lg"
            icon="i-heroicons-document-text"
          >
            {{ t("accountRestricted.tosLink") }}
          </UButton>
          <UButton
            color="neutral"
            variant="ghost"
            size="lg"
            icon="i-heroicons-arrow-right-on-rectangle"
            @click="logout"
          >
            {{ t("accountRestricted.signOut") }}
          </UButton>
        </div>
      </div>
    </UContainer>
  </div>
</template>
