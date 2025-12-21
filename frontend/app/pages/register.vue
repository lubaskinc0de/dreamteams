<script setup lang="ts">
const userStore = useUserStore();
const { navigateTo } = useNavigation();
const { t } = useI18n();

// SEO Meta tags
useSeoMeta({
  title: t("seo.register.title"),
  description: t("seo.register.description"),
});

// Redirect if already registered (middleware handles profile loading)
watch(
  () => userStore.isOrganizer,
  (isOrganizer) => {
    if (isOrganizer) {
      navigateTo("/profile");
    }
  },
  { immediate: true },
);
</script>

<template>
  <UPage>
    <div class="max-w-2xl mx-auto">
      <UPageHeader
        :title="t('register.title')"
        :description="t('register.description')"
        :headline="t('register.headline')"
      />
    </div>

    <UPageBody>
      <div class="max-w-2xl mx-auto">
        <OrganizerRegistrationForm />
      </div>
    </UPageBody>
  </UPage>
</template>
