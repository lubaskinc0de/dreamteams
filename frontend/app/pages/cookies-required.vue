<script setup lang="ts">
import type { ButtonProps } from "@nuxt/ui";
import { useCookieConsent } from "~/composables/useCookieConsent";

definePageMeta({ layout: "default" });

const { t } = useI18n();
const { accept } = useCookieConsent();

useHead({ title: () => t("cookieBanner.requiredTitle") });

const onAccept = () => {
  accept();
  navigateTo("/");
};

const links = computed<ButtonProps[]>(() => [
  {
    label: t("cookieBanner.accept"),
    icon: "i-heroicons-check-circle",
    color: "primary",
    size: "xl",
    onClick: onAccept,
  },
  {
    label: t("cookieBanner.readPolicy"),
    icon: "i-heroicons-document-text",
    color: "neutral",
    variant: "ghost",
    size: "xl",
    to: "/legal/cookie-policy",
  },
]);
</script>

<template>
  <UPageHero
    :headline="t('cookieBanner.requiredHeadline')"
    :title="t('cookieBanner.requiredTitle')"
    :description="t('cookieBanner.requiredDescription')"
    :links="links"
    orientation="vertical"
  />
</template>
