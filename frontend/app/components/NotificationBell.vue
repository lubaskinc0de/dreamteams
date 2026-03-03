<script setup lang="ts">
import { useNotificationsStore } from "~/stores/notifications";

const { t } = useI18n();
const store = useNotificationsStore();

const formatTime = (date: Date): string => {
  const diff = Date.now() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return t("notifications.justNow");
  if (minutes < 60) return t("notifications.minutesAgo", { n: minutes });
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return t("notifications.hoursAgo", { n: hours });
  return date.toLocaleDateString();
};

const colorClass = (color: string) => ({
  "text-success-500 dark:text-success-400": color === "success",
  "text-error-500 dark:text-error-400": color === "error",
  "text-warning-500 dark:text-warning-400": color === "warning",
});
</script>

<template>
  <UPopover @update:open="(v) => v && store.markAllRead()">
    <div class="relative">
      <UButton
        color="neutral"
        variant="ghost"
        size="md"
        icon="i-heroicons-bell"
        square
        :aria-label="t('notifications.title')"
      />
      <span
        v-if="store.unreadCount > 0"
        class="pointer-events-none absolute -top-1 -right-1 min-w-4 h-4 px-1 bg-red-500 rounded-full flex items-center justify-center text-white text-[10px] font-bold leading-none"
      >
        {{ store.unreadCount > 9 ? "9+" : store.unreadCount }}
      </span>
    </div>

    <template #content>
      <div class="w-80">
        <!-- Header -->
        <div class="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700">
          <span class="text-sm font-semibold text-gray-900 dark:text-gray-100">
            {{ t("notifications.title") }}
          </span>
          <UButton
            v-if="store.items.length > 0"
            size="xs"
            variant="ghost"
            color="neutral"
            :label="t('notifications.clearAll')"
            @click="store.clear()"
          />
        </div>

        <!-- Empty state -->
        <div v-if="store.items.length === 0" class="px-4 py-8 text-center">
          <UIcon name="i-heroicons-bell-slash" class="text-3xl text-gray-300 dark:text-gray-600 mb-2" />
          <p class="text-sm text-gray-500 dark:text-gray-400">{{ t("notifications.empty") }}</p>
        </div>

        <!-- Notification list -->
        <div v-else class="max-h-80 overflow-y-auto divide-y divide-gray-100 dark:divide-gray-800">
          <div
            v-for="n in store.items"
            :key="n.id"
            class="flex gap-3 px-4 py-3 transition-colors"
            :class="n.read ? 'opacity-55' : 'bg-gray-50/50 dark:bg-gray-800/30'"
          >
            <UIcon
              :name="n.icon || 'i-heroicons-bell'"
              class="mt-0.5 shrink-0 text-lg"
              :class="colorClass(n.color)"
            />
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 dark:text-gray-100 leading-snug">
                {{ n.title }}
              </p>
              <p v-if="n.description" class="text-xs text-gray-500 dark:text-gray-400 mt-0.5 leading-snug">
                {{ n.description }}
              </p>
              <p class="text-xs text-gray-400 dark:text-gray-600 mt-1">
                {{ formatTime(n.createdAt) }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </template>
  </UPopover>
</template>
