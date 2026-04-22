import { useNotificationsStore } from '~/stores/notifications';

type FormErrorItem = { id?: string; message?: string; name?: string };

export const useFormErrorScroll = () => {
  const notifications = useNotificationsStore();
  const { t } = useI18n();

  const handleFormError = async (event: any) => {
    const errors: FormErrorItem[] = event?.errors || [];
    if (errors.length === 0) return;

    // Zod schemas already localise messages via t(), so errors[i].message is ready to show.
    const messages = errors
      .map((e) => (e.message ?? '').trim())
      .filter((m) => m.length > 0);

    const description = messages.length === 0
      ? t('competition.create.validation.scrollToErrors')
      : messages.length === 1
        ? messages[0]!
        : messages.map((m) => `• ${m}`).join('\n');

    notifications.add({
      title: t('competition.create.validation.errorsFound', { count: errors.length }),
      description,
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
