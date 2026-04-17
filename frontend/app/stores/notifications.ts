import { defineStore } from "pinia";

export interface AppNotification {
  id: string;
  title: string;
  description?: string;
  color: "success" | "error" | "warning";
  icon?: string;
  read: boolean;
  createdAt: Date;
}

export const useNotificationsStore = defineStore("notifications", {
  state: () => ({
    items: [] as AppNotification[],
  }),

  getters: {
    unreadCount: (state) => state.items.filter((n) => !n.read).length,
  },

  actions: {
    add(notification: Omit<AppNotification, "id" | "read" | "createdAt">) {
      this.items.unshift({
        ...notification,
        id: crypto.randomUUID(),
        read: true,
        createdAt: new Date(),
      });
      // Keep at most 50 notifications
      if (this.items.length > 50) {
        this.items = this.items.slice(0, 50);
      }
    },

    markAllRead() {
      this.items.forEach((n) => (n.read = true));
    },

    clear() {
      this.items = [];
    },
  },
});
