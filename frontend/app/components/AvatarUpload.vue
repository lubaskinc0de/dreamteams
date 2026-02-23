<script setup lang="ts">
const props = defineProps<{
  currentAvatarUrl?: string | null;
  loading?: boolean;
  showDelete?: boolean;
}>();

const emit = defineEmits<{
  upload: [file: File];
  delete: [];
}>();

const { t } = useI18n();

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

  // Emit upload event
  emit("upload", file);
});

// Handle delete
const handleDelete = () => {
  selectedFile.value = null;
  previewUrl.value = null;
  uploadError.value = null;

  emit("delete");
};
</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-col items-center gap-4">
      <!-- Avatar Preview -->
      <div class="relative w-20 h-20">
        <UAvatar
          :src="previewUrl || '/no-photo.png'"
          :alt="t('avatar.preview')"
          size="3xl"
          :ui="{ root: 'w-full h-full' }"
          class="ring-2 ring-gray-200 dark:ring-gray-700"
        />
        <UButton
          v-if="previewUrl && showDelete"
          color="error"
          variant="soft"
          size="xs"
          icon="i-heroicons-x-mark"
          class="absolute -top-2 -right-2 rounded-full"
          :loading="loading"
          @click="handleDelete"
          :aria-label="t('avatar.deleteButton')"
        />
      </div>

      <!-- File Upload -->
      <div class="flex flex-col items-center gap-2 w-full max-w-xs">
        <UFileUpload
          v-model="selectedFile"
          accept="image/jpeg,image/png,image/gif,image/webp"
          :disabled="loading"
        >
          <template #default="{ open }">
            <UButton
              color="primary"
              variant="soft"
              size="md"
              icon="i-heroicons-arrow-up-tray"
              :loading="loading"
              :disabled="loading"
              @click="() => open()"
            >
              {{ previewUrl ? t("avatar.changeButton") : t("avatar.uploadButton") }}
            </UButton>
          </template>
        </UFileUpload>

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
        class="w-full"
      />
    </div>
  </div>
</template>
