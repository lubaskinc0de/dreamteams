import { success } from "zod";
import type {
  ApiError,
  OrganizerForm,
  CreatedOrganizer,
  ProfileModel,
  CompetitionForm,
  UpdateCompetitionForm,
  CreatedCompetition,
  CompetitionModel,
  CompetitionsList,
  CompetitionSortBy,
  SortOrder,
} from "~/types/api";

// Mock data
const mockUser: ProfileModel = {
  user_id: "123e4567-e89b-12d3-a456-426614174000",
  organizer: {
    id: "123e4567-e89b-12d3-a456-426614174001",
    user_id: "123e4567-e89b-12d3-a456-426614174000",
    organizer_name: "IT-компания TechHub",
    phone_number: "+79991234567",
    contact_email: "ivan@example.com",
    logo: null,
  },
};

const mockUserWithoutOrganizer: ProfileModel = {
  user_id: "123e4567-e89b-12d3-a456-426614174000",
  organizer: null,
};

// Storage for current state
let isRegistered = false;

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
    participant_limits: { min: 50, max: 200 },
    domains: ["frontend", "backend"],
    participant_type: "student",
    venue: { format: "hybrid", location: "Москва, Технопарк" },
    team_size: { min: 2, max: 5 },
    milestones: [
      { title: "Открытие регистрации", timestamp: "2026-02-01T00:00:00Z" },
      { title: "Начало хакатона", timestamp: "2026-03-15T10:00:00Z" },
      { title: "Защита проектов", timestamp: "2026-03-17T14:00:00Z" },
    ],
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
    participant_limits: { min: 20, max: 100 },
    domains: ["ai", "backend"],
    participant_type: "any",
    venue: { format: "online", location: null },
    team_size: { min: 1, max: 3 },
    milestones: [],
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
    participant_limits: { min: 30, max: 150 },
    domains: ["mobile"],
    participant_type: "schoolchild",
    venue: { format: "offline", location: "Санкт-Петербург" },
    team_size: { min: 2, max: 4 },
    milestones: [
      { title: "Старт регистрации", timestamp: "2026-03-01T00:00:00Z" },
    ],
    is_archived: false,
    created_at: "2025-12-15T12:00:00Z",
    updated_at: "2025-12-15T12:00:00Z",
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

    return {
      data: isRegistered ? mockUser : mockUserWithoutOrganizer,
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
  ): Promise<{ data: CompetitionsList | null; error: ApiError | null }> => {
    await delay(300);

    // Filter by is_archived if specified
    let filtered = mockCompetitions;
    if (isArchived !== undefined) {
      filtered = mockCompetitions.filter((c) => c.is_archived === isArchived);
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

    const newCompetition: CompetitionModel = {
      id: `comp-${Date.now()}`,
      organizer_id: "123e4567-e89b-12d3-a456-426614174001",
      title: form.title,
      banner: null,
      description: form.description,
      schedule: form.schedule,
      participant_limits: form.participant_limits,
      domains: form.domains,
      participant_type: form.participant_type,
      venue: form.venue,
      team_size: form.team_size,
      milestones: form.milestones || [],
      is_archived: false,
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

  const updateCompetition = async (
    competitionId: string,
    form: UpdateCompetitionForm,
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

    // Update the competition
    const currentCompetition = mockCompetitions[index]!;
    mockCompetitions[index] = {
      id: currentCompetition.id,
      organizer_id: currentCompetition.organizer_id,
      banner: currentCompetition.banner,
      title: form.title,
      description: form.description,
      schedule: form.schedule,
      participant_limits: form.participant_limits,
      domains: form.domains,
      participant_type: form.participant_type,
      venue: form.venue,
      team_size: form.team_size,
      milestones: form.milestones,
      is_archived: form.is_archived,
      created_at: currentCompetition.created_at,
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

  return {
    checkAuth,
    registerOrganizer,
    getUserProfile,
    listCompetitions,
    createCompetition,
    getCompetition,
    updateCompetition,
    deleteCompetition,
    deleteUserProfile,
  };
};
