<script setup lang="ts">
import { useCompetitionStore } from '~/stores/competition';

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const competitionStore = useCompetitionStore();
const toast = useToast();
const { getDomainLabel } = useCompetitionFormatters();
const { getRegistrationStatus } = useCompetitionStatus();

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
  router.push('/competitions');
};

// Navigate to edit page
const goToEdit = () => {
  router.push(`/competitions/${competitionId.value}/edit`);
};

// Delete competition
const isDeleteModalOpen = ref(false);
const isDeleting = ref(false);

const handleDelete = async () => {
  isDeleting.value = true;
  const result = await competitionStore.deleteCompetition(competitionId.value);
  isDeleting.value = false;

  if (result.success) {
    toast.add({
      title: t('toast.competitionDeleted.title'),
      description: t('toast.competitionDeleted.description'),
      icon: 'i-heroicons-check-circle',
      color: 'success',
    });
    router.push('/competitions');
  } else {
    toast.add({
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
      <div class="max-w-7xl mx-auto">
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
              <h1 class="text-3xl font-bold text-gray-900 dark:text-white flex-1">
                {{ competition.title }}
              </h1>
              <UBadge
                v-if="competition.is_archived"
                color="warning"
                variant="subtle"
                size="lg"
                :label="t('competition.detail.archivedBadge')"
              />
              <UBadge
                v-else
                :color="getRegistrationStatus(competition).color"
                variant="subtle"
                size="lg"
                :label="getRegistrationStatus(competition).label"
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
          </div>
        </div>

        <!-- Loading state -->
        <div v-if="competitionStore.loading && !competition" class="flex justify-center py-12">
          <UProgress indeterminate size="md" />
        </div>

        <!-- View Mode -->
        <CompetitionDetailsView v-if="competition" :competition="competition" />
      </div>
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
