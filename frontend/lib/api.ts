/**
 * API Client for ImageLab Backend
 * Connects to FastAPI backend running on localhost:8000
 */

import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('imagelab_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Types matching the backend models
export interface User {
  userid: number;
  username: string;
  givenname: string;
  familyname: string;
  is_admin: boolean;
}

export interface Image {
  assetid: number;
  userid: number;
  localname: string;
  bucketkey: string;
}

export interface ImageLabel {
  label: string;
  confidence: number;
}

export interface ImageWithLabel {
  assetid: number;
  localname: string;
  label: string;
  confidence: number;
}

export interface PingResponse {
  bucket_items: number | string;
  database_users: number | string;
}

export interface ImageUploadResponse {
  assetid: number;
  message: string;
}

export interface DeleteResponse {
  success: boolean;
  message: string;
}

export interface CreateUserRequest {
  username: string;
  givenname: string;
  familyname: string;
  password: string;
}

// API Functions

/**
 * Health check - ping the backend
 */
export const ping = async (): Promise<PingResponse> => {
  const response = await api.get<PingResponse>('/ping');
  return response.data;
};

/**
 * Get all users
 */
export const getUsers = async (): Promise<User[]> => {
  const response = await api.get<User[]>('/users/');
  return response.data;
};

/**
 * Create a new user
 */
export const createUser = async (userData: CreateUserRequest): Promise<User> => {
  const response = await api.post<User>('/users/', userData);
  return response.data;
};

/**
 * Delete a user and all their images and labels
 */
export const deleteUser = async (userid: number): Promise<void> => {
  await api.delete(`/users/${userid}`);
};

/**
 * Get all images, optionally filtered by userid
 */
export const getImages = async (userid?: number): Promise<Image[]> => {
  const params = userid ? { userid } : {};
  const response = await api.get<Image[]>('/images/', { params });
  return response.data;
};

/**
 * Upload an image
 */
export const uploadImage = async (
  userid: number,
  file: File
): Promise<ImageUploadResponse> => {
  const formData = new FormData();
  formData.append('userid', userid.toString());
  formData.append('file', file);

  const response = await api.post<ImageUploadResponse>('/images/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

/**
 * Download/view an image
 */
export const getImageUrl = (assetid: number, thumbnail: boolean = false): string => {
  return `${API_URL}/images/${assetid}${thumbnail ? '?thumbnail=true' : ''}`;
};

/**
 * Download an image file
 */
export const downloadImage = async (assetid: number, filename: string): Promise<void> => {
  const url = `${API_URL}/images/${assetid}?download=true`;

  // Trigger a direct download to avoid CORS/XHR issues with streaming responses.
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  link.rel = 'noopener';
  document.body.appendChild(link);
  link.click();
  link.remove();
};

/**
 * Delete all images
 */
export const deleteAllImages = async (userid?: number): Promise<DeleteResponse> => {
  const params = userid !== undefined ? { userid } : {};
  const response = await api.delete<DeleteResponse>('/images/', { params });
  return response.data;
};

/**
 * Delete a single image
 */
export const deleteImage = async (assetid: number): Promise<DeleteResponse> => {
  const response = await api.delete<DeleteResponse>(`/images/${assetid}`);
  return response.data;
};

/**
 * Get labels for a specific image
 */
export const getImageLabels = async (assetid: number): Promise<ImageLabel[]> => {
  const response = await api.get<ImageLabel[]>(`/labels/image/${assetid}`);
  return response.data;
};

/**
 * Get total count of all AI labels
 */
export const getLabelsCount = async (): Promise<number> => {
  const response = await api.get<{ count: number }>('/labels/count');
  return response.data.count;
};

/**
 * Search images by label
 */
export const searchImagesByLabel = async (label: string, userid?: number): Promise<ImageWithLabel[]> => {
  const params: { label: string; userid?: number } = { label };
  if (userid) {
    params.userid = userid;
  }
  const response = await api.get<ImageWithLabel[]>('/labels/search', {
    params,
  });
  return response.data;
};

export default api;
