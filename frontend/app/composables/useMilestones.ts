import { Time } from '@internationalized/date';
import type { MilestoneInput } from '~/components/competition/form/MilestonesFormSection.vue';

export const useMilestones = (combineDateTimeFn: (date: any, time: any) => string) => {
  const milestones = ref<MilestoneInput[]>([]);

  const addMilestone = () => {
    milestones.value.push({ title: '', date: undefined, time: new Time(0, 0), description: null });
  };

  const removeMilestone = (index: number) => {
    milestones.value.splice(index, 1);
  };

  const getMilestonesForSubmit = (): Array<{ title: string; timestamp: string; description: string | null }> => {
    return milestones.value
      .filter(m => m.title && m.date)
      .map(m => ({
        title: m.title,
        timestamp: combineDateTimeFn(m.date, m.time),
        description: m.description && m.description.trim().length > 0 ? m.description : null,
      }));
  };

  return { milestones, addMilestone, removeMilestone, getMilestonesForSubmit };
};
