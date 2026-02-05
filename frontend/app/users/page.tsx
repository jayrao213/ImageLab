'use client';

import { useEffect, useState } from 'react';
import { getUsers, createUser, deleteUser, type User, type CreateUserRequest } from '@/lib/api';
import { useAuth } from '@/lib/auth';
import AdminRoute from '@/components/AdminRoute';

function UsersPageContent() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [creating, setCreating] = useState(false);
  const [deletingUserId, setDeletingUserId] = useState<number | null>(null);
  const [formData, setFormData] = useState<CreateUserRequest>({
    username: '',
    givenname: '',
    familyname: '',
    password: '',
  });

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const data = await getUsers();
      setUsers(data);
      setError(null);
    } catch (err) {
      setError('Failed to load users');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setCreating(true);
      setError(null);
      
      const newUser = await createUser(formData);
      
      // Add to list and close form
      setUsers([...users, newUser]);
      setShowCreateForm(false);
      setFormData({ username: '', givenname: '', familyname: '', password: '' });
      
      alert(`User created successfully!\nUser ID: ${newUser.userid}`);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Failed to create user';
      setError(errorMsg);
      console.error(err);
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteUser = async (userid: number, username: string) => {
    if (!confirm(`Are you sure you want to delete user "${username}"?\n\nThis will permanently delete:\n- The user account\n- All their images\n- All image labels\n\nThis action cannot be undone!`)) {
      return;
    }

    try {
      setDeletingUserId(userid);
      setError(null);
      
      await deleteUser(userid);
      
      // Remove from list
      setUsers(users.filter(u => u.userid !== userid));
      
      alert(`User "${username}" deleted successfully`);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Failed to delete user';
      setError(errorMsg);
      alert(errorMsg);
      console.error(err);
    } finally {
      setDeletingUserId(null);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading users...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
          <p className="text-red-800 dark:text-red-200">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
              User Management
            </h1>
            <p className="text-gray-400 mt-1">Admin-only access</p>
          </div>
          <button
            onClick={() => setShowCreateForm(true)}
            className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
          >
            Create User
          </button>
        </div>

        <div className="border border-gray-700 bg-transparent rounded-lg p-6 mb-6">
          <p className="text-gray-400">
            Total users: <span className="font-semibold text-indigo-400">{users.length}</span>
          </p>
        </div>

        <div className="space-y-4">
          {users.map((user) => (
            <div
              key={user.userid}
              className="border border-gray-700 bg-transparent rounded-lg p-6 hover:border-indigo-500 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                      {user.givenname} {user.familyname}
                    </h3>
                    {user.is_admin && (
                      <span className="px-2 py-0.5 text-xs font-semibold bg-indigo-600 text-white rounded">
                        ADMIN
                      </span>
                    )}
                  </div>
                  <p className="text-gray-600 dark:text-gray-400">
                    @{user.username}
                  </p>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      User ID
                    </p>
                    <p className="text-lg font-semibold text-indigo-400">
                      {user.userid}
                    </p>
                  </div>
                  <button
                    onClick={() => handleDeleteUser(user.userid, user.username)}
                    disabled={deletingUserId === user.userid}
                    className="bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {deletingUserId === user.userid ? 'Deleting...' : 'Delete'}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {users.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 dark:text-gray-400">No users found</p>
          </div>
        )}

        {/* Create User Modal */}
        {showCreateForm && (
          <div
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
            onClick={() => !creating && setShowCreateForm(false)}
          >
            <div
              className="border border-gray-700 bg-[#0a0a0a] rounded-lg max-w-md w-full p-6"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Create New User
                </h2>
                <button
                  onClick={() => setShowCreateForm(false)}
                  disabled={creating}
                  className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 disabled:opacity-50"
                >
                  ×
                </button>
              </div>

              <form onSubmit={handleCreateUser} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Username *
                  </label>
                  <input
                    type="text"
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    required
                    disabled={creating}
                    placeholder="e.g., jdoe"
                    className="w-full px-4 py-2 border border-gray-700 rounded-lg bg-[#0a0a0a] text-white focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    First Name *
                  </label>
                  <input
                    type="text"
                    value={formData.givenname}
                    onChange={(e) => setFormData({ ...formData, givenname: e.target.value })}
                    required
                    disabled={creating}
                    placeholder="e.g., John"
                    className="w-full px-4 py-2 border border-gray-700 rounded-lg bg-[#0a0a0a] text-white focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Last Name *
                  </label>
                  <input
                    type="text"
                    value={formData.familyname}
                    onChange={(e) => setFormData({ ...formData, familyname: e.target.value })}
                    required
                    disabled={creating}
                    placeholder="e.g., Doe"
                    className="w-full px-4 py-2 border border-gray-700 rounded-lg bg-[#0a0a0a] text-white focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
                  />
                </div>


                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Password *
                  </label>
                  <input
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    required
                    disabled={creating}
                    placeholder="Set a password for this user"
                    className="w-full px-4 py-2 border border-gray-700 rounded-lg bg-[#0a0a0a] text-white focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
                  />
                </div>

                {error && (
                  <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                    <p className="text-red-800 dark:text-red-200 text-sm">{error}</p>
                  </div>
                )}

                <div className="flex gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowCreateForm(false)}
                    disabled={creating}
                    className="flex-1 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 font-semibold py-2 px-4 rounded-lg transition-colors disabled:opacity-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={creating}
                    className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors disabled:opacity-50"
                  >
                    {creating ? 'Creating...' : 'Create User'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function UsersPage() {
  return (
    <AdminRoute>
      <UsersPageContent />
    </AdminRoute>
  );
}