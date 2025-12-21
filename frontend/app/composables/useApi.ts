import type {
  ApiError,
  OrganizerForm,
  CreatedOrganizer,
  ProfileModel,
} from "~/types/api";

export const useApi = () => {
  const config = useRuntimeConfig();
  const apiBase = config.public.apiBase;
  const useMock = config.public.useMock;

  // If mock mode is enabled, use mock API
  if (useMock === "true" || useMock.toString() === "true") {
    return useMockApi();
  }

  const handleApiError = (error: any): ApiError => {
    if (error.data && typeof error.data === "object") {
      return {
        code: error.data.code || "UNKNOWN_ERROR",
        message: error.data.message || "An unexpected error occurred",
        meta: error.data.meta || null,
      };
    }

    return {
      code: "NETWORK_ERROR",
      message: error.message || "Network error occurred",
      meta: null,
    };
  };

  const registerOrganizer = async (
    form: OrganizerForm,
  ): Promise<{ data: CreatedOrganizer | null; error: ApiError | null }> => {
    try {
      const data = await $fetch<CreatedOrganizer>(`${apiBase}/organizers/`, {
        method: "POST",
        body: form,
        headers: {
          "Content-Type": "application/json",
        },
      });
      return { data, error: null };
    } catch (err: any) {
      return { data: null, error: handleApiError(err) };
    }
  };

  const getUserProfile = async (): Promise<{
    data: ProfileModel | null;
    error: ApiError | null;
  }> => {
    try {
      const data = await $fetch<ProfileModel>(`${apiBase}/users/me`, {
        method: "GET",
      });
      return { data, error: null };
    } catch (err: any) {
      return { data: null, error: handleApiError(err) };
    }
  };

  return {
    registerOrganizer,
    getUserProfile,
  };
};
