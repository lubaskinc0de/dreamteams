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

  /**
   * Check if user is authenticated via OAuth2
   * Returns true if authenticated, false otherwise
   */
  const checkAuth = async (): Promise<boolean> => {
    try {
      await $fetch(`${apiBase}/oauth2/auth`, {
        method: "GET",
      });
      return true;
    } catch {
      return false;
    }
  };

  const registerOrganizer = async (
    form: OrganizerForm,
  ): Promise<{ data: CreatedOrganizer | null; error: ApiError | null }> => {
    try {
      const data = await $fetch<CreatedOrganizer>(`${apiBase}/api/organizers/`, {
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
      const data = await $fetch<ProfileModel>(`${apiBase}/api/users/me`, {
        method: "GET",
      });
      return { data, error: null };
    } catch (err: any) {
      return { data: null, error: handleApiError(err) };
    }
  };

  const deleteUserProfile = async (): Promise<{
    data: null;
    error: ApiError | null;
  }> => {
    try {
      const data = await $fetch<null>(`${apiBase}/api/users/me`, {
        method: "DELETE",
      });
      return { data, error: null };
    } catch (err: any) {
      return { data: null, error: handleApiError(err) };
    }
  };

  const listCompetitions = async (
    page: number = 1,
    sortBy: CompetitionSortBy = "created_at",
    sortOrder: SortOrder = "desc",
    isArchived?: boolean,
    search?: string,
  ): Promise<{ data: CompetitionsList | null; error: ApiError | null }> => {
    try {
      const params: Record<string, any> = {
        page,
        sort_by: sortBy,
        sort_order: sortOrder,
      };

      if (isArchived !== undefined) {
        params.is_archived = isArchived;
      }

      if (search) {
        params.search = search;
      }

      const data = await $fetch<CompetitionsList>(
        `${apiBase}/api/competitions/`,
        {
          method: "GET",
          params,
        },
      );
      return { data, error: null };
    } catch (err: any) {
      return { data: null, error: handleApiError(err) };
    }
  };

  const createCompetition = async (
    form: CompetitionForm,
  ): Promise<{ data: CreatedCompetition | null; error: ApiError | null }> => {
    try {
      const data = await $fetch<CreatedCompetition>(
        `${apiBase}/api/competitions/`,
        {
          method: "POST",
          body: form,
          headers: {
            "Content-Type": "application/json",
          },
        },
      );
      return { data, error: null };
    } catch (err: any) {
      return { data: null, error: handleApiError(err) };
    }
  };

  const getCompetition = async (
    competitionId: string,
  ): Promise<{ data: CompetitionModel | null; error: ApiError | null }> => {
    try {
      const data = await $fetch<CompetitionModel>(
        `${apiBase}/api/competitions/${competitionId}`,
        {
          method: "GET",
        },
      );
      return { data, error: null };
    } catch (err: any) {
      return { data: null, error: handleApiError(err) };
    }
  };

  const updateCompetition = async (
    competitionId: string,
    form: UpdateCompetitionForm,
  ): Promise<{ data: {} | null; error: ApiError | null }> => {
    try {
      const data = await $fetch<{}>(
        `${apiBase}/api/competitions/${competitionId}`,
        {
          method: "PUT",
          body: form,
          headers: {
            "Content-Type": "application/json",
          },
        },
      );
      return { data, error: null };
    } catch (err: any) {
      return { data: null, error: handleApiError(err) };
    }
  };

  const deleteCompetition = async (
    competitionId: string,
  ): Promise<{ data: {} | null; error: ApiError | null }> => {
    try {
      const data = await $fetch<{}>(
        `${apiBase}/api/competitions/${competitionId}`,
        {
          method: "DELETE",
        },
      );
      return { data, error: null };
    } catch (err: any) {
      return { data: null, error: handleApiError(err) };
    }
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
