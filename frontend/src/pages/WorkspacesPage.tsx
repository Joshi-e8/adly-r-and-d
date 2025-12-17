import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { workspaceAPI } from '@/services/workspaces/workspaceApi';
import type { Workspace } from '@/types/auth';

export const WorkspacesPage: React.FC = () => {
  const navigate = useNavigate();
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [name, setName] = useState('');

  const load = async () => {
    try {
      setLoading(true);
      const ws = await workspaceAPI.list();
      setWorkspaces(ws);
    } catch {
      toast.error('Failed to load workspaces');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const createWorkspace = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return toast.error('Enter a workspace name');
    try {
      setCreating(true);
      const ws = await workspaceAPI.create({ name: name.trim() });
      toast.success('Workspace created');
      setName('');
      setWorkspaces([ws, ...workspaces]);
    } catch {
      toast.error('Failed to create workspace');
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-primary-600">Workspaces</h1>
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
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Create Workspace</h3>
              <form onSubmit={createWorkspace} className="space-y-3">
                <input className="input-field" placeholder="Workspace Name" value={name} onChange={(e) => setName(e.target.value)} />
                <button type="submit" className="btn-primary w-full" disabled={creating}>{creating ? 'Creating…' : 'Create'}</button>
              </form>
            </div>

            <div className="card md:col-span-2">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold">Your Workspaces</h3>
                <button className="btn-secondary" onClick={load} disabled={loading}>{loading ? 'Loading…' : 'Refresh'}</button>
              </div>
              {workspaces.length === 0 ? (
                <p className="text-gray-600">No workspaces found</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead>
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Name</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">ID</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Role</th>
                        <th className="px-4 py-2"></th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {workspaces.map((w) => (
                        <tr key={w.id}>
                          <td className="px-4 py-2">{w.name}</td>
                          <td className="px-4 py-2">{w.id}</td>
                          <td className="px-4 py-2">{w.role}</td>
                          <td className="px-4 py-2 text-right">
                            <div className="flex gap-2 justify-end">
                              <button className="btn-secondary" onClick={() => navigate(`/ad-accounts/${w.id}`)}>Connect Ad Accounts</button>
                              <button className="btn-secondary" onClick={() => navigate(`/content/${w.id}`)}>Open Content</button>
                            </div>
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

export default WorkspacesPage;
