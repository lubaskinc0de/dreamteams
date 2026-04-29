<script setup lang="ts">
import { useInfiniteScroll } from "@vueuse/core";
import { useAdminTagsStore } from "~/stores/adminTags";
import { useNotificationsStore } from "~/stores/notifications";
import type { CompetitionTag } from "~/types/api";

definePageMeta({ layout: "default" });

const { t } = useI18n();
const store = useAdminTagsStore();
const notifications = useNotificationsStore();

const adminNavItems = computed(() => [
  { label: t("admin.users.nav"), icon: "i-heroicons-users", to: "/admin/users" },
  { label: t("admin.invites.nav"), icon: "i-heroicons-ticket", to: "/admin/invites" },
  { label: t("admin.tags.nav"), icon: "i-heroicons-tag", to: "/admin/tags" },
]);

const createModalOpen = ref(false);
const deleteModalOpen = ref(false);
const tagValue = ref("");
const deleteTarget = ref<CompetitionTag | null>(null);

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
  await store.fetchTags(1);
  useInfiniteScroll(
    window,
    () => store.loadNextPage(),
    {
      distance: 400,
      canLoadMore: () => store.hasMore && !store.loading && !store.loadingMore,
    },
  );
});

onBeforeUnmount(() => {
  if (searchTimer) clearTimeout(searchTimer);
});

useHead({ title: t("admin.tags.title") });

const openCreateModal = () => {
  tagValue.value = "";
  store.clearError();
  createModalOpen.value = true;
};

const handleCreate = async () => {
  const success = await store.createTag({ value: tagValue.value });
  if (success) {
    notifications.add({
      title: t("toast.tagCreated.title"),
      description: t("toast.tagCreated.description"),
      color: "success",
      icon: "i-heroicons-check-circle",
    });
    createModalOpen.value = false;
  } else if (store.error) {
    notifications.add({
      title: t("apiErrors." + store.error.code),
      color: "error",
      icon: "i-heroicons-exclamation-triangle",
    });
  }
};

const openDeleteModal = (tag: CompetitionTag) => {
  deleteTarget.value = tag;
  store.clearError();
  deleteModalOpen.value = true;
};

const handleDelete = async () => {
  if (!deleteTarget.value) return;

  const success = await store.deleteTag(deleteTarget.value.id);
  if (success) {
    notifications.add({
      title: t("toast.tagDeleted.title"),
      description: t("toast.tagDeleted.description"),
      color: "success",
      icon: "i-heroicons-check-circle",
    });
    deleteModalOpen.value = false;
    deleteTarget.value = null;
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
    <div class="flex flex-col gap-4 mb-8">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 class="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-900 dark:text-gray-100">
            {{ t("admin.tags.title") }}
          </h1>
          <p class="text-sm text-gray-500 dark:text-gray-400 mt-2">
            {{ t("admin.tags.subtitle", { total: store.total }) }}
          </p>
        </div>
        <UButton
          icon="i-heroicons-plus"
          :label="t('admin.tags.createButton')"
          class="w-full sm:w-auto justify-center"
          @click="openCreateModal"
        />
      </div>
      <UNavigationMenu :items="adminNavItems" variant="pill" class="w-full sm:w-auto" />
      <UInput
        v-model="store.search"
        icon="i-heroicons-magnifying-glass"
        :placeholder="t('admin.tags.searchPlaceholder')"
        class="w-full"
      />
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
      @click="store.fetchTags(1)"
      class="mb-4"
    />

    <div v-if="store.loading && store.tags.length === 0" class="space-y-3">
      <USkeleton v-for="i in 6" :key="i" class="h-16 w-full rounded-lg" />
    </div>

    <div v-else-if="store.tags.length > 0" class="space-y-3">
      <UCard v-for="tag in store.tags" :key="tag.id">
        <div class="flex flex-col sm:flex-row sm:items-center gap-3">
          <UBadge variant="soft" color="primary" icon="i-heroicons-tag" class="self-start">
            {{ tag.value }}
          </UBadge>
          <code class="flex-1 text-xs text-gray-500 dark:text-gray-400 break-all">
            {{ tag.id }}
          </code>
          <UButton
            color="error"
            variant="soft"
            size="sm"
            icon="i-heroicons-trash"
            :label="t('admin.tags.deleteButton')"
            class="w-full sm:w-auto justify-center"
            @click="openDeleteModal(tag)"
          />
        </div>
      </UCard>

      <div v-if="store.loadingMore" class="flex justify-center py-6">
        <UProgress indeterminate size="xs" class="w-48" />
      </div>
    </div>

    <div v-else class="text-center py-16">
      <UIcon name="i-heroicons-tag" class="text-5xl text-gray-400 dark:text-gray-600 mb-4" />
      <h3 class="text-lg font-semibold text-default mb-2">
        {{ t("admin.tags.emptyTitle") }}
      </h3>
      <p class="text-muted mb-6">
        {{ t("admin.tags.empty") }}
      </p>
      <UButton
        icon="i-heroicons-plus"
        :label="t('admin.tags.createButton')"
        @click="openCreateModal"
      />
    </div>
  </UContainer>

  <UModal v-model:open="createModalOpen" :title="t('admin.tags.createModal.title')">
    <template #body>
      <div class="space-y-4">
        <UAlert
          v-if="store.error"
          color="error"
          variant="soft"
          :title="t('apiErrors.' + store.error.code)"
          icon="i-heroicons-exclamation-circle"
        />
        <UFormField :label="t('admin.tags.createModal.value')" required>
          <UInput
            v-model="tagValue"
            :placeholder="t('admin.tags.createModal.placeholder')"
            icon="i-heroicons-tag"
            :maxlength="100"
            class="w-full"
            @keydown.enter.prevent="handleCreate"
          />
        </UFormField>
      </div>
    </template>

    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton
          color="neutral"
          variant="ghost"
          :label="t('common.cancel')"
          @click="createModalOpen = false"
        />
        <UButton
          icon="i-heroicons-plus"
          :label="store.creating ? t('common.creating') : t('admin.tags.createModal.submit')"
          :loading="store.creating"
          :disabled="store.creating || !tagValue.trim()"
          @click="handleCreate"
        />
      </div>
    </template>
  </UModal>

  <UModal v-model:open="deleteModalOpen" :title="t('admin.tags.deleteModal.title')">
    <template #body>
      <p class="text-gray-600 dark:text-gray-400">
        {{ t("admin.tags.deleteModal.description", { value: deleteTarget?.value }) }}
      </p>
    </template>

    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton
          color="neutral"
          variant="ghost"
          :label="t('common.cancel')"
          @click="deleteModalOpen = false"
        />
        <UButton
          color="error"
          icon="i-heroicons-trash"
          :label="t('admin.tags.deleteButton')"
          :loading="store.deleting"
          :disabled="store.deleting"
          @click="handleDelete"
        />
      </div>
    </template>
  </UModal>
</template>
