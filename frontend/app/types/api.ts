export interface ApiError {
  code: string;
  message: string;
  meta: Record<string, any> | null;
}

export interface OrganizerForm {
  organizer_name: string;
  phone_number: string;
  invite_code: string;
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
  participant: ParticipantProfile | null;
  avatar_url: string | null;
  is_admin: boolean;
}

export interface InviteForm {
  display_name: string | null;
}

export interface CreatedInvite {
  invite_id: string;
  code: string;
}

export interface InviteUsedBy {
  id: string;
  name: string;
  avatar_url: string | null;
}

export interface InviteModel {
  id: string;
  code: string;
  display_name: string | null;
  created_by: string;
  is_revoked: boolean;
  is_used: boolean;
  used_by: InviteUsedBy | null;
  created_at: string;
}

export interface InvitesList {
  items: InviteModel[];
  total: number;
  page: number;
}

export type ErrorCode =
  | "VALIDATION_ERROR"
  | "UNAUTHORIZED"
  | "AUTH_USER_ALREADY_EXISTS"
  | "ORGANIZER_ALREADY_EXISTS"
  | "USER_NOT_FOUND"
  | "USER_HAS_NO_ROLE"
  | "ACCESS_DENIED"
  | "INTERNAL_SERVER_ERROR"
  | "INVALID_AVATAR_ERROR"
  | "INVITE_NOT_FOUND"
  | "INVITE_ALREADY_REVOKED"
  | "INVITE_ALREADY_USED"
  | "INVITE_REVOKED"
  | "INVALID_SUPERUSER_PASSWORD"
  | "PARTICIPANT_ALREADY_EXISTS"
  | "COMPETITION_NOT_FOUND"
  | "APPLICATION_FORM_ALREADY_EXISTS"
  | "APPLICATION_FORM_NOT_FOUND"
  | "INVALID_APPLICATION_FORM_DATA"
  | "APPLICATION_NOT_FOUND"
  | "APPLICATION_ALREADY_EXISTS"
  | "APPLICATION_ALREADY_RESOLVED"
  | "INVALID_APPLICATION_DATA";

export interface CreatedSuperuser {
  user_id: string;
}

// Participant types
export type ExperienceLevel = "JUNIOR" | "MID" | "SENIOR";
export type SkillLevel = "BEGINNER" | "INTERMEDIATE" | "ADVANCED" | "EXPERT";
export type ParticipantDomain = Domain;

export interface ParticipantSkill {
  name: string;
  level: SkillLevel;
}

export interface ParticipantContact {
  title: string;
  url: string;
}

export interface ParticipantProfile {
  id: string;
  user_id: string;
  full_name: string;
  bio: string;
  skills: ParticipantSkill[];
  experience_level: ExperienceLevel;
  preferred_domains: ParticipantDomain[];
  contacts: ParticipantContact[];
}

export interface ParticipantSkillForm {
  name: string;
  level: SkillLevel;
}

export interface ParticipantContactForm {
  title: string;
  url: string;
}

export interface ParticipantForm {
  full_name: string;
  bio: string;
  skills: ParticipantSkillForm[];
  experience_level: ExperienceLevel;
  preferred_domains: Domain[];
  contacts: ParticipantContactForm[];
}

export interface CreatedParticipant {
  participant_id: string;
  user_id: string;
}

// Competition types
export type Domain = "frontend" | "mobile" | "backend" | "ai" | "devops";

export type ParticipantType = "schoolchild" | "student" | "any";

export type CompetitionFormat = "online" | "offline" | "hybrid";

export type CompetitionSortBy =
  | "created_at"
  | "title"
  | "registration_start"
  | "team_formation_start";

export type SortOrder = "asc" | "desc";

export interface CompetitionSchedule {
  registration_start: string;
  registration_end: string;
  team_formation_start: string | null;
  team_formation_end: string | null;
}

export interface ParticipantLimits {
  min: number;
  max: number;
}

export interface TeamSizeRange {
  min: number;
  max: number;
}

export interface CompetitionVenue {
  format: CompetitionFormat;
  location: string | null;
}

export interface MilestoneForm {
  title: string;
  timestamp: string;
}

export interface Milestone {
  title: string;
  timestamp: string;
}

export interface CompetitionForm {
  title: string;
  description: string;
  schedule: CompetitionSchedule;
  participant_limits: ParticipantLimits;
  domains: Domain[];
  participant_type: ParticipantType;
  venue: CompetitionVenue;
  team_size: TeamSizeRange;
  auto_accept: boolean;
  milestones?: MilestoneForm[];
}

export interface UpdateCompetitionForm {
  title: string;
  description: string;
  schedule: CompetitionSchedule;
  participant_limits: ParticipantLimits;
  domains: Domain[];
  participant_type: ParticipantType;
  venue: CompetitionVenue;
  team_size: TeamSizeRange;
  milestones: MilestoneForm[];
  auto_accept: boolean;
  is_archived: boolean;
}

export interface CompetitionModel {
  id: string;
  organizer_id: string;
  title: string;
  banner: string | null;
  description: string;
  schedule: CompetitionSchedule;
  participant_limits: ParticipantLimits;
  domains: Domain[];
  participant_type: ParticipantType;
  venue: CompetitionVenue;
  team_size: TeamSizeRange;
  milestones: Milestone[];
  auto_accept: boolean;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
}

export interface CompetitionsList {
  items: CompetitionModel[];
  total: number;
  page: number;
}

export interface CreatedCompetition {
  competition_id: string;
}

// Preview types for public competition browsing
export interface PreviewOrganizerModel {
  id: string;
  name: string;
  avatar_url: string | null;
}

export interface PreviewCompetitionModel {
  id: string;
  organizer: PreviewOrganizerModel;
  title: string;
  banner: string | null;
  description: string;
  schedule: CompetitionSchedule;
  participant_limits: ParticipantLimits;
  domains: Domain[];
  participant_type: ParticipantType;
  venue: CompetitionVenue;
  team_size: TeamSizeRange;
  milestones: Milestone[];
  is_archived: boolean;
  created_at: string;
  updated_at: string;
}

export interface PreviewCompetitionsList {
  items: PreviewCompetitionModel[];
  total: number;
  page: number;
}

// Application Form types
export type FieldType = "string" | "int" | "select" | "multiselect";

export interface FieldChoiceForm {
  value: string;
  label: string;
}

export interface FieldForm {
  name: string;
  label: string;
  type: FieldType;
  required?: boolean;
  choices?: FieldChoiceForm[] | null;
}

export interface ApplicationFormInput {
  fields: FieldForm[];
}

export interface CreatedApplicationForm {
  application_form_id: string;
}

export interface FieldChoiceModel {
  value: string;
  label: string;
}

export interface FieldModel {
  name: string;
  label: string;
  type: FieldType;
  required: boolean;
  choices: FieldChoiceModel[] | null;
}

export interface ApplicationFormModel {
  id: string;
  competition_id: string;
  created_at: string;
  fields: FieldModel[];
}

// Application types
export type ApplicationStatus = "pending" | "accepted" | "rejected";

export interface SubmitApplicationForm {
  domains: Domain[];
  form_data: Record<string, any> | null;
}

export interface CreatedApplication {
  application_id: string;
}

export interface ApplicationModel {
  id: string;
  participant_id: string;
  competition_id: string;
  domains: Domain[];
  status: ApplicationStatus;
  created_at: string;
  form_data: Record<string, any> | null;
}

export interface ApplicationsList {
  items: ApplicationModel[];
  total: number;
  page: number;
}
