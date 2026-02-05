'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ping, getUsers, getImages, getLabelsCount, type PingResponse } from '@/lib/api';
import { useAuth } from '@/lib/auth';

export default function Home() {
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();
  const [status, setStatus] = useState<PingResponse | null>(null);
  const [userCount, setUserCount] = useState<number>(0);
  const [imageCount, setImageCount] = useState<number>(0);
  const [labelCount, setLabelCount] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const pingData = await ping();
        setStatus(pingData);
        const users = await getUsers();
        const images = await getImages();
        const labelsCount = await getLabelsCount();
        setUserCount(users.length);
        setImageCount(images.length);
        setLabelCount(labelsCount);
        setError(null);
      } catch (err) {
        setError('Failed to connect to backend');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const stats = [
    { label: 'S3 Items', value: typeof status?.bucket_items === 'number' ? status.bucket_items : '-' },
    { label: 'Users', value: userCount },
    { label: 'Images', value: imageCount },
    { label: 'AI Labels', value: labelCount },
  ];

  return (
    <div className="px-6 py-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-5xl font-bold text-white mb-3">
            <span className="bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
              ImageLab
            </span>
          </h1>
          <p className="text-gray-400">
            Photo management with AI-powered editing and intelligent search
          </p>
          
          {/* Auth-aware welcome message */}
          {!authLoading && (
            <div className="mt-4">
              {isAuthenticated ? (
                <p className="text-indigo-400">
                  Welcome back, <span className="font-semibold">{user?.givenname || user?.username}</span>!
                </p>
              ) : (
                <p className="text-gray-500">
                  <Link href="/login" className="text-indigo-400 hover:text-indigo-300">Sign in</Link>
                  {' '}or{' '}
                  <Link href="/register" className="text-indigo-400 hover:text-indigo-300">create an account</Link>
                  {' '}to upload and manage your photos
                </p>
              )}
            </div>
          )}
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {loading ? (
            <div className="col-span-4 text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
            </div>
          ) : error ? (
            <div className="col-span-4 border border-red-800 rounded-lg p-4 bg-red-900/20 text-center">
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          ) : (
            stats.map((stat) => (
              <div key={stat.label} className="border border-gray-700 rounded-lg p-4 text-center hover:border-indigo-500 transition-colors">
                <p className="text-2xl font-bold text-indigo-400">{stat.value}</p>
                <p className="text-xs text-gray-500 mt-1">{stat.label}</p>
              </div>
            ))
          )}
        </div>

        {/* Features */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="border border-gray-700 rounded-lg p-5 hover:border-indigo-500 transition-colors">
            <div className="w-10 h-10 rounded-lg bg-indigo-600/20 flex items-center justify-center mb-3">
              <svg className="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
              </svg>
            </div>
            <h3 className="font-semibold text-white mb-1">Cloud Storage</h3>
            <p className="text-sm text-gray-400">Secure AWS S3 storage for all your images</p>
          </div>

          <div className="border border-gray-700 rounded-lg p-5 hover:border-indigo-500 transition-colors">
            <div className="w-10 h-10 rounded-lg bg-indigo-600/20 flex items-center justify-center mb-3">
              <svg className="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h3 className="font-semibold text-white mb-1">AI Labeling</h3>
            <p className="text-sm text-gray-400">AWS Rekognition detects objects & scenes</p>
          </div>

          <div className="border border-gray-700 rounded-lg p-5 hover:border-indigo-500 transition-colors">
            <div className="w-10 h-10 rounded-lg bg-indigo-600/20 flex items-center justify-center mb-3">
              <svg className="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h3 className="font-semibold text-white mb-1">Smart Search</h3>
            <p className="text-sm text-gray-400">Find images by AI-detected labels</p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-3 gap-4">
          <Link href="/upload" className="border border-gray-700 rounded-lg p-5 hover:border-indigo-500 hover:bg-indigo-900/10 transition-all group">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-indigo-600 flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-white group-hover:text-indigo-400 transition-colors">Upload</h3>
                <p className="text-xs text-gray-500">Add new images</p>
              </div>
            </div>
          </Link>

          <Link href="/edit" className="border border-gray-700 rounded-lg p-5 hover:border-indigo-500 hover:bg-indigo-900/10 transition-all group">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-indigo-600 flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-white group-hover:text-indigo-400 transition-colors">Edit</h3>
                <p className="text-xs text-gray-500">Transform photos</p>
              </div>
            </div>
          </Link>

          <Link href="/search" className="border border-gray-700 rounded-lg p-5 hover:border-indigo-500 hover:bg-indigo-900/10 transition-all group">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-indigo-600 flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-white group-hover:text-indigo-400 transition-colors">Search</h3>
                <p className="text-xs text-gray-500">Find by labels</p>
              </div>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}
