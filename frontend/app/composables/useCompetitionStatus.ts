import type { CompetitionModel } from '~/types/api';

/**
 * Composable для определения статуса соревнования
 */
export const useCompetitionStatus = () => {
  const { t } = useI18n();

  /**
   * Определяет статус регистрации на соревнование
   * @returns объект с label (текст статуса) и color (цвет бейджа)
   */
  const getRegistrationStatus = (competition: CompetitionModel) => {
    const now = new Date();
    const regStart = new Date(competition.schedule.registration_start);
    const regEnd = new Date(competition.schedule.registration_end);

    if (now < regStart) {
      return {
        label: t('competitions.status.notOpen'),
        color: 'warning' as const,
      };
    } else if (now >= regStart && now <= regEnd) {
      return {
        label: t('competitions.status.open'),
        color: 'success' as const,
      };
    } else {
      return {
        label: t('competitions.status.closed'),
        color: 'info' as const,
      };
    }
  };

  /**
   * Проверяет, архивировано ли соревнование
   */
  const isArchived = (competition: CompetitionModel) => {
    return competition.is_archived;
  };

  /**
   * Проверяет, является ли соревнование командным
   */
  const isTeamCompetition = (competition: CompetitionModel) => {
    return !(competition.team_size.min === 1 && competition.team_size.max === 1);
  };

  return {
    getRegistrationStatus,
    isArchived,
    isTeamCompetition,
  };
};
