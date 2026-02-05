'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/lib/auth';

export default function Navigation() {
  const pathname = usePathname();
  const { user, isAuthenticated, logout, isLoading } = useAuth();

  // Base nav items available to all users
  const baseNavItems = [
    { href: '/', label: 'Home' },
    { href: '/images', label: 'Images' },
    { href: '/upload', label: 'Upload' },
    { href: '/edit', label: 'Edit' },
    { href: '/search', label: 'Search' },
  ];
  
  // Admin-only nav items
  const adminNavItems = [
    { href: '/users', label: 'Users' },
  ];
  
  // Combine nav items based on admin status
  const navItems = user?.is_admin 
    ? [...baseNavItems.slice(0, 1), ...adminNavItems, ...baseNavItems.slice(1)]
    : baseNavItems;

  return (
    <nav className="bg-[#0a0a0a] border-b border-gray-700 text-white shadow-lg mb-6">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="text-2xl font-bold hover:text-indigo-400 transition-colors">
            ImageLab
          </Link>

          <div className="flex items-center space-x-2">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`px-4 py-2 rounded-md transition-colors text-sm font-medium ${
                  pathname === item.href
                    ? 'bg-indigo-600 text-white'
                    : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                }`}
              >
                {item.label}
              </Link>
            ))}
            
            {/* Auth buttons */}
            <div className="ml-4 pl-4 border-l border-gray-700 flex items-center space-x-2">
              {isLoading ? (
                <span className="text-gray-400 text-sm">Loading...</span>
              ) : isAuthenticated ? (
                <>
                  <span className="text-gray-400 text-sm flex items-center gap-2">
                    Hi, <span className="text-indigo-400 font-medium">{user?.givenname || user?.username}</span>
                    {user?.is_admin && (
                      <span className="px-1.5 py-0.5 text-xs font-semibold bg-indigo-600 text-white rounded">
                        ADMIN
                      </span>
                    )}
                  </span>
                  <button
                    onClick={logout}
                    className="px-4 py-2 rounded-md text-sm font-medium text-gray-300 hover:bg-gray-800 hover:text-white transition-colors"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link
                    href="/login"
                    className={`px-4 py-2 rounded-md transition-colors text-sm font-medium ${
                      pathname === '/login'
                        ? 'bg-indigo-600 text-white'
                        : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                    }`}
                  >
                    Login
                  </Link>
                  <Link
                    href="/register"
                    className={`px-4 py-2 rounded-md transition-colors text-sm font-medium ${
                      pathname === '/register'
                        ? 'bg-indigo-600 text-white'
                        : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                    }`}
                  >
                    Sign Up
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
