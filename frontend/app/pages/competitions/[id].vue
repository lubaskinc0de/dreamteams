<script setup lang="ts">
import { useMyApplicationsStore } from '~/stores/myApplications';
import { useNotificationsStore } from '~/stores/notifications';
import type { Domain, FieldModel } from '~/types/api';

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const appStore = useMyApplicationsStore();
const notifications = useNotificationsStore();
const { hasProfile } = useAuth();
const userStore = useUserStore();

const competitionId = computed(() => route.params.id as string);

useSeoMeta({ title: t('competitionsPreview.title') });

// Competition data
const competition = ref<any | null>(null);
const competitionLoading = ref(true);
const competitionError = ref<string | null>(null);

// Application form schema
const applicationForm = ref<{ fields: FieldModel[] } | null>(null);

onMounted(async () => {
  const api = useApi();

  // Load competition details
  const { data: comp, error: compErr } = await api.getCompetition(competitionId.value);
  competitionLoading.value = false;

  if (compErr) {
    competitionError.value = compErr.code;
    return;
  }
  competition.value = comp;

  // Try to load the application form (may not exist or may be inaccessible)
  const { data: form, error: formErr } = await api.getApplicationForm(competitionId.value);
  if (form) {
    applicationForm.value = { fields: form.fields };
  }
  // Silently ignore form errors (NOT_FOUND = no form, ACCESS_DENIED = organizer-only)
});

// Apply modal state
const isApplyModalOpen = ref(false);
const selectedDomains = ref<Domain[]>([]);
const formAnswers = ref<Record<string, any>>({});

const domainOptions = computed(() =>
  (competition.value?.domains ?? []).map((d: Domain) => ({ value: d, label: d }))
);

const openApply = () => {
  selectedDomains.value = [];
  formAnswers.value = {};
  isApplyModalOpen.value = true;
};

const handleApply = async () => {
  if (selectedDomains.value.length === 0) return;

  const form_data = applicationForm.value ? { ...formAnswers.value } : null;

  const result = await appStore.submit(competitionId.value, {
    domains: selectedDomains.value,
    form_data,
  });

  if (result.success) {
    isApplyModalOpen.value = false;
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

const isParticipant = computed(() => userStore.isParticipant);
</script>

<template>
  <UPage>
    <UPageBody>
      <UContainer class="!max-w-4xl">
        <!-- Back button -->
        <div class="mb-6">
          <UButton
            icon="i-heroicons-arrow-left"
            color="neutral"
            variant="ghost"
            :label="t('common.back')"
            @click="router.push('/competitions')"
          />
        </div>

        <!-- Loading -->
        <div v-if="competitionLoading" class="space-y-4">
          <USkeleton class="h-10 w-3/4 rounded" />
          <USkeleton class="h-32 w-full rounded-lg" />
          <USkeleton class="h-48 w-full rounded-lg" />
        </div>

        <!-- Error -->
        <UAlert
          v-else-if="competitionError"
          color="error"
          variant="soft"
          :title="t('apiErrors.' + competitionError)"
          icon="i-heroicons-exclamation-circle"
        />

        <template v-else-if="competition">
          <!-- Title & domains -->
          <div class="mb-6">
            <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-3">{{ competition.title }}</h1>
            <div class="flex flex-wrap gap-2 mb-4">
              <UBadge
                v-for="domain in competition.domains"
                :key="domain"
                variant="soft"
                :label="domain"
              />
            </div>

            <!-- Apply button (only for participants) -->
            <UButton
              v-if="isParticipant"
              color="primary"
              icon="i-heroicons-paper-airplane"
              :label="t('myApplications.applyButton')"
              @click="openApply"
            />
            <UAlert
              v-else-if="hasProfile && !isParticipant"
              color="info"
              variant="soft"
              :title="t('myApplications.applyButton')"
              description="Только участники могут подавать заявки"
              icon="i-heroicons-information-circle"
              class="mt-2"
            />
          </div>

          <!-- Description -->
          <UCard class="mb-4">
            <p class="text-gray-700 dark:text-gray-300 whitespace-pre-line">{{ competition.description }}</p>
          </UCard>

          <!-- Schedule -->
          <UCard class="mb-4">
            <template #header>
              <h2 class="font-semibold text-gray-900 dark:text-white">Расписание</h2>
            </template>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-500">Начало регистрации</span>
                <span>{{ new Date(competition.schedule.registration_start).toLocaleDateString() }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500">Конец регистрации</span>
                <span>{{ new Date(competition.schedule.registration_end).toLocaleDateString() }}</span>
              </div>
            </div>
          </UCard>

          <!-- Venue -->
          <UCard>
            <template #header>
              <h2 class="font-semibold text-gray-900 dark:text-white">Формат</h2>
            </template>
            <div class="space-y-1 text-sm">
              <p>{{ competition.venue.format }}</p>
              <p v-if="competition.venue.location" class="text-gray-500">{{ competition.venue.location }}</p>
            </div>
          </UCard>
        </template>
      </UContainer>
    </UPageBody>

    <!-- Apply modal -->
    <UModal v-model:open="isApplyModalOpen" :title="t('myApplications.applyButton')">
      <template #body>
        <div class="space-y-4 p-4">
          <!-- Domain selection -->
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

          <!-- Dynamic form fields -->
          <template v-if="applicationForm">
            <UFormField
              v-for="field in applicationForm.fields"
              :key="field.name"
              :label="field.label"
              :required="field.required"
            >
              <!-- String field -->
              <UInput
                v-if="field.type === 'string'"
                v-model="formAnswers[field.name]"
                :placeholder="field.label"
                class="w-full"
              />

              <!-- Int field -->
              <UInput
                v-else-if="field.type === 'int'"
                v-model.number="formAnswers[field.name]"
                type="number"
                :placeholder="field.label"
                class="w-full"
              />

              <!-- Select field -->
              <USelect
                v-else-if="field.type === 'select'"
                v-model="formAnswers[field.name]"
                :items="(field.choices ?? []).map(c => ({ value: c.value, label: c.label }))"
                value-key="value"
                label-key="label"
                class="w-full"
              />

              <!-- Multiselect field -->
              <div v-else-if="field.type === 'multiselect'" class="flex flex-wrap gap-2">
                <UCheckbox
                  v-for="choice in (field.choices ?? [])"
                  :key="choice.value"
                  :label="choice.label"
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
      </template>

      <template #footer>
        <div class="flex justify-end gap-3">
          <UButton
            color="neutral"
            variant="ghost"
            :label="t('common.cancel')"
            @click="isApplyModalOpen = false"
          />
          <UButton
            color="primary"
            :label="appStore.submitting ? t('myApplications.applying') : t('myApplications.applyButton')"
            :loading="appStore.submitting"
            :disabled="appStore.submitting || selectedDomains.length === 0"
            @click="handleApply"
          />
        </div>
      </template>
    </UModal>
  </UPage>
</template>
