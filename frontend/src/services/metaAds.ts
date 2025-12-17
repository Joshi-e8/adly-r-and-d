import api from './api';

export const metaAdsAPI = {
  upload: (workspaceId: string, form: FormData) => api
    .post<{ creative_id: string; status: string }>(`/workspaces/${workspaceId}/ad-accounts/v1/ad-accounts/meta/upload-ad/`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    .then(r => r.data),
  listPages: (workspaceId: string, adAccountId?: string) => api
    .get<{ pages: { id: string; name: string }[] }>(`/workspaces/${workspaceId}/ad-accounts/v1/ad-accounts/meta/pages/`, {
      params: adAccountId ? { ad_account_id: adAccountId } : undefined,
    })
    .then(r => r.data.pages),
};

export default metaAdsAPI;
