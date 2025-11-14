/**
 * API client for backend communication
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface User {
  id: number;
  email: string;
  username: string;
  created_at: string;
}

export interface AuthResponse {
  message: string;
  user: User;
  token: string;
}

export interface ErrorResponse {
  error: string;
  message?: string;
}

export interface FileItem {
  id: number;
  filename: string;
  size: number;
  mime_type: string;
  uploaded_at: string;
  download_count: number;
}

export interface FileListResponse {
  files: FileItem[];
  pagination: {
    page: number;
    size: number;
    total: number;
    pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

export interface FileUploadResponse {
  message: string;
  file: FileItem;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;

    const headers: Record<string, string> = {
      ...options.headers as Record<string, string>,
    };

    // Only set Content-Type if not already set (for FormData uploads)
    if (!headers['Content-Type'] && !(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'An error occurred');
    }

    return data;
  }

  async signup(email: string, password: string, username: string): Promise<AuthResponse> {
    return this.request<AuthResponse>('/api/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ email, password, username }),
    });
  }

  async login(email: string, password: string): Promise<AuthResponse> {
    return this.request<AuthResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async logout(): Promise<{ message: string }> {
    return this.request<{ message: string }>('/api/auth/logout', {
      method: 'POST',
    });
  }

  async getProfile(): Promise<{ user: User }> {
    return this.request<{ user: User }>('/api/auth/me');
  }

  async updateProfile(data: { username?: string; password?: string }): Promise<{ user: User }> {
    return this.request<{ user: User }>('/api/auth/me', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // File management methods
  async uploadFile(file: File): Promise<FileUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const url = `${this.baseUrl}/api/files`;
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;

    const headers: HeadersInit = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    // Don't set Content-Type for FormData - browser will set it with boundary

    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Failed to upload file');
    }

    return data;
  }

  async listFiles(page: number = 1, size: number = 10): Promise<FileListResponse> {
    return this.request<FileListResponse>(`/api/files?page=${page}&size=${size}`);
  }

  async getFile(fileId: number): Promise<{ file: FileItem }> {
    return this.request<{ file: FileItem }>(`/api/files/${fileId}`);
  }

  async downloadFile(fileId: number, filename: string): Promise<void> {
    const url = `${this.baseUrl}/api/files/${fileId}/download`;
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;

    const headers: HeadersInit = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, { headers });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || 'Failed to download file');
    }

    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(downloadUrl);
    document.body.removeChild(a);
  }

  async renameFile(fileId: number, filename: string): Promise<{ message: string; file: FileItem }> {
    return this.request<{ message: string; file: FileItem }>(`/api/files/${fileId}`, {
      method: 'PATCH',
      body: JSON.stringify({ filename }),
    });
  }

  async deleteFile(fileId: number): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/api/files/${fileId}`, {
      method: 'DELETE',
    });
  }
}

export const api = new ApiClient(API_URL);