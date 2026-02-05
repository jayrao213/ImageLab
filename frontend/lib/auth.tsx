'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface AuthUser {
  userid: number;
  username: string;
  givenname: string;
  familyname: string;
  is_admin: boolean;
}

export interface AuthResponse {
  token: string;
  userid: number;
  username: string;
  givenname: string;
  familyname: string;
  is_admin: boolean;
}

interface AuthContextType {
  user: AuthUser | null;
  token: string | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string, givenname: string, familyname: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load token from localStorage on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('imagelab_token');
    const storedUser = localStorage.getItem('imagelab_user');
    
    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
      
      // Verify token is still valid
      verifyToken(storedToken).catch(() => {
        // Token invalid, clear storage
        logout();
      });
    }
    
    setIsLoading(false);
  }, []);

  const verifyToken = async (authToken: string) => {
    const response = await fetch(`${API_URL}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });
    
    if (!response.ok) {
      throw new Error('Token invalid');
    }
    
    return response.json();
  };

  const login = async (username: string, password: string) => {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data: AuthResponse = await response.json();
    
    // Store in state
    setToken(data.token);
    setUser({
      userid: data.userid,
      username: data.username,
      givenname: data.givenname,
      familyname: data.familyname,
      is_admin: data.is_admin,
    });
    
    // Store in localStorage
    localStorage.setItem('imagelab_token', data.token);
    localStorage.setItem('imagelab_user', JSON.stringify({
      userid: data.userid,
      username: data.username,
      givenname: data.givenname,
      familyname: data.familyname,
      is_admin: data.is_admin,
    }));
  };

  const register = async (username: string, password: string, givenname: string, familyname: string) => {
    const response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password, givenname, familyname }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }

    const data: AuthResponse = await response.json();
    
    // Store in state
    setToken(data.token);
    setUser({
      userid: data.userid,
      username: data.username,
      givenname: data.givenname,
      familyname: data.familyname,
      is_admin: data.is_admin,
    });
    
    // Store in localStorage
    localStorage.setItem('imagelab_token', data.token);
    localStorage.setItem('imagelab_user', JSON.stringify({
      userid: data.userid,
      username: data.username,
      givenname: data.givenname,
      familyname: data.familyname,
      is_admin: data.is_admin,
    }));
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('imagelab_token');
    localStorage.removeItem('imagelab_user');
  };

  return (
    <AuthContext.Provider value={{
      user,
      token,
      isLoading,
      login,
      register,
      logout,
      isAuthenticated: !!token && !!user,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// Helper function to get auth headers for API calls
export function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem('imagelab_token');
  if (token) {
    return {
      'Authorization': `Bearer ${token}`,
    };
  }
  return {};
}
