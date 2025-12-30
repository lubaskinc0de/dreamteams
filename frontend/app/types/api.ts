export interface ApiError {
  code: string;
  message: string;
  meta: Record<string, any> | null;
}

export interface OrganizerForm {
  organizer_name: string;
  phone_number: string;
}

export interface CreatedOrganizer {
  organizer_id: string;
  user_id: string;
}

export interface OrganizerModel {
  id: string;
  user_id: string;
  organizer_name: string;
  phone_number: string;
  contact_email: string;
  logo: string | null;
}

export interface ProfileModel {
  user_id: string;
  organizer: OrganizerModel | null;
}

export type ErrorCode =
  | "VALIDATION_ERROR"
  | "UNAUTHORIZED"
  | "AUTH_USER_ALREADY_EXISTS"
  | "ORGANIZER_ALREADY_EXISTS"
  | "USER_NOT_FOUND"
  | "USER_HAS_NO_ROLE"
  | "ACCESS_DENIED"
  | "INTERNAL_SERVER_ERROR";
