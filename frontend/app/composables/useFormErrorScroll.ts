import { useNotificationsStore } from '~/stores/notifications';

export const useFormErrorScroll = () => {
  const notifications = useNotificationsStore();
  const { t } = useI18n();

  const handleFormError = async (event: any) => {
    const errors: Array<{ id?: string }> = event.errors || [];
    if (errors.length === 0) return;

    notifications.add({
      title: t('competition.create.validation.errorsFound', { count: errors.length }),
      description: t('competition.create.validation.scrollToErrors'),
      icon: 'i-heroicons-exclamation-circle',
      color: 'error',
    });

    await nextTick();
    const firstId = errors[0]?.id;
    if (firstId) {
      const el = document.getElementById(firstId);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        el.focus();
      }
    }
  };

  return { handleFormError };
};
