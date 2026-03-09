import { Time } from '@internationalized/date';
import type { MilestoneInput } from '~/components/competition/form/MilestonesFormSection.vue';

export const useMilestones = (combineDateTimeFn: (date: any, time: any) => string) => {
  const milestones = ref<MilestoneInput[]>([]);

  const addMilestone = () => {
    milestones.value.push({ title: '', date: undefined, time: new Time(0, 0) });
  };

  const removeMilestone = (index: number) => {
    milestones.value.splice(index, 1);
  };

  const getMilestonesForSubmit = (): Array<{ title: string; timestamp: string }> => {
    return milestones.value
      .filter(m => m.title && m.date)
      .map(m => ({
        title: m.title,
        timestamp: combineDateTimeFn(m.date, m.time),
      })) as Array<{ title: string; timestamp: string }>;
  };

  return { milestones, addMilestone, removeMilestone, getMilestonesForSubmit };
};
