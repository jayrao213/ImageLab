'use client';

import { useState, useEffect } from 'react';
import { searchImagesByLabel, getImageUrl, getImageLabels, downloadImage, deleteImage, getUsers, type ImageWithLabel, type ImageLabel, type User } from '@/lib/api';
import { useAuth } from '@/lib/auth';
import ProtectedRoute from '@/components/ProtectedRoute';

function SearchPageContent() {
  const { user: authUser } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState<ImageWithLabel[]>([]);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [selectedImage, setSelectedImage] = useState<{ assetid: number; localname: string } | null>(null);
  const [allLabels, setAllLabels] = useState<ImageLabel[]>([]);
  const [loadingLabels, setLoadingLabels] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [deletingSingleImage, setDeletingSingleImage] = useState(false);
  
  // Admin filter
  const [users, setUsers] = useState<User[]>([]);
  const [filterUserId, setFilterUserId] = useState<number | null>(null);

  // Load users if admin
  useEffect(() => {
    if (authUser?.is_admin) {
      getUsers().then(setUsers).catch(console.error);
    }
  }, [authUser?.is_admin]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!searchTerm.trim()) {
      setError('Please enter a search term');
      return;
    }

    if (!authUser) {
      setError('Please log in to search');
      return;
    }

    try {
      setSearching(true);
      setError(null);
      setHasSearched(true);

      // Admin can search all images or filter by user; regular users only search their own
      const targetUserId = authUser.is_admin 
        ? (filterUserId ?? undefined)  // Admin: use filter or undefined for all
        : authUser.userid;             // Regular user: only their own
      
      const data = await searchImagesByLabel(searchTerm, targetUserId);
      setResults(data);
    } catch (err) {
      setError('Failed to search images');
      console.error(err);
    } finally {
      setSearching(false);
    }
  };

  const handleImageClick = async (assetId: number, localname: string) => {
    setSelectedImage({ assetid: assetId, localname });
    setLoadingLabels(true);
    
    try {
      const labels = await getImageLabels(assetId);
      setAllLabels(labels);
    } catch (err) {
      console.error('Failed to load labels:', err);
      setAllLabels([]);
    } finally {
      setLoadingLabels(false);
    }
  };

  const handleDownload = async (assetId: number, localname: string) => {
    try {
      setDownloading(true);
      await downloadImage(assetId, localname);
    } catch (err) {
      console.error('Failed to download image:', err);
      alert('Failed to download image');
    } finally {
      setDownloading(false);
    }
  };

  const handleDeleteImage = async (assetId: number, localname: string) => {
    if (!confirm(`Are you sure you want to delete "${localname}"?\n\nThis will permanently delete the image and all its labels. This action cannot be undone!`)) {
      return;
    }

    try {
      setDeletingSingleImage(true);
      await deleteImage(assetId);
      
      // Remove from search results
      setResults(results.filter(result => result.assetid !== assetId));
      setSelectedImage(null);
      
      alert('Image deleted successfully');
    } catch (err) {
      console.error('Failed to delete image:', err);
      alert('Failed to delete image');
    } finally {
      setDeletingSingleImage(false);
    }
  };

  // Group results by assetid
  const groupedResults = results.reduce((acc, item) => {
    if (!acc[item.assetid]) {
      acc[item.assetid] = [];
    }
    acc[item.assetid].push(item);
    return acc;
  }, {} as Record<number, ImageWithLabel[]>);

  const assetIds = Object.keys(groupedResults).map(Number);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
            {authUser?.is_admin ? 'Search All Images' : 'Search My Images'}
          </h1>
          {authUser?.is_admin && (
            <p className="text-gray-400 mt-1">Admin view - search across all users&apos; images</p>
          )}
        </div>

        {/* Admin user filter */}
        {authUser?.is_admin && (
          <div className="border border-gray-700 bg-transparent rounded-lg p-4 mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Filter by User
            </label>
            <select
              value={filterUserId ?? ''}
              onChange={(e) => setFilterUserId(e.target.value ? Number(e.target.value) : null)}
              className="w-full md:w-64 px-4 py-2 border border-gray-700 rounded-lg bg-[#0a0a0a] text-white focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">All Users</option>
              {users.map((user) => (
                <option key={user.userid} value={user.userid}>
                  {user.givenname} {user.familyname} (@{user.username})
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Search Form */}
        <div className="border border-gray-700 bg-transparent rounded-lg p-8 mb-8">
          <form onSubmit={handleSearch} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Search for objects, scenes, or activities
              </label>
              <div className="flex gap-4">
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="e.g., person, car, sunset, food..."
                  className="flex-1 px-4 py-3 border border-gray-700 rounded-lg bg-transparent text-white focus:ring-2 focus:ring-indigo-500"
                />
                <button
                  type="submit"
                  disabled={searching}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-8 py-3 rounded-lg transition-colors disabled:opacity-50"
                >
                  {searching ? 'Searching...' : 'Search'}
                </button>
              </div>
              <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                Search supports partial matches (e.g., "boat" will find "sailboat")
              </p>
            </div>
          </form>

          {error && (
            <div className="mt-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <p className="text-red-800 dark:text-red-200">{error}</p>
            </div>
          )}
        </div>

        {/* Results */}
        {searching ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">Searching images...</p>
          </div>
        ) : hasSearched && (
          <>
            <div className="border border-gray-700 bg-transparent rounded-lg p-6 mb-6">
              <p className="text-gray-300">
                Found <span className="font-semibold text-indigo-400">{assetIds.length}</span> image
                {assetIds.length !== 1 ? 's' : ''} matching "<span className="font-semibold">{searchTerm}</span>"
              </p>
            </div>

            {assetIds.length === 0 ? (
              <div className="text-center py-12 border border-gray-700 bg-transparent rounded-lg">
                <p className="text-gray-400 text-lg">No images found</p>
                <p className="text-gray-500 mt-2">
                  Try a different search term or upload more images
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {assetIds.map((assetId) => {
                  const imageResults = groupedResults[assetId];
                  const localname = imageResults[0].localname;
                  return (
                    <div
                      key={assetId}
                      onClick={() => handleImageClick(assetId, localname)}
                      className="border border-gray-700 bg-transparent rounded-lg overflow-hidden hover:border-indigo-500 transition-colors cursor-pointer"
                    >
                      <div className="aspect-video bg-gray-800 relative overflow-hidden">
                        <img
                          src={getImageUrl(assetId, true)}
                          alt={localname}
                          className="w-full h-full object-cover transition-opacity duration-300"
                          loading="lazy"
                          decoding="async"
                          onLoad={(e) => e.currentTarget.style.opacity = '1'}
                          style={{ opacity: 0 }}
                        />
                      </div>
                      <div className="p-4">
                        <h3 className="font-semibold text-gray-900 dark:text-white truncate">
                          {localname}
                        </h3>
                        <p className="text-xs text-gray-500 dark:text-gray-500 mt-1 mb-2">
                          Asset ID: {assetId}
                        </p>
                        <div className="space-y-1">
                          <p className="text-xs font-semibold text-gray-700 dark:text-gray-300">
                            Matching Labels:
                          </p>
                          <div className="flex flex-wrap gap-1">
                            {imageResults.map((item, idx) => (
                              <span
                                key={idx}
                                className="bg-indigo-600/20 text-indigo-300 px-2 py-1 rounded text-xs border border-indigo-600/40"
                              >
                                {item.label} ({item.confidence}%)
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </>
        )}

        {/* Info Section */}
        {!hasSearched && (
          <div className="border border-gray-700 bg-transparent rounded-lg p-8">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
              How AI Image Search Works
            </h2>
            <div className="grid md:grid-cols-2 gap-6 text-gray-700 dark:text-gray-300">
              <div>
                <h3 className="font-semibold mb-2">Automatic Labeling</h3>
                <p className="text-sm">
                  When images are uploaded, AWS Rekognition automatically analyzes them
                  and detects objects, scenes, activities, and more.
                </p>
              </div>
              <div>
                <h3 className="font-semibold mb-2">Smart Search</h3>
                <p className="text-sm">
                  Search for any label to find all images containing that object.
                  Partial matches are supported for flexible searching.
                </p>
              </div>
              <div>
                <h3 className="font-semibold mb-2">Confidence Scores</h3>
                <p className="text-sm">
                  Each label has a confidence score showing how certain the AI is
                  about the detection. Only labels above 80% are saved.
                </p>
              </div>
              <div>
                <h3 className="font-semibold mb-2">Instant Results</h3>
                <p className="text-sm">
                  Search results are retrieved instantly from the database,
                  making it easy to find specific images in large collections.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Image Details Modal */}
        {selectedImage && (
          <div
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
            onClick={() => setSelectedImage(null)}
          >
            <div
              className="border border-gray-700 bg-[#0a0a0a] rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                    Image Details
                  </h2>
                  <button
                    onClick={() => setSelectedImage(null)}
                    className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                  >
                    ×
                  </button>
                </div>

                <div className="mb-4">
                  <img
                    src={getImageUrl(selectedImage.assetid)}
                    alt={selectedImage.localname}
                    className="w-full rounded-lg"
                    loading="eager"
                  />
                </div>

                <div className="space-y-2 mb-4">
                  <p><strong>Filename:</strong> {selectedImage.localname}</p>
                  <p><strong>Asset ID:</strong> {selectedImage.assetid}</p>
                </div>

                <div className="flex gap-3 mb-4">
                  <button
                    onClick={() => handleDownload(selectedImage.assetid, selectedImage.localname)}
                    disabled={downloading || deletingSingleImage}
                    className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors disabled:opacity-50"
                  >
                    {downloading ? 'Downloading...' : 'Download Image'}
                  </button>
                  <button
                    onClick={() => handleDeleteImage(selectedImage.assetid, selectedImage.localname)}
                    disabled={downloading || deletingSingleImage}
                    className="flex-1 bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors disabled:opacity-50"
                  >
                    {deletingSingleImage ? 'Deleting...' : 'Delete Image'}
                  </button>
                </div>

                <div>
                  <h3 className="font-semibold mb-2 text-gray-900 dark:text-white">
                    AI-Detected Labels
                  </h3>
                  {loadingLabels ? (
                    <div className="text-center py-4">
                      <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                    </div>
                  ) : allLabels.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {allLabels.map((label, idx) => (
                        <span
                          key={idx}
                          className="bg-indigo-600/20 text-indigo-300 px-3 py-1 rounded-full text-sm border border-indigo-600/40"
                        >
                          {label.label} ({label.confidence}%)
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 dark:text-gray-400">No labels found</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function SearchPage() {
  return (
    <ProtectedRoute>
      <SearchPageContent />
    </ProtectedRoute>
  );
}