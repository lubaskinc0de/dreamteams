<script setup lang="ts">
const { t } = useI18n();

/**
 * Theme toggle component
 * Allows users to switch between light and dark color modes
 * Uses Nuxt UI's useColorMode composable for reactive theme switching
 */
const colorMode = useColorMode();

const isDark = computed(() => colorMode.value === "dark");
const icon = computed(() =>
  isDark.value ? "i-heroicons-moon" : "i-heroicons-sun",
);
const label = computed(() =>
  isDark.value ? t("theme.dark") : t("theme.light"),
);

const toggleColorMode = () => {
  colorMode.preference = colorMode.value === "dark" ? "light" : "dark";
};

// Optional: Accept custom button props
interface Props {
  variant?: "solid" | "outline" | "soft" | "ghost" | "link";
  color?:
    | "primary"
    | "secondary"
    | "success"
    | "info"
    | "warning"
    | "error"
    | "neutral";
  size?: "xs" | "sm" | "md" | "lg" | "xl";
  showLabel?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  variant: "ghost",
  color: "neutral",
  size: "md",
  showLabel: false,
});
</script>

<template>
  <UButton
    :icon="icon"
    :variant="props.variant"
    :color="props.color"
    :size="props.size"
    :aria-label="t('theme.toggle')"
    @click="toggleColorMode"
  >
    <template v-if="props.showLabel">
      {{ label }}
    </template>
  </UButton>
</template>
