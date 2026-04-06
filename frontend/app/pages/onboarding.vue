<script setup lang="ts">
import { useOnboarding } from "~/composables/useOnboarding";
import { useParticipantStore } from "~/stores/participant";

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

const showOrganizerForm = ref(false);
const showParticipantForm = ref(false);
const organizerStore = useOrganizerStore();
const participantStore = useParticipantStore();

const startOrganizerRegistration = () => {
  showOrganizerForm.value = true;
  showParticipantForm.value = false;
};

const startParticipantRegistration = () => {
  showParticipantForm.value = true;
  showOrganizerForm.value = false;
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

watch(
  () => participantStore.registrationSuccess,
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
          <div v-if="!showOrganizerForm && !showParticipantForm" class="text-center">
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

            <!-- Buttons -->
            <div class="flex flex-col sm:flex-row gap-3 justify-center">
              <UButton
                @click="startParticipantRegistration"
                color="primary"
                size="lg"
                icon="i-heroicons-user"
                class="shadow-lg hover:shadow-xl transition-all"
              >
                {{ t('onboarding.roleSelection.participantButton') }}
              </UButton>

              <UButton
                @click="startOrganizerRegistration"
                color="neutral"
                variant="outline"
                size="lg"
                icon="i-heroicons-building-office"
                class="shadow-lg hover:shadow-xl transition-all"
              >
                {{ t('onboarding.roleSelection.organizerButton') }}
              </UButton>
            </div>
          </div>

          <!-- Organizer Registration Form -->
          <div v-else-if="showOrganizerForm" class="animate-fade-in">
            <div class="mb-6 text-center">
              <UButton
                @click="showOrganizerForm = false"
                icon="i-heroicons-arrow-left"
                color="neutral"
                variant="ghost"
                size="sm"
                class="mb-4"
              >
                {{ t('common.back') }}
              </UButton>
              <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                {{ t("register.title") }}
              </h2>
            </div>

            <div class="bg-primary-50 dark:bg-primary-950/30 rounded-lg p-4 mb-6 text-left">
              <div class="flex items-start gap-3">
                <UIcon name="i-heroicons-information-circle" class="text-primary-500 text-lg mt-0.5 shrink-0" />
                <p class="text-sm text-toned">
                  {{ t('onboarding.roleSelection.inviteHint') }}
                </p>
              </div>
            </div>

            <OrganizerRegistrationForm />
          </div>

          <!-- Participant Registration Form -->
          <div v-else-if="showParticipantForm" class="animate-fade-in">
            <div class="mb-6 text-center">
              <UButton
                @click="showParticipantForm = false"
                icon="i-heroicons-arrow-left"
                color="neutral"
                variant="ghost"
                size="sm"
                class="mb-4"
              >
                {{ t('common.back') }}
              </UButton>
              <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                {{ t("participant.register.title") }}
              </h2>
            </div>

            <ParticipantRegistrationForm />
          </div>
        </div>
      </div>
    </UPageBody>
  </UPage>
</template>
