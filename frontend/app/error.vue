<script setup lang="ts">
const props = defineProps<{
  error: {
    statusCode: number;
    statusMessage: string;
    message?: string;
  };
}>();

const { t } = useI18n();

const handleError = () => clearError({ redirect: '/' });

// Create localized error object
const localizedError = computed(() => {
  let statusMessage = '';
  let message = '';

  switch (props.error.statusCode) {
    case 401:
      statusMessage = t('errors.unauthorized.title');
      message = t('errors.unauthorized.description');
      break;
    case 404:
      statusMessage = t('errors.notFound.title');
      message = t('errors.notFound.description');
      break;
    case 500:
      statusMessage = t('errors.serverError.title');
      message = t('errors.serverError.description');
      break;
    default:
      statusMessage = t('errors.default.title');
      message = t('errors.default.description');
      break;
  }

  return {
    statusCode: props.error.statusCode,
    statusMessage,
    message,
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
