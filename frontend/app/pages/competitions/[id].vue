<script setup lang="ts">
import type { CompetitionModel, UpdateCompetitionForm, Domain, ParticipantType, CompetitionFormat } from '~/types/api';
import { useCompetitionStore } from '~/stores/competition';
import { CalendarDate, Time, parseDateTime } from '@internationalized/date';
import { createCompetitionSchemas } from '~/schemas/competition';

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const competitionStore = useCompetitionStore();
const toast = useToast();

// SEO Meta tags
useSeoMeta({
  title: t('seo.competitionDetail.title'),
  description: t('seo.competitionDetail.description'),
});

// Get competition ID from route
const competitionId = computed(() => route.params.id as string);

// Edit mode state
const isEditMode = ref(false);
const isSubmitting = ref(false);

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

// Format date for display
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

// Format time for display
const formatTime = (dateString: string) => {
  return new Date(dateString).toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
  });
};

// Get domain label
const getDomainLabel = (domain: string) => {
  return t(`competition.form.domains.options.${domain}`);
};

// Get format label
const getFormatLabel = (format: string) => {
  return t(`competition.formats.${format}`);
};

// Get participant type label
const getParticipantTypeLabel = (type: string) => {
  return t(`competition.participantTypes.${type}`);
};

// Get registration status
const getRegistrationStatus = (comp: CompetitionModel) => {
  const now = new Date();
  const regStart = new Date(comp.schedule.registration_start);
  const regEnd = new Date(comp.schedule.registration_end);

  if (now < regStart) {
    return { label: t('competitions.status.notOpen'), color: 'warning' as const };
  } else if (now >= regStart && now <= regEnd) {
    return { label: t('competitions.status.open'), color: 'success' as const };
  } else {
    return { label: t('competitions.status.closed'), color: 'info' as const };
  }
};

// Format team size display
const formatTeamSize = (teamSize: { min: number; max: number }) => {
  if (teamSize.min === 1 && teamSize.max === 1) {
    return t('competitions.card.noTeams');
  }
  return `${teamSize.min}—${teamSize.max}`;
};

// ===== EDIT MODE FORM STATE =====
const { competitionFormSchema } = createCompetitionSchemas(t);
const isTeamCompetition = ref(true);

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

// Template refs for calendar popovers
const registrationDateInput = useTemplateRef('registrationDateInput');
const teamFormationDateInput = useTemplateRef('teamFormationDateInput');

// Date ranges for schedule
const registrationDateRange = ref<{ start: CalendarDate; end: CalendarDate } | undefined>(undefined);
const registrationStartTime = ref<Time | undefined>(new Time(0, 0));
const registrationEndTime = ref<Time | undefined>(new Time(0, 0));

const teamFormationDateRange = ref<{ start: CalendarDate; end: CalendarDate } | undefined>(undefined);
const teamFormationStartTime = ref<Time | undefined>(new Time(0, 0));
const teamFormationEndTime = ref<Time | undefined>(new Time(0, 0));

// Milestone management
interface MilestoneInput {
  title: string;
  date: CalendarDate | undefined;
  time: Time | undefined;
}

const milestones = ref<MilestoneInput[]>([]);

// Helper function to combine date and time into ISO string
const combineDateTime = (date: any, time: any): string => {
  if (!date) return '';
  const hour = time?.hour ?? 0;
  const minute = time?.minute ?? 0;
  return new Date(date.year, date.month - 1, date.day, hour, minute).toISOString();
};

// Watch date range and time changes for registration
watch([registrationDateRange, registrationStartTime, registrationEndTime], () => {
  if (registrationDateRange.value?.start) {
    formState.value.schedule.registration_start = combineDateTime(registrationDateRange.value.start, registrationStartTime.value);
  }
  if (registrationDateRange.value?.end) {
    formState.value.schedule.registration_end = combineDateTime(registrationDateRange.value.end, registrationEndTime.value);
  }
});

// Watch date range and time changes for team formation
watch([teamFormationDateRange, teamFormationStartTime, teamFormationEndTime], () => {
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
  formState.value.milestones = getMilestonesForSubmit();
}, { deep: true });

// Initialize form when entering edit mode
watch([competition, isEditMode], ([comp, editMode]) => {
  if (comp && editMode) {
    // Initialize team competition flag
    isTeamCompetition.value = !(comp.team_size.min === 1 && comp.team_size.max === 1);

    // Parse registration dates
    const regStart = parseDateTime(comp.schedule.registration_start);
    const regEnd = parseDateTime(comp.schedule.registration_end);

    registrationDateRange.value = {
      start: new CalendarDate(regStart.year, regStart.month, regStart.day),
      end: new CalendarDate(regEnd.year, regEnd.month, regEnd.day),
    };
    registrationStartTime.value = new Time(regStart.hour, regStart.minute);
    registrationEndTime.value = new Time(regEnd.hour, regEnd.minute);

    // Parse team formation dates if they exist
    if (comp.schedule.team_formation_start && comp.schedule.team_formation_end) {
      const teamStart = parseDateTime(comp.schedule.team_formation_start);
      const teamEnd = parseDateTime(comp.schedule.team_formation_end);

      teamFormationDateRange.value = {
        start: new CalendarDate(teamStart.year, teamStart.month, teamStart.day),
        end: new CalendarDate(teamEnd.year, teamEnd.month, teamEnd.day),
      };
      teamFormationStartTime.value = new Time(teamStart.hour, teamStart.minute);
      teamFormationEndTime.value = new Time(teamEnd.hour, teamEnd.minute);
    } else {
      teamFormationDateRange.value = undefined;
      teamFormationStartTime.value = new Time(0, 0);
      teamFormationEndTime.value = new Time(0, 0);
    }

    // Parse milestones
    milestones.value = comp.milestones.map(m => {
      const dt = parseDateTime(m.timestamp);
      return {
        title: m.title,
        date: new CalendarDate(dt.year, dt.month, dt.day),
        time: new Time(dt.hour, dt.minute),
      };
    });

    // Set form state
    formState.value = {
      title: comp.title,
      description: comp.description,
      schedule: {
        registration_start: comp.schedule.registration_start,
        registration_end: comp.schedule.registration_end,
        team_formation_start: comp.schedule.team_formation_start,
        team_formation_end: comp.schedule.team_formation_end,
      },
      participant_limits: {
        min: comp.participant_limits.min,
        max: comp.participant_limits.max,
      },
      domains: comp.domains,
      participant_type: comp.participant_type,
      venue: {
        format: comp.venue.format,
        location: comp.venue.location,
      },
      team_size: {
        min: comp.team_size.min,
        max: comp.team_size.max,
      },
      milestones: comp.milestones.map(m => ({
        title: m.title,
        timestamp: m.timestamp,
      })),
      is_archived: comp.is_archived,
    };
  }
}, { immediate: true });

// Toggle edit mode
const toggleEditMode = () => {
  if (isEditMode.value) {
    // Cancel editing - reload competition data
    competitionStore.fetchCompetition(competitionId.value);
  }
  isEditMode.value = !isEditMode.value;
};

// Domain options
const domainOptions = [
  { value: 'frontend' as Domain, label: t('competition.form.domains.options.frontend') },
  { value: 'mobile' as Domain, label: t('competition.form.domains.options.mobile') },
  { value: 'backend' as Domain, label: t('competition.form.domains.options.backend') },
  { value: 'ai' as Domain, label: t('competition.form.domains.options.ai') },
  { value: 'devops' as Domain, label: t('competition.form.domains.options.devops') },
];

// Participant type options
const participantTypeOptions = [
  { value: 'schoolchild' as ParticipantType, label: t('competition.form.participantType.options.schoolchild') },
  { value: 'student' as ParticipantType, label: t('competition.form.participantType.options.student') },
  { value: 'any' as ParticipantType, label: t('competition.form.participantType.options.any') },
];

// Venue format options
const venueFormatOptions = [
  { value: 'online' as CompetitionFormat, label: t('competition.form.venue.format.options.online') },
  { value: 'offline' as CompetitionFormat, label: t('competition.form.venue.format.options.offline') },
  { value: 'hybrid' as CompetitionFormat, label: t('competition.form.venue.format.options.hybrid') },
];

const addMilestone = () => {
  milestones.value.push({
    title: '',
    date: undefined,
    time: new Time(0, 0)
  });
};

const removeMilestone = (index: number) => {
  milestones.value.splice(index, 1);
};

// Convert milestones to the format expected by the API
const getMilestonesForSubmit = (): Array<{ title: string; timestamp: string }> => {
  return milestones.value
    .filter(m => m.title && m.date)
    .map(m => ({
      title: m.title,
      timestamp: combineDateTime(m.date, m.time)
    })) as Array<{ title: string; timestamp: string }>;
};

// Handle form submission
const handleSubmit = async () => {
  isSubmitting.value = true;

  try {
    const result = await competitionStore.updateCompetition(
      competitionId.value,
      formState.value
    );

    if (result.success) {
      isEditMode.value = false;
    } else if (result.error) {
      toast.add({
        title: t('errors.default.title'),
        description: result.error.message,
        icon: 'i-heroicons-exclamation-triangle',
        color: 'error',
      });
    }
  } catch (error: any) {
    toast.add({
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
const handleError = async (event: any) => {
  const errors = event.errors || [];
  if (errors.length > 0) {
    toast.add({
      title: t('competition.create.validation.errorsFound', { count: errors.length }),
      description: t('competition.create.validation.scrollToErrors'),
      icon: 'i-heroicons-exclamation-circle',
      color: 'error',
    });
    await nextTick();
    const firstErrorElement = document.getElementById(errors[0].id);
    if (firstErrorElement) {
      firstErrorElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
      firstErrorElement.focus();
    }
  }
};
</script>

<template>
  <UPage>
    <UPageBody>
      <div class="max-w-7xl mx-auto">
        <!-- Header -->
        <div class="mb-6 flex items-center justify-between">
          <div class="flex items-center gap-4">
            <UButton
              icon="i-heroicons-arrow-left"
              color="neutral"
              variant="ghost"
              @click="goBack"
            />
            <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
              {{ isEditMode ? t('competition.edit.title') : competition?.title }}
            </h1>
          </div>

          <div v-if="!isEditMode" class="flex items-center gap-3">
            <UBadge
              v-if="competition?.is_archived"
              color="warning"
              variant="subtle"
              :label="t('competitions.badge.archived')"
            />
            <UBadge
              v-else-if="competition"
              :color="getRegistrationStatus(competition).color"
              variant="subtle"
              :label="getRegistrationStatus(competition).label"
            />
            <UButton
              icon="i-heroicons-pencil"
              color="primary"
              :label="t('competition.detail.editButton')"
              @click="toggleEditMode"
            />
          </div>
        </div>

        <!-- Loading state -->
        <div v-if="competitionStore.loading && !competition" class="flex justify-center py-12">
          <UProgress indeterminate size="md" />
        </div>

        <!-- View Mode -->
        <div v-else-if="!isEditMode && competition" class="space-y-6">
          <!-- Description -->
          <UCard>
            <template #header>
              <h2 class="text-xl font-semibold">{{ t('competition.detail.description') }}</h2>
            </template>
            <p class="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ competition.description }}</p>
          </UCard>

          <!-- Schedule -->
          <UCard>
            <template #header>
              <h2 class="text-xl font-semibold">{{ t('competition.detail.schedule') }}</h2>
            </template>
            <div class="space-y-4">
              <div>
                <h3 class="font-medium mb-2">{{ t('competition.form.schedule.registrationPeriod.label') }}</h3>
                <p class="text-gray-700 dark:text-gray-300">
                  {{ formatDate(competition.schedule.registration_start) }} {{ formatTime(competition.schedule.registration_start) }}
                  —
                  {{ formatDate(competition.schedule.registration_end) }} {{ formatTime(competition.schedule.registration_end) }}
                </p>
              </div>

              <div v-if="competition.schedule.team_formation_start && competition.schedule.team_formation_end">
                <h3 class="font-medium mb-2">{{ t('competition.form.schedule.teamFormationPeriod.label') }}</h3>
                <p class="text-gray-700 dark:text-gray-300">
                  {{ formatDate(competition.schedule.team_formation_start) }} {{ formatTime(competition.schedule.team_formation_start) }}
                  —
                  {{ formatDate(competition.schedule.team_formation_end) }} {{ formatTime(competition.schedule.team_formation_end) }}
                </p>
              </div>
            </div>
          </UCard>

          <!-- Details -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <UCard>
              <template #header>
                <h2 class="text-xl font-semibold">{{ t('competition.detail.participants') }}</h2>
              </template>
              <div class="space-y-3">
                <div>
                  <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                    {{ t('competition.form.participantLimits.label') }}
                  </h3>
                  <p class="text-gray-900 dark:text-white">
                    {{ competition.participant_limits.min }}—{{ competition.participant_limits.max }}
                  </p>
                </div>

                <div>
                  <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                    {{ t('competition.form.participantType.label') }}
                  </h3>
                  <p class="text-gray-900 dark:text-white">
                    {{ getParticipantTypeLabel(competition.participant_type) }}
                  </p>
                </div>

                <div>
                  <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                    {{ competition.team_size.min === 1 && competition.team_size.max === 1 ? t('competitions.card.noTeams') : t('competitions.card.teamSize') }}
                  </h3>
                  <p v-if="!(competition.team_size.min === 1 && competition.team_size.max === 1)" class="text-gray-900 dark:text-white">
                    {{ formatTeamSize(competition.team_size) }}
                  </p>
                </div>
              </div>
            </UCard>

            <UCard>
              <template #header>
                <h2 class="text-xl font-semibold">{{ t('competition.detail.venue') }}</h2>
              </template>
              <div class="space-y-3">
                <div>
                  <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                    {{ t('competition.form.venue.format.label') }}
                  </h3>
                  <p class="text-gray-900 dark:text-white">
                    {{ getFormatLabel(competition.venue.format) }}
                  </p>
                </div>

                <div v-if="competition.venue.location">
                  <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                    {{ t('competition.form.venue.location.label') }}
                  </h3>
                  <p class="text-gray-900 dark:text-white">
                    {{ competition.venue.location }}
                  </p>
                </div>
              </div>
            </UCard>
          </div>

          <!-- Domains -->
          <UCard>
            <template #header>
              <h2 class="text-xl font-semibold">{{ t('competition.form.domains.label') }}</h2>
            </template>
            <div class="flex flex-wrap gap-2">
              <UBadge
                v-for="domain in competition.domains"
                :key="domain"
                variant="soft"
                :label="getDomainLabel(domain)"
              />
            </div>
          </UCard>

          <!-- Milestones -->
          <UCard v-if="competition.milestones.length > 0">
            <template #header>
              <h2 class="text-xl font-semibold">{{ t('competition.form.milestones') }}</h2>
            </template>
            <div class="space-y-3">
              <div
                v-for="(milestone, index) in competition.milestones"
                :key="index"
                class="flex items-center gap-4 p-3 rounded-lg bg-gray-50 dark:bg-gray-800"
              >
                <UIcon name="i-heroicons-flag" class="size-5 text-primary-500" />
                <div class="flex-1">
                  <p class="font-medium text-gray-900 dark:text-white">{{ milestone.title }}</p>
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ formatDate(milestone.timestamp) }} {{ formatTime(milestone.timestamp) }}
                  </p>
                </div>
              </div>
            </div>
          </UCard>
        </div>

        <!-- Edit Mode -->
        <div v-else-if="isEditMode" class="max-w-4xl mx-auto">
          <p class="text-gray-600 dark:text-gray-400 mb-6">
            {{ t('competition.edit.description') }}
          </p>

          <!-- Form -->
          <UForm
            :state="formState"
            :schema="competitionFormSchema"
            @submit="handleSubmit"
            @error="handleError"
            class="space-y-6"
          >
            <!-- Cards Grid - Two columns on large screens -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <!-- Basic Information -->
              <UCard class="lg:col-span-2">
                <template #header>
                  <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
                    {{ t('competition.create.sections.basic') }}
                  </h2>
                </template>

                <div class="space-y-6">
                  <!-- Title -->
                  <UFormField
                    name="title"
                    :label="t('competition.form.title.label')"
                    required
                    size="xl"
                  >
                    <UInput
                      v-model="formState.title"
                      :placeholder="t('competition.form.title.placeholder')"
                      size="xl"
                      class="w-full text-lg"
                    />
                  </UFormField>

                  <!-- Description -->
                  <UFormField
                    name="description"
                    :label="t('competition.form.description.label')"
                    required
                    size="xl"
                  >
                    <UTextarea
                      v-model="formState.description"
                      :placeholder="t('competition.form.description.placeholder')"
                      :rows="6"
                      size="xl"
                      class="w-full text-lg"
                    />
                  </UFormField>

                  <!-- Domains -->
                  <UFormField
                    name="domains"
                    :label="t('competition.form.domains.label')"
                    required
                    size="xl"
                  >
                    <UCheckboxGroup
                      v-model="formState.domains"
                      :items="domainOptions"
                      orientation="horizontal"
                      size="xl"
                    />
                  </UFormField>

                  <!-- Participant Type -->
                  <UFormField
                    name="participant_type"
                    :label="t('competition.form.participantType.label')"
                    required
                    size="xl"
                  >
                    <URadioGroup
                      v-model="formState.participant_type"
                      :items="participantTypeOptions"
                      size="xl"
                    />
                  </UFormField>

                  <!-- Is Team Competition -->
                  <UFormField
                    :label="t('competition.form.isTeam.label')"
                    size="xl"
                  >
                    <UCheckbox
                      v-model="isTeamCompetition"
                      :label="t('competition.form.isTeam.checkboxLabel')"
                      size="xl"
                    />
                  </UFormField>

                  <!-- Is Archived -->
                  <UFormField
                    :label="t('competition.form.isArchived.label')"
                    size="xl"
                  >
                    <UCheckbox
                      v-model="formState.is_archived"
                      :label="t('competition.form.isArchived.checkboxLabel')"
                      size="xl"
                    />
                  </UFormField>
                </div>
              </UCard>

              <!-- Schedule -->
              <UCard class="lg:col-span-2">
                <template #header>
                  <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
                    {{ t('competition.create.sections.schedule') }}
                  </h2>
                </template>

                <div class="space-y-6">
                  <!-- Registration Period -->
                  <div>
                    <UFormField
                      name="schedule.registration_start"
                      :label="t('competition.form.schedule.registrationPeriod.label')"
                      required
                      size="xl"
                      class="mb-3"
                      :error-pattern="/schedule\.(registration_start|registration_end)/"
                    >
                      <UInputDate
                        ref="registrationDateInput"
                        :model-value="(registrationDateRange as any)"
                        @update:model-value="(val: any) => registrationDateRange = val"
                        range
                        size="xl"
                      >
                        <template #trailing>
                          <UPopover :reference="registrationDateInput?.inputsRef[0]?.$el">
                            <UButton
                              color="neutral"
                              variant="link"
                              size="sm"
                              icon="i-heroicons-calendar"
                              :aria-label="t('competition.form.schedule.selectDateRange')"
                              class="px-0"
                            />

                            <template #content>
                              <UCalendar
                                :model-value="(registrationDateRange as any)"
                                @update:model-value="(val: any) => registrationDateRange = val"
                                class="p-2"
                                :number-of-months="2"
                                range
                              />
                            </template>
                          </UPopover>
                        </template>
                      </UInputDate>
                    </UFormField>

                    <div class="space-y-3 mt-3">
                      <UFormField
                        :label="t('competition.form.schedule.startTime.label')"
                        size="lg"
                      >
                        <UInputTime
                          :model-value="(registrationStartTime as any)"
                          @update:model-value="(val: any) => registrationStartTime = val"
                          size="xl"
                          :hour-cycle="24"
                          leading-icon="i-heroicons-clock"
                        />
                      </UFormField>

                      <UFormField
                        :label="t('competition.form.schedule.endTime.label')"
                        size="lg"
                      >
                        <UInputTime
                          :model-value="(registrationEndTime as any)"
                          @update:model-value="(val: any) => registrationEndTime = val"
                          size="xl"
                          :hour-cycle="24"
                          leading-icon="i-heroicons-clock"
                        />
                      </UFormField>
                    </div>
                  </div>

                  <!-- Team Formation Period (only for team competitions) -->
                  <div v-if="isTeamCompetition">
                    <UFormField
                      name="schedule.team_formation_start"
                      :label="t('competition.form.schedule.teamFormationPeriod.label')"
                      :required="isTeamCompetition"
                      size="xl"
                      class="mb-3"
                      :error-pattern="/schedule\.team_formation_(start|end)/"
                    >
                      <UInputDate
                        ref="teamFormationDateInput"
                        :model-value="(teamFormationDateRange as any)"
                        @update:model-value="(val: any) => teamFormationDateRange = val"
                        range
                        size="xl"
                      >
                        <template #trailing>
                          <UPopover :reference="teamFormationDateInput?.inputsRef[0]?.$el">
                            <UButton
                              color="neutral"
                              variant="link"
                              size="sm"
                              icon="i-heroicons-calendar"
                              :aria-label="t('competition.form.schedule.selectDateRange')"
                              class="px-0"
                            />

                            <template #content>
                              <UCalendar
                                :model-value="(teamFormationDateRange as any)"
                                @update:model-value="(val: any) => teamFormationDateRange = val"
                                class="p-2"
                                :number-of-months="2"
                                range
                              />
                            </template>
                          </UPopover>
                        </template>
                      </UInputDate>
                    </UFormField>

                    <div class="space-y-3 mt-3">
                      <UFormField
                        :label="t('competition.form.schedule.startTime.label')"
                        size="lg"
                      >
                        <UInputTime
                          :model-value="(teamFormationStartTime as any)"
                          @update:model-value="(val: any) => teamFormationStartTime = val"
                          size="xl"
                          :hour-cycle="24"
                          leading-icon="i-heroicons-clock"
                        />
                      </UFormField>

                      <UFormField
                        :label="t('competition.form.schedule.endTime.label')"
                        size="lg"
                      >
                        <UInputTime
                          :model-value="(teamFormationEndTime as any)"
                          @update:model-value="(val: any) => teamFormationEndTime = val"
                          size="xl"
                          :hour-cycle="24"
                          leading-icon="i-heroicons-clock"
                        />
                      </UFormField>
                    </div>
                  </div>
                </div>
              </UCard>

              <!-- Participants -->
              <UCard>
                <template #header>
                  <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
                    {{ t('competition.create.sections.participants') }}
                  </h2>
                </template>

                <div class="space-y-6">
                  <!-- Participant Limits -->
                  <UFormField
                    name="participant_limits"
                    :label="t('competition.form.participantLimits.label')"
                    required
                    size="xl"
                  >
                    <div class="space-y-3">
                      <div class="flex justify-between text-base font-medium text-gray-700 dark:text-gray-300">
                        <span>{{ t('competition.form.participantLimits.min.label') }}: {{ formState.participant_limits.min }}</span>
                        <span>{{ t('competition.form.participantLimits.max.label') }}: {{ formState.participant_limits.max }}</span>
                      </div>
                      <USlider
                        :model-value="[formState.participant_limits.min, formState.participant_limits.max]"
                        :min="1"
                        :max="1000"
                        :step="1"
                        size="xl"
                        @update:model-value="(val) => {
                          if (val && val[0] !== undefined && val[1] !== undefined) {
                            formState.participant_limits.min = val[0];
                            formState.participant_limits.max = val[1];
                          }
                        }"
                      />
                    </div>
                  </UFormField>

                  <!-- Team Size (only for team competitions) -->
                  <UFormField
                    v-if="isTeamCompetition"
                    name="team_size"
                    :label="t('competition.form.teamSize.label')"
                    :required="isTeamCompetition"
                    size="xl"
                  >
                    <div class="space-y-3">
                      <div class="flex justify-between text-base font-medium text-gray-700 dark:text-gray-300">
                        <span>{{ t('competition.form.teamSize.min.label') }}: {{ formState.team_size.min }}</span>
                        <span>{{ t('competition.form.teamSize.max.label') }}: {{ formState.team_size.max }}</span>
                      </div>
                      <USlider
                        :model-value="[formState.team_size.min, formState.team_size.max]"
                        :min="1"
                        :max="20"
                        :step="1"
                        size="xl"
                        @update:model-value="(val) => {
                          if (val && val[0] !== undefined && val[1] !== undefined) {
                            formState.team_size.min = val[0];
                            formState.team_size.max = val[1];
                          }
                        }"
                      />
                    </div>
                  </UFormField>
                </div>
              </UCard>

              <!-- Venue -->
              <UCard>
                <template #header>
                  <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
                    {{ t('competition.create.sections.venue') }}
                  </h2>
                </template>

                <div class="space-y-6">
                  <!-- Format -->
                  <UFormField
                    name="venue.format"
                    :label="t('competition.form.venue.format.label')"
                    required
                    size="xl"
                  >
                    <URadioGroup
                      v-model="formState.venue.format"
                      :items="venueFormatOptions"
                      size="xl"
                    />
                  </UFormField>

                  <!-- Location -->
                  <UFormField
                    v-if="formState.venue.format !== 'online'"
                    name="venue.location"
                    :label="t('competition.form.venue.location.label')"
                    size="xl"
                  >
                    <UInput
                      v-model="formState.venue.location"
                      :placeholder="t('competition.form.venue.location.placeholder')"
                      size="xl"
                      class="w-full text-lg"
                    />
                  </UFormField>
                </div>
              </UCard>

              <!-- Milestones (Optional) -->
              <UCard class="lg:col-span-2">
                <template #header>
                  <div class="flex items-center justify-between">
                    <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
                      {{ t('competition.create.sections.milestones') }}
                    </h2>
                    <UButton
                      icon="i-heroicons-plus"
                      variant="soft"
                      size="sm"
                      :label="t('competition.form.milestone.addButton')"
                      @click="addMilestone"
                    />
                  </div>
                </template>

                <div v-if="milestones.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400 text-lg">
                  {{ t('competition.form.milestone.empty') }}
                </div>

                <div v-else class="space-y-4">
                  <div
                    v-for="(milestone, index) in milestones"
                    :key="index"
                    class="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
                  >
                    <div class="space-y-4">
                      <!-- Title -->
                      <UFormField
                        :label="t('competition.form.milestone.title.label')"
                        required
                        size="lg"
                      >
                        <UInput
                          v-model="milestone.title"
                          :placeholder="t('competition.form.milestone.title.placeholder')"
                          size="xl"
                          class="w-full text-lg"
                        />
                      </UFormField>

                      <!-- Date and Time -->
                      <UFormField
                        :label="t('competition.form.milestone.datetime.label')"
                        required
                        size="lg"
                      >
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                          <UInputDate
                            :model-value="(milestone.date as any)"
                            @update:model-value="(val: any) => milestone.date = val"
                            size="xl"
                          />
                          <UInputTime
                            :model-value="(milestone.time as any)"
                            @update:model-value="(val: any) => milestone.time = val"
                            size="xl"
                            :hour-cycle="24"
                            leading-icon="i-heroicons-clock"
                          />
                        </div>
                      </UFormField>

                      <!-- Remove Button -->
                      <div class="flex justify-end">
                        <UButton
                          icon="i-heroicons-trash"
                          color="error"
                          variant="soft"
                          size="lg"
                          :label="t('common.remove')"
                          @click="removeMilestone(index)"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </UCard>
            </div>

            <!-- Submit Button -->
            <div class="flex justify-end gap-4 pt-4">
              <UButton
                variant="outline"
                color="neutral"
                size="xl"
                :label="t('common.cancel')"
                @click="toggleEditMode"
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
      </div>
    </UPageBody>
  </UPage>
</template>
