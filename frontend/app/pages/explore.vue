<script setup lang="ts">
import type { ExploreCompetitionsFilters, ExploreSortBy, Domain, ExploreCompetitionModel, FieldModel, CompetitionModel } from "~/types/api";
import { useExploreCompetitions } from "~/composables/useExploreCompetitions";
import { useInfiniteScroll } from "@vueuse/core";
import { useMyApplicationsStore } from "~/stores/myApplications";
import { useNotificationsStore } from "~/stores/notifications";
import { extractMilestoneDescription } from "~/utils/milestone";

const { t } = useI18n();
const { getErrorMessage } = useErrorHandler();
const router = useRouter();
const appStore = useMyApplicationsStore();
const notifications = useNotificationsStore();

const {
  competitions,
  total,
  loading,
  error,
  hasMore,
  loadMore,
  reset,
  applyFilters,
} = useExploreCompetitions();

// Local filter state
const search = ref("");
const sortBy = ref<ExploreSortBy>("most_popular");
const minTeamSize = ref<number | null>(null);
const maxTeamSize = ref<number | null>(null);
const autoAccept = ref<boolean | null>(null);
const selectedDomains = ref<Domain[]>([]);

const domainOptions = computed(() => [
  { value: "frontend", label: t("competition.form.domains.options.frontend") },
  { value: "backend", label: t("competition.form.domains.options.backend") },
  { value: "mobile", label: t("competition.form.domains.options.mobile") },
  { value: "ai", label: t("competition.form.domains.options.ai") },
  { value: "devops", label: t("competition.form.domains.options.devops") },
]);

const sortOptions = computed(() => [
  { value: "most_popular", label: t("explore.sort.mostPopular") },
  { value: "newest", label: t("explore.sort.newest") },
]);

const buildFilters = (): ExploreCompetitionsFilters => ({
  sort_by: sortBy.value,
  search: search.value.trim() || undefined,
  min_team_size: minTeamSize.value ?? undefined,
  max_team_size: maxTeamSize.value ?? undefined,
  auto_accept: autoAccept.value ?? undefined,
  domains: selectedDomains.value.length > 0 ? selectedDomains.value : undefined,
});

const commitFilters = () => applyFilters(buildFilters());

let searchTimer: ReturnType<typeof setTimeout> | null = null;
watch(search, () => {
  if (searchTimer) clearTimeout(searchTimer);
  searchTimer = setTimeout(commitFilters, 300);
});

watch([sortBy, minTeamSize, maxTeamSize, autoAccept, selectedDomains], commitFilters, { deep: true });

onMounted(() => {
  reset();
  useInfiniteScroll(
    window,
    () => loadMore(),
    {
      distance: 400,
      canLoadMore: () => hasMore.value && !loading.value,
    },
  );
});

// ── Apply modal ──────────────────────────────────────────────────────────────

const isModalOpen = ref(false);
const modalLoading = ref(false);
const modalError = ref<string | null>(null);
const modalCompetition = ref<CompetitionModel | null>(null);
const applicationForm = ref<{ fields: FieldModel[] } | null>(null);

const applyDomains = ref<Domain[]>([]);
const formAnswers = ref<Record<string, any>>({});

const applyDomainOptions = computed(() =>
  (modalCompetition.value?.domains ?? []).map((d: Domain) => ({ value: d, label: d }))
);

const openRegisterModal = async (competitionId: string) => {
  modalCompetition.value = null;
  applicationForm.value = null;
  applyDomains.value = [];
  formAnswers.value = {};
  modalError.value = null;
  modalLoading.value = true;
  isModalOpen.value = true;

  const api = useApi();
  const [{ data: comp, error: compErr }, { data: form }] = await Promise.all([
    api.getExploreCompetition(competitionId),
    api.getMyApplicationForm(competitionId),
  ]);

  modalLoading.value = false;

  if (compErr) {
    modalError.value = compErr.code;
    return;
  }
  modalCompetition.value = comp;
  if (form) {
    applicationForm.value = { fields: form.fields };
  }
};

const handleApply = async () => {
  if (!modalCompetition.value || applyDomains.value.length === 0) return;

  const form_data = applicationForm.value ? { ...formAnswers.value } : null;

  const result = await appStore.submit(modalCompetition.value.id, {
    domains: applyDomains.value,
    form_data,
  });

  if (result.success) {
    isModalOpen.value = false;
    notifications.add({
      title: t("toast.applicationSubmitted.title"),
      description: t("toast.applicationSubmitted.description"),
      icon: "i-heroicons-check-circle",
      color: "success",
    });
    router.push("/me/applications");
  } else if (appStore.error) {
    notifications.add({
      title: t("apiErrors." + appStore.error.code),
      icon: "i-heroicons-exclamation-circle",
      color: "error",
    });
  }
};

const handleRegister = (competition: ExploreCompetitionModel) => {
  openRegisterModal(competition.id);
};

const handleViewDetails = (competition: ExploreCompetitionModel) => {
  openRegisterModal(competition.id);
};

useHead({ title: t("explore.title") });

const activeFilterCount = computed(() => {
  let n = 0;
  if (search.value.trim().length > 0) n += 1;
  if (minTeamSize.value !== null) n += 1;
  if (maxTeamSize.value !== null) n += 1;
  if (autoAccept.value !== null) n += 1;
  if (selectedDomains.value.length > 0) n += 1;
  if (sortBy.value !== "most_popular") n += 1;
  return n;
});
</script>

<template>
  <UPage>
    <UPageBody>
      <UContainer class="!max-w-7xl py-6">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">
          {{ t("explore.title") }}
        </h1>

        <!-- Filters -->
        <UCollapsible class="mb-6 group">
          <UButton
            type="button"
            variant="soft"
            color="neutral"
            size="md"
            leading-icon="i-heroicons-adjustments-horizontal"
            trailing-icon="i-heroicons-chevron-down"
            class="w-full justify-between"
            :ui="{ trailingIcon: 'transition-transform duration-200 group-data-[state=open]:rotate-180' }"
          >
            <span class="flex items-center gap-2">
              {{ t('explore.filters.title') }}
              <UBadge v-if="activeFilterCount > 0" variant="solid" color="primary" size="xs" :label="String(activeFilterCount)" />
            </span>
          </UButton>
          <template #content>
            <UCard class="mt-2">
              <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                <UFormField :label="t('explore.filters.search')">
                  <UInput v-model="search" icon="i-heroicons-magnifying-glass" :placeholder="t('explore.filters.searchPlaceholder')" class="w-full" />
                </UFormField>

                <UFormField :label="t('explore.filters.sort')">
                  <URadioGroup v-model="sortBy" :items="sortOptions" />
                </UFormField>

                <UFormField :label="t('explore.filters.autoAccept')">
                  <USelect
                    class="w-full"
                    :model-value="autoAccept === null ? 'any' : (autoAccept ? 'yes' : 'no')"
                    @update:model-value="(v) => autoAccept = v === 'any' ? null : v === 'yes'"
                    :items="[
                      { value: 'any', label: t('explore.filters.autoAcceptAny') },
                      { value: 'yes', label: t('explore.filters.autoAcceptYes') },
                      { value: 'no', label: t('explore.filters.autoAcceptNo') },
                    ]"
                  />
                </UFormField>

                <UFormField :label="t('explore.filters.teamSize')">
                  <div class="flex gap-2">
                    <UInput
                      :model-value="minTeamSize ?? ''"
                      @update:model-value="(v) => minTeamSize = v === '' ? null : Number(v)"
                      type="number"
                      :min="1"
                      :placeholder="t('explore.filters.teamSizeMin')"
                    />
                    <UInput
                      :model-value="maxTeamSize ?? ''"
                      @update:model-value="(v) => maxTeamSize = v === '' ? null : Number(v)"
                      type="number"
                      :min="1"
                      :placeholder="t('explore.filters.teamSizeMax')"
                    />
                  </div>
                </UFormField>

                <UFormField :label="t('explore.filters.domains')" class="sm:col-span-2 lg:col-span-2">
                  <div class="flex flex-wrap gap-x-4 gap-y-2">
                    <UCheckbox
                      v-for="opt in domainOptions"
                      :key="opt.value"
                      :model-value="selectedDomains.includes(opt.value as Domain)"
                      @update:model-value="(checked) => {
                        const d = opt.value as Domain;
                        if (checked) {
                          if (!selectedDomains.includes(d)) selectedDomains = [...selectedDomains, d];
                        } else {
                          selectedDomains = selectedDomains.filter((x) => x !== d);
                        }
                      }"
                      :label="opt.label"
                    />
                  </div>
                </UFormField>
              </div>
            </UCard>
          </template>
        </UCollapsible>

        <!-- Results -->
        <section>
          <div class="flex items-center justify-between mb-4">
            <span class="text-sm text-gray-500">
              {{ t("explore.resultsCount", { count: total }) }}
            </span>
          </div>

          <div v-if="error" class="text-center py-16">
            <UIcon name="i-heroicons-exclamation-triangle" class="size-12 text-red-400 mb-4" />
            <p class="text-red-600 dark:text-red-400 text-lg mb-4">
              {{ getErrorMessage(error) }}
            </p>
            <UButton variant="soft" icon="i-heroicons-arrow-path" :label="t('common.retry')" @click="reset" />
          </div>

          <div v-else-if="loading && competitions.length === 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            <USkeleton v-for="i in 6" :key="i" class="h-64 w-full rounded-xl" />
          </div>

          <UAlert
            v-else-if="!loading && competitions.length === 0"
            color="info"
            variant="soft"
            :title="t('explore.empty')"
            :description="t('explore.emptyDescription')"
            icon="i-heroicons-inbox"
          />

          <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 sm:gap-6">
            <CompetitionPreviewCard
              v-for="c in competitions"
              :key="c.id"
              :competition="c"
              @register="() => handleRegister(c)"
              @click="() => handleViewDetails(c)"
            />
          </div>

          <div v-if="loading && competitions.length > 0" class="flex justify-center py-6">
            <UProgress indeterminate size="xs" class="w-48" />
          </div>
        </section>
      </UContainer>
    </UPageBody>
  </UPage>

  <!-- Apply modal -->
  <UModal v-model:open="isModalOpen" :title="modalCompetition?.title ?? t('myApplications.applyButton')" :ui="{ body: 'p-0' }">
    <template #body>
      <!-- Loading -->
      <div v-if="modalLoading" class="p-6 space-y-4">
        <USkeleton class="h-6 w-3/4 rounded" />
        <USkeleton class="h-24 w-full rounded-lg" />
        <USkeleton class="h-16 w-full rounded-lg" />
      </div>

      <!-- Error -->
      <div v-else-if="modalError" class="p-6">
        <UAlert
          color="error"
          variant="soft"
          :title="t('apiErrors.' + modalError)"
          icon="i-heroicons-exclamation-circle"
        />
      </div>

      <!-- Content -->
      <template v-else-if="modalCompetition">
        <!-- Competition info -->
        <div class="px-6 pt-2 pb-4 space-y-4 max-h-[60vh] overflow-y-auto">
          <!-- Domains -->
          <div class="flex flex-wrap gap-2">
            <UBadge
              v-for="domain in modalCompetition.domains"
              :key="domain"
              variant="soft"
              :label="domain"
            />
          </div>

          <!-- Description -->
          <p class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-line">{{ modalCompetition.description }}</p>

          <!-- Schedule -->
          <UCard :ui="{ body: 'py-3 px-4' }">
            <div class="space-y-1 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-500">{{ t('competition.form.schedule.registrationStart.label') }}</span>
                <span>{{ new Date(modalCompetition.schedule.registration_start).toLocaleDateString() }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500">{{ t('competition.form.schedule.registrationEnd.label') }}</span>
                <span>{{ new Date(modalCompetition.schedule.registration_end).toLocaleDateString() }}</span>
              </div>
            </div>
          </UCard>

          <!-- Milestones -->
          <div v-if="modalCompetition.milestones.length > 0" class="space-y-1">
            <p class="text-xs font-medium text-gray-500 uppercase tracking-wide">{{ t('competitionsPreview.detail.milestones') }}</p>
            <ul class="space-y-1">
              <li
                v-for="m in modalCompetition.milestones"
                :key="m.title"
                class="text-sm flex items-start gap-2"
              >
                <UIcon name="i-heroicons-flag" class="size-4 mt-0.5 text-primary-500 shrink-0" />
                <span>
                  <span class="font-medium">{{ m.title }}</span>
                  <span v-if="extractMilestoneDescription(m.description)" class="text-gray-500"> — {{ extractMilestoneDescription(m.description) }}</span>
                </span>
              </li>
            </ul>
          </div>

          <UDivider />

          <!-- Domain selection -->
          <UFormField :label="t('myApplications.selectDomains')" required>
            <div class="flex flex-wrap gap-2">
              <UCheckbox
                v-for="opt in applyDomainOptions"
                :key="opt.value"
                :label="opt.label"
                :model-value="applyDomains.includes(opt.value)"
                @update:model-value="(checked) => {
                  if (checked) applyDomains.push(opt.value);
                  else applyDomains = applyDomains.filter(d => d !== opt.value);
                }"
              />
            </div>
            <p v-if="applyDomains.length === 0" class="text-xs text-red-500 mt-1">
              {{ t('myApplications.domainsRequired') }}
            </p>
          </UFormField>

          <!-- Dynamic form fields -->
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
      </template>
    </template>

    <template #footer>
      <div class="flex justify-end gap-3">
        <UButton
          color="neutral"
          variant="ghost"
          :label="t('common.cancel')"
          @click="isModalOpen = false"
        />
        <UButton
          v-if="modalCompetition && !modalError"
          color="primary"
          icon="i-heroicons-paper-airplane"
          :label="appStore.submitting ? t('myApplications.applying') : t('myApplications.applyButton')"
          :loading="appStore.submitting"
          :disabled="appStore.submitting || applyDomains.length === 0 || modalLoading"
          @click="handleApply"
        />
      </div>
    </template>
  </UModal>
</template>
