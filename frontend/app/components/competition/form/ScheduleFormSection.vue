<script setup lang="ts">
/**
 * Секция формы с расписанием соревнования
 */

interface Props {
  registrationDateRange: any;
  registrationStartTime: any;
  registrationEndTime: any;
  teamFormationDateRange: any;
  teamFormationStartTime: any;
  teamFormationEndTime: any;
  isTeamCompetition: boolean;
  // Locked date props (for edit mode - past dates cannot be changed)
  lockedRegistrationStart?: boolean;
  lockedRegistrationEnd?: boolean;
  lockedTeamFormationStart?: boolean;
  lockedTeamFormationEnd?: boolean;
  // Min value props for date restrictions
  registrationMinValue?: any;
  registrationEndMinValue?: any;
  teamFormationMinValue?: any;
  teamFormationEndMinValue?: any;
}

const props = withDefaults(defineProps<Props>(), {
  lockedRegistrationStart: false,
  lockedRegistrationEnd: false,
  lockedTeamFormationStart: false,
  lockedTeamFormationEnd: false,
});
const emit = defineEmits(['update:registrationDateRange', 'update:registrationStartTime', 'update:registrationEndTime', 'update:teamFormationDateRange', 'update:teamFormationStartTime', 'update:teamFormationEndTime']);

const { t } = useI18n();

// Template refs for calendar popovers
const registrationDateInput = useTemplateRef('registrationDateInput');
const teamFormationDateInput = useTemplateRef('teamFormationDateInput');

// Computed: is entire registration period locked?
const isRegistrationLocked = computed(() => props.lockedRegistrationStart && props.lockedRegistrationEnd);

// Computed: is entire team formation period locked?
const isTeamFormationLocked = computed(() => props.lockedTeamFormationStart && props.lockedTeamFormationEnd);
</script>

<template>
  <UCard class="lg:col-span-2">
    <template #header>
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
        {{ t('competition.create.sections.schedule') }}
      </h2>
    </template>

    <div class="space-y-6">
      <!-- Registration Period -->
      <div>
        <!-- Locked notice — specific to which parts of the period are in the past -->
        <div v-if="lockedRegistrationStart || lockedRegistrationEnd" class="mb-3 p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
          <p class="text-sm text-amber-700 dark:text-amber-300 flex items-center gap-2">
            <UIcon name="i-heroicons-lock-closed" class="w-4 h-4" />
            <span v-if="isRegistrationLocked">{{ t('competition.form.schedule.lockedNotice.both') }}</span>
            <span v-else-if="lockedRegistrationStart">{{ t('competition.form.schedule.lockedNotice.startOnly') }}</span>
            <span v-else>{{ t('competition.form.schedule.lockedNotice.endOnly') }}</span>
          </p>
        </div>

        <UFormField
          name="schedule.registration_start"
          required
          size="xl"
          class="mb-3"
          :error-pattern="/schedule\.(registration_start|registration_end)/"
        >
          <template #label>
            {{ t('competition.form.schedule.registrationPeriod.label') }}
            <HelpTooltip :text="t('competition.form.schedule.registrationPeriod.tooltip')" />
          </template>
          <UInputDate
            ref="registrationDateInput"
            :model-value="(registrationDateRange as any)"
            @update:model-value="(val: any) => emit('update:registrationDateRange', val)"
            range
            size="xl"
            :disabled="isRegistrationLocked"
            :min-value="registrationMinValue"
          >
            <template #trailing>
              <UPopover v-if="!isRegistrationLocked" :reference="registrationDateInput?.inputsRef[0]?.$el">
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
                    @update:model-value="(val: any) => emit('update:registrationDateRange', val)"
                    class="p-2"
                    :number-of-months="2"
                    range
                    :min-value="registrationMinValue"
                  />
                </template>
              </UPopover>
              <UIcon v-else name="i-heroicons-lock-closed" class="w-4 h-4 text-gray-400" />
            </template>
          </UInputDate>
        </UFormField>

        <UCollapsible class="mt-3 group">
          <UButton
            type="button"
            variant="ghost"
            color="neutral"
            size="sm"
            trailing-icon="i-heroicons-chevron-down"
            class="w-full justify-between text-sm font-medium text-gray-600 dark:text-gray-300"
            :label="t('competition.form.schedule.timeToggle.label')"
            :ui="{ trailingIcon: 'transition-transform duration-200 group-data-[state=open]:rotate-180' }"
          />
          <template #content>
            <div class="space-y-3 mt-3">
              <UFormField
                :label="t('competition.form.schedule.startTime.label')"
                size="lg"
              >
                <UInputTime
                  :model-value="(registrationStartTime as any)"
                  @update:model-value="(val: any) => emit('update:registrationStartTime', val)"
                  size="xl"
                  :hour-cycle="24"
                  leading-icon="i-heroicons-clock"
                  :disabled="lockedRegistrationStart"
                />
              </UFormField>

              <UFormField
                :label="t('competition.form.schedule.endTime.label')"
                size="lg"
              >
                <UInputTime
                  :model-value="(registrationEndTime as any)"
                  @update:model-value="(val: any) => emit('update:registrationEndTime', val)"
                  size="xl"
                  :hour-cycle="24"
                  leading-icon="i-heroicons-clock"
                  :disabled="lockedRegistrationEnd"
                />
              </UFormField>
            </div>
          </template>
        </UCollapsible>
      </div>

      <!-- Team Formation Period (only for team competitions) -->
      <div v-if="isTeamCompetition">
        <!-- Locked notice — specific to which parts of the period are in the past -->
        <div v-if="lockedTeamFormationStart || lockedTeamFormationEnd" class="mb-3 p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
          <p class="text-sm text-amber-700 dark:text-amber-300 flex items-center gap-2">
            <UIcon name="i-heroicons-lock-closed" class="w-4 h-4" />
            <span v-if="isTeamFormationLocked">{{ t('competition.form.schedule.lockedNotice.bothTeam') }}</span>
            <span v-else-if="lockedTeamFormationStart">{{ t('competition.form.schedule.lockedNotice.startOnlyTeam') }}</span>
            <span v-else>{{ t('competition.form.schedule.lockedNotice.endOnlyTeam') }}</span>
          </p>
        </div>

        <UFormField
          name="schedule.team_formation_start"
          :required="isTeamCompetition"
          size="xl"
          class="mb-3"
          :error-pattern="/schedule\.team_formation_(start|end)/"
        >
          <template #label>
            {{ t('competition.form.schedule.teamFormationPeriod.label') }}
            <HelpTooltip :text="t('competition.form.schedule.teamFormationPeriod.tooltip')" />
          </template>
          <UInputDate
            ref="teamFormationDateInput"
            :model-value="(teamFormationDateRange as any)"
            @update:model-value="(val: any) => emit('update:teamFormationDateRange', val)"
            range
            size="xl"
            :disabled="isTeamFormationLocked"
            :min-value="teamFormationMinValue"
          >
            <template #trailing>
              <UPopover v-if="!isTeamFormationLocked" :reference="teamFormationDateInput?.inputsRef[0]?.$el">
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
                    @update:model-value="(val: any) => emit('update:teamFormationDateRange', val)"
                    class="p-2"
                    :number-of-months="2"
                    range
                    :min-value="teamFormationMinValue"
                  />
                </template>
              </UPopover>
              <UIcon v-else name="i-heroicons-lock-closed" class="w-4 h-4 text-gray-400" />
            </template>
          </UInputDate>
        </UFormField>

        <UCollapsible class="mt-3 group">
          <UButton
            type="button"
            variant="ghost"
            color="neutral"
            size="sm"
            trailing-icon="i-heroicons-chevron-down"
            class="w-full justify-between text-sm font-medium text-gray-600 dark:text-gray-300"
            :label="t('competition.form.schedule.timeToggle.label')"
            :ui="{ trailingIcon: 'transition-transform duration-200 group-data-[state=open]:rotate-180' }"
          />
          <template #content>
            <div class="space-y-3 mt-3">
              <UFormField
                :label="t('competition.form.schedule.startTime.label')"
                size="lg"
              >
                <UInputTime
                  :model-value="(teamFormationStartTime as any)"
                  @update:model-value="(val: any) => emit('update:teamFormationStartTime', val)"
                  size="xl"
                  :hour-cycle="24"
                  leading-icon="i-heroicons-clock"
                  :disabled="lockedTeamFormationStart"
                />
              </UFormField>

              <UFormField
                :label="t('competition.form.schedule.endTime.label')"
                size="lg"
              >
                <UInputTime
                  :model-value="(teamFormationEndTime as any)"
                  @update:model-value="(val: any) => emit('update:teamFormationEndTime', val)"
                  size="xl"
                  :hour-cycle="24"
                  leading-icon="i-heroicons-clock"
                  :disabled="lockedTeamFormationEnd"
                />
              </UFormField>
            </div>
          </template>
        </UCollapsible>
      </div>
    </div>
  </UCard>
</template>
