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
}

defineProps<Props>();
const emit = defineEmits(['update:registrationDateRange', 'update:registrationStartTime', 'update:registrationEndTime', 'update:teamFormationDateRange', 'update:teamFormationStartTime', 'update:teamFormationEndTime']);

const { t } = useI18n();

// Template refs for calendar popovers
const registrationDateInput = useTemplateRef('registrationDateInput');
const teamFormationDateInput = useTemplateRef('teamFormationDateInput');
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
            @update:model-value="(val: any) => emit('update:registrationDateRange', val)"
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
                    @update:model-value="(val: any) => emit('update:registrationDateRange', val)"
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
              @update:model-value="(val: any) => emit('update:registrationStartTime', val)"
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
              @update:model-value="(val: any) => emit('update:registrationEndTime', val)"
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
            @update:model-value="(val: any) => emit('update:teamFormationDateRange', val)"
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
                    @update:model-value="(val: any) => emit('update:teamFormationDateRange', val)"
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
              @update:model-value="(val: any) => emit('update:teamFormationStartTime', val)"
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
              @update:model-value="(val: any) => emit('update:teamFormationEndTime', val)"
              size="xl"
              :hour-cycle="24"
              leading-icon="i-heroicons-clock"
            />
          </UFormField>
        </div>
      </div>
    </div>
  </UCard>
</template>
