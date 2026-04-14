import type {
  ApiError,
  OrganizerForm,
  CreatedOrganizer,
  ProfileModel,
  ParticipantForm,
  CreatedParticipant,
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
  ApplicationFormInput,
  CreatedApplicationForm,
  ApplicationFormModel,
  SubmitApplicationForm,
  CreatedApplication,
  ApplicationModel,
  ApplicationsList,
} from "~/types/api";

interface RetryConfig {
  timeout: number;
  maxRetries: number;
  baseDelay: number;
  maxDelay: number;
}

const sleep = (ms: number) => new Promise<void>((resolve) => setTimeout(resolve, ms));

/**
 * Wraps a $fetch call with exponential backoff retry logic.
 * Retries only on transient errors: network failures, 5xx, and 429.
 * 4xx client errors (except 429) are not retried.
 */
const retryFetch = async <T>(
  fn: () => Promise<T>,
  cfg: RetryConfig,
): Promise<T> => {
  let attempt = 0;
  while (true) {
    try {
      return await fn();
    } catch (err: any) {
      const status: number = err.status ?? err.statusCode ?? 0;
      const isTransient = status === 0 || status === 429 || status >= 500;

      if (!isTransient || attempt >= cfg.maxRetries) {
        throw err;
      }

      const jitter = Math.random() * cfg.baseDelay;
      const delay = Math.min(
        cfg.baseDelay * Math.pow(2, attempt) + jitter,
        cfg.maxDelay,
      );
      await sleep(delay);
      attempt++;
    }
  }
};

export const useApi = () => {
  const config = useRuntimeConfig();
  const apiBase = config.public.apiBase;
  const useMock = config.public.useMock;

  // If mock mode is enabled, use mock API
  if (useMock === "true" || useMock.toString() === "true") {
    return useMockApi();
  }

  const retryCfg: RetryConfig = {
    timeout: config.public.apiTimeout as number,
    maxRetries: config.public.apiMaxRetries as number,
    baseDelay: config.public.apiRetryBaseDelay as number,
    maxDelay: config.public.apiRetryMaxDelay as number,
  };

  /** $fetch with timeout and automatic exponential-backoff retries. */
  const apiFetch = <T>(
    url: string,
    options?: Parameters<typeof $fetch>[1],
  ): Promise<T> =>
    retryFetch(
      () => $fetch<T>(url, { timeout: retryCfg.timeout, ...options }),
      retryCfg,
    );

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
        timeout: retryCfg.timeout,
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
      const data = await apiFetch<CreatedOrganizer>(`${apiBase}/api/organizers/`, {
        method: "POST",
        body: form,
        headers: { "Content-Type": "application/json" },
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
      const data = await apiFetch<ProfileModel>(`${apiBase}/api/users/me`, {
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
      const data = await apiFetch<null>(`${apiBase}/api/users/me`, {
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

      const data = await apiFetch<CompetitionsList>(
        `${apiBase}/api/competitions/`,
        { method: "GET", params },
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
      const data = await apiFetch<PreviewCompetitionsList>(
        `${apiBase}/api/competitions/preview`,
        { method: "GET", params: { page } },
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
      const data = await apiFetch<CreatedCompetition>(
        `${apiBase}/api/competitions/`,
        { method: "POST", body: form, headers: { "Content-Type": "application/json" } },
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
      const data = await apiFetch<CompetitionModel>(
        `${apiBase}/api/competitions/${competitionId}`,
        { method: "GET" },
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
      const data = await apiFetch<{}>(
        `${apiBase}/api/competitions/${competitionId}`,
        { method: "PUT", body: form, headers: { "Content-Type": "application/json" } },
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
      const data = await apiFetch<{}>(
        `${apiBase}/api/competitions/${competitionId}`,
        { method: "DELETE" },
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

      const data = await apiFetch<{}>(`${apiBase}/api/users/me/avatar`, {
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
      const data = await apiFetch<{}>(`${apiBase}/api/users/me/avatar`, {
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
      const data = await apiFetch<CreatedInvite>(`${apiBase}/api/invites/`, {
        method: "POST",
        body: form,
        headers: { "Content-Type": "application/json" },
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
      const data = await apiFetch<InvitesList>(`${apiBase}/api/invites/`, {
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
      const data = await apiFetch<{}>(`${apiBase}/api/invites/${inviteId}`, {
        method: "DELETE",
      });
      return { data, error: null };
    } catch (err: any) {
      return { data: null, error: handleApiError(err) };
    }
  };

  const registerParticipant = async (
    form: ParticipantForm,
  ): Promise<{ data: CreatedParticipant | null; error: ApiError | null }> => {
    try {
      const data = await apiFetch<CreatedParticipant>(`${apiBase}/api/participants/`, {
        method: "POST",
        body: form,
        headers: { "Content-Type": "application/json" },
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
      const data = await apiFetch<CreatedSuperuser>(`${apiBase}/api/users/superuser/`, {
        method: "POST",
        body: { password },
        headers: { "Content-Type": "application/json" },
      });
      return { data, error: null };
    } catch (err: any) {
      return { data: null, error: handleApiError(err) };
    }
  };

  // Application Form endpoints

  const getApplicationForm = async (
    competitionId: string,
  ): Promise<{ data: ApplicationFormModel | null; error: ApiError | null }> => {
    try {
      const data = await apiFetch<ApplicationFormModel>(
        `${apiBase}/api/competitions/${competitionId}/application-form/`,
        { method: "GET" },
      );
      return { data, error: null };
    } catch (err: any) {
      return { data: null, error: handleApiError(err) };
    }
  };

  const createApplicationForm = async (
    competitionId: string,
    form: ApplicationFormInput,
  ): Promise<{ data: CreatedApplicationForm | null; error: ApiError | null }> => {
    try {
      const data = await apiFetch<CreatedApplicationForm>(
        `${apiBase}/api/competitions/${competitionId}/application-form/`,
        { method: "POST", body: form, headers: { "Content-Type": "application/json" } },
      );
      return { data, error: null };
    } catch (err: any) {
      return { data: null, error: handleApiError(err) };
    }
  };

  const deleteApplicationForm = async (
    competitionId: string,
  ): Promise<{ data: {} | null; error: ApiError | null }> => {
    try {
      const data = await apiFetch<{}>(
        `${apiBase}/api/competitions/${competitionId}/application-form/`,
        { method: "DELETE" },
      );
      return { data, error: null };
    } catch (err: any) {
      return { data: null, error: handleApiError(err) };
    }
  };

  // Application endpoints

  const submitApplication = async (
    competitionId: string,
    form: SubmitApplicationForm,
  ): Promise<{ data: CreatedApplication | null; error: ApiError | null }> => {
    try {
      const data = await apiFetch<CreatedApplication>(
        `${apiBase}/api/competitions/${competitionId}/applications/`,
        { method: "POST", body: form, headers: { "Content-Type": "application/json" } },
      );
      return { data, error: null };
    } catch (err: any) {
      return { data: null, error: handleApiError(err) };
    }
  };

  const listApplicationsByCompetition = async (
    competitionId: string,
    page: number = 1,
  ): Promise<{ data: ApplicationsList | null; error: ApiError | null }> => {
    try {
      const data = await apiFetch<ApplicationsList>(
        `${apiBase}/api/competitions/${competitionId}/applications/`,
        { method: "GET", params: { page } },
      );
      return { data, error: null };
    } catch (err: any) {
      return { data: null, error: handleApiError(err) };
    }
  };

  const listMyApplications = async (
    page: number = 1,
  ): Promise<{ data: ApplicationsList | null; error: ApiError | null }> => {
    try {
      const data = await apiFetch<ApplicationsList>(
        `${apiBase}/api/applications/`,
        { method: "GET", params: { page } },
      );
      return { data, error: null };
    } catch (err: any) {
      return { data: null, error: handleApiError(err) };
    }
  };

  const readMyApplication = async (
    applicationId: string,
  ): Promise<{ data: ApplicationModel | null; error: ApiError | null }> => {
    try {
      const data = await apiFetch<ApplicationModel>(
        `${apiBase}/api/applications/${applicationId}/my/`,
        { method: "GET" },
      );
      return { data, error: null };
    } catch (err: any) {
      return { data: null, error: handleApiError(err) };
    }
  };

  const readApplication = async (
    applicationId: string,
  ): Promise<{ data: ApplicationModel | null; error: ApiError | null }> => {
    try {
      const data = await apiFetch<ApplicationModel>(
        `${apiBase}/api/applications/${applicationId}/`,
        { method: "GET" },
      );
      return { data, error: null };
    } catch (err: any) {
      return { data: null, error: handleApiError(err) };
    }
  };

  const withdrawApplication = async (
    applicationId: string,
  ): Promise<{ data: {} | null; error: ApiError | null }> => {
    try {
      const data = await apiFetch<{}>(
        `${apiBase}/api/applications/${applicationId}/`,
        { method: "DELETE" },
      );
      return { data, error: null };
    } catch (err: any) {
      return { data: null, error: handleApiError(err) };
    }
  };

  const acceptApplication = async (
    applicationId: string,
  ): Promise<{ data: {} | null; error: ApiError | null }> => {
    try {
      const data = await apiFetch<{}>(
        `${apiBase}/api/applications/${applicationId}/accept/`,
        { method: "POST" },
      );
      return { data, error: null };
    } catch (err: any) {
      return { data: null, error: handleApiError(err) };
    }
  };

  const rejectApplication = async (
    applicationId: string,
  ): Promise<{ data: {} | null; error: ApiError | null }> => {
    try {
      const data = await apiFetch<{}>(
        `${apiBase}/api/applications/${applicationId}/reject/`,
        { method: "POST" },
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
    registerParticipant,
    registerSuperuser,
    getApplicationForm,
    createApplicationForm,
    deleteApplicationForm,
    submitApplication,
    listApplicationsByCompetition,
    listMyApplications,
    readMyApplication,
    readApplication,
    withdrawApplication,
    acceptApplication,
    rejectApplication,
  };
};
