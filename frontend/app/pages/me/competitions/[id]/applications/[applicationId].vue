<script setup lang="ts">
import { useCompetitionApplicationsStore } from '~/stores/competitionApplications';
import { useNotificationsStore } from '~/stores/notifications';
import { contactHref } from '~/utils/contact';

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const store = useCompetitionApplicationsStore();
const notifications = useNotificationsStore();
const { navigateBack } = useBackNavigation();

const competitionId = computed(() => route.params.id as string);
const applicationId = computed(() => route.params.applicationId as string);

useSeoMeta({ title: t('applications.title') });

onMounted(async () => {
  await store.fetchApplication(applicationId.value);
});

const app = computed(() => store.currentApplication);

// Collapsed by default — organiser sees just the name, expands for full info.
const participantExpanded = ref(false);

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
            @click="navigateBack({ fallback: `/me/competitions/${competitionId}/applications` })"
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
          <!-- Participant card (collapsible) -->
          <UCard class="mb-6" :ui="{ body: participantExpanded ? '' : '!p-0' }">
            <template #header>
              <button
                type="button"
                class="w-full flex items-center justify-between gap-4 text-left"
                @click="participantExpanded = !participantExpanded"
              >
                <div class="min-w-0">
                  <p class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                    {{ t('applications.participant') }}
                  </p>
                  <p class="text-lg font-semibold text-gray-900 dark:text-white truncate">
                    {{ app.participant.full_name }}
                  </p>
                </div>
                <UIcon
                  :name="participantExpanded ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'"
                  class="size-5 text-gray-500 flex-shrink-0"
                />
              </button>
            </template>

            <div v-if="participantExpanded" class="space-y-5">
              <div>
                <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ app.participant.full_name }}</p>
                <p class="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
                  {{ t('applications.participantAge') }}: {{ app.participant.age }}
                </p>
              </div>

              <div>
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                  {{ t('applications.participantBio') }}
                </p>
                <p
                  v-if="app.participant.bio"
                  class="text-base text-gray-700 dark:text-gray-300 whitespace-pre-line"
                >{{ app.participant.bio }}</p>
                <p v-else class="text-sm text-gray-400 italic">{{ t('applications.notProvided') }}</p>
              </div>

              <div>
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                  {{ t('applications.participantExperience') }}
                </p>
                <p v-if="app.participant.experience_level" class="text-base text-gray-700 dark:text-gray-300">
                  {{ app.participant.experience_level }}
                </p>
                <p v-else class="text-sm text-gray-400 italic">{{ t('applications.notProvided') }}</p>
              </div>

              <div>
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                  {{ t('applications.participantSkills') }}
                </p>
                <div v-if="app.participant.skills.length > 0" class="flex flex-wrap gap-1.5">
                  <UBadge
                    v-for="s in app.participant.skills"
                    :key="s.name"
                    size="sm"
                    variant="outline"
                    :label="`${s.name} · ${s.level}`"
                  />
                </div>
                <p v-else class="text-sm text-gray-400 italic">{{ t('applications.notProvided') }}</p>
              </div>

              <div>
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                  {{ t('applications.participantContacts') }}
                </p>
                <ul v-if="app.participant.contacts.length > 0" class="space-y-1.5 text-base">
                  <li v-for="c in app.participant.contacts" :key="`${c.title}:${c.value}`" class="flex gap-3">
                    <span class="text-gray-500 dark:text-gray-400 min-w-32">{{ c.title }}</span>
                    <a
                      v-if="contactHref(c.value)"
                      :href="contactHref(c.value)!"
                      target="_blank"
                      rel="noopener"
                      class="text-primary-600 dark:text-primary-400 hover:underline break-all"
                    >{{ c.value }}</a>
                    <span v-else class="text-gray-700 dark:text-gray-300 break-all">{{ c.value }}</span>
                  </li>
                </ul>
                <p v-else class="text-sm text-gray-400 italic">{{ t('applications.notProvided') }}</p>
              </div>
            </div>
          </UCard>

          <!-- Application card -->
          <UCard>
            <template #header>
              <div class="flex items-center justify-between gap-4">
                <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
                  {{ t('applications.applicationDetails') }}
                </h2>
                <UBadge
                  :color="statusColor(app.status)"
                  variant="subtle"
                  size="md"
                  :label="t('applications.status.' + app.status)"
                />
              </div>
            </template>

            <div class="space-y-5">
              <div>
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                  {{ t('applications.competition') }}
                </p>
                <p class="text-base text-gray-700 dark:text-gray-300">{{ app.competition_name }}</p>
              </div>

              <div>
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                  {{ t('applications.track') }}
                </p>
                <UBadge size="sm" variant="soft" :label="app.track.name" />
              </div>

              <div>
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                  {{ t('applications.submittedAt') }}
                </p>
                <p class="text-base text-gray-700 dark:text-gray-300">{{ new Date(app.created_at).toLocaleString() }}</p>
              </div>

              <div>
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                  {{ t('applications.formData') }}
                </p>
                <template v-if="app.form_data">
                  <div class="space-y-2">
                    <div
                      v-for="(value, key) in app.form_data"
                      :key="key"
                      class="flex flex-col sm:flex-row sm:gap-3 text-base"
                    >
                      <span class="text-gray-500 dark:text-gray-400 sm:min-w-56 font-medium">{{ key }}</span>
                      <span class="text-gray-700 dark:text-gray-300">{{ Array.isArray(value) ? value.join(', ') : value }}</span>
                    </div>
                  </div>
                </template>
                <p v-else class="text-sm text-gray-400 italic">{{ t('applications.noFormData') }}</p>
              </div>

              <div class="pt-1">
                <p class="text-xs text-gray-400 font-mono">ID: {{ app.id }}</p>
              </div>
            </div>

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
