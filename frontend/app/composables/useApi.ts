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
  PreviewCompetitionsList,
  InviteForm,
  CreatedInvite,
  InvitesList,
  CreatedSuperuser,
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
    // Structured API error response with a known error code
    if (error.data && typeof error.data === "object" && error.data.code) {
      return {
        code: error.data.code,
        message: error.data.message || "An unexpected error occurred",
        meta: error.data.meta || null,
      };
    }

    // Server responded but without a structured body (e.g. 500 plain-text)
    const statusCode: number = error.status ?? error.statusCode ?? 0;
    if (statusCode >= 500) {
      return {
        code: "INTERNAL_SERVER_ERROR",
        message: "Internal server error",
        meta: null,
      };
    }

    // Network-level failure: server unreachable, DNS failure, timeout, etc.
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

  const getPreviewCompetitions = async (
    page: number = 1,
  ): Promise<{ data: PreviewCompetitionsList | null; error: ApiError | null }> => {
    try {
      const data = await $fetch<PreviewCompetitionsList>(
        `${apiBase}/api/competitions/preview`,
        {
          method: "GET",
          params: { page },
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

  const attachAvatar = async (
    file: File,
  ): Promise<{ data: {} | null; error: ApiError | null }> => {
    try {
      const formData = new FormData();
      formData.append("file", file);

      const data = await $fetch<{}>(`${apiBase}/api/users/me/avatar`, {
        method: "PUT",
        body: formData,
      });
      return { data, error: null };
    } catch (err: any) {
      return { data: null, error: handleApiError(err) };
    }
  };

  const detachAvatar = async (): Promise<{
    data: {} | null;
    error: ApiError | null;
  }> => {
    try {
      const data = await $fetch<{}>(`${apiBase}/api/users/me/avatar`, {
        method: "DELETE",
      });
      return { data, error: null };
    } catch (err: any) {
      return { data: null, error: handleApiError(err) };
    }
  };

  const issueInvite = async (
    form: InviteForm,
  ): Promise<{ data: CreatedInvite | null; error: ApiError | null }> => {
    try {
      const data = await $fetch<CreatedInvite>(`${apiBase}/api/invites/`, {
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

  const listInvites = async (
    page: number = 1,
  ): Promise<{ data: InvitesList | null; error: ApiError | null }> => {
    try {
      const data = await $fetch<InvitesList>(`${apiBase}/api/invites/`, {
        method: "GET",
        params: { page },
      });
      return { data, error: null };
    } catch (err: any) {
      return { data: null, error: handleApiError(err) };
    }
  };

  const revokeInvite = async (
    inviteId: string,
  ): Promise<{ data: {} | null; error: ApiError | null }> => {
    try {
      const data = await $fetch<{}>(`${apiBase}/api/invites/${inviteId}`, {
        method: "DELETE",
      });
      return { data, error: null };
    } catch (err: any) {
      return { data: null, error: handleApiError(err) };
    }
  };

  const registerSuperuser = async (
    password: string,
  ): Promise<{ data: CreatedSuperuser | null; error: ApiError | null }> => {
    try {
      const data = await $fetch<CreatedSuperuser>(`${apiBase}/api/users/superuser/`, {
        method: "POST",
        body: { password },
        headers: { "Content-Type": "application/json" },
      });
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
    getPreviewCompetitions,
    createCompetition,
    getCompetition,
    updateCompetition,
    deleteCompetition,
    deleteUserProfile,
    attachAvatar,
    detachAvatar,
    issueInvite,
    listInvites,
    revokeInvite,
    registerSuperuser,
  };
};
