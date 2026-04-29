<script setup lang="ts">
import type { StepperItem } from '@nuxt/ui';
import type { CompetitionForm } from '~/types/api';
import { createCompetitionSchemas } from '~/schemas/competition';
import { useCompetitionStore } from '~/stores/competition';
import { useNotificationsStore } from '~/stores/notifications';
import { CalendarDate, Time, today, getLocalTimeZone } from '@internationalized/date';
import { combineDateTime } from '~/utils/dateTime';

const { t } = useI18n();
const router = useRouter();
const competitionStore = useCompetitionStore();
const notifications = useNotificationsStore();
const { navigateBack } = useBackNavigation('/me/competitions');

useSeoMeta({
  title: t('seo.createCompetition.title'),
  description: t('seo.createCompetition.description'),
});

// Stepper
const stepperRef = useTemplateRef('stepperRef');
const formRef = useTemplateRef('formRef');
const currentStep = ref(0);

const stepperItems = computed<StepperItem[]>(() => [
  {
    title: t('competition.create.steps.basics.title'),
    icon: 'i-heroicons-information-circle',
  },
  {
    title: t('competition.create.steps.scheduleParticipants.title'),
    icon: 'i-heroicons-calendar-days',
  },
  {
    title: t('competition.create.steps.venue.title'),
    icon: 'i-heroicons-map-pin',
  },
  {
    title: t('competition.create.steps.milestones.title'),
    icon: 'i-heroicons-flag',
  },
]);

const stepFields: string[][] = [
  ['title', 'description', 'tag_ids', 'tracks'],
  ['schedule', 'participant_limits', 'team_size'],
  ['venue'],
  ['milestones'],
];

const isLastStep = computed(() => currentStep.value === stepperItems.value.length - 1);

const topAnchor = useTemplateRef<HTMLElement>('topAnchor');

const scrollToTop = () => {
  if (!import.meta.client) return;
  // UMain / UPage often owns the scroll container, not window — use scrollIntoView
  // on a top-of-form anchor so the browser walks up to whichever element scrolls.
  topAnchor.value?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  // Belt-and-braces for layouts where window itself scrolls.
  window.scrollTo({ top: 0, behavior: 'smooth' });
  document.documentElement.scrollTo({ top: 0, behavior: 'smooth' });
};

// Inline alert errors shown above the form when a step validation or submit fails.
// Kept visible until the user advances or fixes them — a transient toast is easy to miss.
const submissionErrors = ref<Array<{ name?: string; message: string }>>([]);

const collectErrors = (errs: Array<{ name?: string; message?: string }>) =>
  errs
    .map((e) => ({ name: e.name, message: (e.message ?? '').trim() }))
    .filter((e) => e.message.length > 0);

const goNext = async () => {
  // UForm keeps errors from previous validation runs in its internal ref. After a failed
  // submit on the last step, stale errors (e.g. milestone date in past) would still be in
  // `errors.value`, and validate() throws if the combined list is non-empty — even when the
  // fields for the current step are all valid. Clearing before re-validating fixes that.
  (formRef.value as any)?.clear?.();
  try {
    await (formRef.value as any)?.validate({ name: stepFields[currentStep.value] });
    submissionErrors.value = [];
    // UStepper is v-model'd on currentStep — mutating it moves both. Don't also call
    // stepperRef.next() or the two sources fight and desync after a validation miss.
    if (currentStep.value < stepperItems.value.length - 1) {
      currentStep.value++;
    }
    await nextTick();
    scrollToTop();
  } catch (err: any) {
    submissionErrors.value = collectErrors(err?.errors ?? []);
    handleError({ errors: err?.errors ?? [] });
  }
};

const goPrev = () => {
  submissionErrors.value = [];
  (formRef.value as any)?.clear?.();
  if (currentStep.value > 0) {
    currentStep.value--;
  }
  nextTick(scrollToTop);
};

// Is team competition toggle
const isTeamCompetition = ref(true);

// UI default for the team-size slider when the user first enables "team competition".
// A team needs at least 2 members to make sense; 5 is the typical hackathon cap.
const DEFAULT_TEAM_SIZE = { min: 2, max: 5 } as const;

// Form state
const formState = reactive<CompetitionForm & { is_team: boolean }>({
  title: '',
  description: '',
  schedule: {
    registration_start: '',
    registration_end: '',
    team_formation_start: null,
    team_formation_end: null,
  },
  participant_limits: {
    max: 100,
  },
  tag_ids: [],
  tracks: [{ name: 'Общий' }],
  participant_type: 'any',
  venue: {
    format: 'online',
    location: null,
  },
  team_size: { ...DEFAULT_TEAM_SIZE },
  auto_accept: false,
  milestones: [],
  is_team: true,
});

// Date ranges for schedule
const registrationDateRange = ref<{ start: CalendarDate; end: CalendarDate } | undefined>(undefined);
const registrationStartTime = ref<Time | undefined>(new Time(0, 0));
const registrationEndTime = ref<Time | undefined>(new Time(0, 0));

const teamFormationDateRange = ref<{ start: CalendarDate; end: CalendarDate } | undefined>(undefined);
const teamFormationStartTime = ref<Time | undefined>(new Time(0, 0));
const teamFormationEndTime = ref<Time | undefined>(new Time(0, 0));

const registrationMinValue = computed(() => today(getLocalTimeZone()));

const teamFormationMinValue = computed(() => {
  if (registrationDateRange.value?.end) {
    return registrationDateRange.value.end.add({ days: 1 });
  }
  return today(getLocalTimeZone());
});

watch(isTeamCompetition, (isTeam) => {
  formState.is_team = isTeam;
  if (!isTeam) {
    teamFormationDateRange.value = undefined;
    teamFormationStartTime.value = new Time(0, 0);
    teamFormationEndTime.value = new Time(0, 0);
    formState.schedule.team_formation_start = null;
    formState.schedule.team_formation_end = null;
    // Pairing invariant: team_size must be null whenever team_formation dates are null.
    formState.team_size = null;
  } else if (formState.team_size === null) {
    formState.team_size = { min: 1, max: 5 };
  }
});

watch([registrationDateRange, registrationStartTime, registrationEndTime], () => {
  if (registrationDateRange.value?.start) {
    formState.schedule.registration_start = combineDateTime(registrationDateRange.value.start, registrationStartTime.value);
  }
  if (registrationDateRange.value?.end) {
    formState.schedule.registration_end = combineDateTime(registrationDateRange.value.end, registrationEndTime.value);
  }
});

watch([teamFormationDateRange, teamFormationStartTime, teamFormationEndTime], () => {
  if (teamFormationDateRange.value?.start) {
    formState.schedule.team_formation_start = combineDateTime(teamFormationDateRange.value.start, teamFormationStartTime.value);
  } else {
    formState.schedule.team_formation_start = null;
  }
  if (teamFormationDateRange.value?.end) {
    formState.schedule.team_formation_end = combineDateTime(teamFormationDateRange.value.end, teamFormationEndTime.value);
  } else {
    formState.schedule.team_formation_end = null;
  }
});

const schemas = createCompetitionSchemas(t);
const { milestones, addMilestone, removeMilestone, getMilestonesForSubmit } = useMilestones(combineDateTime);

watch(milestones, () => {
  formState.milestones = getMilestonesForSubmit();
}, { deep: true });

const isSubmitting = ref(false);

const handleSubmit = async () => {
  isSubmitting.value = true;
  try {
    const { is_team, ...formDataWithoutIsTeam } = formState;
    const formData: CompetitionForm = {
      ...formDataWithoutIsTeam,
      milestones: getMilestonesForSubmit(),
    };
    await competitionStore.createCompetition(formData);
    if (competitionStore.creationSuccess) {
      router.push('/me/competitions');
    } else if (competitionStore.error) {
      notifications.add({
        title: t('errors.default.title'),
        description: getErrorMessage(competitionStore.error) ?? t('errors.default.description'),
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

const { handleFormError: baseHandleError } = useFormErrorScroll();
const { getErrorMessage } = useErrorHandler();

const handleError = async (event: any) => {
  submissionErrors.value = collectErrors(event?.errors ?? []);
  await baseHandleError(event);
  await nextTick();
  scrollToTop();
};

const goBack = () => {
  navigateBack();
};
</script>

<template>
  <UPage>
    <UPageBody>
      <UContainer class="!max-w-3xl">
        <div ref="topAnchor" aria-hidden="true" />
        <!-- Header -->
        <div class="mb-6">
          <UButton
            icon="i-heroicons-arrow-left"
            variant="ghost"
            color="neutral"
            :label="t('competition.create.backButton')"
            @click="goBack"
            class="mb-4"
          />
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-1">
            {{ t('competition.create.title') }}
          </h1>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ t('competition.create.description') }}
          </p>
        </div>

        <!-- Mobile: compact step indicator -->
        <div class="flex md:hidden mb-6 items-center gap-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-800">
          <div class="flex items-center justify-center w-7 h-7 rounded-full bg-primary-500 text-white text-xs font-bold shrink-0">
            {{ currentStep + 1 }}
          </div>
          <div class="min-w-0">
            <div class="text-xs text-gray-500 dark:text-gray-400">{{ t('competition.create.stepLabel', { current: currentStep + 1, total: stepperItems.length }) }}</div>
            <div class="text-sm font-semibold truncate">{{ stepperItems[currentStep]?.title }}</div>
          </div>
        </div>

        <!-- Desktop: full stepper -->
        <UStepper
          ref="stepperRef"
          v-model="currentStep"
          :items="stepperItems"
          disabled
          class="hidden md:flex mb-8"
        />

        <!-- Inline validation alert — persistent, unlike the toast the user may miss -->
        <UAlert
          v-if="submissionErrors.length > 0"
          :title="t('competition.create.validation.alertTitle')"
          color="error"
          variant="soft"
          icon="i-heroicons-exclamation-triangle"
          class="mb-4"
          :close="false"
        >
          <template #description>
            <ul class="list-disc pl-5 space-y-1 text-sm">
              <li v-for="(err, i) in submissionErrors" :key="i">
                {{ err.message }}
              </li>
            </ul>
          </template>
        </UAlert>

        <!-- Form (wraps all steps for unified validation) -->
        <UForm
          ref="formRef"
          :state="formState"
          :schema="schemas.competitionFormSchema"
          @submit="handleSubmit"
          @error="handleError"
        >
          <!-- Step 0: Basics -->
          <div v-show="currentStep === 0">
            <CompetitionFormBasicInfoFormSection
              v-model:title="formState.title"
              v-model:description="formState.description"
              v-model:tag-ids="formState.tag_ids"
              v-model:tracks="formState.tracks"
              v-model:participant-type="formState.participant_type"
              v-model:is-team-competition="isTeamCompetition"
              v-model:auto-accept="formState.auto_accept"
            />
          </div>

          <!-- Step 1: Schedule + Participants -->
          <div v-show="currentStep === 1" class="space-y-6">
            <CompetitionFormScheduleFormSection
              v-model:registration-date-range="registrationDateRange"
              v-model:registration-start-time="registrationStartTime"
              v-model:registration-end-time="registrationEndTime"
              v-model:team-formation-date-range="teamFormationDateRange"
              v-model:team-formation-start-time="teamFormationStartTime"
              v-model:team-formation-end-time="teamFormationEndTime"
              :is-team-competition="isTeamCompetition"
              :registration-min-value="registrationMinValue"
              :team-formation-min-value="teamFormationMinValue"
            />
            <CompetitionFormParticipantsFormSection
              v-model:participant-limits-max="formState.participant_limits.max"
              v-model:team-size="formState.team_size"
              :is-team-competition="isTeamCompetition"
            />
          </div>

          <!-- Step 2: Venue -->
          <div v-show="currentStep === 2">
            <CompetitionFormVenueFormSection
              v-model:format="formState.venue.format"
              v-model:location="formState.venue.location"
            />
          </div>

          <!-- Step 3: Milestones -->
          <div v-show="currentStep === 3">
            <CompetitionFormMilestonesFormSection
              v-model:milestones="milestones"
              @add-milestone="addMilestone"
              @remove-milestone="removeMilestone"
            />
          </div>

          <!-- Navigation -->
          <div class="flex flex-col-reverse sm:flex-row sm:justify-center sm:items-center gap-2 sm:gap-3 mt-6">
            <UButton
              v-if="currentStep > 0"
              icon="i-heroicons-arrow-left"
              variant="ghost"
              color="neutral"
              size="lg"
              :label="t('competition.create.prevStep')"
              @click="goPrev"
              :disabled="isSubmitting"
              class="w-full sm:w-auto justify-center"
            />
            <UButton
              v-if="!isLastStep"
              icon="i-heroicons-arrow-right"
              trailing
              color="primary"
              size="lg"
              :label="t('competition.create.nextStep')"
              @click="goNext"
              class="w-full sm:w-auto justify-center"
            />
            <UButton
              v-else
              type="submit"
              icon="i-heroicons-check-circle"
              color="primary"
              size="lg"
              :label="isSubmitting ? t('competition.create.submitting') : t('competition.create.submitButton')"
              :loading="isSubmitting"
              :disabled="isSubmitting"
              class="w-full sm:w-auto justify-center"
            />
          </div>
        </UForm>
      </UContainer>
    </UPageBody>
  </UPage>
</template>
