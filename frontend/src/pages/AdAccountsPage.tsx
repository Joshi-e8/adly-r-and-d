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
  const [search, setSearch] = useState('');

  

  

  const iconSources = (key: string) => {
    const sources: Record<string, string[]> = {
      twitter: [
        'https://cdn.simpleicons.org/x?viewbox=auto',
        'https://cdn.simpleicons.org/x',
        'https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/x.svg',
        'https://unpkg.com/simple-icons@latest/icons/x.svg',
      ],
      meta: [
        'https://cdn.simpleicons.org/meta?viewbox=auto',
        'https://cdn.simpleicons.org/meta',
        'https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/meta.svg',
        'https://unpkg.com/simple-icons@latest/icons/meta.svg',
      ],
      linkedin: [
        'https://cdn.simpleicons.org/linkedin/0A66C2?viewbox=auto',
        'https://cdn.simpleicons.org/linkedin/0A66C2',
        'https://cdn.simpleicons.org/linkedin?viewbox=auto',
        'https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/linkedin.svg',
        'https://unpkg.com/simple-icons@latest/icons/linkedin.svg',
      ],
      snapchat: [
        'https://cdn.simpleicons.org/snapchat?viewbox=auto',
        'https://cdn.simpleicons.org/snapchat',
        'https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/snapchat.svg',
        'https://unpkg.com/simple-icons@latest/icons/snapchat.svg',
      ],
      youtube: [
        'https://cdn.simpleicons.org/youtube?viewbox=auto',
        'https://cdn.simpleicons.org/youtube',
        'https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/youtube.svg',
        'https://unpkg.com/simple-icons@latest/icons/youtube.svg',
      ],
    };
    return sources[key] || [];
  };

  const handleIconError = (e: React.SyntheticEvent<HTMLImageElement>) => {
    const el = e.currentTarget;
    const rest = (el.dataset.fallbacks || '').split('|').filter(Boolean);
    if (rest.length === 0) {
      el.onerror = null;
      return;
    }
    const next = rest.shift() as string;
    el.src = next;
    el.dataset.fallbacks = rest.join('|');
  };

  const providerIcon = (key: string) => {
    const srcs = iconSources(key);
    if (srcs.length === 0) return null;
    const name = key === 'twitter' ? 'X' : key;
    return (
      <img
        src={srcs[0]}
        data-fallbacks={srcs.slice(1).join('|')}
        alt={`${name} logo`}
        className="w-6 h-6"
        loading="lazy"
        decoding="async"
        fetchPriority="low"
        onError={handleIconError}
      />
    );
  };

  const providerLabelClass = (_p: string) => {
    return _p ? 'bg-transparent text-gray-900 border-gray-200' : 'bg-transparent text-gray-900 border-gray-200';
  };

  const copyWorkspaceId = async () => {
    if (!workspaceId) return;
    try {
      await navigator.clipboard.writeText(workspaceId);
      toast.success('Workspace ID copied');
    } catch {
      toast.error('Failed to copy');
    }
  };

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

  


  const startTwitterOAuth = async () => {
    if (!(workspaceId && workspaceId.length > 0)) return toast.error('Enter a workspace ID');
    try {
      const url = await adAccountsAPI.startTwitterOAuth(workspaceId);
      window.location.href = url;
    } catch {
      toast.error('Failed to start X Ads OAuth');
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

  const startMetaOAuth = async () => {
    if (!(workspaceId && workspaceId.length > 0)) return toast.error('Enter a workspace ID');
    try {
      const url = await adAccountsAPI.startMetaOAuth(workspaceId);
      window.location.href = url;
    } catch {
      toast.error('Failed to start Meta OAuth');
    }
  };

  const startLinkedInOAuth = async () => {
    if (!(workspaceId && workspaceId.length > 0)) return toast.error('Enter a workspace ID');
    try {
      const url = await adAccountsAPI.startLinkedInOAuth(workspaceId);
      window.location.href = url;
    } catch {
      toast.error('Failed to start LinkedIn OAuth');
    }
  };

  const startYouTubeOAuth = async () => {
    if (!(workspaceId && workspaceId.length > 0)) return toast.error('Enter a workspace ID');
    try {
      const url = await adAccountsAPI.startYouTubeOAuth(workspaceId);
      window.location.href = url;
    } catch {
      toast.error('Failed to start YouTube OAuth');
    }
  };

  const isProviderConnected = (provider: string) => {
    return accounts.some(a => a.provider === provider && a.status === 'connected');
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

      <main className="max-w-7xl mx-auto py-8 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="space-y-6">
            <div className="card">
              <label className="block text-sm font-medium text-gray-700 mb-2">Workspace ID</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={workspaceId}
                  onChange={(e) => setWorkspaceId(e.target.value)}
                  placeholder="Enter workspace UUID"
                  className="input-field flex-1"
                />
                <button className="btn-outline" onClick={copyWorkspaceId} disabled={!workspaceId}>Copy</button>
              </div>
              {!workspaceId && (
                <div className="mt-2 rounded-md border border-orange-200 bg-orange-50 text-orange-700 text-sm px-3 py-2">
                  Enter a workspace ID to enable provider connections
                </div>
              )}
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

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { key: 'twitter', title: 'Twitter', desc: 'Connect and fetch your X Ads accounts.' },
              { key: 'meta', title: 'Meta (Facebook/Instagram)', desc: 'Connect to manage Meta ad assets.' },
              { key: 'linkedin', title: 'LinkedIn Ads', desc: 'Connect to link your LinkedIn profile and pages.' },
              { key: 'snapchat', title: 'Snapchat Ads', desc: 'Connect to enable Snapchat campaign management.' },
              { key: 'youtube', title: 'YouTube', desc: 'Connect your channel to sync content and analytics.' },
            ].map((p) => (
                <div key={p.key} className="card h-full min-h-[220px] flex flex-col">
                  <div className="flex items-center gap-3 mb-2">
                    <div className={`badge ${providerLabelClass(p.key)}`}>
                      {providerIcon(p.key)}
                      <span className="text-sm font-medium">{p.title}</span>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 mb-4 flex-1">{p.desc}</p>
                  <div className="mt-auto flex gap-2">
                    {p.key === 'twitter' && (
                      <button onClick={startTwitterOAuth} className="btn-primary w-full" disabled={!workspaceId || isProviderConnected('twitter')} aria-label="Connect X via OAuth" aria-disabled={!workspaceId || isProviderConnected('twitter')}>{isProviderConnected('twitter') ? 'Connected' : 'Connect'}</button>
                    )}
                    {p.key === 'meta' && (
                      <button onClick={startMetaOAuth} className="btn-primary w-full" disabled={!workspaceId || isProviderConnected('meta')} aria-label="Connect Meta" aria-disabled={!workspaceId || isProviderConnected('meta')}>{isProviderConnected('meta') ? 'Connected' : 'Connect'}</button>
                    )}
                    {p.key === 'linkedin' && (
                      <button onClick={startLinkedInOAuth} className="btn-primary w-full" disabled={!workspaceId || isProviderConnected('linkedin')} aria-label="Connect LinkedIn" aria-disabled={!workspaceId || isProviderConnected('linkedin')}>{isProviderConnected('linkedin') ? 'Connected' : 'Connect'}</button>
                    )}
                    {p.key === 'snapchat' && (
                      <button onClick={startSnapchatOAuth} className="btn-primary w-full" disabled={!workspaceId || isProviderConnected('snapchat')} aria-label="Connect Snapchat" aria-disabled={!workspaceId || isProviderConnected('snapchat')}>{isProviderConnected('snapchat') ? 'Connected' : 'Connect'}</button>
                    )}
                    {p.key === 'youtube' && (
                      <button onClick={startYouTubeOAuth} className="btn-primary w-full" disabled={!workspaceId || isProviderConnected('youtube')} aria-label="Connect YouTube" aria-disabled={!workspaceId || isProviderConnected('youtube')}>{isProviderConnected('youtube') ? 'Connected' : 'Connect'}</button>
                    )}
                  </div>
                  
                </div>
              ))}
            </div>

            <div className="card">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold">Connected Accounts</h3>
                <div className="flex items-center gap-2">
                  <input
                    className="input-field w-56"
                    placeholder="Search accounts"
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    aria-label="Search accounts"
                  />
                  <button className="btn-secondary" onClick={loadAccounts} disabled={loading} aria-disabled={loading} aria-label="Refresh connected accounts">{loading ? 'Loading…' : 'Refresh'}</button>
                </div>
              </div>
              {accounts.length === 0 ? (
                <p className="text-gray-600">No accounts connected</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200" role="table" aria-label="Connected accounts table">
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
                      {(accounts.filter(a => [a.provider, a.account_name || '', a.external_account_id || ''].some(s => s.toLowerCase().includes(search.toLowerCase())))).map((a) => (
                        <tr key={a.id}>
                          <td className="px-4 py-2">
                            <div className={`badge ${providerLabelClass(a.provider)}`}>
                              {providerIcon(a.provider)}
                              <span className="text-xs font-medium capitalize">{a.provider === 'twitter' ? 'X' : a.provider}</span>
                            </div>
                          </td>
                          <td className="px-4 py-2">{a.account_name || '-'}</td>
                          <td className="px-4 py-2">{a.external_account_id || '-'}</td>
                          <td className="px-4 py-2">
                            <span className={`px-2.5 py-1 rounded-md text-xs font-medium ${a.status === 'connected' ? 'bg-green-50 text-green-700 border border-green-200' : a.status === 'disconnected' ? 'bg-gray-50 text-gray-700 border border-gray-200' : 'bg-orange-50 text-orange-700 border border-orange-200'}`}>{a.status}</span>
                          </td>
                          <td className="px-4 py-2 text-right">
                            <button className="btn-outline" onClick={() => disconnect(a.id)} aria-label={`Disconnect ${a.provider} account ${a.external_account_id || ''}`}>Disconnect</button>
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
