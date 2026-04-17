<script setup lang="ts">
import type { FormSubmitEvent } from "#ui/types";
import type { UpdateOrganizerForm } from "~/types/api";
import { createOrganizerSchemas, type OrganizerUpdateSchema } from "~/schemas/organizer";
import { useOrganizerStore } from "~/stores/organizer";

interface Props {
  open: boolean;
  organizerName: string;
  contactEmail: string;
}

const props = defineProps<Props>();
const emit = defineEmits<{ "update:open": [value: boolean] }>();

const { t } = useI18n();
const organizerStore = useOrganizerStore();
const { getErrorMessage } = useErrorHandler();

const { organizerUpdateSchema } = createOrganizerSchemas(t);

const state = reactive({
  organizer_name: props.organizerName,
  contact_email: props.contactEmail,
});

watch(() => props.open, (val) => {
  if (val) {
    state.organizer_name = props.organizerName;
    state.contact_email = props.contactEmail;
    organizerStore.clearError();
  }
});

const onSubmit = async (event: FormSubmitEvent<OrganizerUpdateSchema>) => {
  const form: UpdateOrganizerForm = {
    organizer_name: event.data.organizer_name,
    contact_email: event.data.contact_email,
  };
  await organizerStore.updateOrganizer(form);
  if (organizerStore.updateSuccess) {
    emit("update:open", false);
  }
};

const apiError = computed(() => getErrorMessage(organizerStore.error));
</script>

<template>
  <UModal :open="open" @update:open="$emit('update:open', $event)">
    <template #content>
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold">{{ t("profile.fields.organizerName") }}</h3>
            <UButton icon="i-heroicons-x-mark" color="neutral" variant="ghost" @click="$emit('update:open', false)" />
          </div>
        </template>

        <UAlert
          v-if="apiError"
          color="error"
          variant="soft"
          :title="apiError"
          icon="i-heroicons-exclamation-circle"
          :close-button="{ icon: 'i-heroicons-x-mark-20-solid', color: 'neutral', variant: 'ghost', padded: false }"
          @close="organizerStore.clearError()"
          class="mb-4"
        />

        <UForm
          :schema="organizerUpdateSchema"
          :state="state"
          @submit="onSubmit"
          :validate-on="['input', 'change']"
          class="space-y-4"
        >
          <UFormField :label="t('form.organizerName.label')" name="organizer_name" required>
            <UInput
              v-model="state.organizer_name"
              :placeholder="t('form.organizerName.placeholder')"
              icon="i-heroicons-building-office"
              size="xl"
              :maxlength="70"
              class="w-full"
            />
          </UFormField>

          <UFormField :label="t('form.contactEmail.label')" name="contact_email" required>
            <UInput
              v-model="state.contact_email"
              :placeholder="t('form.contactEmail.placeholder')"
              icon="i-heroicons-envelope"
              type="email"
              size="xl"
              class="w-full"
            />
          </UFormField>

          <div class="flex justify-end gap-3 pt-2">
            <UButton color="neutral" variant="ghost" @click="$emit('update:open', false)">
              {{ t("common.cancel") }}
            </UButton>
            <UButton type="submit" :loading="organizerStore.loading" icon="i-heroicons-check">
              {{ t("common.save") }}
            </UButton>
          </div>
        </UForm>
      </UCard>
    </template>
  </UModal>
</template>
