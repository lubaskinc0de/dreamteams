<script setup lang="ts">
const { t } = useI18n();
const api = useApi();

useSeoMeta({
  title: t("superuserRegister.title"),
});

definePageMeta({
  layout: "onboarding",
});

const password = ref("");
const loading = ref(false);
const error = ref<string | null>(null);
const createdUserId = ref<string | null>(null);

const submit = async () => {
  error.value = null;
  loading.value = true;

  const { data, error: apiError } = await api.registerSuperuser(password.value);

  loading.value = false;

  if (apiError) {
    const key = `apiErrors.${apiError.code}`;
    error.value = t(key) !== key ? t(key) : apiError.message;
    return;
  }

  if (data) {
    createdUserId.value = data.user_id;
    password.value = "";
  }
};
</script>

<template>
  <UPage>
    <UPageBody>
      <div class="flex items-center justify-center px-4 min-h-[60vh]">
        <div class="w-full max-w-sm mx-auto">
          <!-- Success state -->
          <div v-if="createdUserId" class="text-center">
            <div class="inline-flex p-4 rounded-2xl bg-green-500/10 mb-6">
              <UIcon
                name="i-heroicons-check-circle"
                class="text-6xl text-green-500"
              />
            </div>
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              {{ t("superuserRegister.success.title") }}
            </h1>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
              {{ t("superuserRegister.success.description") }}
            </p>
            <div class="bg-gray-100 dark:bg-gray-800 rounded-lg px-4 py-3 text-left mb-6">
              <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">
                {{ t("superuserRegister.success.userId") }}
              </p>
              <p class="font-mono text-sm text-gray-900 dark:text-gray-100 break-all">
                {{ createdUserId }}
              </p>
            </div>
            <UButton to="/" icon="i-heroicons-home" size="lg">
              {{ t("common.backToHome") }}
            </UButton>
          </div>

          <!-- Form state -->
          <div v-else>
            <div class="text-center mb-8">
              <div class="inline-flex p-4 rounded-2xl bg-primary-500/10 mb-4">
                <UIcon
                  name="i-heroicons-shield-check"
                  class="text-6xl text-primary-500"
                />
              </div>
              <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
                {{ t("superuserRegister.title") }}
              </h1>
            </div>

            <UAlert
              v-if="error"
              color="error"
              variant="soft"
              :description="error"
              icon="i-heroicons-exclamation-triangle"
              class="mb-4"
            />

            <form @submit.prevent="submit" class="space-y-4">
              <UFormField :label="t('superuserRegister.passwordLabel')">
                <UInput
                  v-model="password"
                  type="password"
                  :placeholder="t('superuserRegister.passwordPlaceholder')"
                  size="lg"
                  class="w-full"
                  autocomplete="current-password"
                  required
                />
              </UFormField>

              <UButton
                type="submit"
                color="primary"
                size="lg"
                block
                :loading="loading"
                :disabled="!password"
              >
                {{ t("superuserRegister.submitButton") }}
              </UButton>
            </form>
          </div>
        </div>
      </div>
    </UPageBody>
  </UPage>
</template>
