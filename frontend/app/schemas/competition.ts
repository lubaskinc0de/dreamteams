import { z } from "zod";

export const createCompetitionSchemas = (t: (key: string) => string) => {
  const titleSchema = z
    .string()
    .min(1, t("competition.form.title.required"))
    .max(200, t("competition.form.title.maxLength"))
    .transform((val) => val.trim());

  const descriptionSchema = z
    .string()
    .min(1, t("competition.form.description.required"));

  const scheduleSchema = z.object({
    registration_start: z.string().min(1, t("competition.form.schedule.registrationStart.required")),
    registration_end: z.string().min(1, t("competition.form.schedule.registrationEnd.required")),
    team_formation_start: z.string().nullable().optional(),
    team_formation_end: z.string().nullable().optional(),
  });

  const participantLimitsSchema = z.object({
    min: z
      .number()
      .min(1, t("competition.form.participantLimits.min.minValue")),
    max: z
      .number()
      .min(1, t("competition.form.participantLimits.max.minValue")),
  });

  const teamSizeSchema = z.object({
    min: z.number().min(1, t("competition.form.teamSize.min.minValue")),
    max: z.number().min(1, t("competition.form.teamSize.max.minValue")),
  });

  const venueSchema = z.object({
    format: z.enum(["online", "offline", "hybrid"]),
    location: z.string().nullable().optional(),
  });

  const milestoneSchema = z.object({
    title: z
      .string()
      .min(1, t("competition.form.milestone.title.required"))
      .max(50, t("competition.form.milestone.title.maxLength")),
    timestamp: z.string().min(1, t("competition.form.milestone.timestamp.required")),
  });

  const competitionFormSchema = z.object({
    title: titleSchema,
    description: descriptionSchema,
    schedule: scheduleSchema,
    participant_limits: participantLimitsSchema,
    domains: z.array(z.enum(["frontend", "mobile", "backend", "ai", "devops"])).min(1, t("competition.form.domains.required")),
    participant_type: z.enum(["schoolchild", "student", "any"]),
    venue: venueSchema,
    team_size: teamSizeSchema,
    milestones: z.array(milestoneSchema).optional(),
  });

  return {
    titleSchema,
    descriptionSchema,
    scheduleSchema,
    participantLimitsSchema,
    teamSizeSchema,
    venueSchema,
    milestoneSchema,
    competitionFormSchema,
  };
};

export type CompetitionFormSchema = z.infer<
  ReturnType<typeof createCompetitionSchemas>["competitionFormSchema"]
>;
