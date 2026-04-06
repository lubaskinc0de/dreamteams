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
  }).refine(
    (data) => {
      // registration_start must not be in the past
      if (data.registration_start) {
        return new Date(data.registration_start) >= new Date();
      }
      return true;
    },
    {
      message: t("competition.form.schedule.validation.dateInPast"),
      path: ["registration_start"],
    }
  ).refine(
    (data) => {
      // registration_end must not be in the past
      if (data.registration_end) {
        return new Date(data.registration_end) >= new Date();
      }
      return true;
    },
    {
      message: t("competition.form.schedule.validation.dateInPast"),
      path: ["registration_end"],
    }
  ).refine(
    (data) => {
      // registration_start must be before registration_end
      if (data.registration_start && data.registration_end) {
        return new Date(data.registration_start) < new Date(data.registration_end);
      }
      return true;
    },
    {
      message: t("competition.form.schedule.validation.registrationEndAfterStart"),
      path: ["registration_end"],
    }
  ).refine(
    (data) => {
      // If team formation is specified, both start and end must be provided
      const hasStart = data.team_formation_start !== null && data.team_formation_start !== undefined && data.team_formation_start !== '';
      const hasEnd = data.team_formation_end !== null && data.team_formation_end !== undefined && data.team_formation_end !== '';

      if (hasStart || hasEnd) {
        return hasStart && hasEnd;
      }
      return true;
    },
    {
      message: t("competition.form.schedule.validation.teamFormationBothRequired"),
      path: ["team_formation_end"],
    }
  ).refine(
    (data) => {
      // team_formation_start must not be in the past
      if (data.team_formation_start) {
        return new Date(data.team_formation_start) >= new Date();
      }
      return true;
    },
    {
      message: t("competition.form.schedule.validation.dateInPast"),
      path: ["team_formation_start"],
    }
  ).refine(
    (data) => {
      // team_formation_end must not be in the past
      if (data.team_formation_end) {
        return new Date(data.team_formation_end) >= new Date();
      }
      return true;
    },
    {
      message: t("competition.form.schedule.validation.dateInPast"),
      path: ["team_formation_end"],
    }
  ).refine(
    (data) => {
      // team_formation_start must be >= registration_end
      if (data.team_formation_start && data.registration_end) {
        return new Date(data.team_formation_start) >= new Date(data.registration_end);
      }
      return true;
    },
    {
      message: t("competition.form.schedule.validation.teamFormationAfterRegistration"),
      path: ["team_formation_start"],
    }
  ).refine(
    (data) => {
      // team_formation_end must be > team_formation_start
      if (data.team_formation_start && data.team_formation_end) {
        return new Date(data.team_formation_end) > new Date(data.team_formation_start);
      }
      return true;
    },
    {
      message: t("competition.form.schedule.validation.teamFormationEndAfterStart"),
      path: ["team_formation_end"],
    }
  );

  const participantLimitsSchema = z.object({
    min: z
      .number()
      .min(1, t("competition.form.participantLimits.min.minValue")),
    max: z
      .number()
      .min(1, t("competition.form.participantLimits.max.minValue")),
  }).refine(
    (data) => data.min <= data.max,
    {
      message: t("competition.form.participantLimits.validation.minLessThanMax"),
      path: ["max"],
    }
  );

  const teamSizeSchema = z.object({
    min: z.number().min(1, t("competition.form.teamSize.min.minValue")),
    max: z.number().min(1, t("competition.form.teamSize.max.minValue")),
  }).refine(
    (data) => data.min <= data.max,
    {
      message: t("competition.form.teamSize.validation.minLessThanMax"),
      path: ["max"],
    }
  );

  const venueSchema = z.object({
    format: z.enum(["online", "offline", "hybrid"]),
    location: z.string().nullable().optional(),
  }).refine(
    (data) => {
      // Location is required for offline and hybrid formats
      if (data.format === 'offline' || data.format === 'hybrid') {
        return data.location !== null && data.location !== undefined && data.location.trim() !== '';
      }
      return true;
    },
    {
      message: t("competition.form.venue.validation.locationRequired"),
      path: ["location"],
    }
  );

  const milestoneSchema = z.object({
    title: z
      .string()
      .min(1, t("competition.form.milestone.title.required"))
      .max(50, t("competition.form.milestone.title.maxLength")),
    timestamp: z.string().min(1, t("competition.form.milestone.timestamp.required")),
  }).refine(
    (data) => {
      // timestamp must not be in the past
      if (data.timestamp) {
        return new Date(data.timestamp) >= new Date();
      }
      return true;
    },
    {
      message: t("competition.form.milestone.validation.dateInPast"),
      path: ["timestamp"],
    }
  );

  const competitionFormSchema = z.object({
    title: titleSchema,
    description: descriptionSchema,
    schedule: scheduleSchema,
    participant_limits: participantLimitsSchema,
    domains: z.array(z.enum(["frontend", "mobile", "backend", "ai", "devops"])).min(1, t("competition.form.domains.required")),
    participant_type: z.enum(["schoolchild", "student", "any"]),
    venue: venueSchema,
    team_size: teamSizeSchema,
    auto_accept: z.boolean(),
    milestones: z.array(milestoneSchema).optional(),
    is_team: z.boolean(),
  }).refine(
    (data) => {
      // Check that milestone timestamps are unique
      if (data.milestones && data.milestones.length > 0) {
        const timestamps = data.milestones.map(m => m.timestamp);
        const uniqueTimestamps = new Set(timestamps);
        return timestamps.length === uniqueTimestamps.size;
      }
      return true;
    },
    {
      message: t("competition.form.milestone.validation.duplicateTimestamp"),
      path: ["milestones"],
    }
  ).refine(
    (data) => {
      // If is_team is true, team_size must be valid (min <= max and min >= 2)
      if (data.is_team) {
        return data.team_size.min >= 1 && data.team_size.min <= data.team_size.max;
      }
      return true;
    },
    {
      message: t("competition.form.teamSize.validation.minLessThanMax"),
      path: ["team_size"],
    }
  ).refine(
    (data) => {
      // If is_team is true, team formation period is required
      if (data.is_team) {
        const hasStart = data.schedule.team_formation_start !== null && data.schedule.team_formation_start !== undefined && data.schedule.team_formation_start !== '';
        const hasEnd = data.schedule.team_formation_end !== null && data.schedule.team_formation_end !== undefined && data.schedule.team_formation_end !== '';
        return hasStart && hasEnd;
      }
      return true;
    },
    {
      message: t("competition.form.schedule.validation.teamFormationRequired"),
      path: ["schedule.team_formation_start"],
    }
  );

  // Update schema - no "date in past" validation, uses is_archived instead of is_team
  const updateScheduleSchema = z.object({
    registration_start: z.string().min(1, t("competition.form.schedule.registrationStart.required")),
    registration_end: z.string().min(1, t("competition.form.schedule.registrationEnd.required")),
    team_formation_start: z.string().nullable().optional(),
    team_formation_end: z.string().nullable().optional(),
  }).refine(
    (data) => {
      // registration_start must be before registration_end
      if (data.registration_start && data.registration_end) {
        return new Date(data.registration_start) < new Date(data.registration_end);
      }
      return true;
    },
    {
      message: t("competition.form.schedule.validation.registrationEndAfterStart"),
      path: ["registration_end"],
    }
  ).refine(
    (data) => {
      // If team formation is specified, both start and end must be provided
      const hasStart = data.team_formation_start !== null && data.team_formation_start !== undefined && data.team_formation_start !== '';
      const hasEnd = data.team_formation_end !== null && data.team_formation_end !== undefined && data.team_formation_end !== '';

      if (hasStart || hasEnd) {
        return hasStart && hasEnd;
      }
      return true;
    },
    {
      message: t("competition.form.schedule.validation.teamFormationBothRequired"),
      path: ["team_formation_end"],
    }
  ).refine(
    (data) => {
      // team_formation_start must be >= registration_end
      if (data.team_formation_start && data.registration_end) {
        return new Date(data.team_formation_start) >= new Date(data.registration_end);
      }
      return true;
    },
    {
      message: t("competition.form.schedule.validation.teamFormationAfterRegistration"),
      path: ["team_formation_start"],
    }
  ).refine(
    (data) => {
      // team_formation_end must be > team_formation_start
      if (data.team_formation_start && data.team_formation_end) {
        return new Date(data.team_formation_end) > new Date(data.team_formation_start);
      }
      return true;
    },
    {
      message: t("competition.form.schedule.validation.teamFormationEndAfterStart"),
      path: ["team_formation_end"],
    }
  );

  const updateMilestoneSchema = z.object({
    title: z
      .string()
      .min(1, t("competition.form.milestone.title.required"))
      .max(50, t("competition.form.milestone.title.maxLength")),
    timestamp: z.string().min(1, t("competition.form.milestone.timestamp.required")),
  });

  const competitionUpdateSchema = z.object({
    title: titleSchema,
    description: descriptionSchema,
    schedule: updateScheduleSchema,
    participant_limits: participantLimitsSchema,
    domains: z.array(z.enum(["frontend", "mobile", "backend", "ai", "devops"])).min(1, t("competition.form.domains.required")),
    participant_type: z.enum(["schoolchild", "student", "any"]),
    venue: venueSchema,
    team_size: teamSizeSchema,
    milestones: z.array(updateMilestoneSchema).optional(),
    auto_accept: z.boolean().optional(),
    is_archived: z.boolean().optional(),
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
    competitionUpdateSchema,
  };
};

export type CompetitionFormSchema = z.infer<
  ReturnType<typeof createCompetitionSchemas>["competitionFormSchema"]
>;
