<script setup lang="ts">
import { useOnboarding } from "~/composables/useOnboarding";

const { t } = useI18n();
const { completeOnboarding } = useOnboarding();

// SEO Meta tags
useSeoMeta({
  title: t("seo.onboarding.title"),
  description: t("seo.onboarding.description"),
});

definePageMeta({
  layout: "onboarding",
});

const showForm = ref(false);
const organizerStore = useOrganizerStore();

const startRegistration = () => {
  showForm.value = true;
};

// Watch for successful registration to complete onboarding
watch(
  () => organizerStore.registrationSuccess,
  async (success) => {
    if (success) {
      await completeOnboarding();
    }
  }
);
</script>

<template>
  <UPage>
    <UPageBody>
      <div class="flex items-center justify-center px-4 min-h-[60vh]">
        <div class="w-full max-w-md mx-auto">
          <!-- Role Selection -->
          <div v-if="!showForm" class="text-center">
            <!-- Icon -->
            <div class="inline-flex p-4 rounded-2xl bg-primary-500/10 mb-6">
              <UIcon
                name="i-heroicons-user-circle"
                class="text-6xl text-primary-500"
              />
            </div>

            <!-- Title -->
            <h1 class="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              {{ t('onboarding.roleSelection.title') }}
            </h1>

            <p class="text-muted mb-4 text-sm">
              {{ t('onboarding.roleSelection.description') }}
            </p>
            <div class="bg-primary-50 dark:bg-primary-950/30 rounded-lg p-4 mb-6 text-left">
              <div class="flex items-start gap-3">
                <UIcon name="i-heroicons-information-circle" class="text-primary-500 text-lg mt-0.5 shrink-0" />
                <p class="text-sm text-toned">
                  {{ t('onboarding.roleSelection.inviteHint') }}
                </p>
              </div>
            </div>

            <!-- Button -->
            <UButton
              @click="startRegistration"
              color="primary"
              size="lg"
              icon="i-heroicons-building-office"
              class="shadow-lg hover:shadow-xl transition-all"
            >
              {{ t('onboarding.roleSelection.organizerButton') }}
            </UButton>
          </div>

          <!-- Registration Form -->
          <div v-else class="animate-fade-in">
            <div class="mb-6 text-center">
              <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                {{ t("register.title") }}
              </h2>
            </div>

            <OrganizerRegistrationForm />
          </div>
        </div>
      </div>
    </UPageBody>
  </UPage>
</template>
