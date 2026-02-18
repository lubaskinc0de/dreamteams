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
  avatar_url: string | null;
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
  | "INVALID_AVATAR_ERROR";

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
