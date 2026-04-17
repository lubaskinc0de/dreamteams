<script setup lang="ts">
import { useInvitesStore } from "~/stores/invites";
import { useNotificationsStore } from "~/stores/notifications";

definePageMeta({ layout: "default" });

const { t } = useI18n();
const notifications = useNotificationsStore();
const invitesStore = useInvitesStore();

// Create invite modal state
const isCreateModalOpen = ref(false);
const displayName = ref("");
const issuedCode = ref<string | null>(null);

// Revoke confirm modal state
const isRevokeModalOpen = ref(false);
const revokeTargetId = ref<string | null>(null);
const revokeLoading = ref(false);

onMounted(async () => {
  await invitesStore.fetchInvites(1);
});

const openCreateModal = () => {
  displayName.value = "";
  issuedCode.value = null;
  invitesStore.clearIssuedInvite();
  invitesStore.clearError();
  isCreateModalOpen.value = true;
};

const handleCreateInvite = async () => {
  await invitesStore.issueInvite({
    display_name: displayName.value.trim() || null,
  });

  if (invitesStore.issuedInvite) {
    issuedCode.value = invitesStore.issuedInvite.code;
    notifications.add({
      title: t("toast.inviteCreated.title"),
      description: t("toast.inviteCreated.description"),
      color: "success",
      icon: "i-heroicons-check-circle",
    });
  }
};

const copyCode = async (code: string) => {
  try {
    await navigator.clipboard.writeText(code);
    notifications.add({
      title: t("admin.invites.codeCopied"),
      color: "success",
      icon: "i-heroicons-clipboard-document-check",
    });
  } catch {
    notifications.add({
      title: t("toast.inviteCopyFailed.title"),
      color: "error",
      icon: "i-heroicons-exclamation-triangle",
    });
  }
};

const openRevokeModal = (inviteId: string) => {
  revokeTargetId.value = inviteId;
  isRevokeModalOpen.value = true;
};

const handleRevoke = async () => {
  if (!revokeTargetId.value) return;

  revokeLoading.value = true;
  const success = await invitesStore.revokeInvite(revokeTargetId.value);
  revokeLoading.value = false;

  if (success) {
    notifications.add({
      title: t("toast.inviteRevoked.title"),
      color: "success",
      icon: "i-heroicons-check-circle",
    });
  } else if (invitesStore.error) {
    notifications.add({
      title: t("apiErrors." + invitesStore.error.code),
      color: "error",
      icon: "i-heroicons-exclamation-triangle",
    });
  }

  isRevokeModalOpen.value = false;
  revokeTargetId.value = null;
};

const handlePageChange = async (page: number) => {
  await invitesStore.fetchInvites(page);
};

const formatDate = (iso: string) => {
  return new Date(iso).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
};

const getStatusColor = (invite: { is_revoked: boolean; is_used: boolean }) => {
  if (invite.is_revoked) return "error";
  if (invite.is_used) return "neutral";
  return "success";
};

const getStatusLabel = (invite: { is_revoked: boolean; is_used: boolean }) => {
  if (invite.is_revoked) return t("admin.invites.status.revoked");
  if (invite.is_used) return t("admin.invites.status.used");
  return t("admin.invites.status.active");
};

const getStatusIcon = (invite: { is_revoked: boolean; is_used: boolean }) => {
  if (invite.is_revoked) return "i-heroicons-x-circle";
  if (invite.is_used) return "i-heroicons-user";
  return "i-heroicons-check-circle";
};

const totalPages = computed(() =>
  Math.max(1, Math.ceil(invitesStore.total / 20)),
);
</script>

<template>
  <UContainer class="py-8">
    <!-- Page header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
      <div>
        <h1 class="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-900 dark:text-gray-100">
          {{ t("admin.invites.title") }}
        </h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-2">
          {{ t("admin.invites.subtitle", { total: invitesStore.total }) }}
        </p>
      </div>
      <UButton
        icon="i-heroicons-plus"
        :label="t('admin.invites.createButton')"
        class="w-full sm:w-auto justify-center"
        @click="openCreateModal"
      />
    </div>

    <!-- Error alert -->
    <UAlert
      v-if="invitesStore.error && !invitesStore.loading"
      color="error"
      variant="soft"
      :title="t('apiErrors.' + invitesStore.error.code)"
      icon="i-heroicons-exclamation-circle"
      class="mb-4"
    />

    <!-- Retry button -->
    <UButton
      v-if="invitesStore.error && !invitesStore.loading"
      variant="soft"
      icon="i-heroicons-arrow-path"
      :label="t('common.retry')"
      @click="invitesStore.fetchInvites(invitesStore.page)"
      class="mb-4"
    />

    <!-- Loading skeleton -->
    <div v-if="invitesStore.loading" class="space-y-3">
      <USkeleton v-for="i in 5" :key="i" class="h-16 w-full rounded-lg" />
    </div>

    <!-- Invite list -->
    <div v-else-if="invitesStore.invites.length > 0" class="space-y-3">
      <UCard
        v-for="invite in invitesStore.invites"
        :key="invite.id"
        class="transition-all"
      >
        <div class="flex flex-col sm:flex-row sm:items-center gap-3">
          <!-- Status badge -->
          <UBadge :color="getStatusColor(invite)" variant="subtle" :icon="getStatusIcon(invite)" class="self-start sm:self-auto shrink-0 min-w-24 justify-center">
            {{ getStatusLabel(invite) }}
          </UBadge>

          <!-- Invite info -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <code class="text-sm sm:text-base font-mono bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded break-all max-w-full sm:max-w-xs"
                    :title="invite.code">
                {{ invite.code }}
              </code>
              <UButton
                icon="i-heroicons-clipboard-document"
                variant="ghost"
                size="xs"
                square
                :aria-label="t('admin.invites.copyButton')"
                :title="t('admin.invites.copyButton')"
                @click="copyCode(invite.code)"
              />
            </div>
            <div class="flex items-center gap-3 mt-1 flex-wrap">
              <span v-if="invite.display_name" class="text-base text-gray-600 dark:text-gray-400 font-medium">
                {{ invite.display_name }}
              </span>
              <span v-if="invite.used_by" class="text-sm text-gray-500 dark:text-gray-500 flex items-center gap-1">
                <UIcon name="i-heroicons-user" class="text-xs" />
                {{ invite.used_by.name }}
              </span>
              <span class="text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(invite.created_at) }}
              </span>
            </div>
          </div>

          <!-- Actions -->
          <UButton
            v-if="!invite.is_revoked && !invite.is_used"
            color="error"
            variant="soft"
            size="sm"
            icon="i-heroicons-x-circle"
            :label="t('admin.invites.revokeButton')"
            class="w-full sm:w-auto justify-center"
            @click="openRevokeModal(invite.id)"
          />
        </div>
      </UCard>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex justify-center pt-4">
        <UPagination
          :model-value="invitesStore.page"
          :total="invitesStore.total"
          :page-count="20"
          @update:model-value="handlePageChange"
        />
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="text-center py-16">
      <UIcon name="i-heroicons-ticket" class="text-5xl text-gray-400 dark:text-gray-600 mb-4" />
      <h3 class="text-lg font-semibold text-default mb-2">
        {{ t("admin.invites.emptyTitle") }}
      </h3>
      <p class="text-muted mb-6">
        {{ t("admin.invites.empty") }}
      </p>
      <UButton
        icon="i-heroicons-plus"
        :label="t('admin.invites.createButton')"
        @click="openCreateModal"
      />
    </div>
  </UContainer>

  <!-- Create invite modal -->
  <UModal v-model:open="isCreateModalOpen" :title="t('admin.invites.createModal.title')">
    <template #body>
      <div class="space-y-4">
        <!-- After creation: show the code -->
        <template v-if="issuedCode">
          <UAlert
            color="success"
            variant="soft"
            icon="i-heroicons-check-circle"
            :title="t('admin.invites.createModal.successTitle')"
          />
          <div class="space-y-2">
            <p class="text-sm text-gray-600 dark:text-gray-400">
              {{ t("admin.invites.createModal.shareHint") }}
            </p>
            <div class="flex items-center gap-2">
              <code class="flex-1 text-sm font-mono bg-gray-100 dark:bg-gray-800 px-3 py-2 rounded-lg break-all">
                {{ issuedCode }}
              </code>
              <UButton
                icon="i-heroicons-clipboard-document"
                variant="ghost"
                square
                :aria-label="t('admin.invites.copyButton')"
                :title="t('admin.invites.copyButton')"
                @click="copyCode(issuedCode)"
              />
            </div>
          </div>
        </template>

        <!-- Before creation: form -->
        <template v-else>
          <UAlert
            v-if="invitesStore.error"
            color="error"
            variant="soft"
            :title="t('apiErrors.' + invitesStore.error.code)"
            icon="i-heroicons-exclamation-circle"
          />
          <UFormField :label="t('admin.invites.createModal.displayName')">
            <UInput
              v-model="displayName"
              :placeholder="t('admin.invites.createModal.displayNamePlaceholder')"
              icon="i-heroicons-tag"
              class="w-full"
            />
            <p class="mt-3 text-sm text-gray-500 dark:text-gray-400">
              {{ t("admin.invites.createModal.displayNameHint") }}
            </p>
          </UFormField>
        </template>
      </div>
    </template>

    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton
          color="neutral"
          variant="ghost"
          :label="t('common.close')"
          @click="isCreateModalOpen = false"
        />
        <UButton
          v-if="!issuedCode"
          icon="i-heroicons-plus"
          :label="invitesStore.issuing ? t('common.creating') : t('admin.invites.createModal.submit')"
          :loading="invitesStore.issuing"
          :disabled="invitesStore.issuing"
          @click="handleCreateInvite"
        />
      </div>
    </template>
  </UModal>

  <!-- Revoke confirm modal -->
  <UModal v-model:open="isRevokeModalOpen" :title="t('admin.invites.revokeModal.title')">
    <template #body>
      <p class="text-gray-600 dark:text-gray-400">
        {{ t("admin.invites.revokeModal.description") }}
      </p>
    </template>

    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton
          color="neutral"
          variant="ghost"
          :label="t('common.cancel')"
          @click="isRevokeModalOpen = false"
        />
        <UButton
          color="error"
          icon="i-heroicons-x-circle"
          :label="t('admin.invites.revokeButton')"
          :loading="revokeLoading"
          :disabled="revokeLoading"
          @click="handleRevoke"
        />
      </div>
    </template>
  </UModal>
</template>
