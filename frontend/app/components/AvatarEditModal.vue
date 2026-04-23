<script setup lang="ts">
const props = defineProps<{
  currentAvatarUrl?: string | null;
}>();

const emit = defineEmits<{
  upload: [file: File];
  delete: [];
}>();

const { t } = useI18n();

const isOpen = defineModel<boolean>('open', { required: true });
const selectedFile = ref<File | null>(null);
const previewUrl = ref<string | null>(null);
const uploadError = ref<string | null>(null);

// Watch for current avatar URL changes
watch(
  () => props.currentAvatarUrl,
  (newUrl) => {
    if (newUrl && !selectedFile.value) {
      previewUrl.value = newUrl;
    }
  },
  { immediate: true },
);

// Watch for v-model changes from UFileUpload
watch(selectedFile, (file) => {
  uploadError.value = null;

  if (!file) {
    return;
  }

  // Validate file type
  const allowedTypes = ["image/jpeg", "image/png", "image/gif", "image/webp"];
  if (!allowedTypes.includes(file.type)) {
    uploadError.value = t("avatar.errors.invalidFormat");
    selectedFile.value = null;
    return;
  }

  // Validate file size (max 5MB)
  const maxSize = 5 * 1024 * 1024;
  if (file.size > maxSize) {
    uploadError.value = t("avatar.errors.tooLarge");
    selectedFile.value = null;
    return;
  }

  // Create preview
  const reader = new FileReader();
  reader.onload = (e) => {
    previewUrl.value = e.target?.result as string;
  };
  reader.readAsDataURL(file);
});

// Handle upload
const handleUpload = () => {
  if (selectedFile.value) {
    emit("upload", selectedFile.value);
    // Don't clear immediately - let parent handle after successful upload
  }
};

// Handle delete
const handleDelete = () => {
  emit("delete");
  selectedFile.value = null;
  previewUrl.value = null;
  uploadError.value = null;
  isOpen.value = false;
};
</script>

<template>
  <UModal v-model:open="isOpen" :title="t('avatar.modal.title')">
    <template #body>
      <div class="space-y-6 p-4">
        <!-- Avatar Preview -->
        <div class="flex justify-center">
          <div class="w-20 h-20">
            <UAvatar
              :src="previewUrl || '/no-photo.png'"
              :alt="t('avatar.preview')"
              size="3xl"
              :ui="{ root: 'w-full h-full' }"
              class="ring-2 ring-gray-200 dark:ring-gray-700"
            />
          </div>
        </div>

        <!-- File Upload -->
        <div class="flex flex-col items-center gap-4">
          <UFileUpload
            v-model="selectedFile"
            accept="image/jpeg,image/png,image/gif,image/webp"
          >
            <template #default="{ open }">
              <UButton
                color="primary"
                variant="outline"
                size="md"
                icon="i-heroicons-arrow-up-tray"
                @click="() => open()"
              >
                {{ t("avatar.selectButton") }}
              </UButton>
            </template>
          </UFileUpload>

          <p class="text-xs text-gray-500 dark:text-gray-400 text-center">
            {{ t("avatar.hint") }}
          </p>
        </div>

        <!-- Error Message -->
        <UAlert
          v-if="uploadError"
          color="error"
          variant="soft"
          :title="uploadError"
          icon="i-heroicons-exclamation-triangle"
          :close-button="{
            icon: 'i-heroicons-x-mark-20-solid',
            color: 'neutral',
            variant: 'ghost',
            padded: false,
          }"
          @close="uploadError = null"
        />
      </div>
    </template>

    <template #footer>
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 w-full">
        <UButton
          v-if="previewUrl"
          color="error"
          variant="outline"
          icon="i-heroicons-trash"
          @click="handleDelete"
          class="w-full sm:w-auto"
        >
          {{ t("avatar.deleteButton") }}
        </UButton>
        <UButton
          v-if="selectedFile"
          color="primary"
          variant="solid"
          icon="i-heroicons-check"
          @click="handleUpload"
          class="w-full sm:w-auto sm:ml-auto"
        >
          {{ t("common.save") }}
        </UButton>
      </div>
    </template>
  </UModal>
</template>
