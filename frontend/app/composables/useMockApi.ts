import type {
  ApiError,
  OrganizerForm,
  CreatedOrganizer,
  ProfileModel,
  ParticipantForm,
  UpdateParticipantForm,
  CreatedParticipant,
  CompetitionForm,
  UpdateCompetitionGeneralInfoForm,
  RescheduleCompetitionForm,
  ChangeCompetitionArchiveStatusForm,
  CreatedCompetition,
  CompetitionModel,
  CompetitionsList,
  CompetitionSortBy,
  SortOrder,
  PreviewCompetitionModel,
  PreviewCompetitionsList,
  InviteForm,
  CreatedInvite,
  InviteModel,
  InvitesList,
  AdminBlockUserInput,
  AdminUserDetails,
  AdminUserListItem,
  AdminUsersFilters,
  AdminUsersList,
  CreatedSuperuser,
  CompetitionTag,
  CompetitionTagForm,
  CompetitionTagsFilters,
  CompetitionTagsList,
  ExploreCompetitionsFilters,
  ExploreCompetitionsList,
  ApplicationStatus,
  SubmitApplicationForm,
  CreatedApplication,
  MyApplicationModel,
  MyApplicationsList,
  ApplicationModel,
  ApplicationsList,
  CreateExportJobInput,
  CreatedExportJob,
  ExportJobModel,
} from "~/types/api";

// Mock invite code accepted in mock mode
const MOCK_INVITE_CODE = "MOCK-INVITE-2026";

let mockTags: CompetitionTag[] = [
  { id: "11111111-1111-4111-8111-111111111111", value: "Frontend" },
  { id: "22222222-2222-4222-8222-222222222222", value: "Backend" },
  { id: "33333333-3333-4333-8333-333333333333", value: "Mobile" },
  { id: "44444444-4444-4444-8444-444444444444", value: "AI" },
  { id: "55555555-5555-4555-8555-555555555555", value: "DevOps" },
  { id: "66666666-6666-4666-8666-666666666666", value: "Python" },
];

const tagByValue = (value: string) => {
  const tag = mockTags.find((item) => item.value.toLowerCase() === value.toLowerCase());
  if (!tag) {
    throw new Error(`Unknown mock tag: ${value}`);
  }
  return tag;
};

const tags = (values: string[]) => values.map(tagByValue);
const tracks = (names: string[]) => names.map((name) => ({ name }));

const tagsByIds = (ids: string[]) =>
  ids.map((id) => mockTags.find((tag) => tag.id === id)).filter((tag): tag is CompetitionTag => Boolean(tag));

// Mock data
const mockOrganizerUser: ProfileModel = {
  user_id: "123e4567-e89b-12d3-a456-426614174000",
  organizer: {
    id: "123e4567-e89b-12d3-a456-426614174001",
    user_id: "123e4567-e89b-12d3-a456-426614174000",
    organizer_name: "IT-компания TechHub",
    phone_number: "+79991234567",
    contact_email: "ivan@example.com",
    logo: null,
  },
  participant: null,
  avatar_url: null,
  is_admin: false,
};

const mockParticipantUser: ProfileModel = {
  user_id: "123e4567-e89b-12d3-a456-426614174000",
  organizer: null,
  participant: {
    id: "123e4567-e89b-12d3-a456-426614174002",
    user_id: "123e4567-e89b-12d3-a456-426614174000",
    full_name: "Иван Петров",
    participant_type: "student" as const,
    age: 22,
    bio: "Fullstack разработчик с 3 годами опыта. Люблю хакатоны и командную работу.",
    skills: [
      { name: "Python", level: "ADVANCED" },
      { name: "React", level: "INTERMEDIATE" },
    ],
    experience_level: "MID",
    contacts: [{ title: "Telegram", value: "@ivan_dev" }],
  },
  avatar_url: null,
  is_admin: false,
};

const mockUnregisteredUser: ProfileModel = {
  user_id: "123e4567-e89b-12d3-a456-426614174000",
  organizer: null,
  participant: null,
  avatar_url: null,
  is_admin: false,
};

// Storage for current state
let isRegistered = false;
let isParticipantRegistered = false;
let currentAvatarUrl: string | null = null;

// Mock invite state
let mockInvites: InviteModel[] = [
  {
    id: "invite-1",
    code: MOCK_INVITE_CODE,
    display_name: "Test invite",
    created_by: "123e4567-e89b-12d3-a456-426614174000",
    is_revoked: false,
    is_used: false,
    used_by: null,
    created_at: "2026-02-20T10:00:00Z",
  },
  {
    id: "invite-2",
    code: "USED-INVITE-CODE",
    display_name: "Used invite",
    created_by: "123e4567-e89b-12d3-a456-426614174000",
    is_revoked: false,
    is_used: true,
    used_by: {
      id: "org-used-1",
      name: "Иванов Иван",
      avatar_url: null,
    },
    created_at: "2026-02-19T09:00:00Z",
  },
  {
    id: "invite-3",
    code: "REVOKED-INVITE-CODE",
    display_name: null,
    created_by: "123e4567-e89b-12d3-a456-426614174000",
    is_revoked: true,
    is_used: false,
    used_by: null,
    created_at: "2026-02-18T08:00:00Z",
  },
];
let mockInviteCounter = 4;

let mockAdminUsers: AdminUserDetails[] = [
  {
    user: {
      id: "123e4567-e89b-12d3-a456-426614174000",
      avatar_url: null,
      is_admin: true,
      ban_status: {
        is_blocked: false,
        reason: null,
        blocked_at: null,
      },
    },
    organizer: {
      id: "123e4567-e89b-12d3-a456-426614174001",
      user_id: "123e4567-e89b-12d3-a456-426614174000",
      organizer_name: "IT-компания TechHub",
      phone_number: "+79991234567",
      contact_email: "ivan@example.com",
    },
    participant: null,
  },
  {
    user: {
      id: "223e4567-e89b-12d3-a456-426614174000",
      avatar_url: "https://i.pravatar.cc/150?img=12",
      is_admin: false,
      ban_status: {
        is_blocked: true,
        reason: "Spam in applications",
        blocked_at: "2026-04-15T09:30:00Z",
      },
    },
    organizer: null,
    participant: {
      full_name: "Анна Смирнова",
      participant_type: "student",
      age: 21,
      bio: "Frontend developer interested in product hackathons.",
      skills: [
        { name: "Vue", level: "ADVANCED" },
        { name: "TypeScript", level: "INTERMEDIATE" },
      ],
      experience_level: "MID",
      contacts: [{ title: "GitHub", value: "https://github.com/anna" }],
      created_at: "2026-02-03T10:00:00Z",
      updated_at: "2026-04-14T12:20:00Z",
    },
  },
  {
    user: {
      id: "323e4567-e89b-12d3-a456-426614174000",
      avatar_url: null,
      is_admin: false,
      ban_status: {
        is_blocked: false,
        reason: null,
        blocked_at: null,
      },
    },
    organizer: {
      id: "323e4567-e89b-12d3-a456-426614174001",
      user_id: "323e4567-e89b-12d3-a456-426614174000",
      organizer_name: "Future Labs",
      phone_number: "+79995550123",
      contact_email: "events@futurelabs.example",
    },
    participant: null,
  },
];

// Mock preview competitions data
const mockPreviewCompetitions: PreviewCompetitionModel[] = [
  {
    id: "preview-1",
    organizer: {
      id: "org-1",
      name: "TechHub Москва",
      avatar_url: "https://i.pravatar.cc/150?img=60",
    },
    title: "AI Hack 2026: Искусственный интеллект будущего",
    banner: null,
    description: "Создайте революционное AI-решение за 48 часов. Призовой фонд 500 000₽. Лучшие команды получат менторство от экспертов и возможность реализовать проект.",
    schedule: {
      registration_start: "2026-03-01T00:00:00Z",
      registration_end: "2026-03-25T23:59:59Z",
      team_formation_start: "2026-03-05T00:00:00Z",
      team_formation_end: "2026-03-25T23:59:59Z",
    },
    participant_limits: { max: 500 },
    members_count: 120,
    tags: tags(["AI", "Backend", "Python"]),
    tracks: tracks(["AI/ML", "Backend"]),
    participant_type: "any",
    venue: { format: "hybrid", location: "Москва, Сколково" },
    team_size: { min: 2, max: 5 },
    milestones: [],
    is_archived: false,
    created_at: "2026-02-01T10:00:00Z",
    updated_at: "2026-02-01T10:00:00Z",
  },
  {
    id: "preview-2",
    organizer: {
      id: "org-2",
      name: "Инновации Будущего",
      avatar_url: "https://i.pravatar.cc/150?img=12",
    },
    title: "FinTech Challenge: Цифровые финансы",
    banner: null,
    description: "Разработайте инновационное финансовое приложение. Партнерство с ведущими банками. Призы до 1 000 000₽ и возможность внедрения решения.",
    schedule: {
      registration_start: "2026-02-20T00:00:00Z",
      registration_end: "2026-03-15T23:59:59Z",
      team_formation_start: "2026-02-25T00:00:00Z",
      team_formation_end: "2026-03-15T23:59:59Z",
    },
    participant_limits: { max: 200 },
    members_count: 45,
    tags: tags(["Frontend", "Backend"]),
    tracks: tracks(["Frontend", "Backend"]),
    participant_type: "student",
    venue: { format: "offline", location: "Санкт-Петербург, Технопарк" },
    team_size: { min: 3, max: 5 },
    milestones: [],
    is_archived: false,
    created_at: "2026-02-10T12:00:00Z",
    updated_at: "2026-02-10T12:00:00Z",
  },
  {
    id: "preview-3",
    organizer: {
      id: "org-3",
      name: "Mobile Dev Community",
      avatar_url: "https://i.pravatar.cc/150?img=25",
    },
    title: "Mobile Apps Marathon 2026",
    banner: null,
    description: "48-часовой марафон разработки мобильных приложений. iOS и Android. Менторы от Google и Apple. Призовой фонд 300 000₽.",
    schedule: {
      registration_start: "2026-02-10T00:00:00Z",
      registration_end: "2026-03-10T23:59:59Z",
      team_formation_start: "2026-02-15T00:00:00Z",
      team_formation_end: "2026-03-10T23:59:59Z",
    },
    participant_limits: { max: 150 },
    members_count: 10,
    tags: tags(["Mobile"]),
    tracks: tracks(["Mobile"]),
    participant_type: "any",
    venue: { format: "hybrid", location: "Казань, IT-парк" },
    team_size: { min: 2, max: 4 },
    milestones: [],
    is_archived: false,
    created_at: "2026-02-05T14:00:00Z",
    updated_at: "2026-02-05T14:00:00Z",
  },
  {
    id: "preview-4",
    organizer: {
      id: "org-4",
      name: "DevOps Masters",
      avatar_url: "https://i.pravatar.cc/150?img=33",
    },
    title: "Cloud Infrastructure Hackathon",
    banner: null,
    description: "Постройте масштабируемую облачную инфраструктуру. Работа с Kubernetes, Docker, CI/CD. Призы от облачных провайдеров.",
    schedule: {
      registration_start: "2026-03-05T00:00:00Z",
      registration_end: "2026-03-30T23:59:59Z",
      team_formation_start: "2026-03-10T00:00:00Z",
      team_formation_end: "2026-03-30T23:59:59Z",
    },
    participant_limits: { max: 180 },
    members_count: 0,
    tags: tags(["DevOps", "Backend"]),
    tracks: tracks(["DevOps", "Backend"]),
    participant_type: "any",
    venue: { format: "online", location: null },
    team_size: { min: 2, max: 4 },
    milestones: [],
    is_archived: false,
    created_at: "2026-02-12T09:00:00Z",
    updated_at: "2026-02-12T09:00:00Z",
  },
  {
    id: "preview-5",
    organizer: {
      id: "org-5",
      name: "StartupHub Екатеринбург",
      avatar_url: "https://i.pravatar.cc/150?img=45",
    },
    title: "EduTech Innovation: Образование будущего",
    banner: null,
    description: "Создайте платформу для онлайн-обучения следующего поколения. VR/AR приветствуется. Партнерство с образовательными учреждениями.",
    schedule: {
      registration_start: "2026-02-15T00:00:00Z",
      registration_end: "2026-03-20T23:59:59Z",
      team_formation_start: null,
      team_formation_end: null,
    },
    participant_limits: { max: 100 },
    members_count: 80,
    tags: tags(["Frontend", "AI"]),
    tracks: tracks(["Frontend", "AI/ML"]),
    participant_type: "student",
    venue: { format: "offline", location: "Екатеринбург" },
    team_size: { min: 3, max: 6 },
    milestones: [],
    is_archived: false,
    created_at: "2026-02-08T11:00:00Z",
    updated_at: "2026-02-08T11:00:00Z",
  },
  {
    id: "preview-6",
    organizer: {
      id: "org-6",
      name: "GameDev Alliance",
      avatar_url: "https://i.pravatar.cc/150?img=52",
    },
    title: "Indie Game Jam 2026",
    banner: null,
    description: "72 часа на создание уникальной инди-игры. Любой движок и платформа. Призы от издателей игр и Steam ключи для победителей.",
    schedule: {
      registration_start: "2026-02-18T00:00:00Z",
      registration_end: "2026-03-18T23:59:59Z",
      team_formation_start: "2026-02-20T00:00:00Z",
      team_formation_end: "2026-03-18T23:59:59Z",
    },
    participant_limits: { max: 80 },
    members_count: 15,
    tags: tags(["Frontend", "Mobile"]),
    tracks: tracks(["Frontend", "Mobile"]),
    participant_type: "any",
    venue: { format: "hybrid", location: "Новосибирск, Академгородок" },
    team_size: { min: 1, max: 4 },
    milestones: [],
    is_archived: false,
    created_at: "2026-02-11T15:00:00Z",
    updated_at: "2026-02-11T15:00:00Z",
  },
  {
    id: "preview-7",
    organizer: {
      id: "org-7",
      name: "CyberSecurity Pro",
      avatar_url: "https://i.pravatar.cc/150?img=68",
    },
    title: "Capture The Flag: Безопасность 2026",
    banner: null,
    description: "Соревнование по информационной безопасности. Пентест, криптография, реверс-инжиниринг. Для профессионалов и новичков.",
    schedule: {
      registration_start: "2026-02-25T00:00:00Z",
      registration_end: "2026-03-22T23:59:59Z",
      team_formation_start: "2026-03-01T00:00:00Z",
      team_formation_end: "2026-03-22T23:59:59Z",
    },
    participant_limits: { max: 250 },
    members_count: 200,
    tags: tags(["Backend", "DevOps"]),
    tracks: tracks(["Security", "Backend"]),
    participant_type: "any",
    venue: { format: "online", location: null },
    team_size: { min: 1, max: 3 },
    milestones: [],
    is_archived: false,
    created_at: "2026-02-13T16:00:00Z",
    updated_at: "2026-02-13T16:00:00Z",
  },
  {
    id: "preview-8",
    organizer: {
      id: "org-8",
      name: "HealthTech Innovations",
      avatar_url: "https://i.pravatar.cc/150?img=71",
    },
    title: "MedTech Hackathon: Здоровье и технологии",
    banner: null,
    description: "Разработайте решение для медицины. Телемедицина, носимые устройства, AI-диагностика. Партнерство с медицинскими центрами.",
    schedule: {
      registration_start: "2026-03-01T00:00:00Z",
      registration_end: "2026-03-28T23:59:59Z",
      team_formation_start: "2026-03-05T00:00:00Z",
      team_formation_end: "2026-03-28T23:59:59Z",
    },
    participant_limits: { max: 120 },
    members_count: 5,
    tags: tags(["AI", "Mobile", "Frontend"]),
    tracks: tracks(["AI/ML", "Mobile"]),
    participant_type: "student",
    venue: { format: "offline", location: "Москва, Сеченовский Университет" },
    team_size: { min: 3, max: 5 },
    milestones: [],
    is_archived: false,
    created_at: "2026-02-14T10:00:00Z",
    updated_at: "2026-02-14T10:00:00Z",
  },
  {
    id: "preview-9",
    organizer: {
      id: "org-9",
      name: "GreenTech Initiative",
      avatar_url: "https://i.pravatar.cc/150?img=18",
    },
    title: "EcoHack: Технологии для экологии",
    banner: null,
    description: "Создайте решение для защиты окружающей среды. IoT, мониторинг, предсказательная аналитика. Призы от экологических фондов.",
    schedule: {
      registration_start: "2026-02-22T00:00:00Z",
      registration_end: "2026-03-25T23:59:59Z",
      team_formation_start: "2026-02-27T00:00:00Z",
      team_formation_end: "2026-03-25T23:59:59Z",
    },
    participant_limits: { max: 100 },
    members_count: 90,
    tags: tags(["Backend", "AI", "DevOps"]),
    tracks: tracks(["Backend", "AI/ML"]),
    participant_type: "any",
    venue: { format: "hybrid", location: "Краснодар" },
    team_size: { min: 2, max: 5 },
    milestones: [],
    is_archived: false,
    created_at: "2026-02-09T13:00:00Z",
    updated_at: "2026-02-09T13:00:00Z",
  },
  {
    id: "preview-10",
    organizer: {
      id: "org-10",
      name: "Blockchain Hub",
      avatar_url: "https://i.pravatar.cc/150?img=41",
    },
    title: "Web3 Revolution: Децентрализованные приложения",
    banner: null,
    description: "Постройте dApp на блокчейне. Ethereum, Solana, Polygon. NFT, DeFi, DAO. Призы в криптовалюте и менторство от крипто-фондов.",
    schedule: {
      registration_start: "2026-03-10T00:00:00Z",
      registration_end: "2026-04-05T23:59:59Z",
      team_formation_start: "2026-03-15T00:00:00Z",
      team_formation_end: "2026-04-05T23:59:59Z",
    },
    participant_limits: { max: 200 },
    members_count: 60,
    tags: tags(["Frontend", "Backend"]),
    tracks: tracks(["Frontend", "Backend"]),
    participant_type: "any",
    venue: { format: "online", location: null },
    team_size: { min: 2, max: 4 },
    milestones: [],
    is_archived: false,
    created_at: "2026-02-16T14:00:00Z",
    updated_at: "2026-02-16T14:00:00Z",
  },
  {
    id: "preview-11",
    organizer: {
      id: "org-11",
      name: "Data Science Society",
      avatar_url: "https://i.pravatar.cc/150?img=29",
    },
    title: "Big Data Analytics Challenge",
    banner: null,
    description: "Анализ больших данных и предсказательная аналитика. Реальные датасеты от компаний. Призы до 400 000₽ и оффер на стажировку.",
    schedule: {
      registration_start: "2026-02-12T00:00:00Z",
      registration_end: "2026-03-12T23:59:59Z",
      team_formation_start: null,
      team_formation_end: null,
    },
    participant_limits: { max: 150 },
    members_count: 150,
    tags: tags(["AI", "Backend"]),
    tracks: tracks(["Data Science", "Backend"]),
    participant_type: "student",
    venue: { format: "online", location: null },
    team_size: { min: 1, max: 3 },
    milestones: [],
    is_archived: false,
    created_at: "2026-02-07T12:00:00Z",
    updated_at: "2026-02-07T12:00:00Z",
  },
  {
    id: "preview-12",
    organizer: {
      id: "org-12",
      name: "RetailTech Innovations",
      avatar_url: "https://i.pravatar.cc/150?img=54",
    },
    title: "E-Commerce UX Revolution",
    banner: null,
    description: "Улучшите пользовательский опыт в электронной коммерции. AR-примерки, персонализация, voice shopping. Призы от ритейл-гигантов.",
    schedule: {
      registration_start: "2026-02-28T00:00:00Z",
      registration_end: "2026-03-27T23:59:59Z",
      team_formation_start: "2026-03-02T00:00:00Z",
      team_formation_end: "2026-03-27T23:59:59Z",
    },
    participant_limits: { max: 100 },
    members_count: 35,
    tags: tags(["Frontend", "Mobile", "AI"]),
    tracks: tracks(["Frontend", "Mobile"]),
    participant_type: "any",
    venue: { format: "hybrid", location: "Москва, Skolkovo" },
    team_size: { min: 3, max: 5 },
    milestones: [],
    is_archived: false,
    created_at: "2026-02-15T11:00:00Z",
    updated_at: "2026-02-15T11:00:00Z",
  },
];

// Mock competitions data
const mockCompetitions: CompetitionModel[] = [
  {
    id: "comp-1",
    organizer_id: "123e4567-e89b-12d3-a456-426614174001",
    title: "Хакатон по веб-разработке 2026",
    banner: null,
    description:
      "Соревнование для разработчиков фронтенда и бэкенда. Создайте инновационное веб-приложение за 48 часов!",
    schedule: {
      registration_start: "2026-02-01T00:00:00Z",
      registration_end: "2026-02-28T23:59:59Z",
      team_formation_start: "2026-02-15T00:00:00Z",
      team_formation_end: "2026-02-28T23:59:59Z",
    },
    participant_limits: { max: 200 },
    members_count: 180,
    tags: tags(["Frontend", "Backend"]),
    tracks: tracks(["Frontend", "Backend"]),
    participant_type: "student",
    venue: { format: "hybrid", location: "Москва, Технопарк" },
    team_size: { min: 2, max: 5 },
    milestones: [
      { title: "Открытие регистрации", timestamp: "2026-02-01T00:00:00Z", description: null },
      { title: "Начало хакатона", timestamp: "2026-03-15T10:00:00Z", description: null },
      { title: "Защита проектов", timestamp: "2026-03-17T14:00:00Z", description: null },
    ],
    auto_accept: false,
    is_archived: false,
    created_at: "2026-01-01T12:00:00Z",
    updated_at: "2026-01-01T12:00:00Z",
  },
  {
    id: "comp-2",
    organizer_id: "123e4567-e89b-12d3-a456-426614174001",
    title: "AI Challenge: Чат-боты нового поколения",
    banner: null,
    description:
      "Создайте интеллектуального чат-бота с использованием современных AI технологий",
    schedule: {
      registration_start: "2026-01-15T00:00:00Z",
      registration_end: "2026-02-15T23:59:59Z",
      team_formation_start: null,
      team_formation_end: null,
    },
    participant_limits: { max: 100 },
    members_count: 25,
    tags: tags(["AI", "Backend", "Python"]),
    tracks: tracks(["AI/ML", "Backend"]),
    participant_type: "any",
    venue: { format: "online", location: null },
    team_size: { min: 1, max: 3 },
    milestones: [],
    auto_accept: false,
    is_archived: false,
    created_at: "2025-12-20T12:00:00Z",
    updated_at: "2025-12-20T12:00:00Z",
  },
  {
    id: "comp-3",
    organizer_id: "123e4567-e89b-12d3-a456-426614174001",
    title: "Mobile Dev Cup",
    banner: null,
    description:
      "Разработка мобильных приложений для iOS и Android. Покажи свои навыки!",
    schedule: {
      registration_start: "2026-03-01T00:00:00Z",
      registration_end: "2026-03-20T23:59:59Z",
      team_formation_start: "2026-03-05T00:00:00Z",
      team_formation_end: "2026-03-20T23:59:59Z",
    },
    participant_limits: { max: 150 },
    members_count: 70,
    tags: tags(["Mobile"]),
    tracks: tracks(["Mobile"]),
    participant_type: "schoolchild",
    venue: { format: "offline", location: "Санкт-Петербург" },
    team_size: { min: 2, max: 4 },
    milestones: [
      { title: "Старт регистрации", timestamp: "2026-03-01T00:00:00Z", description: null },
    ],
    auto_accept: false,
    is_archived: false,
    created_at: "2025-12-15T12:00:00Z",
    updated_at: "2025-12-15T12:00:00Z",
  },
];

let mockApplications: ApplicationModel[] = [
  {
    id: "app-1",
    competition_id: "comp-1",
    competition_name: "Хакатон по веб-разработке 2026",
    track: { name: "Backend" },
    status: "pending",
    created_at: "2026-02-10T10:00:00Z",
    form_data: { experience: "Node.js, Python" },
    participant: {
      id: "participant-1",
      full_name: "Анна Смирнова",
      participant_type: "student",
      age: 21,
      bio: "Frontend developer interested in product hackathons.",
      skills: [
        { name: "Vue", level: "ADVANCED" },
        { name: "TypeScript", level: "INTERMEDIATE" },
      ],
      experience_level: "MID",
      contacts: [{ title: "GitHub", value: "https://github.com/anna" }],
    },
  },
];

export const useMockApi = () => {
  const delay = (ms: number) =>
    new Promise((resolve) => setTimeout(resolve, ms));

  const checkAuth = async (): Promise<boolean> => {
    // Simulate network delay
    await delay(200);
    // In mock mode, user is always authenticated
    return true;
  };

  const registerOrganizer = async (
    form: OrganizerForm,
  ): Promise<{ data: CreatedOrganizer | null; error: ApiError | null }> => {
    // Simulate network delay
    await delay(500);

    // Validate form
    if (form.organizer_name.length > 70) {
      return {
        data: null,
        error: {
          code: "VALIDATION_ERROR",
          message: "Имя не должно превышать 70 символов",
          meta: {
            detail: [
              {
                loc: ["body", "organizer_name"],
                msg: "ensure this value has at most 70 characters",
                type: "value_error.any_str.max_length",
              },
            ],
          },
        },
      };
    }

    const phoneRegex = /^\+7\d{10}$/;
    if (!phoneRegex.test(form.phone_number)) {
      return {
        data: null,
        error: {
          code: "VALIDATION_ERROR",
          message: "Неверный формат номера телефона",
          meta: {
            detail: [
              {
                loc: ["body", "phone_number"],
                msg: "invalid phone number format",
                type: "value_error.phone",
              },
            ],
          },
        },
      };
    }

    // Validate invite code
    const invite = mockInvites.find((i) => i.code === form.invite_code);
    if (!invite) {
      return {
        data: null,
        error: {
          code: "INVITE_NOT_FOUND",
          message: "Invite not found",
          meta: null,
        },
      };
    }
    if (invite.is_revoked) {
      return {
        data: null,
        error: {
          code: "INVITE_REVOKED",
          message: "This invite has been revoked",
          meta: null,
        },
      };
    }
    if (invite.is_used) {
      return {
        data: null,
        error: {
          code: "INVITE_ALREADY_USED",
          message: "This invite has already been used",
          meta: null,
        },
      };
    }

    // Mark invite as used
    invite.is_used = true;
    invite.used_by = {
      id: "123e4567-e89b-12d3-a456-426614174001",
      name: form.organizer_name,
      avatar_url: null,
    };

    // Check if already registered
    if (isRegistered) {
      return {
        data: null,
        error: {
          code: "AUTH_USER_ALREADY_EXISTS",
          message: "Вы уже зарегистрированы как организатор",
          meta: null,
        },
      };
    }

    // Success
    isRegistered = true;
    return {
      data: {
        organizer_id: "123e4567-e89b-12d3-a456-426614174001",
        user_id: "123e4567-e89b-12d3-a456-426614174000",
      },
      error: null,
    };
  };

  const getUserProfile = async (): Promise<{
    data: ProfileModel | null;
    error: ApiError | null;
  }> => {
    // Simulate network delay
    await delay(300);

    let profile: ProfileModel;
    if (isRegistered) {
      profile = mockOrganizerUser;
    } else if (isParticipantRegistered) {
      profile = mockParticipantUser;
    } else {
      profile = mockUnregisteredUser;
    }

    return {
      data: { ...profile, avatar_url: currentAvatarUrl },
      error: null,
    };
  };

  const deleteUserProfile = async () => {
    // Simulate network delay
    await delay(300);

    return {
      success: "true",
      error: null,
    };
  };

  const listCompetitions = async (
    page: number = 1,
    sortBy: CompetitionSortBy = "created_at",
    sortOrder: SortOrder = "desc",
    isArchived?: boolean,
    search?: string,
  ): Promise<{ data: CompetitionsList | null; error: ApiError | null }> => {
    await delay(300);

    // Filter by is_archived if specified
    let filtered = mockCompetitions;
    if (isArchived !== undefined) {
      filtered = mockCompetitions.filter((c) => c.is_archived === isArchived);
    }

    // Filter by search query
    if (search) {
      const query = search.toLowerCase();
      filtered = filtered.filter(
        (c) =>
          c.title.toLowerCase().includes(query) ||
          c.description.toLowerCase().includes(query),
      );
    }

    // Sort competitions
    const sorted = [...filtered].sort((a, b) => {
      let aVal: any;
      let bVal: any;

      if (sortBy === "created_at") {
        aVal = new Date(a.created_at).getTime();
        bVal = new Date(b.created_at).getTime();
      } else if (sortBy === "title") {
        aVal = a.title;
        bVal = b.title;
      } else if (sortBy === "registration_start") {
        aVal = new Date(a.schedule.registration_start).getTime();
        bVal = new Date(b.schedule.registration_start).getTime();
      } else if (sortBy === "team_formation_start") {
        aVal = a.schedule.team_formation_start
          ? new Date(a.schedule.team_formation_start).getTime()
          : 0;
        bVal = b.schedule.team_formation_start
          ? new Date(b.schedule.team_formation_start).getTime()
          : 0;
      }

      if (sortOrder === "asc") {
        return aVal > bVal ? 1 : -1;
      } else {
        return aVal < bVal ? 1 : -1;
      }
    });

    return {
      data: {
        items: sorted,
        total: filtered.length,
        page,
      },
      error: null,
    };
  };

  const createCompetition = async (
    form: CompetitionForm,
  ): Promise<{ data: CreatedCompetition | null; error: ApiError | null }> => {
    await delay(500);

    // Validate title
    if (form.title.length > 200) {
      return {
        data: null,
        error: {
          code: "VALIDATION_ERROR",
          message: "Название не должно превышать 200 символов",
          meta: {
            detail: [
              {
                loc: ["body", "title"],
                msg: "ensure this value has at most 200 characters",
                type: "value_error.any_str.max_length",
              },
            ],
          },
        },
      };
    }

    const selectedTags = tagsByIds(form.tag_ids);
    if (selectedTags.length !== form.tag_ids.length) {
      return {
        data: null,
        error: {
          code: "COMPETITION_TAG_NOT_FOUND",
          message: "Competition tag not found",
          meta: null,
        },
      };
    }

    const newCompetition: CompetitionModel = {
      id: `comp-${Date.now()}`,
      organizer_id: "123e4567-e89b-12d3-a456-426614174001",
      title: form.title,
      banner: null,
      description: form.description,
      schedule: form.schedule,
      participant_limits: form.participant_limits,
      tags: selectedTags,
      tracks: form.tracks,
      participant_type: form.participant_type,
      venue: form.venue,
      team_size: form.team_size,
      milestones: (form.milestones || []).map((m) => ({
        title: m.title,
        timestamp: m.timestamp,
        description: m.description,
      })),
      auto_accept: form.auto_accept,
      is_archived: false,
      members_count: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    mockCompetitions.push(newCompetition);

    return {
      data: {
        competition_id: newCompetition.id,
      },
      error: null,
    };
  };

  const getCompetition = async (
    competitionId: string,
  ): Promise<{ data: CompetitionModel | null; error: ApiError | null }> => {
    await delay(300);

    const competition = mockCompetitions.find((c) => c.id === competitionId);

    if (!competition) {
      return {
        data: null,
        error: {
          code: "USER_NOT_FOUND",
          message: "Соревнование не найдено",
          meta: null,
        },
      };
    }

    return {
      data: competition,
      error: null,
    };
  };

  const getExploreCompetition = async (
    competitionId: string,
  ): Promise<{ data: CompetitionModel | null; error: ApiError | null }> => {
    await delay(300);

    const organizerCompetition = mockCompetitions.find((c) => c.id === competitionId);
    if (organizerCompetition) {
      return { data: organizerCompetition, error: null };
    }

    const preview = mockPreviewCompetitions.find((c) => c.id === competitionId);
    if (!preview) {
      return {
        data: null,
        error: {
          code: "COMPETITION_NOT_FOUND",
          message: "Competition not found",
          meta: null,
        },
      };
    }

    return {
      data: {
        ...preview,
        organizer_id: preview.organizer.id,
        auto_accept: false,
      },
      error: null,
    };
  };

  const updateCompetitionGeneralInfo = async (
    competitionId: string,
    form: UpdateCompetitionGeneralInfoForm,
  ): Promise<{ data: {} | null; error: ApiError | null }> => {
    await delay(500);

    const index = mockCompetitions.findIndex((c) => c.id === competitionId);

    if (index === -1) {
      return {
        data: null,
        error: {
          code: "USER_NOT_FOUND",
          message: "Соревнование не найдено",
          meta: null,
        },
      };
    }

    const currentCompetition = mockCompetitions[index]!;
    const selectedTags = tagsByIds(form.tag_ids);
    if (selectedTags.length !== form.tag_ids.length) {
      return {
        data: null,
        error: {
          code: "COMPETITION_TAG_NOT_FOUND",
          message: "Competition tag not found",
          meta: null,
        },
      };
    }

    mockCompetitions[index] = {
      id: currentCompetition.id,
      organizer_id: currentCompetition.organizer_id,
      banner: currentCompetition.banner,
      title: form.title,
      description: form.description,
      schedule: currentCompetition.schedule,
      participant_limits: form.participant_limits,
      tags: selectedTags,
      tracks: form.tracks,
      participant_type: form.participant_type,
      venue: form.venue,
      team_size: currentCompetition.team_size,
      milestones: (form.milestones ?? []).map((m) => ({
        title: m.title,
        timestamp: m.timestamp,
        description: m.description,
      })),
      auto_accept: form.auto_accept,
      is_archived: currentCompetition.is_archived,
      members_count: currentCompetition.members_count,
      created_at: currentCompetition.created_at,
      updated_at: new Date().toISOString(),
    };

    return {
      data: {},
      error: null,
    };
  };

  const rescheduleCompetition = async (
    competitionId: string,
    form: RescheduleCompetitionForm,
  ): Promise<{ data: {} | null; error: ApiError | null }> => {
    await delay(500);

    const index = mockCompetitions.findIndex((c) => c.id === competitionId);

    if (index === -1) {
      return {
        data: null,
        error: {
          code: "USER_NOT_FOUND",
          message: "Соревнование не найдено",
          meta: null,
        },
      };
    }

    const currentCompetition = mockCompetitions[index]!;
    mockCompetitions[index] = {
      ...currentCompetition,
      schedule: form.schedule,
      team_size: form.team_size,
      updated_at: new Date().toISOString(),
    };

    return {
      data: {},
      error: null,
    };
  };

  const changeCompetitionArchiveStatus = async (
    competitionId: string,
    form: ChangeCompetitionArchiveStatusForm,
  ): Promise<{ data: {} | null; error: ApiError | null }> => {
    await delay(500);

    const index = mockCompetitions.findIndex((c) => c.id === competitionId);

    if (index === -1) {
      return {
        data: null,
        error: {
          code: "USER_NOT_FOUND",
          message: "Соревнование не найдено",
          meta: null,
        },
      };
    }

    const currentCompetition = mockCompetitions[index]!;
    mockCompetitions[index] = {
      ...currentCompetition,
      is_archived: form.is_archived,
      updated_at: new Date().toISOString(),
    };

    return {
      data: {},
      error: null,
    };
  };

  const deleteCompetition = async (
    competitionId: string,
  ): Promise<{ data: {} | null; error: ApiError | null }> => {
    await delay(400);

    const index = mockCompetitions.findIndex((c) => c.id === competitionId);

    if (index === -1) {
      return {
        data: null,
        error: {
          code: "USER_NOT_FOUND",
          message: "Соревнование не найдено",
          meta: null,
        },
      };
    }

    mockCompetitions.splice(index, 1);

    return {
      data: {},
      error: null,
    };
  };

  const attachAvatar = async (
    file: File,
  ): Promise<{ data: {} | null; error: ApiError | null }> => {
    await delay(500);

    // Validate file type
    const allowedTypes = ["image/jpeg", "image/png", "image/gif", "image/webp"];
    if (!allowedTypes.includes(file.type)) {
      return {
        data: null,
        error: {
          code: "INVALID_AVATAR_ERROR",
          message: "Неверный формат файла. Допустимы только JPEG, PNG, GIF, WEBP",
          meta: { reason: "Invalid file format" },
        },
      };
    }

    // Validate file size (max 5MB)
    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
      return {
        data: null,
        error: {
          code: "INVALID_AVATAR_ERROR",
          message: "Размер файла не должен превышать 5 МБ",
          meta: { reason: "File too large" },
        },
      };
    }

    // Simulate successful upload by creating a temporary URL
    currentAvatarUrl = URL.createObjectURL(file);

    return {
      data: {},
      error: null,
    };
  };

  const detachAvatar = async (): Promise<{
    data: {} | null;
    error: ApiError | null;
  }> => {
    await delay(300);

    currentAvatarUrl = null;

    return {
      data: {},
      error: null,
    };
  };

  const getPreviewCompetitions = async (
    page: number = 1,
  ): Promise<{ data: PreviewCompetitionsList | null; error: ApiError | null }> => {
    await delay(400);

    const pageSize = 10;
    const start = (page - 1) * pageSize;
    const items = mockPreviewCompetitions.slice(start, start + pageSize);

    return {
      data: {
        items,
        total: mockPreviewCompetitions.length,
        page,
      },
      error: null,
    };
  };

  const exploreCompetitions = async (
    filters: ExploreCompetitionsFilters = {},
  ): Promise<{ data: ExploreCompetitionsList | null; error: ApiError | null }> => {
    await delay(350);

    const page = filters.page ?? 1;
    if (page < 1) {
      return {
        data: null,
        error: { code: "VALIDATION_ERROR", message: "Invalid page", meta: null },
      };
    }

    let filtered = mockPreviewCompetitions;

    const search = filters.search?.trim().toLowerCase();
    if (search) {
      filtered = filtered.filter((competition) =>
        competition.title.toLowerCase().includes(search) ||
        competition.tags.some((tag) => tag.value.toLowerCase().includes(search)),
      );
    }

    if (filters.tag_ids?.length) {
      const requested = new Set(filters.tag_ids);
      filtered = filtered.filter((competition) =>
        competition.tags.some((tag) => requested.has(tag.id)),
      );
    }

    if (filters.min_team_size !== undefined) {
      filtered = filtered.filter((competition) =>
        (competition.team_size?.min ?? 1) >= filters.min_team_size!,
      );
    }

    if (filters.max_team_size !== undefined) {
      filtered = filtered.filter((competition) =>
        (competition.team_size?.max ?? 1) <= filters.max_team_size!,
      );
    }

    if (filters.auto_accept !== undefined) {
      filtered = filtered.filter(() => filters.auto_accept === false);
    }

    const sorted = [...filtered].sort((a, b) => {
      if ((filters.sort_by ?? "most_popular") === "newest") {
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      }
      return b.members_count - a.members_count;
    });

    const pageSize = 10;
    const start = (page - 1) * pageSize;

    return {
      data: {
        items: sorted.slice(start, start + pageSize),
        total: sorted.length,
        page,
      },
      error: null,
    };
  };

  const issueInvite = async (
    form: InviteForm,
  ): Promise<{ data: CreatedInvite | null; error: ApiError | null }> => {
    await delay(400);

    const newInvite: InviteModel = {
      id: `invite-${mockInviteCounter++}`,
      code: `MOCK-CODE-${Math.random().toString(36).slice(2, 10).toUpperCase()}`,
      display_name: form.display_name,
      created_by: "123e4567-e89b-12d3-a456-426614174000",
      is_revoked: false,
      is_used: false,
      used_by: null,
      created_at: new Date().toISOString(),
    };

    mockInvites.unshift(newInvite);

    return {
      data: {
        invite_id: newInvite.id,
        code: newInvite.code,
      },
      error: null,
    };
  };

  const listInvites = async (
    page: number = 1,
  ): Promise<{ data: InvitesList | null; error: ApiError | null }> => {
    await delay(300);

    const pageSize = 20;
    const start = (page - 1) * pageSize;
    const items = mockInvites.slice(start, start + pageSize);

    return {
      data: {
        items,
        total: mockInvites.length,
        page,
      },
      error: null,
    };
  };

  const revokeInvite = async (
    inviteId: string,
  ): Promise<{ data: {} | null; error: ApiError | null }> => {
    await delay(400);

    const invite = mockInvites.find((i) => i.id === inviteId);

    if (!invite) {
      return {
        data: null,
        error: {
          code: "INVITE_NOT_FOUND",
          message: "Invite not found",
          meta: null,
        },
      };
    }

    if (invite.is_revoked) {
      return {
        data: null,
        error: {
          code: "INVITE_ALREADY_REVOKED",
          message: "Invite is already revoked",
          meta: null,
        },
      };
    }

    if (invite.is_used) {
      return {
        data: null,
        error: {
          code: "INVITE_ALREADY_USED",
          message: "Cannot revoke a used invite",
          meta: null,
        },
      };
    }

    invite.is_revoked = true;

    return {
      data: {},
      error: null,
    };
  };

  const listAdminUsers = async (
    filters: AdminUsersFilters = {},
  ): Promise<{ data: AdminUsersList | null; error: ApiError | null }> => {
    await delay(300);

    const page = filters.page ?? 1;
    if (page < 1) {
      return {
        data: null,
        error: { code: "VALIDATION_ERROR", message: "Invalid page", meta: null },
      };
    }

    let filtered = mockAdminUsers;

    if (filters.search) {
      const query = filters.search.toLowerCase();
      filtered = filtered.filter((item) =>
        item.user.id === filters.search ||
        item.organizer?.organizer_name.toLowerCase().includes(query) ||
        item.participant?.full_name.toLowerCase().includes(query),
      );
    }

    if (filters.is_admin !== undefined) {
      filtered = filtered.filter((item) => item.user.is_admin === filters.is_admin);
    }

    if (filters.is_blocked !== undefined) {
      filtered = filtered.filter(
        (item) => item.user.ban_status.is_blocked === filters.is_blocked,
      );
    }

    if (filters.role === "organizer") {
      filtered = filtered.filter((item) => item.organizer !== null);
    } else if (filters.role === "participant") {
      filtered = filtered.filter((item) => item.participant !== null);
    }

    const pageSize = 20;
    const start = (page - 1) * pageSize;
    const items: AdminUserListItem[] = filtered
      .slice(start, start + pageSize)
      .map((item) => ({
        id: item.user.id,
        is_admin: item.user.is_admin,
        ban_status: item.user.ban_status,
        organizer_name: item.organizer?.organizer_name ?? null,
        participant_full_name: item.participant?.full_name ?? null,
      }));

    return {
      data: {
        items,
        total: filtered.length,
        page,
      },
      error: null,
    };
  };

  const readAdminUser = async (
    userId: string,
  ): Promise<{ data: AdminUserDetails | null; error: ApiError | null }> => {
    await delay(250);

    const user = mockAdminUsers.find((item) => item.user.id === userId);
    if (!user) {
      return {
        data: null,
        error: { code: "USER_NOT_FOUND", message: "User not found", meta: null },
      };
    }

    return { data: user, error: null };
  };

  const blockAdminUser = async (
    userId: string,
    input: AdminBlockUserInput,
  ): Promise<{ data: {} | null; error: ApiError | null }> => {
    await delay(400);

    const user = mockAdminUsers.find((item) => item.user.id === userId);
    if (!user) {
      return {
        data: null,
        error: { code: "USER_NOT_FOUND", message: "User not found", meta: null },
      };
    }

    user.user.ban_status = {
      is_blocked: true,
      reason: input.reason,
      blocked_at: new Date().toISOString(),
    };

    return { data: {}, error: null };
  };

  const unblockAdminUser = async (
    userId: string,
  ): Promise<{ data: {} | null; error: ApiError | null }> => {
    await delay(400);

    const user = mockAdminUsers.find((item) => item.user.id === userId);
    if (!user) {
      return {
        data: null,
        error: { code: "USER_NOT_FOUND", message: "User not found", meta: null },
      };
    }

    user.user.ban_status = {
      is_blocked: false,
      reason: null,
      blocked_at: null,
    };

    return { data: {}, error: null };
  };

  const listTags = async (
    filters: CompetitionTagsFilters = {},
  ): Promise<{ data: CompetitionTagsList | null; error: ApiError | null }> => {
    await delay(250);

    const page = filters.page ?? 1;
    if (page < 1) {
      return {
        data: null,
        error: { code: "VALIDATION_ERROR", message: "Invalid page", meta: null },
      };
    }

    const query = filters.search?.trim().toLowerCase();
    const filtered = mockTags
      .filter((tag) => !query || tag.value.toLowerCase().includes(query))
      .sort((a, b) => a.value.localeCompare(b.value) || a.id.localeCompare(b.id));
    const pageSize = 30;
    const start = (page - 1) * pageSize;

    return {
      data: {
        items: filtered.slice(start, start + pageSize),
        total: filtered.length,
        page,
      },
      error: null,
    };
  };

  const listAdminTags = listTags;

  const createAdminTag = async (
    form: CompetitionTagForm,
  ): Promise<{ data: CompetitionTag | null; error: ApiError | null }> => {
    await delay(300);

    const value = form.value.trim();
    if (!value) {
      return {
        data: null,
        error: {
          code: "INVALID_COMPETITION_DATA",
          message: "Tag value cannot be blank",
          meta: null,
        },
      };
    }

    if (value.length > 100) {
      return {
        data: null,
        error: {
          code: "VALIDATION_ERROR",
          message: "Tag value is too long",
          meta: null,
        },
      };
    }

    if (mockTags.some((tag) => tag.value.toLowerCase() === value.toLowerCase())) {
      return {
        data: null,
        error: {
          code: "COMPETITION_TAG_ALREADY_EXISTS",
          message: "Competition tag already exists",
          meta: null,
        },
      };
    }

    const tag = { id: crypto.randomUUID(), value };
    mockTags = [...mockTags, tag];
    return { data: tag, error: null };
  };

  const readAdminTag = async (
    tagId: string,
  ): Promise<{ data: CompetitionTag | null; error: ApiError | null }> => {
    await delay(200);

    const tag = mockTags.find((item) => item.id === tagId);
    if (!tag) {
      return {
        data: null,
        error: {
          code: "COMPETITION_TAG_NOT_FOUND",
          message: "Competition tag not found",
          meta: null,
        },
      };
    }

    return { data: tag, error: null };
  };

  const deleteAdminTag = async (
    tagId: string,
  ): Promise<{ data: {} | null; error: ApiError | null }> => {
    await delay(300);

    if (!mockTags.some((tag) => tag.id === tagId)) {
      return {
        data: null,
        error: {
          code: "COMPETITION_TAG_NOT_FOUND",
          message: "Competition tag not found",
          meta: null,
        },
      };
    }

    mockTags = mockTags.filter((tag) => tag.id !== tagId);
    for (const competition of [...mockCompetitions, ...mockPreviewCompetitions]) {
      competition.tags = competition.tags.filter((tag) => tag.id !== tagId);
    }

    return { data: {}, error: null };
  };

  const registerParticipant = async (
    form: ParticipantForm,
  ): Promise<{ data: CreatedParticipant | null; error: ApiError | null }> => {
    await delay(500);

    if (isParticipantRegistered || isRegistered) {
      return {
        data: null,
        error: {
          code: "PARTICIPANT_ALREADY_EXISTS",
          message: "Вы уже зарегистрированы как участник",
          meta: null,
        },
      };
    }

    if (!form.full_name.trim() || form.full_name.length > 70) {
      return {
        data: null,
        error: { code: "VALIDATION_ERROR", message: "Некорректное имя", meta: null },
      };
    }


    isParticipantRegistered = true;
    return {
      data: {
        participant_id: crypto.randomUUID(),
        user_id: "123e4567-e89b-12d3-a456-426614174000",
      },
      error: null,
    };
  };

  const updateParticipant = async (
    form: UpdateParticipantForm,
  ): Promise<{ data: {} | null; error: ApiError | null }> => {
    await delay(400);

    if (!form.full_name.trim() || form.full_name.length > 70) {
      return {
        data: null,
        error: { code: "VALIDATION_ERROR", message: "Некорректное имя", meta: null },
      };
    }

    if ((form.contacts?.length ?? 0) > 15) {
      return {
        data: null,
        error: { code: "VALIDATION_ERROR", message: "Too many contacts", meta: null },
      };
    }

    mockParticipantUser.participant = {
      id: mockParticipantUser.participant?.id ?? crypto.randomUUID(),
      user_id: mockParticipantUser.user_id,
      full_name: form.full_name,
      participant_type: form.participant_type,
      age: form.age,
      bio: form.bio ?? null,
      skills: form.skills ?? [],
      experience_level: form.experience_level ?? null,
      contacts: form.contacts ?? [],
    };

    isParticipantRegistered = true;
    return { data: {}, error: null };
  };

  const MOCK_SUPERUSER_PASSWORD = "superuser123";
let mockSuperuserCreated = false;
const mockExportJobs = new Map<string, ExportJobModel>();

  const registerSuperuser = async (
    password: string,
  ): Promise<{ data: CreatedSuperuser | null; error: ApiError | null }> => {
    await delay(500);

    if (password !== MOCK_SUPERUSER_PASSWORD) {
      return {
        data: null,
        error: {
          code: "INVALID_SUPERUSER_PASSWORD",
          message: "Неверный пароль суперпользователя",
          meta: null,
        },
      };
    }

    if (mockSuperuserCreated) {
      return {
        data: null,
        error: {
          code: "AUTH_USER_ALREADY_EXISTS",
          message: "Суперпользователь уже зарегистрирован",
          meta: null,
        },
      };
    }

    mockSuperuserCreated = true;
    mockUnregisteredUser.is_admin = true;
    return {
      data: { user_id: crypto.randomUUID() },
      error: null,
    };
  };

  const createExportJob = async (
    input: CreateExportJobInput,
  ): Promise<{ data: CreatedExportJob | null; error: ApiError | null }> => {
    await delay(300);

    const allowedStatuses: ApplicationStatus[] = ["pending", "accepted", "rejected"];
    const applicationStatus = input.application_status ?? null;
    if (applicationStatus !== null && !allowedStatuses.includes(applicationStatus)) {
      return {
        data: null,
        error: {
          code: "VALIDATION_ERROR",
          message: "Invalid application status",
          meta: null,
        },
      };
    }

    const jobId = crypto.randomUUID();
    const now = new Date().toISOString();
    mockExportJobs.set(jobId, {
      id: jobId,
      user_id: "123e4567-e89b-12d3-a456-426614174000",
      competition_id: input.competition_id,
      application_status: applicationStatus,
      status_kind: "pending",
      status_reason: null,
      file_url: null,
      created_at: now,
      finished_at: null,
    });

    setTimeout(() => {
      const job = mockExportJobs.get(jobId);
      if (!job) {
        return;
      }

      mockExportJobs.set(jobId, {
        ...job,
        status_kind: "success",
        file_url: `/mock-exports/${jobId}.csv`,
        finished_at: new Date().toISOString(),
      });
    }, 1200);

    return {
      data: { job_id: jobId },
      error: null,
    };
  };

  const submitApplication = async (
    competitionId: string,
    form: SubmitApplicationForm,
  ): Promise<{ data: CreatedApplication | null; error: ApiError | null }> => {
    await delay(500);

    const competition = mockCompetitions.find((item) => item.id === competitionId) ??
      (await getExploreCompetition(competitionId)).data;
    if (!competition) {
      return {
        data: null,
        error: {
          code: "COMPETITION_NOT_FOUND",
          message: "Competition not found",
          meta: null,
        },
      };
    }

    const normalizedTrack = form.track.name.trim().toLowerCase();
    const selectedTrack = competition.tracks.find(
      (track) => track.name.trim().toLowerCase() === normalizedTrack,
    );
    if (!selectedTrack) {
      return {
        data: null,
        error: {
          code: "INVALID_APPLICATION_DATA",
          message: "Selected track is not available for this competition",
          meta: null,
        },
      };
    }

    if (mockApplications.some((item) => item.competition_id === competitionId)) {
      return {
        data: null,
        error: {
          code: "APPLICATION_ALREADY_EXISTS",
          message: "Application already exists",
          meta: null,
        },
      };
    }

    const applicationId = crypto.randomUUID();
    mockApplications.unshift({
      id: applicationId,
      competition_id: competitionId,
      competition_name: competition.title,
      track: selectedTrack,
      status: "pending",
      created_at: new Date().toISOString(),
      form_data: form.form_data,
      participant: {
        id: mockParticipantUser.participant?.id ?? crypto.randomUUID(),
        full_name: mockParticipantUser.participant?.full_name ?? "Иван Петров",
        bio: mockParticipantUser.participant?.bio ?? null,
        participant_type: mockParticipantUser.participant?.participant_type ?? "student",
        age: mockParticipantUser.participant?.age ?? 22,
        skills: mockParticipantUser.participant?.skills ?? [],
        experience_level: mockParticipantUser.participant?.experience_level ?? null,
        contacts: mockParticipantUser.participant?.contacts ?? [],
      },
    });

    return { data: { application_id: applicationId }, error: null };
  };

  const toMyApplication = (application: ApplicationModel): MyApplicationModel => ({
    id: application.id,
    participant_id: application.participant.id,
    competition_id: application.competition_id,
    competition_name: application.competition_name,
    track: application.track,
    status: application.status,
    created_at: application.created_at,
    form_data: application.form_data,
  });

  const listApplicationsByCompetition = async (
    competitionId: string,
    page: number = 1,
    _sortOrder: SortOrder = "desc",
    status?: ApplicationStatus,
  ): Promise<{ data: ApplicationsList | null; error: ApiError | null }> => {
    await delay(300);

    let filtered = mockApplications.filter((application) => application.competition_id === competitionId);
    if (status) {
      filtered = filtered.filter((application) => application.status === status);
    }

    const pageSize = 10;
    const start = (page - 1) * pageSize;
    return {
      data: {
        items: filtered.slice(start, start + pageSize),
        total: filtered.length,
        page,
      },
      error: null,
    };
  };

  const listMyApplications = async (
    page: number = 1,
    _sortOrder: SortOrder = "desc",
    status?: ApplicationStatus,
  ): Promise<{ data: MyApplicationsList | null; error: ApiError | null }> => {
    await delay(300);

    let filtered = mockApplications;
    if (status) {
      filtered = filtered.filter((application) => application.status === status);
    }

    const pageSize = 10;
    const start = (page - 1) * pageSize;
    return {
      data: {
        items: filtered.slice(start, start + pageSize).map(toMyApplication),
        total: filtered.length,
        page,
      },
      error: null,
    };
  };

  const readMyApplication = async (
    applicationId: string,
  ): Promise<{ data: MyApplicationModel | null; error: ApiError | null }> => {
    await delay(250);

    const application = mockApplications.find((item) => item.id === applicationId);
    if (!application) {
      return {
        data: null,
        error: {
          code: "APPLICATION_NOT_FOUND",
          message: "Application not found",
          meta: null,
        },
      };
    }

    return { data: toMyApplication(application), error: null };
  };

  const readApplication = async (
    applicationId: string,
  ): Promise<{ data: ApplicationModel | null; error: ApiError | null }> => {
    await delay(250);

    const application = mockApplications.find((item) => item.id === applicationId);
    if (!application) {
      return {
        data: null,
        error: {
          code: "APPLICATION_NOT_FOUND",
          message: "Application not found",
          meta: null,
        },
      };
    }

    return { data: application, error: null };
  };

  const withdrawApplication = async (
    applicationId: string,
  ): Promise<{ data: {} | null; error: ApiError | null }> => {
    await delay(300);

    const before = mockApplications.length;
    mockApplications = mockApplications.filter((item) => item.id !== applicationId);
    if (mockApplications.length === before) {
      return {
        data: null,
        error: {
          code: "APPLICATION_NOT_FOUND",
          message: "Application not found",
          meta: null,
        },
      };
    }

    return { data: {}, error: null };
  };

  const resolveApplication = async (
    applicationId: string,
    status: "accepted" | "rejected",
  ): Promise<{ data: {} | null; error: ApiError | null }> => {
    await delay(300);

    const application = mockApplications.find((item) => item.id === applicationId);
    if (!application) {
      return {
        data: null,
        error: {
          code: "APPLICATION_NOT_FOUND",
          message: "Application not found",
          meta: null,
        },
      };
    }

    application.status = status;
    return { data: {}, error: null };
  };

  const readExportJob = async (
    jobId: string,
  ): Promise<{ data: ExportJobModel | null; error: ApiError | null }> => {
    await delay(250);

    const job = mockExportJobs.get(jobId);
    if (!job) {
      return {
        data: null,
        error: {
          code: "EXPORT_JOB_NOT_FOUND",
          message: "Export job not found",
          meta: null,
        },
      };
    }

    return {
      data: job,
      error: null,
    };
  };

  const notImplemented = async () => ({
    data: null,
    error: { code: "INTERNAL_SERVER_ERROR", message: "Not available in mock mode", meta: null },
  });

  return {
    checkAuth,
    registerOrganizer,
    getUserProfile,
    listCompetitions,
    getPreviewCompetitions,
    exploreCompetitions,
    createCompetition,
    getCompetition,
    updateCompetitionGeneralInfo,
    rescheduleCompetition,
    changeCompetitionArchiveStatus,
    deleteCompetition,
    deleteUserProfile,
    attachAvatar,
    detachAvatar,
    issueInvite,
    listInvites,
    revokeInvite,
    listAdminUsers,
    readAdminUser,
    blockAdminUser,
    unblockAdminUser,
    listTags,
    listAdminTags,
    createAdminTag,
    readAdminTag,
    deleteAdminTag,
    registerParticipant,
    updateParticipant,
    updateOrganizer: notImplemented,
    registerSuperuser,
    getApplicationForm: notImplemented,
    getMyApplicationForm: notImplemented,
    createApplicationForm: notImplemented,
    deleteApplicationForm: notImplemented,
    submitApplication,
    listApplicationsByCompetition,
    listMyApplications,
    readMyApplication,
    readApplication,
    withdrawApplication,
    acceptApplication: (applicationId: string) => resolveApplication(applicationId, "accepted"),
    rejectApplication: (applicationId: string) => resolveApplication(applicationId, "rejected"),
    createExportJob,
    readExportJob,
    getExploreCompetition,
  };
};
