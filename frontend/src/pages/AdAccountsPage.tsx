import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { adAccountsAPI } from '@/services/adAccounts';
import { workspaceAPI } from '@/services/workspaces/workspaceApi';
import { AdAccount } from '@/types/adAccounts';
import type { Workspace } from '@/types/auth';

export const AdAccountsPage: React.FC = () => {
  const navigate = useNavigate();
  const { workspaceId: routeWorkspaceId } = useParams<{ workspaceId: string }>();
  const [workspaceId, setWorkspaceId] = useState(routeWorkspaceId || '');
  const [accounts, setAccounts] = useState<AdAccount[]>([]);
  const [loading, setLoading] = useState(false);
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [workspaceLoading, setWorkspaceLoading] = useState(false);

  const [twitterForm, setTwitterForm] = useState({
    account_name: '',
    external_account_id: '',
    access_token: '',
    access_token_secret: '',
  });

  const [snapForm, setSnapForm] = useState({
    account_name: '',
    external_account_id: '',
    access_token: '',
    refresh_token: '',
  });

  const loadAccounts = useCallback(async () => {
    if (!(workspaceId && workspaceId.length > 0)) return;
    try {
      setLoading(true);
      const data = await adAccountsAPI.list(workspaceId);
      setAccounts(data);
    } catch {
      toast.error('Failed to load ad accounts');
    } finally {
      setLoading(false);
    }
  }, [workspaceId]);

  useEffect(() => {
    loadAccounts();
  }, [loadAccounts]);

  useEffect(() => {
    (async () => {
      try {
        setWorkspaceLoading(true);
        const ws = await workspaceAPI.list();
        setWorkspaces(ws);
        if (!workspaceId && ws.length > 0) {
          setWorkspaceId(ws[0].id);
        }
      } catch {
        toast.error('Failed to load workspaces');
      }
      finally {
        setWorkspaceLoading(false);
      }
    })();
  }, [workspaceId]);

  const connectTwitter = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!(workspaceId && workspaceId.length > 0)) return toast.error('Enter a workspace ID');
    try {
      await adAccountsAPI.connect(workspaceId, {
        provider: 'twitter',
        ...twitterForm,
      });
      toast.success('Twitter connected');
      setTwitterForm({ account_name: '', external_account_id: '', access_token: '', access_token_secret: '' });
      loadAccounts();
    } catch {
      toast.error('Failed to connect Twitter');
    }
  };


  const startTwitterOAuth = async () => {
    if (!(workspaceId && workspaceId.length > 0)) return toast.error('Enter a workspace ID');
    try {
      const url = await adAccountsAPI.startTwitterOAuth(workspaceId);
      window.location.href = url;
    } catch {
      toast.error('Failed to start Twitter Ads OAuth');
    }
  };

  const connectSnapchat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!(workspaceId && workspaceId.length > 0)) return toast.error('Enter a workspace ID');
    try {
      await adAccountsAPI.connect(workspaceId, {
        provider: 'snapchat',
        ...snapForm,
      });
      toast.success('Snapchat connected');
      setSnapForm({ account_name: '', external_account_id: '', access_token: '', refresh_token: '' });
      loadAccounts();
    } catch {
      toast.error('Failed to connect Snapchat');
    }
  };

  const startSnapchatOAuth = async () => {
    if (!(workspaceId && workspaceId.length > 0)) return toast.error('Enter a workspace ID');
    try {
      const url = await adAccountsAPI.startSnapchatOAuth(workspaceId);
      window.location.href = url;
    } catch {
      toast.error('Failed to start Snapchat OAuth');
    }
  };

  const disconnect = async (id: string) => {
    if (!(workspaceId && workspaceId.length > 0)) return toast.error('Enter a workspace ID');
    try {
      await adAccountsAPI.disconnect(workspaceId, id);
      toast.success('Disconnected');
      loadAccounts();
    } catch {
      toast.error('Failed to disconnect');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-primary-600">Ad Accounts</h1>
            </div>
            <div className="flex items-center gap-4">
              <button onClick={() => navigate(-1)} className="btn-secondary text-sm">Back</button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="card md:col-span-3">
              <label className="block text-sm font-medium text-gray-700 mb-2">Workspace ID</label>
              <input
                type="text"
                value={workspaceId}
                onChange={(e) => setWorkspaceId(e.target.value)}
                placeholder="Enter workspace UUID"
                className="input"
              />
              <p className="text-xs text-gray-500 mt-2">Use your workspace UUID. This is required to bind accounts.</p>
              <div className="mt-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-semibold">Your Workspaces</h4>
                  <span className="text-xs text-gray-500">{workspaceLoading ? 'Loading…' : ''}</span>
                </div>
                {workspaces.length === 0 ? (
                  <div className="flex items-center justify-between">
                    <p className="text-sm text-gray-600">No workspaces found.</p>
                    <button className="btn-secondary" onClick={() => navigate('/workspaces')}>Create Workspace</button>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead>
                        <tr>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Name</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">ID</th>
                          <th className="px-4 py-2"></th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {workspaces.map((w) => (
                          <tr key={w.id}>
                            <td className="px-4 py-2">{w.name}</td>
                            <td className="px-4 py-2">{w.id}</td>
                            <td className="px-4 py-2 text-right">
                              <button className="btn-secondary" onClick={() => setWorkspaceId(w.id)}>Use</button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>

            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Connect Twitter</h3>
              <form onSubmit={connectTwitter} className="space-y-3">
                <input className="input" placeholder="Account Name" value={twitterForm.account_name} onChange={(e) => setTwitterForm({ ...twitterForm, account_name: e.target.value })} />
                <input className="input" placeholder="External Account ID" value={twitterForm.external_account_id} onChange={(e) => setTwitterForm({ ...twitterForm, external_account_id: e.target.value })} />
                <input className="input" placeholder="Access Token" value={twitterForm.access_token} onChange={(e) => setTwitterForm({ ...twitterForm, access_token: e.target.value })} />
                <input className="input" placeholder="Access Token Secret" value={twitterForm.access_token_secret} onChange={(e) => setTwitterForm({ ...twitterForm, access_token_secret: e.target.value })} />
                <button type="submit" className="btn-primary w-full">Connect Twitter</button>
              </form>
              <div className="mt-3">
                <button onClick={startTwitterOAuth} className="btn-secondary w-full">Connect via Twitter Ads (OAuth1)</button>
              </div>
            </div>

            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Connect Snapchat</h3>
              <form onSubmit={connectSnapchat} className="space-y-3">
                <input className="input" placeholder="Account Name" value={snapForm.account_name} onChange={(e) => setSnapForm({ ...snapForm, account_name: e.target.value })} />
                <input className="input" placeholder="External Account ID" value={snapForm.external_account_id} onChange={(e) => setSnapForm({ ...snapForm, external_account_id: e.target.value })} />
                <input className="input" placeholder="Access Token" value={snapForm.access_token} onChange={(e) => setSnapForm({ ...snapForm, access_token: e.target.value })} />
                <input className="input" placeholder="Refresh Token" value={snapForm.refresh_token} onChange={(e) => setSnapForm({ ...snapForm, refresh_token: e.target.value })} />
                <button type="submit" className="btn-primary w-full">Connect Snapchat</button>
              </form>
              <div className="mt-3">
                <button onClick={startSnapchatOAuth} className="btn-secondary w-full">Connect via Snapchat OAuth</button>
              </div>
            </div>

            <div className="card md:col-span-3">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold">Connected Accounts</h3>
                <button className="btn-secondary" onClick={loadAccounts} disabled={loading}>{loading ? 'Loading…' : 'Refresh'}</button>
              </div>
              {accounts.length === 0 ? (
                <p className="text-gray-600">No accounts connected</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead>
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Provider</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Account Name</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">External ID</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Status</th>
                        <th className="px-4 py-2"></th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {accounts.map((a) => (
                        <tr key={a.id}>
                          <td className="px-4 py-2">{a.provider}</td>
                          <td className="px-4 py-2">{a.account_name || '-'}</td>
                          <td className="px-4 py-2">{a.external_account_id || '-'}</td>
                          <td className="px-4 py-2">{a.status}</td>
                          <td className="px-4 py-2 text-right">
                            <button className="btn-secondary" onClick={() => disconnect(a.id)}>Disconnect</button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default AdAccountsPage;
