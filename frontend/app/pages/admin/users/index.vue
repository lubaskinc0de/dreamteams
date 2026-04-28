<script setup lang="ts">
import { useAdminUsersStore } from "~/stores/adminUsers";
import { useNotificationsStore } from "~/stores/notifications";
import type { AdminUserListItem, AdminUserRole } from "~/types/api";

definePageMeta({ layout: "default" });

const { t } = useI18n();
const router = useRouter();
const store = useAdminUsersStore();
const notifications = useNotificationsStore();

const blockModalOpen = ref(false);
const unblockModalOpen = ref(false);
const actionTarget = ref<AdminUserListItem | null>(null);
const blockReason = ref("");

const adminNavItems = computed(() => [
  { label: t("admin.users.nav"), icon: "i-heroicons-users", to: "/admin/users" },
  { label: t("admin.invites.nav"), icon: "i-heroicons-ticket", to: "/admin/invites" },
  { label: t("admin.tags.nav"), icon: "i-heroicons-tag", to: "/admin/tags" },
]);

const roleOptions = computed(() => [
  { value: "all", label: t("admin.users.filters.allRoles") },
  { value: "organizer", label: t("admin.users.roles.organizer") },
  { value: "participant", label: t("admin.users.roles.participant") },
]);

const adminOptions = computed(() => [
  { value: "all", label: t("admin.users.filters.allAdminStatuses") },
  { value: "true", label: t("admin.users.filters.adminOnly") },
  { value: "false", label: t("admin.users.filters.nonAdminOnly") },
]);

const blockedOptions = computed(() => [
  { value: "all", label: t("admin.users.filters.allBanStatuses") },
  { value: "true", label: t("admin.users.filters.blockedOnly") },
  { value: "false", label: t("admin.users.filters.activeOnly") },
]);

const roleFilterValue = computed({
  get: () => store.roleFilter ?? "all",
  set: (value: string) => {
    store.roleFilter = value === "all" ? null : (value as AdminUserRole);
    void store.applyFilters();
  },
});

const adminFilterValue = computed({
  get: () => {
    if (store.isAdminFilter === null) return "all";
    return store.isAdminFilter ? "true" : "false";
  },
  set: (value: string) => {
    store.isAdminFilter = value === "all" ? null : value === "true";
    void store.applyFilters();
  },
});

const blockedFilterValue = computed({
  get: () => {
    if (store.isBlockedFilter === null) return "all";
    return store.isBlockedFilter ? "true" : "false";
  },
  set: (value: string) => {
    store.isBlockedFilter = value === "all" ? null : value === "true";
    void store.applyFilters();
  },
});

let searchTimer: ReturnType<typeof setTimeout> | null = null;
watch(
  () => store.search,
  () => {
    if (searchTimer) clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      void store.applyFilters();
    }, 300);
  },
);

onMounted(async () => {
  await store.fetchUsers(1);
});

onBeforeUnmount(() => {
  if (searchTimer) clearTimeout(searchTimer);
});

useHead({ title: t("admin.users.title") });

const totalPages = computed(() => Math.max(1, Math.ceil(store.total / 20)));

const displayName = (user: AdminUserListItem) =>
  user.organizer_name ?? user.participant_full_name ?? t("admin.users.unnamed");

const roleLabel = (user: AdminUserListItem) => {
  if (user.organizer_name) return t("admin.users.roles.organizer");
  if (user.participant_full_name) return t("admin.users.roles.participant");
  return t("admin.users.roles.none");
};

const roleIcon = (user: AdminUserListItem) => {
  if (user.organizer_name) return "i-heroicons-building-office";
  if (user.participant_full_name) return "i-heroicons-user";
  return "i-heroicons-question-mark-circle";
};

const formatDateTime = (value: string | null) => {
  if (!value) return t("admin.users.notProvided");
  return new Date(value).toLocaleString();
};

const openBlockModal = (user: AdminUserListItem) => {
  actionTarget.value = user;
  blockReason.value = "";
  store.clearError();
  blockModalOpen.value = true;
};

const openUnblockModal = (user: AdminUserListItem) => {
  actionTarget.value = user;
  store.clearError();
  unblockModalOpen.value = true;
};

const handleBlock = async () => {
  if (!actionTarget.value) return;

  const success = await store.blockUser(actionTarget.value.id, {
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
    actionTarget.value = null;
  } else if (store.error) {
    notifications.add({
      title: t("apiErrors." + store.error.code),
      color: "error",
      icon: "i-heroicons-exclamation-triangle",
    });
  }
};

const handleUnblock = async () => {
  if (!actionTarget.value) return;

  const success = await store.unblockUser(actionTarget.value.id);

  if (success) {
    notifications.add({
      title: t("toast.userUnblocked.title"),
      description: t("toast.userUnblocked.description"),
      color: "success",
      icon: "i-heroicons-check-circle",
    });
    unblockModalOpen.value = false;
    actionTarget.value = null;
  } else if (store.error) {
    notifications.add({
      title: t("apiErrors." + store.error.code),
      color: "error",
      icon: "i-heroicons-exclamation-triangle",
    });
  }
};
</script>

<template>
  <UContainer class="py-8">
    <div class="flex flex-col gap-5 mb-6">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 class="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-900 dark:text-gray-100">
            {{ t("admin.users.title") }}
          </h1>
          <p class="text-sm text-gray-500 dark:text-gray-400 mt-2">
            {{ t("admin.users.subtitle", { total: store.total }) }}
          </p>
        </div>
        <UNavigationMenu :items="adminNavItems" variant="pill" class="w-full sm:w-auto" />
      </div>

      <div class="grid grid-cols-1 md:grid-cols-[minmax(0,1fr)_12rem_12rem_12rem] gap-3">
        <UInput
          v-model="store.search"
          icon="i-heroicons-magnifying-glass"
          :placeholder="t('admin.users.filters.searchPlaceholder')"
          class="w-full"
        />
        <USelect
          v-model="roleFilterValue"
          :items="roleOptions"
          value-key="value"
          icon="i-heroicons-identification"
          class="w-full"
        />
        <USelect
          v-model="adminFilterValue"
          :items="adminOptions"
          value-key="value"
          icon="i-heroicons-shield-check"
          class="w-full"
        />
        <USelect
          v-model="blockedFilterValue"
          :items="blockedOptions"
          value-key="value"
          icon="i-heroicons-no-symbol"
          class="w-full"
        />
      </div>
    </div>

    <UAlert
      v-if="store.error && !store.loading"
      color="error"
      variant="soft"
      :title="t('apiErrors.' + store.error.code)"
      icon="i-heroicons-exclamation-circle"
      class="mb-4"
    />

    <UButton
      v-if="store.error && !store.loading"
      variant="soft"
      icon="i-heroicons-arrow-path"
      :label="t('common.retry')"
      class="mb-4"
      @click="store.fetchUsers(store.page)"
    />

    <div v-if="store.loading" class="space-y-3">
      <USkeleton v-for="i in 6" :key="i" class="h-24 w-full rounded-lg" />
    </div>

    <div v-else-if="store.users.length > 0" class="space-y-3">
      <UCard v-for="user in store.users" :key="user.id">
        <div class="flex flex-col lg:flex-row lg:items-start gap-4">
          <div class="flex-1 min-w-0 space-y-3">
            <div class="flex items-start gap-3">
              <UIcon :name="roleIcon(user)" class="mt-1 text-xl text-primary-500 shrink-0" />
              <div class="min-w-0">
                <div class="flex flex-wrap items-center gap-2">
                  <p class="text-lg font-semibold text-gray-900 dark:text-white truncate">
                    {{ displayName(user) }}
                  </p>
                  <UBadge variant="soft" color="neutral" :label="roleLabel(user)" />
                  <UBadge
                    v-if="user.is_admin"
                    variant="soft"
                    color="info"
                    icon="i-heroicons-shield-check"
                    :label="t('admin.users.adminBadge')"
                  />
                  <UBadge
                    :color="user.ban_status.is_blocked ? 'error' : 'success'"
                    variant="soft"
                    :icon="user.ban_status.is_blocked ? 'i-heroicons-no-symbol' : 'i-heroicons-check-circle'"
                    :label="user.ban_status.is_blocked ? t('admin.users.status.blocked') : t('admin.users.status.active')"
                  />
                </div>
                <p class="mt-1 text-sm text-gray-500 dark:text-gray-400 break-all">
                  {{ user.id }}
                </p>
              </div>
            </div>

            <div
              v-if="user.ban_status.is_blocked"
              class="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-900 dark:border-red-900/60 dark:bg-red-950/40 dark:text-red-100"
            >
              <p>
                <span class="font-medium">{{ t("admin.users.fields.reason") }}:</span>
                {{ user.ban_status.reason ?? t("admin.users.notProvided") }}
              </p>
              <p class="mt-1">
                <span class="font-medium">{{ t("admin.users.fields.blockedAt") }}:</span>
                {{ formatDateTime(user.ban_status.blocked_at) }}
              </p>
            </div>
          </div>

          <div class="flex flex-col sm:flex-row lg:flex-col gap-2 lg:w-40">
            <UButton
              icon="i-heroicons-eye"
              variant="soft"
              color="neutral"
              :label="t('admin.users.actions.details')"
              class="justify-center"
              @click="router.push(`/admin/users/${user.id}`)"
            />
            <UButton
              v-if="user.ban_status.is_blocked"
              icon="i-heroicons-lock-open"
              variant="soft"
              color="success"
              :label="t('admin.users.actions.unblock')"
              class="justify-center"
              @click="openUnblockModal(user)"
            />
            <UButton
              v-else
              icon="i-heroicons-no-symbol"
              variant="soft"
              color="error"
              :label="t('admin.users.actions.block')"
              class="justify-center"
              @click="openBlockModal(user)"
            />
          </div>
        </div>
      </UCard>

      <div v-if="totalPages > 1" class="flex justify-center pt-4">
        <UPagination
          :model-value="store.page"
          :total="store.total"
          :page-count="20"
          @update:model-value="store.fetchUsers"
        />
      </div>
    </div>

    <div v-else class="text-center py-16">
      <UIcon name="i-heroicons-users" class="text-5xl text-gray-400 dark:text-gray-600 mb-4" />
      <h3 class="text-lg font-semibold text-default mb-2">
        {{ t("admin.users.emptyTitle") }}
      </h3>
      <p class="text-muted">
        {{ t("admin.users.empty") }}
      </p>
    </div>
  </UContainer>

  <UModal v-model:open="blockModalOpen" :title="t('admin.users.blockModal.title')">
    <template #body>
      <div class="space-y-4">
        <p class="text-sm text-gray-600 dark:text-gray-400">
          {{ t("admin.users.blockModal.description", { name: actionTarget ? displayName(actionTarget) : "" }) }}
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
        {{ t("admin.users.unblockModal.description", { name: actionTarget ? displayName(actionTarget) : "" }) }}
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
