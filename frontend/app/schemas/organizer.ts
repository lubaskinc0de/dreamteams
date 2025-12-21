import { z } from "zod";
import { UI_TEXT } from "~/constants/ui-text";

/**
 * Reusable validation schemas for organizer-related forms
 * Centralizes validation logic for consistency and maintainability
 */

/**
 * Russian phone number validation regex
 * Format: +7XXXXXXXXXX (11 digits total)
 */
export const PHONE_REGEX = /^\+7\d{10}$/;

/**
 * Phone number schema
 * Can be reused across different forms
 */
export const phoneSchema = z
  .string()
  .regex(PHONE_REGEX, UI_TEXT.form.phoneNumber.invalid);

/**
 * Organizer name schema
 * Can be reused across different forms
 */
export const organizerNameSchema = z
  .string()
  .min(1, UI_TEXT.form.organizerName.required)
  .max(70, UI_TEXT.form.organizerName.maxLength)
  .transform((val) => val.trim());

/**
 * Complete organizer registration form schema
 */
export const organizerRegistrationSchema = z.object({
  organizer_name: organizerNameSchema,
  phone_number: phoneSchema,
});

/**
 * Type inference for the registration form
 */
export type OrganizerRegistrationSchema = z.infer<
  typeof organizerRegistrationSchema
>;

/**
 * Phone number formatting utility
 * Ensures phone number is in correct format
 */
export const formatPhoneNumber = (value: string): string => {
  // Remove all non-digit characters
  let digits = value.replace(/\D/g, "");

  // Ensure starts with 7
  if (!digits.startsWith("7")) {
    digits = "7" + digits;
  }

  // Limit to 11 digits (7 + 10)
  digits = digits.substring(0, 11);

  // Add + prefix
  return "+" + digits;
};

/**
 * Validate phone number format without throwing
 * Returns boolean instead of throwing error
 */
export const isValidPhoneNumber = (phone: string): boolean => {
  return PHONE_REGEX.test(phone);
};

/**
 * Validate organizer name without throwing
 * Returns boolean instead of throwing error
 */
export const isValidOrganizerName = (name: string): boolean => {
  const trimmed = name.trim();
  return trimmed.length >= 1 && trimmed.length <= 70;
};
