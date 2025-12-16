import api from './api';
import { AdAccount, AdProvider } from '@/types/adAccounts';

export const adAccountsAPI = {
  list: (workspaceId: string) => api
    .get<{ results?: AdAccount[] } | AdAccount[]>(`/workspaces/${workspaceId}/ad-accounts/v1/ad-accounts/`)
    .then(r => (Array.isArray(r.data) ? r.data : (r.data?.results ?? []))),
  connect: (workspaceId: string, data: {
    provider: AdProvider;
    account_name?: string;
    external_account_id?: string;
    access_token?: string;
    access_token_secret?: string;
    refresh_token?: string;
    scopes?: string[];
    metadata?: Record<string, unknown>;
  }) => api.post<AdAccount>(`/workspaces/${workspaceId}/ad-accounts/v1/ad-accounts/`, data).then(r => r.data),
  disconnect: (workspaceId: string, id: string) => api.post<{ status: string }>(`/workspaces/${workspaceId}/ad-accounts/v1/ad-accounts/${id}/disconnect/`).then(r => r.data),
  startTwitterOAuth: (workspaceId: string) => api
    .get<{ authorization_url: string }>(`/workspaces/${workspaceId}/ad-accounts/v1/ad-accounts/twitter/start/`)
    .then(r => r.data.authorization_url),
  startSnapchatOAuth: (workspaceId: string) => api
    .get<{ authorization_url: string }>(`/workspaces/${workspaceId}/ad-accounts/v1/ad-accounts/snapchat/start/`)
    .then(r => r.data.authorization_url),
};
