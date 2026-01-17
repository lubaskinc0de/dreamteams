<script setup lang="ts">
import * as locales from '@nuxt/ui/locale';

interface Props {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
}

withDefaults(defineProps<Props>(), {
  size: 'md',
});

const { locale, setLocale } = useI18n();

// Available locales for LocaleSelect
const availableLocales = Object.values(locales).filter(l => ['en', 'ru'].includes(l.code));
</script>

<template>
  <ULocaleSelect
    :model-value="locale as string"
    :locales="availableLocales"
    :size="size"
    @update:model-value="(val: string) => setLocale(val as 'ru' | 'en')"
  />
</template>
