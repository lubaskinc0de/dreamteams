<script setup lang="ts">
const props = defineProps<{
  error: {
    statusCode: number;
    statusMessage: string;
    message?: string;
  };
}>();

const { t, locale } = useI18n();

const handleError = () => clearError({ redirect: '/' });

// Hardcoded fallbacks for when locale messages aren't loaded yet (SPA lazy loading)
type ErrorEntry = { title: string; desc: string };
const fallback: Record<string, Record<string, ErrorEntry>> = {
  ru: {
    '401': { title: 'Требуется авторизация', desc: 'Для доступа к этой странице необходимо войти в систему' },
    '404': { title: 'Страница не найдена', desc: 'Запрашиваемая страница не существует или была удалена' },
    '500': { title: 'Ошибка сервера', desc: 'Произошла внутренняя ошибка сервера. Попробуйте позже' },
    'default': { title: 'Произошла ошибка', desc: 'Что-то пошло не так. Пожалуйста, попробуйте снова' },
  },
  en: {
    '401': { title: 'Authorization Required', desc: 'You need to sign in to access this page' },
    '404': { title: 'Page Not Found', desc: 'The requested page does not exist or has been removed' },
    '500': { title: 'Server Error', desc: 'An internal server error occurred. Please try again later' },
    'default': { title: 'An Error Occurred', desc: 'Something went wrong. Please try again' },
  },
};

const safeT = (key: string, fallbackStr: string): string => {
  const result = t(key);
  return result !== key ? result : fallbackStr;
};

const localizedError = computed(() => {
  const lang = locale.value in fallback ? locale.value : 'en';
  const fb = fallback[lang]!;
  const code = String(props.error.statusCode);
  const entry: ErrorEntry = fb[code] ?? fb['default']!;

  const keyMap: Record<string, { title: string; desc: string }> = {
    '401': { title: 'errors.unauthorized.title', desc: 'errors.unauthorized.description' },
    '404': { title: 'errors.notFound.title', desc: 'errors.notFound.description' },
    '500': { title: 'errors.serverError.title', desc: 'errors.serverError.description' },
  };

  const keys = keyMap[code] ?? { title: 'errors.default.title', desc: 'errors.default.description' };

  return {
    statusCode: props.error.statusCode,
    statusMessage: safeT(keys.title, entry.title),
    message: safeT(keys.desc, entry.desc),
  };
});
</script>

<template>
  <UPage>
    <div class="min-h-screen flex items-center justify-center px-4">
      <UError :error="localizedError" :clear="{
        label: t('common.backToHome'),
      }">
      </UError>
    </div>
  </UPage>
</template>
