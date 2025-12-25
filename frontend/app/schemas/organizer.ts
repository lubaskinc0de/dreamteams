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

  const organizerRegistrationSchema = z.object({
    organizer_name: organizerNameSchema,
    phone_number: phoneSchema,
  });

  return {
    phoneSchema,
    organizerNameSchema,
    organizerRegistrationSchema,
  };
};

export type OrganizerRegistrationSchema = z.infer<
  ReturnType<typeof createOrganizerSchemas>["organizerRegistrationSchema"]
>;
