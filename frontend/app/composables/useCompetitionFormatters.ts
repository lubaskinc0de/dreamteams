/**
 * Composable для форматирования данных соревнований
 * Централизует всю логику форматирования дат, диапазонов и статусов
 */
export const useCompetitionFormatters = () => {
  const { t } = useI18n();

  /**
   * Форматирует дату в локализованный формат
   */
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  /**
   * Форматирует время в локализованный формат
   */
  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  /**
   * Форматирует дату и время вместе
   */
  const formatDateTime = (dateString: string) => {
    return `${formatDate(dateString)} ${formatTime(dateString)}`;
  };

  /**
   * Форматирует диапазон дат словами
   * Например: "с 16 января 2026 г. 10:00 по 18 января 2026 г. 18:00"
   */
  const formatDateRange = (start: string, end: string) => {
    return `${t('competition.detail.dateRangeFrom')} ${formatDateTime(start)} ${t('competition.detail.dateRangeTo')} ${formatDateTime(end)}`;
  };

  /**
   * Форматирует числовой диапазон словами
   * Например: "от 20 до 100"
   */
  const formatNumericRange = (min: number, max: number) => {
    return `${t('competition.detail.rangeFrom')} ${min} ${t('competition.detail.rangeTo')} ${max}`;
  };

  /**
   * Форматирует размер команды
   * Если min=1 и max=1, возвращает "Индивидуальное"
   * Иначе возвращает диапазон: "от 2 до 5"
   */
  const formatTeamSize = (teamSize: { min: number; max: number }) => {
    if (teamSize.min === 1 && teamSize.max === 1) {
      return t('competitions.card.noTeams');
    }
    return formatNumericRange(teamSize.min, teamSize.max);
  };

  /**
   * Возвращает локализованное название домена
   */
  const getDomainLabel = (domain: string) => {
    return t(`competition.form.domains.options.${domain}`);
  };

  /**
   * Возвращает локализованное название формата проведения
   */
  const getFormatLabel = (format: string) => {
    return t(`competition.formats.${format}`);
  };

  /**
   * Возвращает локализованное название типа участников
   */
  const getParticipantTypeLabel = (type: string) => {
    return t(`competition.participantTypes.${type}`);
  };

  return {
    formatDate,
    formatTime,
    formatDateTime,
    formatDateRange,
    formatNumericRange,
    formatTeamSize,
    getDomainLabel,
    getFormatLabel,
    getParticipantTypeLabel,
  };
};
