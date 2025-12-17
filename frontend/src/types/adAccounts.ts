export type AdProvider = 'twitter' | 'snapchat' | 'meta' | 'linkedin' | 'youtube';

export interface AdAccount {
  id: string;
  workspace: string;
  provider: AdProvider;
  account_name?: string;
  external_account_id?: string;
  status: 'connected' | 'disconnected' | 'error';
  scopes: string[];
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}
