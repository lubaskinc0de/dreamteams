import { z } from "zod";

export const PHONE_REGEX = /^\+7\d{10}$/;

export const createOrganizerSchemas = (t: (key: string) => string) => {
  const phoneSchema = z
    .string()
    .regex(PHONE_REGEX, t("form.phoneNumber.invalid"));

  const organizerNameSchema = z
    .string()
    .min(1, t("form.organizerName.required"))
    .max(70, t("form.organizerName.maxLength"))
    .transform((val) => val.trim());

  const inviteCodeSchema = z
    .string()
    .min(1, t("form.inviteCode.required"));

  const contactEmailSchema = z
    .string()
    .min(1, t("form.contactEmail.required"))
    .email(t("form.contactEmail.invalid"));

  const organizerRegistrationSchema = z.object({
    organizer_name: organizerNameSchema,
    phone_number: phoneSchema,
    invite_code: inviteCodeSchema,
  });

  const organizerUpdateSchema = z.object({
    organizer_name: organizerNameSchema,
    contact_email: contactEmailSchema,
  });

  return {
    phoneSchema,
    organizerNameSchema,
    inviteCodeSchema,
    contactEmailSchema,
    organizerRegistrationSchema,
    organizerUpdateSchema,
  };
};

export type OrganizerRegistrationSchema = z.infer<
  ReturnType<typeof createOrganizerSchemas>["organizerRegistrationSchema"]
>;

export type OrganizerUpdateSchema = z.infer<
  ReturnType<typeof createOrganizerSchemas>["organizerUpdateSchema"]
>;
