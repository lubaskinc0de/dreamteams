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
  ['title', 'description', 'domains'],
  ['schedule', 'participant_limits', 'team_size'],
  ['venue'],
  ['milestones'],
];

const isLastStep = computed(() => currentStep.value === stepperItems.value.length - 1);

const goNext = async () => {
  try {
    await (formRef.value as any)?.validate({ name: stepFields[currentStep.value] });
    currentStep.value++;
    stepperRef.value?.next();
  } catch {
    // validation errors shown inline
  }
};

const goPrev = () => {
  currentStep.value--;
  stepperRef.value?.prev();
};

// Is team competition toggle
const isTeamCompetition = ref(true);

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
    formState.team_size.min = 1;
    formState.team_size.max = 5;
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
        description: competitionStore.error.message,
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

const { handleFormError: handleError } = useFormErrorScroll();

const goBack = () => {
  router.push('/me/competitions');
};
</script>

<template>
  <UPage>
    <UPageBody>
      <UContainer class="!max-w-3xl">
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
              v-model:domains="formState.domains"
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
              v-model:participant-limits-min="formState.participant_limits.min"
              v-model:participant-limits-max="formState.participant_limits.max"
              v-model:team-size-min="formState.team_size.min"
              v-model:team-size-max="formState.team_size.max"
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
          <div class="flex flex-col-reverse sm:flex-row sm:justify-between sm:items-center gap-3 mt-6">
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
            <div v-else class="hidden sm:block" />

            <div class="flex flex-col-reverse sm:flex-row items-stretch sm:items-center gap-2 sm:gap-3">
              <UButton
                variant="ghost"
                color="neutral"
                size="lg"
                :label="t('common.cancel')"
                @click="goBack"
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
          </div>
        </UForm>
      </UContainer>
    </UPageBody>
  </UPage>
</template>
