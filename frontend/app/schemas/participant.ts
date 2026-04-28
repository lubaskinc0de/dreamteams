import { z } from "zod";

export const createParticipantSchemas = (t: (key: string) => string) => {
  const fullNameSchema = z
    .string()
    .min(1, t("form.fullName.required"))
    .max(70, t("form.fullName.maxLength"))
    .transform((val) => val.trim());

  const bioSchema = z
    .string()
    .max(500, t("form.bio.maxLength"));

  const skillLevelSchema = z.enum(
    ["BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT"] as const,
    { message: t("form.skills.levelRequired") },
  );

  const skillSchema = z.object({
    name: z
      .string()
      .min(1, t("form.skills.nameRequired"))
      .max(70, t("form.skills.nameMaxLength")),
    level: skillLevelSchema,
  });

  const contactValueSchema = z
    .string()
    .min(1, t("form.contacts.valueRequired"))
    .max(2083, t("form.contacts.valueMaxLength"));

  const contactSchema = z.object({
    title: z
      .string()
      .min(1, t("form.contacts.titleRequired"))
      .max(70, t("form.contacts.titleMaxLength")),
    value: contactValueSchema,
  });

  const experienceLevelSchema = z.enum(
    ["JUNIOR", "MID", "SENIOR"] as const,
    { message: t("form.experienceLevel.required") },
  );

  const participantTypeSchema = z.enum(
    ["schoolchild", "student"] as const,
    { message: t("form.participantType.required") },
  );

  const ageSchema = z
    .number({ message: t("form.age.required") })
    .int()
    .positive(t("form.age.positive"));

  const privacyConsentSchema = z
    .boolean()
    .refine((val) => val === true, {
      message: t("form.privacyConsent.required"),
    });

  const termsConsentSchema = z
    .boolean()
    .refine((val) => val === true, {
      message: t("form.termsConsent.required"),
    });

  const participantRegistrationSchema = z.object({
    full_name: fullNameSchema,
    participant_type: participantTypeSchema,
    age: ageSchema,
    bio: bioSchema.nullable().optional(),
    experience_level: experienceLevelSchema.nullable().optional(),
    skills: z.array(skillSchema).optional(),
    contacts: z.array(contactSchema).max(15, t("form.contacts.maxItems")).optional(),
    privacy_consent: privacyConsentSchema,
    terms_consent: termsConsentSchema,
  });

  const participantUpdateSchema = z.object({
    full_name: fullNameSchema,
    participant_type: participantTypeSchema,
    age: ageSchema,
    bio: bioSchema.nullable().optional(),
    experience_level: experienceLevelSchema.nullable().optional(),
    skills: z.array(skillSchema).optional(),
    contacts: z.array(contactSchema).max(15, t("form.contacts.maxItems")).optional(),
  });

  return {
    fullNameSchema,
    bioSchema,
    skillLevelSchema,
    skillSchema,
    contactSchema,
    experienceLevelSchema,
    participantTypeSchema,
    ageSchema,
    privacyConsentSchema,
    termsConsentSchema,
    participantRegistrationSchema,
    participantUpdateSchema,
  };
};

export type ParticipantRegistrationSchema = z.infer<
  ReturnType<typeof createParticipantSchemas>["participantRegistrationSchema"]
>;

export type ParticipantUpdateSchema = z.infer<
  ReturnType<typeof createParticipantSchemas>["participantUpdateSchema"]
>;
