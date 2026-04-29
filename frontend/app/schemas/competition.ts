import { z } from "zod";

export const createCompetitionSchemas = (t: (key: string) => string) => {
  const titleSchema = z
    .string()
    .min(1, t("competition.form.title.required"))
    .max(200, t("competition.form.title.maxLength"))
    .transform((val) => val.trim());

  const descriptionSchema = z
    .string();

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
    max: z
      .number()
      .min(1, t("competition.form.participantLimits.max.minValue")),
  });

  const tagIdsSchema = z
    .array(z.string().uuid(t("competition.form.tags.invalid")))
    .max(30, t("competition.form.tags.maxLength"))
    .default([]);

  const trackSchema = z.object({
    name: z
      .string()
      .transform((val) => val.trim())
      .pipe(
        z
          .string()
          .min(1, t("competition.form.tracks.required"))
          .max(100, t("competition.form.tracks.maxLength")),
      ),
  });

  const tracksSchema = z
    .array(trackSchema)
    .min(1, t("competition.form.tracks.required"))
    .superRefine((tracks, ctx) => {
      const normalized = tracks.map((track) => track.name.trim().toLowerCase());
      const seen = new Set<string>();
      for (const [index, name] of normalized.entries()) {
        if (seen.has(name)) {
          ctx.addIssue({
            code: z.ZodIssueCode.custom,
            message: t("competition.form.tracks.duplicate"),
            path: [index, "name"],
          });
        }
        seen.add(name);
      }
    });

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
      .max(50, t("competition.form.milestone.title.maxLength")),
    timestamp: z.string().min(1, t("competition.form.milestone.timestamp.required")),
    description: z
      .string()
      .max(300, t("competition.form.milestone.description.maxLength"))
      .nullable()
      .optional(),
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
    tag_ids: tagIdsSchema,
    tracks: tracksSchema,
    participant_type: z.enum(["schoolchild", "student", "any"]),
    venue: venueSchema,
    team_size: teamSizeSchema.nullable(),
    auto_accept: z.boolean(),
    milestones: z.array(milestoneSchema).optional(),
    is_team: z.boolean().optional(),
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
  ).superRefine((data, ctx) => {
    // Backend invariant: team_size is null ⇔ team_formation_start is null ⇔ team_formation_end is null.
    // Either all three exist (team competition) or all three are null (individual). A half-configured
    // state returns 400/INVALID_COMPETITION_DATA, so block it at the Zod layer.
    const hasTeamSize = data.team_size != null;
    const tfs = data.schedule.team_formation_start;
    const hasTeamFormation = tfs != null && tfs !== "";
    if (hasTeamSize !== hasTeamFormation) {
      const msg = t("errors.team_size_schedule_pairing");
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: msg, path: ["team_size"] });
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: msg, path: ["schedule", "team_formation_start"] });
    }
  });

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
      .max(50, t("competition.form.milestone.title.maxLength")),
    timestamp: z.string().min(1, t("competition.form.milestone.timestamp.required")),
    description: z
      .string()
      .max(300, t("competition.form.milestone.description.maxLength"))
      .nullable()
      .optional(),
  });

  const competitionGeneralInfoUpdateSchema = z.object({
    title: titleSchema,
    description: descriptionSchema,
    participant_limits: participantLimitsSchema,
    tag_ids: tagIdsSchema,
    tracks: tracksSchema,
    participant_type: z.enum(["schoolchild", "student", "any"]),
    venue: venueSchema,
    milestones: z.array(updateMilestoneSchema).nullable(),
    auto_accept: z.boolean(),
  });

  const competitionRescheduleSchema = z.object({
    schedule: updateScheduleSchema,
    team_size: teamSizeSchema.nullable(),
  }).superRefine((data, ctx) => {
    const hasTeamSize = data.team_size != null;
    const tfs = data.schedule.team_formation_start;
    const hasTeamFormation = tfs != null && tfs !== "";
    if (hasTeamSize !== hasTeamFormation) {
      const msg = t("errors.team_size_schedule_pairing");
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: msg, path: ["team_size"] });
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: msg, path: ["schedule", "team_formation_start"] });
    }
  });

  const competitionUpdateSchema = z.object({
    title: titleSchema,
    description: descriptionSchema,
    schedule: updateScheduleSchema,
    participant_limits: participantLimitsSchema,
    tag_ids: tagIdsSchema,
    tracks: tracksSchema,
    participant_type: z.enum(["schoolchild", "student", "any"]),
    venue: venueSchema,
    team_size: teamSizeSchema.nullable(),
    milestones: z.array(updateMilestoneSchema).optional(),
    auto_accept: z.boolean().optional(),
    is_archived: z.boolean().optional(),
  }).superRefine((data, ctx) => {
    // Mirror the create-form pairing invariant on update.
    const hasTeamSize = data.team_size != null;
    const tfs = data.schedule.team_formation_start;
    const hasTeamFormation = tfs != null && tfs !== "";
    if (hasTeamSize !== hasTeamFormation) {
      const msg = t("errors.team_size_schedule_pairing");
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: msg, path: ["team_size"] });
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: msg, path: ["schedule", "team_formation_start"] });
    }
  });

  return {
    titleSchema,
    descriptionSchema,
    scheduleSchema,
    participantLimitsSchema,
    tagIdsSchema,
    trackSchema,
    tracksSchema,
    teamSizeSchema,
    venueSchema,
    milestoneSchema,
    competitionFormSchema,
    competitionGeneralInfoUpdateSchema,
    competitionRescheduleSchema,
    competitionUpdateSchema,
  };
};

export type CompetitionFormSchema = z.infer<
  ReturnType<typeof createCompetitionSchemas>["competitionFormSchema"]
>;
