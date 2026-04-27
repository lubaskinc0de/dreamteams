<script setup lang="ts">
import { useAdminUsersStore } from "~/stores/adminUsers";
import { useNotificationsStore } from "~/stores/notifications";
import { contactHref } from "~/utils/contact";

definePageMeta({ layout: "default" });

const { t } = useI18n();
const route = useRoute();
const store = useAdminUsersStore();
const notifications = useNotificationsStore();

const blockModalOpen = ref(false);
const unblockModalOpen = ref(false);
const blockReason = ref("");

const userId = computed(() => {
  const id = route.params.id;
  return Array.isArray(id) ? id[0] ?? "" : id ?? "";
});

const displayName = computed(() => {
  const details = store.currentUser;
  return (
    details?.organizer?.organizer_name ??
    details?.participant?.full_name ??
    details?.user.id ??
    t("admin.users.unnamed")
  );
});

const roleLabel = computed(() => {
  if (store.currentUser?.organizer) return t("admin.users.roles.organizer");
  if (store.currentUser?.participant) return t("admin.users.roles.participant");
  return t("admin.users.roles.none");
});

const formatDateTime = (value: string | null) => {
  if (!value) return t("admin.users.notProvided");
  return new Date(value).toLocaleString();
};

const openBlockModal = () => {
  blockReason.value = "";
  store.clearError();
  blockModalOpen.value = true;
};

const openUnblockModal = () => {
  store.clearError();
  unblockModalOpen.value = true;
};

const handleBlock = async () => {
  if (!store.currentUser) return;

  const success = await store.blockUser(store.currentUser.user.id, {
    reason: blockReason.value.trim() || null,
  });

  if (success) {
    notifications.add({
      title: t("toast.userBlocked.title"),
      description: t("toast.userBlocked.description"),
      color: "success",
      icon: "i-heroicons-check-circle",
    });
    blockModalOpen.value = false;
  } else if (store.error) {
    notifications.add({
      title: t("apiErrors." + store.error.code),
      color: "error",
      icon: "i-heroicons-exclamation-triangle",
    });
  }
};

const handleUnblock = async () => {
  if (!store.currentUser) return;

  const success = await store.unblockUser(store.currentUser.user.id);

  if (success) {
    notifications.add({
      title: t("toast.userUnblocked.title"),
      description: t("toast.userUnblocked.description"),
      color: "success",
      icon: "i-heroicons-check-circle",
    });
    unblockModalOpen.value = false;
  } else if (store.error) {
    notifications.add({
      title: t("apiErrors." + store.error.code),
      color: "error",
      icon: "i-heroicons-exclamation-triangle",
    });
  }
};

onMounted(async () => {
  await store.fetchUser(userId.value);
});

watch(userId, async (nextUserId) => {
  await store.fetchUser(nextUserId);
});

useHead({
  title: computed(() => `${displayName.value} - ${t("admin.users.detailTitle")}`),
});
</script>

<template>
  <UContainer class="py-8">
    <div class="mb-6 flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
      <div>
        <UButton
          to="/admin/users"
          variant="ghost"
          color="neutral"
          icon="i-heroicons-arrow-left"
          :label="t('common.back')"
          class="mb-3"
        />
        <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-gray-100">
          {{ displayName }}
        </h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-2 break-all">
          {{ userId }}
        </p>
      </div>

      <div v-if="store.currentUser" class="flex flex-col sm:flex-row gap-2">
        <UButton
          v-if="store.currentUser.user.ban_status.is_blocked"
          icon="i-heroicons-lock-open"
          color="success"
          variant="soft"
          :label="t('admin.users.actions.unblock')"
          @click="openUnblockModal"
        />
        <UButton
          v-else
          icon="i-heroicons-no-symbol"
          color="error"
          variant="soft"
          :label="t('admin.users.actions.block')"
          @click="openBlockModal"
        />
      </div>
    </div>

    <UAlert
      v-if="store.error && !store.detailLoading"
      color="error"
      variant="soft"
      :title="t('apiErrors.' + store.error.code)"
      icon="i-heroicons-exclamation-circle"
      class="mb-4"
    />

    <UButton
      v-if="store.error && !store.detailLoading"
      variant="soft"
      icon="i-heroicons-arrow-path"
      :label="t('common.retry')"
      class="mb-4"
      @click="store.fetchUser(userId)"
    />

    <div v-if="store.detailLoading" class="space-y-4">
      <USkeleton class="h-40 w-full rounded-lg" />
      <USkeleton class="h-64 w-full rounded-lg" />
    </div>

    <div v-else-if="store.currentUser" class="grid grid-cols-1 lg:grid-cols-[22rem_minmax(0,1fr)] gap-5">
      <div class="space-y-5">
        <UCard>
          <div class="flex items-center gap-4">
            <UAvatar
              :src="store.currentUser.user.avatar_url || '/no-photo.png'"
              :alt="displayName"
              size="3xl"
            />
            <div class="min-w-0">
              <p class="text-lg font-semibold text-gray-900 dark:text-white truncate">
                {{ displayName }}
              </p>
              <div class="mt-2 flex flex-wrap gap-2">
                <UBadge color="neutral" variant="soft" :label="roleLabel" />
                <UBadge
                  v-if="store.currentUser.user.is_admin"
                  color="info"
                  variant="soft"
                  icon="i-heroicons-shield-check"
                  :label="t('admin.users.adminBadge')"
                />
                <UBadge
                  :color="store.currentUser.user.ban_status.is_blocked ? 'error' : 'success'"
                  variant="soft"
                  :icon="store.currentUser.user.ban_status.is_blocked ? 'i-heroicons-no-symbol' : 'i-heroicons-check-circle'"
                  :label="store.currentUser.user.ban_status.is_blocked ? t('admin.users.status.blocked') : t('admin.users.status.active')"
                />
              </div>
            </div>
          </div>
        </UCard>

        <UCard>
          <template #header>
            <h2 class="font-semibold text-gray-900 dark:text-white">
              {{ t("admin.users.sections.banStatus") }}
            </h2>
          </template>
          <div class="space-y-3 text-sm">
            <div class="flex justify-between gap-4">
              <span class="text-gray-500 dark:text-gray-400">{{ t("admin.users.fields.status") }}</span>
              <span class="font-medium">
                {{ store.currentUser.user.ban_status.is_blocked ? t("admin.users.status.blocked") : t("admin.users.status.active") }}
              </span>
            </div>
            <div v-if="store.currentUser.user.ban_status.is_blocked" class="space-y-3">
              <div class="flex justify-between gap-4">
                <span class="text-gray-500 dark:text-gray-400">{{ t("admin.users.fields.reason") }}</span>
                <span class="font-medium text-right">{{ store.currentUser.user.ban_status.reason ?? t("admin.users.notProvided") }}</span>
              </div>
              <div class="flex justify-between gap-4">
                <span class="text-gray-500 dark:text-gray-400">{{ t("admin.users.fields.blockedAt") }}</span>
                <span class="font-medium text-right">{{ formatDateTime(store.currentUser.user.ban_status.blocked_at) }}</span>
              </div>
            </div>
          </div>
        </UCard>
      </div>

      <div class="space-y-5">
        <UCard v-if="store.currentUser.organizer">
          <template #header>
            <h2 class="font-semibold text-gray-900 dark:text-white">
              {{ t("admin.users.sections.organizer") }}
            </h2>
          </template>
          <dl class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
            <div>
              <dt class="text-gray-500 dark:text-gray-400">{{ t("admin.users.fields.organizerName") }}</dt>
              <dd class="font-medium text-gray-900 dark:text-white">{{ store.currentUser.organizer.organizer_name }}</dd>
            </div>
            <div>
              <dt class="text-gray-500 dark:text-gray-400">{{ t("admin.users.fields.phone") }}</dt>
              <dd class="font-medium text-gray-900 dark:text-white">{{ store.currentUser.organizer.phone_number }}</dd>
            </div>
            <div>
              <dt class="text-gray-500 dark:text-gray-400">{{ t("admin.users.fields.email") }}</dt>
              <dd class="font-medium text-gray-900 dark:text-white break-all">{{ store.currentUser.organizer.contact_email }}</dd>
            </div>
            <div>
              <dt class="text-gray-500 dark:text-gray-400">{{ t("admin.users.fields.organizerId") }}</dt>
              <dd class="font-medium text-gray-900 dark:text-white break-all">{{ store.currentUser.organizer.id }}</dd>
            </div>
          </dl>
        </UCard>

        <UCard v-if="store.currentUser.participant">
          <template #header>
            <h2 class="font-semibold text-gray-900 dark:text-white">
              {{ t("admin.users.sections.participant") }}
            </h2>
          </template>
          <div class="space-y-5">
            <dl class="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
              <div>
                <dt class="text-gray-500 dark:text-gray-400">{{ t("admin.users.fields.fullName") }}</dt>
                <dd class="font-medium text-gray-900 dark:text-white">{{ store.currentUser.participant.full_name }}</dd>
              </div>
              <div>
                <dt class="text-gray-500 dark:text-gray-400">{{ t("admin.users.fields.participantType") }}</dt>
                <dd class="font-medium text-gray-900 dark:text-white">{{ store.currentUser.participant.participant_type }}</dd>
              </div>
              <div>
                <dt class="text-gray-500 dark:text-gray-400">{{ t("admin.users.fields.age") }}</dt>
                <dd class="font-medium text-gray-900 dark:text-white">{{ store.currentUser.participant.age }}</dd>
              </div>
              <div>
                <dt class="text-gray-500 dark:text-gray-400">{{ t("admin.users.fields.experience") }}</dt>
                <dd class="font-medium text-gray-900 dark:text-white">{{ store.currentUser.participant.experience_level ?? t("admin.users.notProvided") }}</dd>
              </div>
              <div>
                <dt class="text-gray-500 dark:text-gray-400">{{ t("admin.users.fields.createdAt") }}</dt>
                <dd class="font-medium text-gray-900 dark:text-white">{{ formatDateTime(store.currentUser.participant.created_at) }}</dd>
              </div>
              <div>
                <dt class="text-gray-500 dark:text-gray-400">{{ t("admin.users.fields.updatedAt") }}</dt>
                <dd class="font-medium text-gray-900 dark:text-white">{{ formatDateTime(store.currentUser.participant.updated_at) }}</dd>
              </div>
            </dl>

            <div v-if="store.currentUser.participant.bio">
              <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-2">
                {{ t("admin.users.fields.bio") }}
              </h3>
              <p class="text-sm leading-relaxed text-gray-700 dark:text-gray-300">
                {{ store.currentUser.participant.bio }}
              </p>
            </div>

            <div v-if="store.currentUser.participant.skills.length">
              <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-2">
                {{ t("admin.users.fields.skills") }}
              </h3>
              <div class="flex flex-wrap gap-2">
                <UBadge
                  v-for="skill in store.currentUser.participant.skills"
                  :key="`${skill.name}-${skill.level}`"
                  color="primary"
                  variant="soft"
                  :label="`${skill.name}: ${skill.level}`"
                />
              </div>
            </div>

            <div v-if="store.currentUser.participant.preferred_domains.length">
              <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-2">
                {{ t("admin.users.fields.domains") }}
              </h3>
              <div class="flex flex-wrap gap-2">
                <UBadge
                  v-for="domain in store.currentUser.participant.preferred_domains"
                  :key="domain"
                  color="neutral"
                  variant="soft"
                  :label="domain"
                />
              </div>
            </div>

            <div v-if="store.currentUser.participant.contacts.length">
              <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-2">
                {{ t("admin.users.fields.contacts") }}
              </h3>
              <div class="space-y-2">
                <template
                  v-for="contact in store.currentUser.participant.contacts"
                  :key="`${contact.title}:${contact.value}`"
                >
                  <a
                    v-if="contactHref(contact.value)"
                    :href="contactHref(contact.value)!"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="inline-flex items-center gap-2 text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
                  >
                    <UIcon name="i-heroicons-link" />
                    <span>{{ contact.title }}</span>
                  </a>
                  <div v-else class="inline-flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
                    <UIcon name="i-heroicons-at-symbol" />
                    <span>{{ contact.title }}: {{ contact.value }}</span>
                  </div>
                </template>
              </div>
            </div>
          </div>
        </UCard>

        <UAlert
          v-if="!store.currentUser.organizer && !store.currentUser.participant"
          color="neutral"
          variant="soft"
          icon="i-heroicons-identification"
          :title="t('admin.users.sections.noRole')"
        />
      </div>
    </div>
  </UContainer>

  <UModal v-model:open="blockModalOpen" :title="t('admin.users.blockModal.title')">
    <template #body>
      <div class="space-y-4">
        <p class="text-sm text-gray-600 dark:text-gray-400">
          {{ t("admin.users.blockModal.description", { name: displayName }) }}
        </p>
        <UAlert
          v-if="store.error"
          color="error"
          variant="soft"
          :title="t('apiErrors.' + store.error.code)"
          icon="i-heroicons-exclamation-circle"
        />
        <UFormField :label="t('admin.users.blockModal.reason')">
          <UTextarea
            v-model="blockReason"
            :placeholder="t('admin.users.blockModal.reasonPlaceholder')"
            :rows="4"
            class="w-full"
          />
        </UFormField>
      </div>
    </template>
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton color="neutral" variant="ghost" :label="t('common.cancel')" @click="blockModalOpen = false" />
        <UButton
          color="error"
          icon="i-heroicons-no-symbol"
          :label="t('admin.users.actions.block')"
          :loading="store.actionLoading"
          :disabled="store.actionLoading"
          @click="handleBlock"
        />
      </div>
    </template>
  </UModal>

  <UModal v-model:open="unblockModalOpen" :title="t('admin.users.unblockModal.title')">
    <template #body>
      <p class="text-sm text-gray-600 dark:text-gray-400">
        {{ t("admin.users.unblockModal.description", { name: displayName }) }}
      </p>
    </template>
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton color="neutral" variant="ghost" :label="t('common.cancel')" @click="unblockModalOpen = false" />
        <UButton
          color="success"
          icon="i-heroicons-lock-open"
          :label="t('admin.users.actions.unblock')"
          :loading="store.actionLoading"
          :disabled="store.actionLoading"
          @click="handleUnblock"
        />
      </div>
    </template>
  </UModal>
</template>
