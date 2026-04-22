<script setup lang="ts">
import { useMyApplicationsStore } from '~/stores/myApplications';
import { useNotificationsStore } from '~/stores/notifications';

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const store = useMyApplicationsStore();
const notifications = useNotificationsStore();

const applicationId = computed(() => route.params.id as string);

useSeoMeta({ title: t('myApplications.title') });

onMounted(async () => {
  await store.fetchMyApplication(applicationId.value);
});

const app = computed(() => store.currentApplication);

const statusColor = (status: string) => {
  if (status === 'accepted') return 'success';
  if (status === 'rejected') return 'error';
  return 'warning';
};

const isWithdrawModalOpen = ref(false);

const handleWithdraw = async () => {
  const ok = await store.withdraw(applicationId.value);
  isWithdrawModalOpen.value = false;

  if (ok) {
    notifications.add({
      title: t('toast.applicationWithdrawn.title'),
      description: t('toast.applicationWithdrawn.description'),
      icon: 'i-heroicons-check-circle',
      color: 'success',
    });
    router.push('/me/applications');
  } else if (store.error) {
    notifications.add({
      title: t('apiErrors.' + store.error.code),
      icon: 'i-heroicons-exclamation-circle',
      color: 'error',
    });
  }
};
</script>

<template>
  <UPage>
    <UPageBody>
      <UContainer class="!max-w-3xl">
        <!-- Header -->
        <div class="flex items-center gap-4 mb-6">
          <UButton
            icon="i-heroicons-arrow-left"
            color="neutral"
            variant="ghost"
            @click="router.push('/me/applications')"
          />
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ t('myApplications.backToList') }}
          </h1>
        </div>

        <!-- Error -->
        <UAlert
          v-if="store.error && !store.loading"
          color="error"
          variant="soft"
          :title="t('apiErrors.' + store.error.code)"
          icon="i-heroicons-exclamation-circle"
          class="mb-4"
        />

        <!-- Loading -->
        <div v-if="store.loading && !app" class="space-y-4">
          <USkeleton class="h-32 w-full rounded-lg" />
          <USkeleton class="h-20 w-full rounded-lg" />
        </div>

        <!-- Application detail -->
        <template v-else-if="app">
          <UCard>
            <template #header>
              <div class="flex items-center justify-between">
                <UBadge
                  :color="statusColor(app.status)"
                  variant="subtle"
                  size="lg"
                  :label="t('myApplications.status.' + app.status)"
                />
                <UButton
                  v-if="app.status === 'pending'"
                  color="error"
                  variant="soft"
                  icon="i-heroicons-trash"
                  :label="t('myApplications.withdrawButton')"
                  @click="isWithdrawModalOpen = true"
                />
              </div>
            </template>

            <div class="space-y-4">
              <!-- Competition -->
              <div>
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400">{{ t('myApplications.competition') }}</p>
                <NuxtLink
                  :to="`/competitions/${app.competition_id}`"
                  class="text-sm text-primary-600 dark:text-primary-400 hover:underline"
                >
                  {{ app.competition_name }}
                </NuxtLink>
              </div>

              <!-- Domains -->
              <div>
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">{{ t('myApplications.domains') }}</p>
                <div class="flex flex-wrap gap-1">
                  <UBadge
                    v-for="domain in app.domains"
                    :key="domain"
                    variant="soft"
                    :label="domain"
                  />
                </div>
              </div>

              <!-- Submitted at -->
              <div>
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400">{{ t('myApplications.submittedAt') }}</p>
                <p class="text-sm text-gray-700 dark:text-gray-300">{{ new Date(app.created_at).toLocaleString() }}</p>
              </div>

              <!-- Form data -->
              <div>
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">{{ t('myApplications.formData') }}</p>
                <template v-if="app.form_data">
                  <div class="space-y-2">
                    <div
                      v-for="(value, key) in app.form_data"
                      :key="key"
                      class="flex gap-2 text-sm"
                    >
                      <span class="font-mono text-gray-400 min-w-32">{{ key }}</span>
                      <span class="text-gray-700 dark:text-gray-300">{{ Array.isArray(value) ? value.join(', ') : value }}</span>
                    </div>
                  </div>
                </template>
                <p v-else class="text-sm text-gray-400 italic">{{ t('myApplications.noFormData') }}</p>
              </div>
            </div>
          </UCard>
        </template>
      </UContainer>
    </UPageBody>

    <!-- Withdraw confirmation -->
    <UiConfirmDeleteModal
      v-model:open="isWithdrawModalOpen"
      :title="t('myApplications.withdrawConfirmTitle')"
      :description="t('myApplications.withdrawConfirmDescription')"
      :confirm-label="t('myApplications.withdrawButton')"
      :cancel-label="t('common.cancel')"
      :is-deleting="store.withdrawing"
      @confirm="handleWithdraw"
    />
  </UPage>
</template>
