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

  const contactUrlSchema = z
    .string()
    .min(1, t("form.contacts.urlRequired"))
    .max(2083, t("form.contacts.urlMaxLength"))
    .url(t("form.contacts.invalidUrl"));

  const contactSchema = z.object({
    title: z
      .string()
      .min(1, t("form.contacts.titleRequired"))
      .max(70, t("form.contacts.titleMaxLength")),
    url: contactUrlSchema,
  });

  const experienceLevelSchema = z.enum(
    ["JUNIOR", "MID", "SENIOR"] as const,
    { message: t("form.experienceLevel.required") },
  );

  const participantRegistrationSchema = z.object({
    full_name: fullNameSchema,
    bio: bioSchema,
    experience_level: experienceLevelSchema,
    preferred_domains: z
      .array(z.enum(["frontend", "mobile", "backend", "ai", "devops"] as const))
      .min(1, t("form.preferredDomains.required")),
    skills: z
      .array(skillSchema)
      .min(1, t("form.skills.minRequired")),
    contacts: z.array(contactSchema),
  });

  return {
    fullNameSchema,
    bioSchema,
    skillLevelSchema,
    skillSchema,
    contactSchema,
    experienceLevelSchema,
    participantRegistrationSchema,
  };
};

export type ParticipantRegistrationSchema = z.infer<
  ReturnType<typeof createParticipantSchemas>["participantRegistrationSchema"]
>;
