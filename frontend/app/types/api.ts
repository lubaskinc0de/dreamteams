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
  | "ACCOUNT_BLOCKED"
  | "AUTH_USER_ALREADY_EXISTS"
  | "ORGANIZER_ALREADY_EXISTS"
  | "ORGANIZER_NOT_FOUND"
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
  | "PARTICIPANT_NOT_FOUND"
  | "INVALID_PARTICIPANT_DATA"
  | "COMPETITION_NOT_FOUND"
  | "INVALID_COMPETITION_DATA"
  | "APPLICATION_FORM_ALREADY_EXISTS"
  | "APPLICATION_FORM_NOT_FOUND"
  | "INVALID_APPLICATION_FORM_DATA"
  | "APPLICATION_NOT_FOUND"
  | "APPLICATION_ALREADY_EXISTS"
  | "APPLICATION_ALREADY_RESOLVED"
  | "INVALID_APPLICATION_DATA"
  | "COMPETITION_NOT_ACTIVE"
  | "PARTICIPANT_LIMITS_EXCEEDED"
  | "PARTICIPANT_TYPE_MISMATCH"
  | "INVALID_ROLE"
  | "EXPORT_JOB_NOT_FOUND"
  | "EXPORT_RATE_LIMIT_EXCEEDED";

export interface CreatedSuperuser {
  user_id: string;
}

// Participant types
export type ExperienceLevel = "JUNIOR" | "MID" | "SENIOR";
export type SkillLevel = "BEGINNER" | "INTERMEDIATE" | "ADVANCED" | "EXPERT";
export type ParticipantDomain = Domain;
export type ParticipantRoleType = "schoolchild" | "student";

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
  participant_type: ParticipantRoleType;
  age: number;
  bio: string | null;
  skills: ParticipantSkill[];
  experience_level: ExperienceLevel | null;
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
  participant_type: ParticipantRoleType;
  age: number;
  bio?: string | null;
  skills?: ParticipantSkillForm[];
  experience_level?: ExperienceLevel | null;
  preferred_domains?: Domain[];
  contacts?: ParticipantContactForm[];
}

export interface UpdateParticipantForm {
  full_name: string;
  participant_type: ParticipantRoleType;
  age: number;
  bio?: string | null;
  skills?: ParticipantSkillForm[];
  experience_level?: ExperienceLevel | null;
  preferred_domains?: Domain[];
  contacts?: ParticipantContactForm[];
}

export interface UpdateOrganizerForm {
  organizer_name: string;
  contact_email: string;
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

export interface MilestoneDescription {
  value: string;
}

export interface MilestoneForm {
  title: string;
  timestamp: string;
  // Wire form: backend expects the raw string (Pydantic MilestoneForm schema),
  // never the {value: ...} VO shape.
  description: string | null;
}

export interface Milestone {
  title: string;
  timestamp: string;
  // Wire read shape: backend serializes the MilestoneDescription value object
  // as { value: "..." }. Unwrap via `milestone.description?.value ?? null` at
  // call sites — prefer `extractMilestoneDescription()` helper.
  description: MilestoneDescription | null;
}

export interface CompetitionForm {
  title: string;
  description: string;
  schedule: CompetitionSchedule;
  participant_limits: ParticipantLimits;
  domains: Domain[];
  participant_type: ParticipantType;
  venue: CompetitionVenue;
  team_size: TeamSizeRange | null;
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
  team_size: TeamSizeRange | null;
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
  team_size: TeamSizeRange | null;
  milestones: Milestone[];
  auto_accept: boolean;
  is_archived: boolean;
  members_count: number;
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
  team_size: TeamSizeRange | null;
  milestones: Milestone[];
  is_archived: boolean;
  members_count: number;
  created_at: string;
  updated_at: string;
}

export interface PreviewCompetitionsList {
  items: PreviewCompetitionModel[];
  total: number;
  page: number;
}

export type ExploreSortBy = "most_popular" | "newest";

export interface ExploreCompetitionsFilters {
  page?: number;
  sort_by?: ExploreSortBy;
  search?: string;
  min_team_size?: number;
  max_team_size?: number;
  auto_accept?: boolean;
  domains?: Domain[];
}

export type ExploreCompetitionModel = PreviewCompetitionModel;

export interface ExploreCompetitionsList {
  items: ExploreCompetitionModel[];
  total: number;
  page: number;
}

// Application Form types
export type FieldType = "string" | "int" | "select" | "multiselect";

export interface FieldChoiceForm {
  value: string;
}

export interface FieldForm {
  name: string;
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
}

export interface FieldModel {
  name: string;
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

// Participant profile nested inside organizer-facing ApplicationModel.
// Same shape as the participant block in GET /users/profile/.
export interface ParticipantInfo {
  id: string;
  full_name: string;
  bio: string | null;
  participant_type: ParticipantRoleType;
  age: number;
  skills: ParticipantSkill[];
  experience_level: ExperienceLevel | null;
  preferred_domains: ParticipantDomain[];
  contacts: ParticipantContact[];
}

// Participant-facing application view (GET /applications/ and /applications/{id}/my/).
export interface MyApplicationModel {
  id: string;
  participant_id: string;
  competition_id: string;
  competition_name: string;
  domains: Domain[];
  status: ApplicationStatus;
  created_at: string;
  form_data: Record<string, any> | null;
}

export interface MyApplicationsList {
  items: MyApplicationModel[];
  total: number;
  page: number;
}

// Organizer-facing application view (GET /competitions/{id}/applications/ and /applications/{id}/).
export interface ApplicationModel {
  id: string;
  competition_id: string;
  competition_name: string;
  domains: Domain[];
  status: ApplicationStatus;
  created_at: string;
  form_data: Record<string, any> | null;
  participant: ParticipantInfo;
}

export interface ApplicationsList {
  items: ApplicationModel[];
  total: number;
  page: number;
}

export type ExportJobStatusKind = "pending" | "success" | "failed";

export interface CreateExportJobInput {
  competition_id: string;
  application_status: ApplicationStatus;
}

export interface CreatedExportJob {
  job_id: string;
}

export interface ExportJobModel {
  id: string;
  user_id: string;
  competition_id: string;
  application_status: ApplicationStatus;
  status_kind: ExportJobStatusKind;
  status_reason: string | null;
  file_url: string | null;
  created_at: string;
  finished_at: string | null;
}
