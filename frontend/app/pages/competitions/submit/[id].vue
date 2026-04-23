<script setup lang="ts">
import { useMyApplicationsStore } from '~/stores/myApplications';
import { useNotificationsStore } from '~/stores/notifications';
import { extractMilestoneDescription } from '~/utils/milestone';
import type { CompetitionModel, Domain, FieldModel } from '~/types/api';

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const appStore = useMyApplicationsStore();
const notifications = useNotificationsStore();
const { hasProfile } = useAuth();
const userStore = useUserStore();
const {
  getDomainLabel,
  getFormatLabel,
  getParticipantTypeLabel,
  formatDateRange,
  formatDateTime,
  formatParticipants,
  formatTeamSize,
} = useCompetitionFormatters();

const competitionId = computed(() => route.params.id as string);

useSeoMeta({ title: t('competitionsPreview.title') });

const competition = ref<CompetitionModel | null>(null);
const competitionLoading = ref(true);
const competitionError = ref<string | null>(null);

const applicationForm = ref<{ fields: FieldModel[] } | null>(null);

const selectedDomains = ref<Domain[]>([]);
const formAnswers = ref<Record<string, any>>({});

onMounted(async () => {
  const api = useApi();

  // Participant-facing read — CompetitionModel shape, auth'd via profile not ownership.
  const { data: comp, error: compErr } = await api.getExploreCompetition(competitionId.value);
  competitionLoading.value = false;

  if (compErr) {
    competitionError.value = compErr.code;
    return;
  }
  competition.value = comp;

  // APPLICATION_FORM_NOT_FOUND is expected when the organiser didn't define a form —
  // the submit flow then sends form_data: null. Other errors surface at submit time.
  const { data: form } = await api.getMyApplicationForm(competitionId.value);
  if (form) {
    applicationForm.value = { fields: form.fields };
  }
});

const domainOptions = computed(() =>
  (competition.value?.domains ?? []).map((d: Domain) => ({ value: d, label: getDomainLabel(d) }))
);

const isParticipant = computed(() => userStore.isParticipant);

// Show a short preview of the description in the info card; long descriptions
// are truncated by character count and the rest lives behind a collapsible.
const DESCRIPTION_PREVIEW_CHARS = 180;
const descriptionExpanded = ref(false);
const descriptionIsLong = computed(
  () => (competition.value?.description ?? '').length > DESCRIPTION_PREVIEW_CHARS,
);
const descriptionPreview = computed(() => {
  const full = competition.value?.description ?? '';
  if (!descriptionIsLong.value) return full;
  return full.slice(0, DESCRIPTION_PREVIEW_CHARS).trimEnd() + '…';
});

const handleApply = async () => {
  if (selectedDomains.value.length === 0) return;

  const form_data = applicationForm.value ? { ...formAnswers.value } : null;

  const result = await appStore.submit(competitionId.value, {
    domains: selectedDomains.value,
    form_data,
  });

  if (result.success) {
    notifications.add({
      title: t('toast.applicationSubmitted.title'),
      description: t('toast.applicationSubmitted.description'),
      icon: 'i-heroicons-check-circle',
      color: 'success',
    });
    router.push('/me/applications');
  } else if (appStore.error) {
    notifications.add({
      title: t('apiErrors.' + appStore.error.code),
      icon: 'i-heroicons-exclamation-circle',
      color: 'error',
    });
  }
};
</script>

<template>
  <UPage>
    <UPageBody>
      <UContainer class="!max-w-6xl">
        <div class="mb-6">
          <UButton
            icon="i-heroicons-arrow-left"
            color="neutral"
            variant="ghost"
            :label="t('common.back')"
            @click="router.push('/explore')"
          />
        </div>

        <div v-if="competitionLoading" class="grid lg:grid-cols-3 gap-6">
          <div class="lg:col-span-2 space-y-4">
            <USkeleton class="h-10 w-3/4 rounded" />
            <USkeleton class="h-64 w-full rounded-lg" />
          </div>
          <USkeleton class="h-80 w-full rounded-lg" />
        </div>

        <UAlert
          v-else-if="competitionError"
          color="error"
          variant="soft"
          :title="t('apiErrors.' + competitionError)"
          icon="i-heroicons-exclamation-circle"
        />

        <template v-else-if="competition">
          <div class="grid lg:grid-cols-3 gap-6">
            <!-- Left: application form (title lives in the right info card) -->
            <div class="lg:col-span-2 space-y-6">
              <UCard v-if="isParticipant">
                <template #header>
                  <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
                    {{ t('myApplications.applyButton') }}
                  </h2>
                </template>

                <div class="space-y-4">
                  <UFormField :label="t('myApplications.selectDomains')" required>
                    <div class="flex flex-wrap gap-2">
                      <UCheckbox
                        v-for="opt in domainOptions"
                        :key="opt.value"
                        :label="opt.label"
                        :model-value="selectedDomains.includes(opt.value)"
                        @update:model-value="(checked) => {
                          if (checked) selectedDomains.push(opt.value);
                          else selectedDomains = selectedDomains.filter(d => d !== opt.value);
                        }"
                      />
                    </div>
                    <p v-if="selectedDomains.length === 0" class="text-xs text-red-500 mt-1">
                      {{ t('myApplications.domainsRequired') }}
                    </p>
                  </UFormField>

                  <template v-if="applicationForm">
                    <UFormField
                      v-for="field in applicationForm.fields"
                      :key="field.name"
                      :label="field.name"
                      :required="field.required"
                    >
                      <UInput
                        v-if="field.type === 'string'"
                        v-model="formAnswers[field.name]"
                        :placeholder="field.name"
                        class="w-full"
                      />
                      <UInput
                        v-else-if="field.type === 'int'"
                        v-model.number="formAnswers[field.name]"
                        type="number"
                        :placeholder="field.name"
                        class="w-full"
                      />
                      <USelect
                        v-else-if="field.type === 'select'"
                        v-model="formAnswers[field.name]"
                        :items="(field.choices ?? []).map(c => ({ value: c.value, label: c.value }))"
                        value-key="value"
                        label-key="label"
                        class="w-full"
                      />
                      <div v-else-if="field.type === 'multiselect'" class="flex flex-wrap gap-2">
                        <UCheckbox
                          v-for="choice in (field.choices ?? [])"
                          :key="choice.value"
                          :label="choice.value"
                          :model-value="(formAnswers[field.name] ?? []).includes(choice.value)"
                          @update:model-value="(checked) => {
                            const current = formAnswers[field.name] ?? [];
                            formAnswers[field.name] = checked
                              ? [...current, choice.value]
                              : current.filter((v: string) => v !== choice.value);
                          }"
                        />
                      </div>
                    </UFormField>
                  </template>
                </div>

                <template #footer>
                  <div class="flex justify-end gap-3">
                    <UButton
                      color="neutral"
                      variant="ghost"
                      :label="t('common.cancel')"
                      @click="router.push('/explore')"
                    />
                    <UButton
                      color="primary"
                      icon="i-heroicons-paper-airplane"
                      :label="appStore.submitting ? t('myApplications.applying') : t('myApplications.applyButton')"
                      :loading="appStore.submitting"
                      :disabled="appStore.submitting || selectedDomains.length === 0"
                      @click="handleApply"
                    />
                  </div>
                </template>
              </UCard>

              <UAlert
                v-else-if="hasProfile"
                color="info"
                variant="soft"
                :title="t('myApplications.applyButton')"
                :description="t('myApplications.onlyParticipantsCanApply')"
                icon="i-heroicons-information-circle"
              />
            </div>

            <!-- Right: brief event info (single card, sticky on desktop) -->
            <div class="lg:col-span-1">
              <UCard class="lg:sticky lg:top-6">
                <template #header>
                  <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
                    {{ competition.title }}
                  </h1>
                </template>

                <div class="space-y-4 text-sm">
                  <div>
                    <p class="text-gray-700 dark:text-gray-300 whitespace-pre-line">
                      <template v-if="!descriptionExpanded">{{ descriptionPreview }}</template>
                      <template v-else>{{ competition.description }}</template>
                    </p>
                    <UButton
                      v-if="descriptionIsLong"
                      size="xs"
                      color="primary"
                      variant="link"
                      :padded="false"
                      class="mt-1 px-0"
                      :label="descriptionExpanded ? t('common.showLess') : t('common.showMore')"
                      :trailing-icon="descriptionExpanded ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'"
                      @click="descriptionExpanded = !descriptionExpanded"
                    />
                  </div>

                  <div class="border-t border-gray-200 dark:border-gray-700" />

                  <div class="flex items-start gap-3">
                    <UIcon name="i-heroicons-calendar" class="size-5 text-primary-500 mt-0.5 flex-shrink-0" />
                    <div class="flex-1 min-w-0">
                      <p class="font-medium text-gray-900 dark:text-white">
                        {{ t('competitionsPreview.detail.registration') }}
                      </p>
                      <p class="text-gray-600 dark:text-gray-400">
                        {{ formatDateRange(competition.schedule.registration_start, competition.schedule.registration_end) }}
                      </p>
                    </div>
                  </div>

                  <div
                    v-if="competition.schedule.team_formation_start && competition.schedule.team_formation_end"
                    class="flex items-start gap-3"
                  >
                    <UIcon name="i-heroicons-user-group" class="size-5 text-primary-500 mt-0.5 flex-shrink-0" />
                    <div class="flex-1 min-w-0">
                      <p class="font-medium text-gray-900 dark:text-white">
                        {{ t('competitionsPreview.detail.teamFormation') }}
                      </p>
                      <p class="text-gray-600 dark:text-gray-400">
                        {{ formatDateRange(competition.schedule.team_formation_start, competition.schedule.team_formation_end) }}
                      </p>
                    </div>
                  </div>

                  <div class="flex items-start gap-3">
                    <UIcon name="i-heroicons-map-pin" class="size-5 text-primary-500 mt-0.5 flex-shrink-0" />
                    <div class="flex-1 min-w-0">
                      <p class="font-medium text-gray-900 dark:text-white">
                        {{ getFormatLabel(competition.venue.format) }}
                      </p>
                      <p v-if="competition.venue.location" class="text-gray-600 dark:text-gray-400 break-words">
                        {{ competition.venue.location }}
                      </p>
                    </div>
                  </div>

                  <div class="flex items-start gap-3">
                    <UIcon name="i-heroicons-users" class="size-5 text-primary-500 mt-0.5 flex-shrink-0" />
                    <div class="flex-1 min-w-0">
                      <p class="font-medium text-gray-900 dark:text-white">
                        {{ formatParticipants(competition.members_count, competition.participant_limits.max) }}
                      </p>
                      <p class="text-gray-600 dark:text-gray-400">
                        {{ getParticipantTypeLabel(competition.participant_type) }}
                      </p>
                      <p v-if="competition.team_size" class="text-gray-600 dark:text-gray-400">
                        {{ formatTeamSize(competition.team_size) }}
                      </p>
                    </div>
                  </div>

                  <template v-if="competition.milestones.length > 0">
                    <div class="border-t border-gray-200 dark:border-gray-700" />
                    <div>
                      <p class="font-medium text-gray-900 dark:text-white mb-3">
                        {{ t('competitionsPreview.detail.milestones') }}
                      </p>
                      <UTimeline
                        :items="competition.milestones.map((milestone) => ({
                          date: formatDateTime(milestone.timestamp),
                          title: milestone.title,
                          description: extractMilestoneDescription(milestone.description) ?? undefined,
                          icon: 'i-heroicons-flag',
                        }))"
                        color="primary"
                        size="sm"
                      />
                    </div>
                  </template>
                </div>
              </UCard>
            </div>
          </div>
        </template>
      </UContainer>
    </UPageBody>
  </UPage>
</template>
