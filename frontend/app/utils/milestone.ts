import type { Milestone, MilestoneDescription } from "~/types/api";

/**
 * Unwrap the backend's MilestoneDescription VO (`{value: string}`) to a plain
 * nullable string for display/editing. Handles null and (defensively) raw
 * strings in case the wire shape ever changes.
 */
export const extractMilestoneDescription = (
  desc: Milestone["description"] | string | null | undefined,
): string | null => {
  if (desc == null) return null;
  if (typeof desc === "string") return desc;
  return (desc as MilestoneDescription).value ?? null;
};
