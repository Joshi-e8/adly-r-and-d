import api from '@/services/api';
import type { Workspace } from '@/types/auth';

export const workspaceAPI = {
  list: () => api.get<{ result: string; records: Workspace[] }>(
    '/workspaces/'
  ).then(r => r.data.records),
  create: (data: { name: string }) => api.post<{ result: string; records: Workspace }>(
    '/workspaces/', data
  ).then(r => r.data.records),
  get: (id: string) => api.get<{ result: string; records: Workspace }>(`/workspaces/${id}/`).then(r => r.data.records),
  update: (id: string, data: Partial<Workspace>) => api.patch<{ result: string; records: Workspace }>(`/workspaces/${id}/`, data).then(r => r.data.records),
  delete: (id: string) => api.delete(`/workspaces/${id}/`),
  getMembers: (id: string) => api.get(`/workspaces/${id}/members/`),
  inviteMember: (id: string, data: { email: string; role: string }) => api.post(`/workspaces/${id}/members/invite/`, data),
  updateMemberRole: (workspaceId: string, userId: string, data: { role: string }) => 
    api.put(`/workspaces/${workspaceId}/members/${userId}/`, data),
  removeMember: (workspaceId: string, userId: string) => 
    api.delete(`/workspaces/${workspaceId}/members/${userId}/remove/`),
  getAuditLogs: (id: string) => api.get(`/workspaces/${id}/audit-logs/`),
};

export default workspaceAPI;
