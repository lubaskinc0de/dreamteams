<script setup lang="ts">
import type {
  ApiError,
  CompetitionModel,
  RescheduleCompetitionForm,
  UpdateCompetitionGeneralInfoForm,
} from '~/types/api';
import { useCompetitionStore } from '~/stores/competition';
import { useNotificationsStore } from '~/stores/notifications';
import { CalendarDate, Time, parseAbsoluteToLocal, today, getLocalTimeZone } from '@internationalized/date';
import { createCompetitionSchemas } from '~/schemas/competition';
import { combineDateTime } from '~/utils/dateTime';

type EditSection = 'general-info' | 'schedule';

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const competitionStore = useCompetitionStore();
const notifications = useNotificationsStore();
const { navigateBack } = useBackNavigation();

useSeoMeta({
  title: t('seo.competitionEdit.title'),
  description: t('seo.competitionEdit.description'),
});

const competitionId = computed(() => route.params.id as string);
const competition = computed(() => competitionStore.currentCompetition);
const selectedSection = computed<EditSection | null>(() => {
  const value = route.query.section;
  return value === 'general-info' || value === 'schedule' ? value : null;
});

const topAnchor = useTemplateRef<HTMLElement>('topAnchor');

const scrollToTop = () => {
  if (!import.meta.client) return;
  topAnchor.value?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  window.scrollTo({ top: 0, behavior: 'smooth' });
  document.documentElement.scrollTo({ top: 0, behavior: 'smooth' });
};

const selectSection = async (section: EditSection) => {
  await router.push({ path: route.path, query: { section } });
  await nextTick();
  scrollToTop();
};

const showChoiceScreen = async () => {
  await router.push({ path: route.path });
  await nextTick();
  scrollToTop();
};

const goBack = () => {
  if (selectedSection.value) {
    void showChoiceScreen();
    return;
  }
  navigateBack({ fallback: () => `/me/competitions/${competitionId.value}` });
};

const { competitionGeneralInfoUpdateSchema, competitionRescheduleSchema } = createCompetitionSchemas(t);
const isTeamCompetition = ref(true);
const isInitializingForm = ref(false);
const isSubmittingGeneralInfo = ref(false);
const isSubmittingSchedule = ref(false);
const isSubmittingArchive = ref(false);

const lockedDates = ref({
  registrationStart: false,
  registrationEnd: false,
  teamFormationStart: false,
  teamFormationEnd: false,
});

const originalDates = ref({
  registrationStart: '',
  registrationEnd: '',
  teamFormationStart: null as string | null,
  teamFormationEnd: null as string | null,
});

const generalInfoState = ref<UpdateCompetitionGeneralInfoForm>({
  title: '',
  description: '',
  participant_limits: {
    max: 100,
  },
  tag_ids: [],
  tracks: [{ name: '' }],
  participant_type: 'any',
  venue: {
    format: 'online',
    location: null,
  },
  milestones: null,
  auto_accept: false,
});

const rescheduleState = ref<RescheduleCompetitionForm>({
  schedule: {
    registration_start: '',
    registration_end: '',
    team_formation_start: null,
    team_formation_end: null,
  },
  team_size: {
    min: 1,
    max: 5,
  },
});

const registrationDateRange = ref<{ start: CalendarDate; end: CalendarDate } | undefined>(undefined);
const registrationStartTime = ref<Time | undefined>(new Time(0, 0));
const registrationEndTime = ref<Time | undefined>(new Time(0, 0));

const teamFormationDateRange = ref<{ start: CalendarDate; end: CalendarDate } | undefined>(undefined);
const teamFormationStartTime = ref<Time | undefined>(new Time(0, 0));
const teamFormationEndTime = ref<Time | undefined>(new Time(0, 0));

const { milestones, addMilestone, removeMilestone, getMilestonesForSubmit } = useMilestones(combineDateTime);

const registrationMinValue = computed(() => today(getLocalTimeZone()));

const teamFormationMinValue = computed(() => {
  if (registrationDateRange.value?.end) {
    return registrationDateRange.value.end.add({ days: 1 });
  }
  return today(getLocalTimeZone());
});

watch(selectedSection, () => {
  void nextTick(scrollToTop);
});

watch([registrationDateRange, registrationStartTime, registrationEndTime], () => {
  if (isInitializingForm.value) return;
  if (registrationDateRange.value?.start) {
    rescheduleState.value.schedule.registration_start = combineDateTime(registrationDateRange.value.start, registrationStartTime.value);
  }
  if (registrationDateRange.value?.end) {
    rescheduleState.value.schedule.registration_end = combineDateTime(registrationDateRange.value.end, registrationEndTime.value);
  }
});

watch([teamFormationDateRange, teamFormationStartTime, teamFormationEndTime], () => {
  if (isInitializingForm.value) return;
  if (teamFormationDateRange.value?.start) {
    rescheduleState.value.schedule.team_formation_start = combineDateTime(teamFormationDateRange.value.start, teamFormationStartTime.value);
  } else {
    rescheduleState.value.schedule.team_formation_start = null;
  }

  if (teamFormationDateRange.value?.end) {
    rescheduleState.value.schedule.team_formation_end = combineDateTime(teamFormationDateRange.value.end, teamFormationEndTime.value);
  } else {
    rescheduleState.value.schedule.team_formation_end = null;
  }
});

watch(isTeamCompetition, (isTeam) => {
  if (!isTeam) {
    teamFormationDateRange.value = undefined;
    teamFormationStartTime.value = new Time(0, 0);
    teamFormationEndTime.value = new Time(0, 0);
    rescheduleState.value.schedule.team_formation_start = null;
    rescheduleState.value.schedule.team_formation_end = null;
    rescheduleState.value.team_size = null;
  } else if (rescheduleState.value.team_size === null) {
    rescheduleState.value.team_size = { min: 1, max: 5 };
  }
});

watch(milestones, () => {
  if (isInitializingForm.value) return;
  const payload = getMilestonesForSubmit();
  generalInfoState.value.milestones = payload.length > 0 ? payload : null;
}, { deep: true });

const isDateInPast = (dateString: string | null): boolean => {
  if (!dateString) return false;
  return new Date(dateString) < new Date();
};

const parseDateTime = (dateString: string) => {
  try {
    const dateTime = parseAbsoluteToLocal(dateString);
    return {
      date: new CalendarDate(dateTime.year, dateTime.month, dateTime.day),
      time: new Time(dateTime.hour, dateTime.minute),
    };
  } catch (error) {
    console.error('Failed to parse date:', error);
    const date = new Date(dateString);
    return {
      date: new CalendarDate(date.getFullYear(), date.getMonth() + 1, date.getDate()),
      time: new Time(date.getHours(), date.getMinutes()),
    };
  }
};

const initializeForm = (comp: CompetitionModel) => {
  isInitializingForm.value = true;

  originalDates.value.registrationStart = comp.schedule.registration_start;
  originalDates.value.registrationEnd = comp.schedule.registration_end;
  originalDates.value.teamFormationStart = comp.schedule.team_formation_start;
  originalDates.value.teamFormationEnd = comp.schedule.team_formation_end;

  lockedDates.value.registrationStart = isDateInPast(comp.schedule.registration_start);
  lockedDates.value.registrationEnd = isDateInPast(comp.schedule.registration_end);
  lockedDates.value.teamFormationStart = isDateInPast(comp.schedule.team_formation_start);
  lockedDates.value.teamFormationEnd = isDateInPast(comp.schedule.team_formation_end);

  generalInfoState.value = {
    title: comp.title,
    description: comp.description,
    participant_limits: {
      max: comp.participant_limits.max,
    },
    tag_ids: comp.tags.map((tag) => tag.id),
    tracks: comp.tracks.length
      ? comp.tracks.map((track) => ({ name: track.name }))
      : [{ name: 'Общий' }],
    participant_type: comp.participant_type,
    venue: {
      format: comp.venue.format,
      location: comp.venue.location,
    },
    milestones: comp.milestones.length
      ? comp.milestones.map((milestone) => ({
          title: milestone.title,
          timestamp: milestone.timestamp,
          description: milestone.description,
        }))
      : null,
    auto_accept: comp.auto_accept,
  };

  rescheduleState.value = {
    schedule: {
      registration_start: comp.schedule.registration_start,
      registration_end: comp.schedule.registration_end,
      team_formation_start: comp.schedule.team_formation_start,
      team_formation_end: comp.schedule.team_formation_end,
    },
    team_size: comp.team_size
      ? { min: comp.team_size.min, max: comp.team_size.max }
      : null,
  };

  const hasTeamFormationDates = Boolean(comp.schedule.team_formation_start && comp.schedule.team_formation_end);
  isTeamCompetition.value = hasTeamFormationDates;

  const registrationStart = parseDateTime(comp.schedule.registration_start);
  const registrationEnd = parseDateTime(comp.schedule.registration_end);
  registrationDateRange.value = {
    start: registrationStart.date,
    end: registrationEnd.date,
  };
  registrationStartTime.value = registrationStart.time;
  registrationEndTime.value = registrationEnd.time;

  if (hasTeamFormationDates && comp.schedule.team_formation_start && comp.schedule.team_formation_end) {
    const teamFormationStart = parseDateTime(comp.schedule.team_formation_start);
    const teamFormationEnd = parseDateTime(comp.schedule.team_formation_end);
    teamFormationDateRange.value = {
      start: teamFormationStart.date,
      end: teamFormationEnd.date,
    };
    teamFormationStartTime.value = teamFormationStart.time;
    teamFormationEndTime.value = teamFormationEnd.time;
  } else {
    teamFormationDateRange.value = undefined;
    teamFormationStartTime.value = new Time(0, 0);
    teamFormationEndTime.value = new Time(0, 0);
  }

  milestones.value = comp.milestones.map((milestone) => {
    const parsed = parseDateTime(milestone.timestamp);
    return {
      title: milestone.title,
      date: parsed.date,
      time: parsed.time,
      description: milestone.description,
    };
  });

  nextTick(() => {
    isInitializingForm.value = false;
  });
};

onMounted(async () => {
  await competitionStore.fetchCompetition(competitionId.value);
  if (competition.value) {
    initializeForm(competition.value);
  }
});

const prepareGeneralInfoSubmit = (): UpdateCompetitionGeneralInfoForm => {
  const milestonePayload = getMilestonesForSubmit();
  return {
    ...generalInfoState.value,
    participant_limits: {
      max: generalInfoState.value.participant_limits.max,
    },
    tag_ids: [...generalInfoState.value.tag_ids],
    tracks: generalInfoState.value.tracks.map((track) => ({ name: track.name })),
    venue: {
      format: generalInfoState.value.venue.format,
      location: generalInfoState.value.venue.location,
    },
    milestones: milestonePayload.length > 0 ? milestonePayload : null,
  };
};

const prepareRescheduleSubmit = (): RescheduleCompetitionForm => {
  const schedule = { ...rescheduleState.value.schedule };

  if (lockedDates.value.registrationStart) {
    schedule.registration_start = originalDates.value.registrationStart;
  }
  if (lockedDates.value.registrationEnd) {
    schedule.registration_end = originalDates.value.registrationEnd;
  }
  if (lockedDates.value.teamFormationStart && originalDates.value.teamFormationStart) {
    schedule.team_formation_start = originalDates.value.teamFormationStart;
  }
  if (lockedDates.value.teamFormationEnd && originalDates.value.teamFormationEnd) {
    schedule.team_formation_end = originalDates.value.teamFormationEnd;
  }

  return {
    schedule,
    team_size: rescheduleState.value.team_size
      ? { min: rescheduleState.value.team_size.min, max: rescheduleState.value.team_size.max }
      : null,
  };
};

const { handleFormError: handleError } = useFormErrorScroll();
const { getErrorMessage } = useErrorHandler();

const notifySuccess = () => {
  notifications.add({
    title: t('toast.competitionUpdated.title'),
    description: t('toast.competitionUpdated.description'),
    icon: 'i-heroicons-check-circle',
    color: 'success',
  });
};

const isApiError = (error: unknown): error is ApiError =>
  typeof error === 'object' && error !== null && 'code' in error && 'message' in error;

const notifyError = (error: unknown) => {
  notifications.add({
    title: t('errors.default.title'),
    description: isApiError(error)
      ? getErrorMessage(error) ?? t('errors.default.description')
      : error instanceof Error
        ? error.message
        : t('errors.default.description'),
    icon: 'i-heroicons-exclamation-triangle',
    color: 'error',
  });
};

const handleGeneralInfoSubmit = async () => {
  isSubmittingGeneralInfo.value = true;

  try {
    const result = await competitionStore.updateCompetitionGeneralInfo(
      competitionId.value,
      prepareGeneralInfoSubmit(),
    );

    if (result.success) {
      notifySuccess();
      await router.push(`/me/competitions/${competitionId.value}`);
    } else if (result.error) {
      notifyError(result.error);
    }
  } catch (error) {
    notifyError(error);
  } finally {
    isSubmittingGeneralInfo.value = false;
  }
};

const handleRescheduleSubmit = async () => {
  isSubmittingSchedule.value = true;

  try {
    const result = await competitionStore.rescheduleCompetition(
      competitionId.value,
      prepareRescheduleSubmit(),
    );

    if (result.success) {
      notifySuccess();
      await router.push(`/me/competitions/${competitionId.value}`);
    } else if (result.error) {
      notifyError(result.error);
    }
  } catch (error) {
    notifyError(error);
  } finally {
    isSubmittingSchedule.value = false;
  }
};

const archiveActionLabel = computed(() =>
  competition.value?.is_archived
    ? t('competition.edit.cards.archiveStatus.unarchive')
    : t('competition.edit.cards.archiveStatus.archive'),
);

const archiveActionIcon = computed(() =>
  competition.value?.is_archived
    ? 'i-heroicons-arrow-uturn-left'
    : 'i-heroicons-archive-box',
);

const handleArchiveStatusChange = async () => {
  if (!competition.value) return;
  isSubmittingArchive.value = true;

  try {
    const result = await competitionStore.changeCompetitionArchiveStatus(
      competitionId.value,
      { is_archived: !competition.value.is_archived },
    );

    if (result.success) {
      notifySuccess();
    } else if (result.error) {
      notifyError(result.error);
    }
  } catch (error) {
    notifyError(error);
  } finally {
    isSubmittingArchive.value = false;
  }
};
</script>

<template>
  <UPage>
    <UPageBody>
      <UContainer class="!max-w-5xl">
        <div ref="topAnchor" aria-hidden="true" />

        <div class="mb-6">
          <UButton
            icon="i-heroicons-arrow-left"
            color="neutral"
            variant="ghost"
            :label="selectedSection ? t('competition.edit.backToChoices') : undefined"
            @click="goBack"
            class="mb-4"
          />

          <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-1">
            {{ t('competition.edit.title') }}
          </h1>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ t('competition.edit.description') }}
          </p>
        </div>

        <div v-if="competitionStore.loading && !competition" class="space-y-6">
          <USkeleton class="h-10 w-3/4" />
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <USkeleton v-for="i in 3" :key="i" class="h-44 w-full rounded-lg" />
          </div>
        </div>

        <div v-else-if="competition">
          <section v-if="!selectedSection" class="space-y-5">
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
              {{ t('competition.edit.question') }}
            </h2>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button
                type="button"
                class="group text-left rounded-lg border border-gray-200 bg-white p-5 transition hover:border-primary-300 hover:bg-primary-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 dark:border-gray-800 dark:bg-gray-900 dark:hover:border-primary-700 dark:hover:bg-primary-950/40"
                @click="selectSection('general-info')"
              >
                <span class="mb-4 flex h-11 w-11 items-center justify-center rounded-lg bg-primary-50 text-primary-600 dark:bg-primary-950 dark:text-primary-300">
                  <UIcon name="i-heroicons-information-circle" class="h-6 w-6" />
                </span>
                <span class="block text-base font-semibold text-gray-900 dark:text-white">
                  {{ t('competition.edit.cards.generalInfo.title') }}
                </span>
                <span class="mt-2 block text-sm text-gray-600 dark:text-gray-400">
                  {{ t('competition.edit.cards.generalInfo.description') }}
                </span>
              </button>

              <button
                type="button"
                class="group text-left rounded-lg border border-gray-200 bg-white p-5 transition hover:border-primary-300 hover:bg-primary-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 dark:border-gray-800 dark:bg-gray-900 dark:hover:border-primary-700 dark:hover:bg-primary-950/40"
                @click="selectSection('schedule')"
              >
                <span class="mb-4 flex h-11 w-11 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600 dark:bg-emerald-950 dark:text-emerald-300">
                  <UIcon name="i-heroicons-calendar-days" class="h-6 w-6" />
                </span>
                <span class="block text-base font-semibold text-gray-900 dark:text-white">
                  {{ t('competition.edit.cards.schedule.title') }}
                </span>
                <span class="mt-2 block text-sm text-gray-600 dark:text-gray-400">
                  {{ t('competition.edit.cards.schedule.description') }}
                </span>
              </button>

              <button
                type="button"
                class="group text-left rounded-lg border border-gray-200 bg-white p-5 transition hover:border-primary-300 hover:bg-primary-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 disabled:cursor-not-allowed disabled:opacity-60 dark:border-gray-800 dark:bg-gray-900 dark:hover:border-primary-700 dark:hover:bg-primary-950/40"
                :disabled="isSubmittingArchive"
                @click="handleArchiveStatusChange"
              >
                <span class="mb-4 flex h-11 w-11 items-center justify-center rounded-lg bg-amber-50 text-amber-600 dark:bg-amber-950 dark:text-amber-300">
                  <UIcon :name="archiveActionIcon" class="h-6 w-6" />
                </span>
                <span class="block text-base font-semibold text-gray-900 dark:text-white">
                  {{ t('competition.edit.cards.archiveStatus.title') }}
                </span>
                <span class="mt-2 block text-sm text-gray-600 dark:text-gray-400">
                  {{ archiveActionLabel }}
                </span>
                <span v-if="isSubmittingArchive" class="mt-4 inline-flex items-center gap-2 text-sm text-primary-600 dark:text-primary-300">
                  <UIcon name="i-heroicons-arrow-path" class="h-4 w-4 animate-spin" />
                  {{ t('common.loading') }}
                </span>
              </button>
            </div>
          </section>

          <UForm
            v-else-if="selectedSection === 'general-info'"
            :state="generalInfoState"
            :schema="competitionGeneralInfoUpdateSchema"
            class="space-y-6"
            @submit="handleGeneralInfoSubmit"
            @error="handleError"
          >
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <CompetitionFormBasicInfoFormSection
                v-model:title="generalInfoState.title"
                v-model:description="generalInfoState.description"
                v-model:tag-ids="generalInfoState.tag_ids"
                v-model:tracks="generalInfoState.tracks"
                v-model:participant-type="generalInfoState.participant_type"
                v-model:is-team-competition="isTeamCompetition"
                v-model:auto-accept="generalInfoState.auto_accept"
                :initial-tags="competition.tags"
                :show-team-competition-field="false"
              />

              <CompetitionFormParticipantsFormSection
                v-model:participant-limits-max="generalInfoState.participant_limits.max"
                v-model:team-size="rescheduleState.team_size"
                :is-team-competition="isTeamCompetition"
                :show-team-size="false"
              />

              <CompetitionFormVenueFormSection
                v-model:format="generalInfoState.venue.format"
                v-model:location="generalInfoState.venue.location"
              />

              <CompetitionFormMilestonesFormSection
                v-model:milestones="milestones"
                @add-milestone="addMilestone"
                @remove-milestone="removeMilestone"
              />
            </div>

            <div class="flex justify-end gap-3 pt-2">
              <UButton
                variant="outline"
                color="neutral"
                size="lg"
                :label="t('common.cancel')"
                :disabled="isSubmittingGeneralInfo"
                @click="showChoiceScreen"
              />
              <UButton
                type="submit"
                color="primary"
                size="lg"
                :label="t('common.save')"
                :loading="isSubmittingGeneralInfo"
                :disabled="isSubmittingGeneralInfo"
              />
            </div>
          </UForm>

          <UForm
            v-else-if="selectedSection === 'schedule'"
            :state="rescheduleState"
            :schema="competitionRescheduleSchema"
            class="space-y-6"
            @submit="handleRescheduleSubmit"
            @error="handleError"
          >
            <UCard>
              <template #header>
                <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
                  {{ t('competition.form.isTeam.label') }}
                </h2>
              </template>
              <div class="flex items-center gap-3">
                <USwitch
                  v-model="isTeamCompetition"
                  size="xl"
                />
                <span class="text-gray-700 dark:text-gray-300">
                  {{ t('competition.form.isTeam.checkboxLabel') }}
                </span>
              </div>
            </UCard>

            <CompetitionFormScheduleFormSection
              v-model:registration-date-range="registrationDateRange"
              v-model:registration-start-time="registrationStartTime"
              v-model:registration-end-time="registrationEndTime"
              v-model:team-formation-date-range="teamFormationDateRange"
              v-model:team-formation-start-time="teamFormationStartTime"
              v-model:team-formation-end-time="teamFormationEndTime"
              :is-team-competition="isTeamCompetition"
              :locked-registration-start="lockedDates.registrationStart"
              :locked-registration-end="lockedDates.registrationEnd"
              :locked-team-formation-start="lockedDates.teamFormationStart"
              :locked-team-formation-end="lockedDates.teamFormationEnd"
              :registration-min-value="registrationMinValue"
              :team-formation-min-value="teamFormationMinValue"
            />

            <CompetitionFormParticipantsFormSection
              v-model:participant-limits-max="generalInfoState.participant_limits.max"
              v-model:team-size="rescheduleState.team_size"
              :is-team-competition="isTeamCompetition"
              :show-participant-limits="false"
            />

            <div class="flex justify-end gap-3 pt-2">
              <UButton
                variant="outline"
                color="neutral"
                size="lg"
                :label="t('common.cancel')"
                :disabled="isSubmittingSchedule"
                @click="showChoiceScreen"
              />
              <UButton
                type="submit"
                color="primary"
                size="lg"
                :label="t('common.save')"
                :loading="isSubmittingSchedule"
                :disabled="isSubmittingSchedule"
              />
            </div>
          </UForm>
        </div>
      </UContainer>
    </UPageBody>
  </UPage>
</template>
