<script setup lang="ts">
import type { UpdateCompetitionForm } from '~/types/api';
import { useCompetitionStore } from '~/stores/competition';
import { useNotificationsStore } from '~/stores/notifications';
import { CalendarDate, Time, parseAbsoluteToLocal, today, getLocalTimeZone } from '@internationalized/date';
import { createCompetitionSchemas } from '~/schemas/competition';
import { combineDateTime } from '~/utils/dateTime';

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const competitionStore = useCompetitionStore();
const notifications = useNotificationsStore();

// SEO Meta tags
useSeoMeta({
  title: t('seo.competitionEdit.title'),
  description: t('seo.competitionEdit.description'),
});

// Get competition ID from route
const competitionId = computed(() => route.params.id as string);

// Fetch competition on mount
onMounted(async () => {
  await competitionStore.fetchCompetition(competitionId.value);
  // Initialize form after fetching
  if (competition.value) {
    initializeForm(competition.value);
  }
});

// Current competition
const competition = computed(() => competitionStore.currentCompetition);

// Navigate back to detail page
const goBack = () => {
  router.push(`/me/competitions/${competitionId.value}`);
};

// ===== FORM STATE =====
const { competitionUpdateSchema } = createCompetitionSchemas(t);
const isTeamCompetition = ref(true);
const isInitializingForm = ref(false);
const isSubmitting = ref(false);

// Track which dates are locked (already in the past and cannot be changed)
const lockedDates = ref({
  registrationStart: false,
  registrationEnd: false,
  teamFormationStart: false,
  teamFormationEnd: false,
});

// Original dates to use when locked
const originalDates = ref({
  registrationStart: '',
  registrationEnd: '',
  teamFormationStart: null as string | null,
  teamFormationEnd: null as string | null,
});

// Form state
const formState = ref<UpdateCompetitionForm>({
  title: '',
  description: '',
  schedule: {
    registration_start: '',
    registration_end: '',
    team_formation_start: null,
    team_formation_end: null,
  },
  participant_limits: {
    min: 1,
    max: 100,
  },
  domains: [],
  participant_type: 'any',
  venue: {
    format: 'online',
    location: null,
  },
  team_size: {
    min: 1,
    max: 5,
  },
  milestones: [],
  is_archived: false,
});

// Date ranges for schedule
const registrationDateRange = ref<{ start: CalendarDate; end: CalendarDate } | undefined>(undefined);
const registrationStartTime = ref<Time | undefined>(new Time(0, 0));
const registrationEndTime = ref<Time | undefined>(new Time(0, 0));

const teamFormationDateRange = ref<{ start: CalendarDate; end: CalendarDate } | undefined>(undefined);
const teamFormationStartTime = ref<Time | undefined>(new Time(0, 0));
const teamFormationEndTime = ref<Time | undefined>(new Time(0, 0));

// Milestones
const { milestones, addMilestone, removeMilestone, getMilestonesForSubmit } = useMilestones(combineDateTime);

// Min values for date pickers
// Registration: must be today or later
const registrationMinValue = computed(() => today(getLocalTimeZone()));

// Team formation: must be after registration end date (or today if not set)
const teamFormationMinValue = computed(() => {
  if (registrationDateRange.value?.end) {
    // Day after registration end
    return registrationDateRange.value.end.add({ days: 1 });
  }
  return today(getLocalTimeZone());
});

// Watch date range and time changes for registration
watch([registrationDateRange, registrationStartTime, registrationEndTime], () => {
  if (isInitializingForm.value) return;
  if (registrationDateRange.value?.start) {
    formState.value.schedule.registration_start = combineDateTime(registrationDateRange.value.start, registrationStartTime.value);
  }
  if (registrationDateRange.value?.end) {
    formState.value.schedule.registration_end = combineDateTime(registrationDateRange.value.end, registrationEndTime.value);
  }
});

// Watch date range and time changes for team formation
watch([teamFormationDateRange, teamFormationStartTime, teamFormationEndTime], () => {
  if (isInitializingForm.value) return;
  if (teamFormationDateRange.value?.start) {
    formState.value.schedule.team_formation_start = combineDateTime(teamFormationDateRange.value.start, teamFormationStartTime.value);
  } else {
    formState.value.schedule.team_formation_start = null;
  }

  if (teamFormationDateRange.value?.end) {
    formState.value.schedule.team_formation_end = combineDateTime(teamFormationDateRange.value.end, teamFormationEndTime.value);
  } else {
    formState.value.schedule.team_formation_end = null;
  }
});

// Watch isTeamCompetition and clear team fields when switching to individual
watch(isTeamCompetition, (isTeam) => {
  if (!isTeam) {
    // Clear team formation dates
    teamFormationDateRange.value = undefined;
    teamFormationStartTime.value = new Time(0, 0);
    teamFormationEndTime.value = new Time(0, 0);
    formState.value.schedule.team_formation_start = null;
    formState.value.schedule.team_formation_end = null;

    // Reset team size to 1-1 for individual
    formState.value.team_size.min = 1;
    formState.value.team_size.max = 1;
  }
});

// Sync milestones into formState
watch(milestones, () => {
  if (isInitializingForm.value) return;
  formState.value.milestones = getMilestonesForSubmit();
}, { deep: true });

// Helper function to check if a date is in the past
const isDateInPast = (dateString: string | null): boolean => {
  if (!dateString) return false;
  const date = new Date(dateString);
  return date < new Date();
};

// Initialize form when entering edit mode
const initializeForm = (comp: any) => {
  // Block watchers during initialization
  isInitializingForm.value = true;

  // Store original dates and check which are locked (in the past)
  originalDates.value.registrationStart = comp.schedule.registration_start;
  originalDates.value.registrationEnd = comp.schedule.registration_end;
  originalDates.value.teamFormationStart = comp.schedule.team_formation_start;
  originalDates.value.teamFormationEnd = comp.schedule.team_formation_end;

  lockedDates.value.registrationStart = isDateInPast(comp.schedule.registration_start);
  lockedDates.value.registrationEnd = isDateInPast(comp.schedule.registration_end);
  lockedDates.value.teamFormationStart = isDateInPast(comp.schedule.team_formation_start);
  lockedDates.value.teamFormationEnd = isDateInPast(comp.schedule.team_formation_end);

  // Set form state first - all the actual form data
  formState.value.title = comp.title;
  formState.value.description = comp.description;
  formState.value.schedule.registration_start = comp.schedule.registration_start;
  formState.value.schedule.registration_end = comp.schedule.registration_end;
  formState.value.schedule.team_formation_start = comp.schedule.team_formation_start;
  formState.value.schedule.team_formation_end = comp.schedule.team_formation_end;
  formState.value.participant_limits.min = comp.participant_limits.min;
  formState.value.participant_limits.max = comp.participant_limits.max;
  formState.value.domains = [...comp.domains];
  formState.value.participant_type = comp.participant_type;
  formState.value.venue.format = comp.venue.format;
  formState.value.venue.location = comp.venue.location;
  formState.value.team_size.min = comp.team_size.min;
  formState.value.team_size.max = comp.team_size.max;
  formState.value.milestones = comp.milestones.map((m: any) => ({
    title: m.title,
    timestamp: m.timestamp,
  }));
  formState.value.is_archived = comp.is_archived;

  // Initialize team competition flag based on whether team_formation dates exist
  const hasTeamFormationDates = !!(comp.schedule.team_formation_start && comp.schedule.team_formation_end);
  isTeamCompetition.value = hasTeamFormationDates;

  // Parse and set registration dates for UI components
  try {
    const regStart = parseAbsoluteToLocal(comp.schedule.registration_start);
    const regEnd = parseAbsoluteToLocal(comp.schedule.registration_end);

    registrationDateRange.value = {
      start: new CalendarDate(regStart.year, regStart.month, regStart.day),
      end: new CalendarDate(regEnd.year, regEnd.month, regEnd.day),
    };
    registrationStartTime.value = new Time(regStart.hour, regStart.minute);
    registrationEndTime.value = new Time(regEnd.hour, regEnd.minute);
  } catch (e) {
    console.error('Failed to parse registration dates:', e);
    // Fallback: try parsing as Date
    const regStartDate = new Date(comp.schedule.registration_start);
    const regEndDate = new Date(comp.schedule.registration_end);

    registrationDateRange.value = {
      start: new CalendarDate(regStartDate.getFullYear(), regStartDate.getMonth() + 1, regStartDate.getDate()),
      end: new CalendarDate(regEndDate.getFullYear(), regEndDate.getMonth() + 1, regEndDate.getDate()),
    };
    registrationStartTime.value = new Time(regStartDate.getHours(), regStartDate.getMinutes());
    registrationEndTime.value = new Time(regEndDate.getHours(), regEndDate.getMinutes());
  }

  // Parse and set team formation dates for UI components if they exist
  if (hasTeamFormationDates) {
    try {
      const teamStart = parseAbsoluteToLocal(comp.schedule.team_formation_start);
      const teamEnd = parseAbsoluteToLocal(comp.schedule.team_formation_end);

      teamFormationDateRange.value = {
        start: new CalendarDate(teamStart.year, teamStart.month, teamStart.day),
        end: new CalendarDate(teamEnd.year, teamEnd.month, teamEnd.day),
      };
      teamFormationStartTime.value = new Time(teamStart.hour, teamStart.minute);
      teamFormationEndTime.value = new Time(teamEnd.hour, teamEnd.minute);
    } catch (e) {
      console.error('Failed to parse team formation dates:', e);
      // Fallback: try parsing as Date
      const teamStartDate = new Date(comp.schedule.team_formation_start);
      const teamEndDate = new Date(comp.schedule.team_formation_end);

      teamFormationDateRange.value = {
        start: new CalendarDate(teamStartDate.getFullYear(), teamStartDate.getMonth() + 1, teamStartDate.getDate()),
        end: new CalendarDate(teamEndDate.getFullYear(), teamEndDate.getMonth() + 1, teamEndDate.getDate()),
      };
      teamFormationStartTime.value = new Time(teamStartDate.getHours(), teamStartDate.getMinutes());
      teamFormationEndTime.value = new Time(teamEndDate.getHours(), teamEndDate.getMinutes());
    }
  } else {
    teamFormationDateRange.value = undefined;
    teamFormationStartTime.value = new Time(0, 0);
    teamFormationEndTime.value = new Time(0, 0);
  }

  // Parse and set milestones for UI components
  milestones.value = comp.milestones.map((m: any) => {
    try {
      const dt = parseAbsoluteToLocal(m.timestamp);
      return {
        title: m.title,
        date: new CalendarDate(dt.year, dt.month, dt.day),
        time: new Time(dt.hour, dt.minute),
      };
    } catch (e) {
      console.error('Failed to parse milestone date:', e);
      // Fallback: try parsing as Date
      const date = new Date(m.timestamp);
      return {
        title: m.title,
        date: new CalendarDate(date.getFullYear(), date.getMonth() + 1, date.getDate()),
        time: new Time(date.getHours(), date.getMinutes()),
      };
    }
  });

  // Unblock watchers after initialization completes
  nextTick(() => {
    isInitializingForm.value = false;
  });
};

// Prepare form data with locked dates replaced by originals
const prepareFormDataForSubmit = (): UpdateCompetitionForm => {
  const data = { ...formState.value };

  // Replace locked dates with original values
  if (lockedDates.value.registrationStart) {
    data.schedule.registration_start = originalDates.value.registrationStart;
  }
  if (lockedDates.value.registrationEnd) {
    data.schedule.registration_end = originalDates.value.registrationEnd;
  }
  if (lockedDates.value.teamFormationStart && originalDates.value.teamFormationStart) {
    data.schedule.team_formation_start = originalDates.value.teamFormationStart;
  }
  if (lockedDates.value.teamFormationEnd && originalDates.value.teamFormationEnd) {
    data.schedule.team_formation_end = originalDates.value.teamFormationEnd;
  }

  return data;
};

// Handle form submission
const handleSubmit = async () => {
  isSubmitting.value = true;

  try {
    const submitData = prepareFormDataForSubmit();
    const result = await competitionStore.updateCompetition(
      competitionId.value,
      submitData
    );

    if (result.success) {
      notifications.add({
        title: t('toast.competitionUpdated.title'),
        description: t('toast.competitionUpdated.description'),
        icon: 'i-heroicons-check-circle',
        color: 'success',
      });
      router.push(`/me/competitions/${competitionId.value}`);
    } else if (result.error) {
      notifications.add({
        title: t('errors.default.title'),
        description: result.error.message,
        icon: 'i-heroicons-exclamation-triangle',
        color: 'error',
      });
    }
  } catch (error: any) {
    notifications.add({
      title: t('errors.default.title'),
      description: error.message || t('errors.default.description'),
      icon: 'i-heroicons-exclamation-triangle',
      color: 'error',
    });
  } finally {
    isSubmitting.value = false;
  }
};

// Handle form error
const { handleFormError: handleError } = useFormErrorScroll();
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

          <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            {{ t('competition.edit.title') }}
          </h1>
          <p class="text-gray-600 dark:text-gray-400">
            {{ t('competition.edit.description') }}
          </p>
        </div>

        <!-- Loading state -->
        <div v-if="competitionStore.loading && !competition" class="space-y-6">
          <div class="flex items-start gap-4">
            <USkeleton class="h-10 w-3/4" />
            <USkeleton class="h-8 w-24 rounded-full" />
          </div>
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <USkeleton v-for="i in 4" :key="i" class="h-48 w-full rounded-lg" />
          </div>
        </div>

        <!-- Edit Form -->
        <div v-else-if="competition">
          <UForm
            :state="formState"
            :schema="competitionUpdateSchema"
            @submit="handleSubmit"
            @error="handleError"
            class="space-y-6"
          >
            <!-- Cards Grid - Two columns on large screens -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <!-- Basic Information -->
              <CompetitionFormBasicInfoFormSection
                v-model:title="formState.title"
                v-model:description="formState.description"
                v-model:domains="formState.domains"
                v-model:participant-type="formState.participant_type"
                v-model:is-team-competition="isTeamCompetition"
                v-model:is-archived="formState.is_archived"
                show-archive-field
              />

              <!-- Schedule -->
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

              <!-- Participants -->
              <CompetitionFormParticipantsFormSection
                v-model:participant-limits-min="formState.participant_limits.min"
                v-model:participant-limits-max="formState.participant_limits.max"
                v-model:team-size-min="formState.team_size.min"
                v-model:team-size-max="formState.team_size.max"
                :is-team-competition="isTeamCompetition"
              />

              <!-- Venue -->
              <CompetitionFormVenueFormSection
                v-model:format="formState.venue.format"
                v-model:location="formState.venue.location"
              />

              <!-- Milestones -->
              <CompetitionFormMilestonesFormSection
                v-model:milestones="milestones"
                @add-milestone="addMilestone"
                @remove-milestone="removeMilestone"
              />
            </div>

            <!-- Submit Button -->
            <div class="flex justify-end gap-4 pt-4">
              <UButton
                variant="outline"
                color="neutral"
                size="xl"
                :label="t('common.cancel')"
                @click="goBack"
                :disabled="isSubmitting"
              />
              <UButton
                type="submit"
                color="primary"
                size="xl"
                :label="t('common.save')"
                :loading="isSubmitting"
                :disabled="isSubmitting"
              />
            </div>
          </UForm>
        </div>
      </UContainer>
    </UPageBody>
  </UPage>
</template>
