import type {
  ApiError,
  OrganizerForm,
  CreatedOrganizer,
  ProfileModel,
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

export const useMockApi = () => {
  const delay = (ms: number) =>
    new Promise((resolve) => setTimeout(resolve, ms));

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

  return {
    registerOrganizer,
    getUserProfile,
  };
};
