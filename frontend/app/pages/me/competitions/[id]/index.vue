<script setup lang="ts">
import { useCompetitionStore } from '~/stores/competition';
import { useNotificationsStore } from '~/stores/notifications';

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const competitionStore = useCompetitionStore();
const notifications = useNotificationsStore();
const { getDomainLabel } = useCompetitionFormatters();
const { getRegistrationStatus } = useCompetitionStatus();
const { navigateBack } = useBackNavigation('/me/competitions');

// SEO Meta tags
useSeoMeta({
  title: t('seo.competitionDetail.title'),
  description: t('seo.competitionDetail.description'),
});

// Get competition ID from route
const competitionId = computed(() => route.params.id as string);

// Fetch competition on mount
onMounted(async () => {
  await competitionStore.fetchCompetition(competitionId.value);
});

// Current competition
const competition = computed(() => competitionStore.currentCompetition);

// Navigate back
const goBack = () => {
  navigateBack();
};

// Navigate to edit page
const goToEdit = () => {
  router.push(`/me/competitions/edit/${competitionId.value}`);
};

// Delete competition
const isDeleteModalOpen = ref(false);
const isDeleting = ref(false);

const handleDelete = async () => {
  isDeleting.value = true;
  const result = await competitionStore.deleteCompetition(competitionId.value);
  isDeleting.value = false;

  if (result.success) {
    notifications.add({
      title: t('toast.competitionDeleted.title'),
      description: t('toast.competitionDeleted.description'),
      icon: 'i-heroicons-check-circle',
      color: 'success',
    });
    router.push('/me/competitions');
  } else {
    notifications.add({
      title: t('toast.competitionDeleteError.title'),
      description: t('toast.competitionDeleteError.description'),
      icon: 'i-heroicons-exclamation-triangle',
      color: 'error',
    });
  }
  isDeleteModalOpen.value = false;
};
</script>

<template>
  <UPage>
    <UPageBody>
      <UContainer class="!max-w-7xl">
        <!-- Header -->
        <div class="mb-6">
          <div class="flex items-center gap-4 mb-4">
            <UButton
              icon="i-heroicons-arrow-left"
              color="neutral"
              variant="ghost"
              @click="goBack"
            />
          </div>

          <div v-if="competition">
            <div class="flex items-start gap-4 mb-4">
              <h1 class="text-3xl font-bold text-gray-900 dark:text-white flex-1 min-w-0 truncate"
                  :title="competition.title">
                {{ competition.title }}
              </h1>
              <UBadge
                v-if="competition.is_archived"
                color="warning"
                variant="subtle"
                size="lg"
                :label="t('competition.detail.archivedBadge')"
                class="hidden sm:inline-flex"
              />
              <UBadge
                v-else
                :color="getRegistrationStatus(competition).color"
                variant="subtle"
                size="lg"
                :label="getRegistrationStatus(competition).label"
                class="hidden sm:inline-flex"
              />
            </div>

            <!-- Domains under title -->
            <div class="flex flex-wrap gap-2 mb-4">
              <UBadge
                v-for="domain in competition.domains"
                :key="domain"
                variant="soft"
                size="md"
                :label="getDomainLabel(domain)"
              />
            </div>

            <!-- Action buttons -->
            <CompetitionActions
              :edit-label="t('competition.detail.editButton')"
              :delete-label="t('competition.detail.deleteButton')"
              @edit="goToEdit"
              @delete="isDeleteModalOpen = true"
            />

            <!-- Application management links -->
            <div class="flex flex-wrap gap-2 mt-3">
              <UButton
                variant="soft"
                icon="i-heroicons-document-text"
                :label="t('applicationForm.title')"
                @click="router.push(`/me/competitions/${competitionId}/application-form`)"
              />
              <UButton
                variant="soft"
                icon="i-heroicons-users"
                :label="t('applications.title')"
                @click="router.push(`/me/competitions/${competitionId}/applications`)"
              />
            </div>
          </div>
        </div>

        <!-- Loading state -->
        <div v-if="competitionStore.loading && !competition" class="space-y-6">
          <div class="flex items-start gap-4">
            <USkeleton class="h-10 w-3/4" />
            <USkeleton class="h-8 w-24 rounded-full" />
          </div>
          <div class="flex gap-2">
            <USkeleton v-for="i in 3" :key="i" class="h-6 w-20 rounded-full" />
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <USkeleton v-for="i in 4" :key="i" class="h-48 w-full rounded-lg" />
          </div>
        </div>

        <!-- View Mode -->
        <CompetitionDetailsView v-if="competition" :competition="competition" />
      </UContainer>
    </UPageBody>

    <!-- Delete Confirmation Modal -->
    <UiConfirmDeleteModal
      v-model:open="isDeleteModalOpen"
      :title="t('competitions.delete.title')"
      :description="t('competitions.delete.description')"
      :confirm-label="t('competitions.delete.confirm')"
      :cancel-label="t('common.cancel')"
      :is-deleting="isDeleting"
      @confirm="handleDelete"
    />
  </UPage>
</template>
