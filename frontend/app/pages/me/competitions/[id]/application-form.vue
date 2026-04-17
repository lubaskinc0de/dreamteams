<script setup lang="ts">
import { useApplicationFormStore } from '~/stores/applicationForm';
import { useNotificationsStore } from '~/stores/notifications';
import type { ApplicationFormInput, FieldForm, FieldChoiceForm, FieldType } from '~/types/api';

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const formStore = useApplicationFormStore();
const notifications = useNotificationsStore();

const competitionId = computed(() => route.params.id as string);

useSeoMeta({ title: t('applicationForm.title') });

onMounted(async () => {
  await formStore.fetchForm(competitionId.value);
});

// Delete
const isDeleteModalOpen = ref(false);

const handleDelete = async () => {
  const ok = await formStore.deleteForm(competitionId.value);
  isDeleteModalOpen.value = false;
  if (ok) {
    notifications.add({
      title: t('toast.applicationFormDeleted.title'),
      description: t('toast.applicationFormDeleted.description'),
      icon: 'i-heroicons-check-circle',
      color: 'success',
    });
  } else if (formStore.error) {
    notifications.add({
      title: t('apiErrors.' + formStore.error.code),
      icon: 'i-heroicons-exclamation-circle',
      color: 'error',
    });
  }
};

// Build form state
interface FieldDraft {
  name: string;
  label: string;
  type: FieldType;
  required: boolean;
  choices: { value: string; label: string }[];
}

const fieldTypes: { value: FieldType; label: string }[] = [
  { value: 'string', label: t('applicationForm.fieldType.string') },
  { value: 'int', label: t('applicationForm.fieldType.int') },
  { value: 'select', label: t('applicationForm.fieldType.select') },
  { value: 'multiselect', label: t('applicationForm.fieldType.multiselect') },
];

const newFields = ref<FieldDraft[]>([
  { name: '', label: '', type: 'string', required: true, choices: [] },
]);

const addField = () => {
  newFields.value.push({ name: '', label: '', type: 'string', required: true, choices: [] });
};

const removeField = (index: number) => {
  newFields.value.splice(index, 1);
};

const addChoice = (field: FieldDraft) => {
  field.choices.push({ value: '', label: '' });
};

const removeChoice = (field: FieldDraft, index: number) => {
  field.choices.splice(index, 1);
};

const needsChoices = (type: FieldType) => type === 'select' || type === 'multiselect';

const onTypeChange = (field: FieldDraft) => {
  if (!needsChoices(field.type)) {
    field.choices = [];
  }
};

const isCreating = ref(false);

const builderTabs = computed(() => [
  { label: t('applicationForm.tabBuild'), slot: 'build' as const },
  { label: t('applicationForm.tabPreview'), slot: 'preview' as const },
]);

const handleCreate = async () => {
  isCreating.value = true;

  const fields: FieldForm[] = newFields.value.map((f) => ({
    name: f.name,
    label: f.label,
    type: f.type,
    required: f.required,
    choices: needsChoices(f.type) ? f.choices : null,
  }));

  const input: ApplicationFormInput = { fields };
  const result = await formStore.createForm(competitionId.value, input);

  isCreating.value = false;

  if (result.success) {
    notifications.add({
      title: t('toast.applicationFormCreated.title'),
      description: t('toast.applicationFormCreated.description'),
      icon: 'i-heroicons-check-circle',
      color: 'success',
    });
    newFields.value = [{ name: '', label: '', type: 'string', required: true, choices: [] }];
  } else if (formStore.error) {
    notifications.add({
      title: t('apiErrors.' + formStore.error.code),
      icon: 'i-heroicons-exclamation-circle',
      color: 'error',
    });
  }
};
</script>

<template>
  <UPage>
    <UPageBody>
      <UContainer class="!max-w-4xl">
        <!-- Header -->
        <div class="flex items-center gap-4 mb-6">
          <UButton
            icon="i-heroicons-arrow-left"
            color="neutral"
            variant="ghost"
            @click="router.push('/me/competitions/application-form')"
          />
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ t('applicationForm.title') }}
          </h1>
        </div>

        <!-- Loading -->
        <div v-if="formStore.loading" class="space-y-4">
          <USkeleton v-for="i in 3" :key="i" class="h-16 w-full rounded-lg" />
        </div>

        <!-- Error -->
        <UAlert
          v-else-if="formStore.error && formStore.error.code !== 'APPLICATION_FORM_NOT_FOUND'"
          color="error"
          variant="soft"
          :title="t('apiErrors.' + formStore.error.code)"
          icon="i-heroicons-exclamation-circle"
          class="mb-4"
        />

        <!-- Existing form -->
        <template v-else-if="formStore.form">
          <UCard class="mb-6">
            <template #header>
              <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ t('applicationForm.createdAt') }}: {{ new Date(formStore.form.created_at).toLocaleDateString() }}
                  </p>
                </div>
                <UButton
                  color="error"
                  variant="soft"
                  icon="i-heroicons-trash"
                  :label="t('applicationForm.deleteButton')"
                  class="w-full sm:w-auto justify-center"
                  @click="isDeleteModalOpen = true"
                />
              </div>
            </template>

            <div class="space-y-4">
              <h2 class="font-semibold text-gray-700 dark:text-gray-300">{{ t('applicationForm.fields') }}</h2>
              <div
                v-for="field in formStore.form.fields"
                :key="field.name"
                class="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
              >
                <div class="flex items-start justify-between gap-4">
                  <div class="flex-1">
                    <div class="flex items-center gap-2 mb-1">
                      <span class="font-medium text-gray-900 dark:text-white">{{ field.label }}</span>
                      <UBadge size="sm" variant="soft" :label="t('applicationForm.fieldType.' + field.type)" />
                      <UBadge v-if="field.required" size="sm" color="error" variant="soft" :label="t('applicationForm.fieldRequired')" />
                    </div>
                    <p class="text-xs text-gray-400 font-mono">{{ field.name }}</p>
                    <div v-if="field.choices && field.choices.length > 0" class="mt-2 flex flex-wrap gap-1">
                      <UBadge
                        v-for="choice in field.choices"
                        :key="choice.value"
                        size="sm"
                        variant="outline"
                        :label="`${choice.label} (${choice.value})`"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </UCard>
        </template>

        <!-- No form — builder -->
        <template v-else>
          <UAlert
            color="info"
            variant="soft"
            :title="t('applicationForm.noForm')"
            :description="t('applicationForm.noFormDescription')"
            icon="i-heroicons-information-circle"
            class="mb-6"
          />

          <UTabs :items="builderTabs">
            <template #build>
              <UCard class="mt-4">
                <template #header>
                  <h2 class="font-semibold text-gray-900 dark:text-white">{{ t('applicationForm.createButton') }}</h2>
                </template>

                <div class="space-y-6">
                  <div
                    v-for="(field, index) in newFields"
                    :key="index"
                    class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 space-y-4"
                  >
                    <div class="flex items-center justify-between">
                      <span class="text-sm font-medium text-gray-600 dark:text-gray-400">
                        {{ t('applicationForm.addField') }} {{ index + 1 }}
                      </span>
                      <UButton
                        v-if="newFields.length > 1"
                        icon="i-heroicons-x-mark"
                        color="neutral"
                        variant="ghost"
                        size="sm"
                        @click="removeField(index)"
                      />
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <UFormField :label="t('applicationForm.fieldName.label')">
                        <UInput
                          v-model="field.name"
                          :placeholder="t('applicationForm.fieldName.placeholder')"
                          class="w-full"
                        />
                      </UFormField>

                      <UFormField :label="t('applicationForm.fieldLabel.label')">
                        <UInput
                          v-model="field.label"
                          :placeholder="t('applicationForm.fieldLabel.placeholder')"
                          class="w-full"
                        />
                      </UFormField>

                      <UFormField :label="t('applicationForm.fieldType.label')">
                        <USelect
                          v-model="field.type"
                          :items="fieldTypes"
                          value-key="value"
                          label-key="label"
                          class="w-full"
                          @change="onTypeChange(field)"
                        />
                      </UFormField>

                      <UFormField :label="t('applicationForm.fieldRequired')">
                        <UCheckbox v-model="field.required" :label="t('applicationForm.fieldRequired')" />
                      </UFormField>
                    </div>

                    <!-- Choices for select/multiselect -->
                    <div v-if="needsChoices(field.type)" class="space-y-2">
                      <p class="text-sm font-medium text-gray-600 dark:text-gray-400">{{ t('applicationForm.choices') }}</p>
                      <div
                        v-for="(choice, ci) in field.choices"
                        :key="ci"
                        class="flex items-center gap-2"
                      >
                        <UInput
                          v-model="choice.value"
                          :placeholder="t('applicationForm.choiceValue.placeholder')"
                          class="flex-1"
                        />
                        <UInput
                          v-model="choice.label"
                          :placeholder="t('applicationForm.choiceLabel.placeholder')"
                          class="flex-1"
                        />
                        <UButton
                          icon="i-heroicons-x-mark"
                          color="neutral"
                          variant="ghost"
                          size="sm"
                          @click="removeChoice(field, ci)"
                        />
                      </div>
                      <UButton
                        size="sm"
                        variant="soft"
                        icon="i-heroicons-plus"
                        :label="t('applicationForm.addChoice')"
                        @click="addChoice(field)"
                      />
                    </div>
                  </div>

                  <UButton
                    variant="outline"
                    icon="i-heroicons-plus"
                    :label="t('applicationForm.addField')"
                    @click="addField"
                  />
                </div>

                <template #footer>
                  <div class="flex justify-end gap-3">
                    <UButton
                      color="primary"
                      icon="i-heroicons-check"
                      :label="isCreating ? t('applicationForm.saving') : t('applicationForm.createButton')"
                      :loading="isCreating"
                      :disabled="isCreating"
                      @click="handleCreate"
                    />
                  </div>
                </template>
              </UCard>
            </template>

            <template #preview>
              <UCard class="mt-4">
                <template #header>
                  <h2 class="font-semibold text-gray-900 dark:text-white">{{ t('applicationForm.tabPreview') }}</h2>
                </template>

                <div v-if="newFields.length === 0" class="text-center py-8 text-gray-400">
                  {{ t('applicationForm.previewEmpty') }}
                </div>

                <div v-else class="space-y-4">
                  <div v-for="(field, index) in newFields" :key="index">
                    <UFormField
                      :label="field.label || field.name || `Field ${index + 1}`"
                      :required="field.required"
                    >
                      <UInput
                        v-if="field.type === 'string'"
                        :placeholder="field.label || field.name"
                        disabled
                        class="w-full"
                      />
                      <UInput
                        v-else-if="field.type === 'int'"
                        type="number"
                        :placeholder="field.label || field.name"
                        disabled
                        class="w-full"
                      />
                      <USelect
                        v-else-if="field.type === 'select'"
                        :items="field.choices.map(c => ({ label: c.label || c.value, value: c.value }))"
                        :placeholder="field.label || field.name"
                        disabled
                        class="w-full"
                      />
                      <div v-else-if="field.type === 'multiselect'" class="flex flex-wrap gap-2">
                        <UCheckbox
                          v-for="choice in field.choices"
                          :key="choice.value"
                          :label="choice.label || choice.value"
                          disabled
                        />
                        <span v-if="field.choices.length === 0" class="text-sm text-gray-400 italic">
                          {{ t('applicationForm.choices') }}...
                        </span>
                      </div>
                    </UFormField>
                  </div>
                </div>
              </UCard>
            </template>
          </UTabs>
        </template>
      </UContainer>
    </UPageBody>

    <!-- Delete confirmation -->
    <UiConfirmDeleteModal
      v-model:open="isDeleteModalOpen"
      :title="t('applicationForm.deleteConfirmTitle')"
      :description="t('applicationForm.deleteConfirmDescription')"
      :confirm-label="t('common.delete')"
      :cancel-label="t('common.cancel')"
      :is-deleting="formStore.deleting"
      @confirm="handleDelete"
    />
  </UPage>
</template>
