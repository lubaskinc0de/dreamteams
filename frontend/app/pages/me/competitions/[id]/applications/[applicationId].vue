<script setup lang="ts">
import { useCompetitionApplicationsStore } from '~/stores/competitionApplications';
import { useNotificationsStore } from '~/stores/notifications';

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const store = useCompetitionApplicationsStore();
const notifications = useNotificationsStore();

const competitionId = computed(() => route.params.id as string);
const applicationId = computed(() => route.params.applicationId as string);

useSeoMeta({ title: t('applications.title') });

onMounted(async () => {
  await store.fetchApplication(applicationId.value);
});

const app = computed(() => store.currentApplication);

const statusColor = (status: string) => {
  if (status === 'accepted') return 'success';
  if (status === 'rejected') return 'error';
  return 'warning';
};

const handleAccept = async () => {
  const ok = await store.accept(applicationId.value);
  if (ok) {
    notifications.add({
      title: t('toast.applicationAccepted.title'),
      description: t('toast.applicationAccepted.description'),
      icon: 'i-heroicons-check-circle',
      color: 'success',
    });
  } else if (store.error) {
    notifications.add({
      title: t('apiErrors.' + store.error.code),
      icon: 'i-heroicons-exclamation-circle',
      color: 'error',
    });
  }
};

const handleReject = async () => {
  const ok = await store.reject(applicationId.value);
  if (ok) {
    notifications.add({
      title: t('toast.applicationRejected.title'),
      description: t('toast.applicationRejected.description'),
      icon: 'i-heroicons-check-circle',
      color: 'warning',
    });
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
            @click="router.push(`/me/competitions/${competitionId}/applications`)"
          />
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ t('applications.backToList') }}
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
          <UCard class="mb-6">
            <template #header>
              <div class="flex items-center justify-between">
                <div class="space-y-1">
                  <div class="flex items-center gap-2">
                    <UBadge
                      :color="statusColor(app.status)"
                      variant="subtle"
                      :label="t('applications.status.' + app.status)"
                    />
                  </div>
                  <p class="text-xs text-gray-400 font-mono">ID: {{ app.id }}</p>
                </div>
              </div>
            </template>

            <div class="space-y-4">
              <!-- Participant -->
              <div class="space-y-3">
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400">{{ t('applications.participant') }}</p>
                <div class="flex items-center gap-2">
                  <span class="text-base font-semibold text-gray-900 dark:text-white">{{ app.participant.full_name }}</span>
                  <UBadge size="xs" variant="subtle" :label="t('competition.participantTypes.' + app.participant.participant_type)" />
                  <UBadge size="xs" variant="soft" :label="String(app.participant.age)" />
                </div>
                <p v-if="app.participant.bio" class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-line">{{ app.participant.bio }}</p>

                <div v-if="app.participant.experience_level" class="text-sm">
                  <span class="text-gray-500">{{ t('applications.participantExperience') }}:</span>
                  <span class="ml-1 font-medium">{{ app.participant.experience_level }}</span>
                </div>

                <div v-if="app.participant.preferred_domains.length > 0">
                  <p class="text-xs text-gray-500 mb-1">{{ t('applications.participantDomains') }}</p>
                  <div class="flex flex-wrap gap-1">
                    <UBadge v-for="d in app.participant.preferred_domains" :key="d" size="xs" variant="outline" :label="d" />
                  </div>
                </div>

                <div v-if="app.participant.skills.length > 0">
                  <p class="text-xs text-gray-500 mb-1">{{ t('applications.participantSkills') }}</p>
                  <div class="flex flex-wrap gap-1">
                    <UBadge v-for="s in app.participant.skills" :key="s.name" size="xs" variant="outline" :label="`${s.name} · ${s.level}`" />
                  </div>
                </div>

                <div v-if="app.participant.contacts.length > 0">
                  <p class="text-xs text-gray-500 mb-1">{{ t('applications.participantContacts') }}</p>
                  <ul class="space-y-1 text-sm">
                    <li v-for="c in app.participant.contacts" :key="c.url" class="flex gap-2">
                      <span class="text-gray-500 min-w-24">{{ c.title }}</span>
                      <a :href="c.url" target="_blank" rel="noopener" class="text-primary-600 dark:text-primary-400 hover:underline break-all">{{ c.url }}</a>
                    </li>
                  </ul>
                </div>
              </div>

              <!-- Competition -->
              <div>
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400">{{ t('applications.competition') }}</p>
                <p class="text-sm text-gray-700 dark:text-gray-300">{{ app.competition_name }}</p>
              </div>

              <!-- Domains -->
              <div>
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">{{ t('applications.domains') }}</p>
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
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400">{{ t('applications.submittedAt') }}</p>
                <p class="text-sm text-gray-700 dark:text-gray-300">{{ new Date(app.created_at).toLocaleString() }}</p>
              </div>

              <!-- Form data -->
              <div>
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">{{ t('applications.formData') }}</p>
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
                <p v-else class="text-sm text-gray-400 italic">{{ t('applications.noFormData') }}</p>
              </div>
            </div>

            <!-- Actions -->
            <template v-if="app.status === 'pending'" #footer>
              <div class="flex gap-3 justify-end">
                <UButton
                  color="error"
                  variant="soft"
                  icon="i-heroicons-x-mark"
                  :label="store.acting ? t('applications.rejecting') : t('applications.rejectButton')"
                  :loading="store.acting"
                  :disabled="store.acting"
                  @click="handleReject"
                />
                <UButton
                  color="success"
                  icon="i-heroicons-check"
                  :label="store.acting ? t('applications.accepting') : t('applications.acceptButton')"
                  :loading="store.acting"
                  :disabled="store.acting"
                  @click="handleAccept"
                />
              </div>
            </template>
            <template v-else #footer>
              <p class="text-sm text-gray-400 italic">{{ t('applications.alreadyResolved') }}</p>
            </template>
          </UCard>
        </template>
      </UContainer>
    </UPageBody>
  </UPage>
</template>
