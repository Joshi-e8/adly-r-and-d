import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { adAccountsAPI } from '@/services/adAccounts';
import metaAdsAPI from '@/services/metaAds';
import type { AdAccount } from '@/types/adAccounts';
import type { Workspace } from '@/types/auth';
import { workspaceAPI } from '@/services/workspaces/workspaceApi';

export const MetaAdsUploadPage: React.FC = () => {
  const navigate = useNavigate();
  const { workspaceId: routeWorkspaceId } = useParams<{ workspaceId: string }>();
  const [workspaceId, setWorkspaceId] = useState(routeWorkspaceId || '');
  const [accounts, setAccounts] = useState<AdAccount[]>([]);
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [loading, setLoading] = useState(false);
  const [workspaceLoading, setWorkspaceLoading] = useState(false);
  const [selectedAccountId, setSelectedAccountId] = useState('');
  const [name, setName] = useState('ADLY Creative');
  const [pageId, setPageId] = useState('');
  const [message, setMessage] = useState('');
  const [linkUrl, setLinkUrl] = useState('');
  const [creativeType, setCreativeType] = useState<'image' | 'video'>('image');
  const [file, setFile] = useState<File | null>(null);
  const [pages, setPages] = useState<{ id: string; name: string }[]>([]);

  const loadAccounts = useCallback(async () => {
    if (!(workspaceId && workspaceId.length > 0)) return;
    try {
      setLoading(true);
      const data = await adAccountsAPI.list(workspaceId);
      const metaAccounts = data.filter(a => a.provider === 'meta');
      setAccounts(metaAccounts);
      if (metaAccounts.length > 0 && !selectedAccountId) {
        setSelectedAccountId(metaAccounts[0].external_account_id || '');
      }
    } catch {
      toast.error('Failed to load ad accounts');
    } finally {
      setLoading(false);
    }
  }, [workspaceId, selectedAccountId]);

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
      } finally {
        setWorkspaceLoading(false);
      }
    })();
  }, [workspaceId]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!(workspaceId && workspaceId.length > 0)) return toast.error('Enter a workspace ID');
    if (!pageId) return toast.error('Enter a Page ID');
    try {
      const form = new FormData();
      form.append('name', name);
      form.append('page_id', pageId);
      form.append('message', message);
      form.append('link_url', linkUrl);
      form.append('creative_type', creativeType);
      if (selectedAccountId) form.append('ad_account_id', selectedAccountId);
      if (file) form.append('media', file);
      const res = await metaAdsAPI.upload(workspaceId, form);
      toast.success(`Creative created: ${res.creative_id}`);
    } catch {
      toast.error('Failed to upload creative');
    }
  };

  const loadPages = async () => {
    if (!(workspaceId && workspaceId.length > 0)) return toast.error('Enter a workspace ID');
    try {
      const res = await metaAdsAPI.listPages(workspaceId, selectedAccountId || undefined);
      setPages(res);
      if (res.length > 0 && !pageId) setPageId(res[0].id);
      toast.success('Loaded Pages');
    } catch {
      toast.error('Failed to load Pages');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-primary-600">Meta Ads Upload</h1>
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
                className="input-field"
              />
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
              <h3 className="text-lg font-semibold mb-4">Select Meta Account</h3>
              {accounts.length === 0 ? (
                <p className="text-gray-600">No Meta accounts connected</p>
              ) : (
                <select className="input-field" value={selectedAccountId} onChange={(e) => setSelectedAccountId(e.target.value)}>
                  {accounts.map(a => (
                    <option key={a.id} value={a.external_account_id || ''}>
                      {a.account_name || a.external_account_id}
                    </option>
                  ))}
                </select>
              )}
            </div>

            <div className="card md:col-span-2">
              <h3 className="text-lg font-semibold mb-4">Creative Details</h3>
              <form onSubmit={submit} className="space-y-3">
                <input className="input-field" placeholder="Creative Name" value={name} onChange={(e) => setName(e.target.value)} />
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <input className="input-field" placeholder="Page ID" value={pageId} onChange={(e) => setPageId(e.target.value)} />
                  <button type="button" onClick={loadPages} className="btn-secondary">Find My Page IDs</button>
                </div>
                {pages.length > 0 && (
                  <select className="input-field" value={pageId} onChange={(e) => setPageId(e.target.value)}>
                    {pages.map(p => (
                      <option key={p.id} value={p.id}>{p.name} ({p.id})</option>
                    ))}
                  </select>
                )}
                <textarea className="input-field" placeholder="Message" value={message} onChange={(e) => setMessage(e.target.value)} />
                <input className="input-field" placeholder="Link URL (optional)" value={linkUrl} onChange={(e) => setLinkUrl(e.target.value)} />
                <div className="flex items-center gap-4">
                  <label className="flex items-center gap-2">
                    <input type="radio" name="creative_type" checked={creativeType === 'image'} onChange={() => setCreativeType('image')} />
                    <span>Image</span>
                  </label>
                  <label className="flex items-center gap-2">
                    <input type="radio" name="creative_type" checked={creativeType === 'video'} onChange={() => setCreativeType('video')} />
                    <span>Video</span>
                  </label>
                </div>
                <input type="file" className="input-field" onChange={(e) => setFile(e.target.files?.[0] || null)} />
                <button type="submit" className="btn-primary w-full">Upload Creative</button>
              </form>
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
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {accounts.map((a) => (
                        <tr key={a.id}>
                          <td className="px-4 py-2">{a.provider}</td>
                          <td className="px-4 py-2">{a.account_name || '-'}</td>
                          <td className="px-4 py-2">{a.external_account_id || '-'}</td>
                          <td className="px-4 py-2">{a.status}</td>
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

export default MetaAdsUploadPage;
