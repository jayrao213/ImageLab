'use client';

import { useEffect, useState, useRef } from 'react';
import { getImages, getImageLabels, deleteAllImages, deleteImage, getImageUrl, downloadImage, getUsers, type Image, type ImageLabel, type User } from '@/lib/api';
import { useAuth } from '@/lib/auth';
import ProtectedRoute from '@/components/ProtectedRoute';

function ImagesPageContent() {
  const { user: authUser } = useAuth();
  const [images, setImages] = useState<Image[]>([]);
  const [selectedImage, setSelectedImage] = useState<Image | null>(null);
  const [labels, setLabels] = useState<ImageLabel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [deletingSingleImage, setDeletingSingleImage] = useState(false);
  const [downloading, setDownloading] = useState(false);
  
  // Admin filter
  const [users, setUsers] = useState<User[]>([]);
  const [filterUserId, setFilterUserId] = useState<number | null | 'select'>(authUser?.is_admin ? 'select' : null);
  
  // Pagination state
  const [displayedImages, setDisplayedImages] = useState<Image[]>([]);
  const [page, setPage] = useState(1);
  const IMAGES_PER_PAGE = 12;
  const observerTarget = useRef<HTMLDivElement>(null);

  // Load users if admin
  useEffect(() => {
    if (authUser?.is_admin) {
      getUsers().then(setUsers).catch(console.error);
    }
  }, [authUser?.is_admin]);

  const fetchImages = async () => {
    if (!authUser) return;
    
    // For admin, don't load images until a user is selected
    if (authUser.is_admin && filterUserId === 'select') {
      setLoading(false);
      setImages([]);
      return;
    }
    
    try {
      setLoading(true);
      // Admin can view all images or filter by user; regular users only see their own
      const targetUserId = authUser.is_admin 
        ? (filterUserId === null ? undefined : filterUserId as number)  // Admin: use filter or undefined for all
        : authUser.userid;             // Regular user: only their own
      const data = await getImages(targetUserId);
      setImages(data);
      setPage(1);
      setError(null);
    } catch (err) {
      setError('Failed to load images');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Update displayed images when images or page changes
  useEffect(() => {
    const endIndex = page * IMAGES_PER_PAGE;
    setDisplayedImages(images.slice(0, endIndex));
  }, [images, page]);

  // Infinite scroll observer
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && displayedImages.length < images.length) {
          setPage((prev) => prev + 1);
        }
      },
      { threshold: 0.1 }
    );

    const currentTarget = observerTarget.current;
    if (currentTarget) {
      observer.observe(currentTarget);
    }

    return () => {
      if (currentTarget) {
        observer.unobserve(currentTarget);
      }
    };
  }, [displayedImages.length, images.length]);

  useEffect(() => {
    if (authUser) {
      fetchImages();
    }
  }, [authUser, filterUserId]);

  const handleImageClick = async (image: Image) => {
    setSelectedImage(image);
    try {
      const imageLabels = await getImageLabels(image.assetid);
      setLabels(imageLabels);
    } catch (err) {
      console.error('Failed to load labels:', err);
      setLabels([]);
    }
  };

  const handleDeleteAll = async () => {
    if (!authUser) return;
    
    // Determine which images will be deleted
    let confirmMessage = '';
    let deleteUserId: number | undefined = undefined;
    
    if (authUser.is_admin) {
      if (filterUserId === null) {
        // Admin viewing all users' images - delete everything
        confirmMessage = 'Are you sure you want to delete ALL images from ALL users? This cannot be undone!';
        deleteUserId = undefined; // Delete all
      } else if (filterUserId === authUser.userid) {
        // Admin viewing their own images
        confirmMessage = 'Are you sure you want to delete ALL your images? This cannot be undone!';
        deleteUserId = authUser.userid;
      } else {
        // Admin viewing another user's images
        const targetUser = users.find(u => u.userid === filterUserId);
        const username = targetUser ? targetUser.username : `User ${filterUserId}`;
        confirmMessage = `Are you sure you want to delete ALL images for ${username}? This cannot be undone!`;
        deleteUserId = filterUserId as number;
      }
    } else {
      // Regular user - only delete their own images
      confirmMessage = 'Are you sure you want to delete ALL your images? This cannot be undone!';
      deleteUserId = authUser.userid;
    }
    
    if (!confirm(confirmMessage)) {
      return;
    }

    try {
      setDeleting(true);
      await deleteAllImages(deleteUserId);
      await fetchImages();
      alert('All images deleted successfully');
    } catch (err) {
      alert('Failed to delete images');
      console.error(err);
    } finally {
      setDeleting(false);
    }
  };

  const handleDownload = async (image: Image) => {
    try {
      setDownloading(true);
      await downloadImage(image.assetid, image.localname);
    } catch (err) {
      console.error('Failed to download image:', err);
      alert('Failed to download image');
    } finally {
      setDownloading(false);
    }
  };

  const handleDeleteSingleImage = async (image: Image) => {
    if (!confirm(`Are you sure you want to delete "${image.localname}"?\n\nThis will permanently delete the image and all its labels. This action cannot be undone!`)) {
      return;
    }

    try {
      setDeletingSingleImage(true);
      await deleteImage(image.assetid);
      
      // Remove from local state
      setImages(images.filter(img => img.assetid !== image.assetid));
      setSelectedImage(null);
      
      alert('Image deleted successfully');
    } catch (err) {
      console.error('Failed to delete image:', err);
      alert('Failed to delete image');
    } finally {
      setDeletingSingleImage(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
              {authUser?.is_admin ? 'All Images' : 'My Images'}
            </h1>
            {authUser?.is_admin && (
              <p className="text-gray-400 mt-1">Admin view - viewing all users&apos; images</p>
            )}
          </div>
          {images.length > 0 && (
            <button
              onClick={handleDeleteAll}
              disabled={deleting}
              className="bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors disabled:opacity-50"
            >
              {deleting ? 'Deleting...' : 'Delete All'}
            </button>
          )}
        </div>

        {/* Admin user filter */}
        {authUser?.is_admin && (
          <div className="border border-gray-700 bg-transparent rounded-lg p-4 mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Filter by User
            </label>
            <select
              value={filterUserId === 'select' ? 'select' : (filterUserId ?? '')}
              onChange={(e) => {
                const val = e.target.value;
                if (val === 'select') {
                  setFilterUserId('select');
                } else if (val === '') {
                  setFilterUserId(null);
                } else {
                  setFilterUserId(Number(val));
                }
              }}
              className="w-full md:w-64 px-4 py-2 border border-gray-700 rounded-lg bg-[#0a0a0a] text-white focus:ring-2 focus:ring-indigo-500"
            >
              <option value="select">Select a User</option>
              <option value="">All Users</option>
              {users.map((user) => (
                <option key={user.userid} value={user.userid}>
                  {user.givenname} {user.familyname} (@{user.username})
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Image count */}
        <div className="border border-gray-700 bg-transparent rounded-lg p-6 mb-6">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Showing {displayedImages.length} of {images.length} image{images.length !== 1 ? 's' : ''}
          </p>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">Loading images...</p>
          </div>
        ) : error ? (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
            <p className="text-red-800 dark:text-red-200">{error}</p>
          </div>
        ) : images.length === 0 ? (
          <div className="text-center py-12 border border-gray-700 bg-transparent rounded-lg">
            <p className="text-gray-400 text-lg">No images found</p>
            <p className="text-gray-400 dark:text-gray-500 mt-2">
              {authUser?.is_admin && filterUserId === 'select' 
                ? 'Select a user from the dropdown above to view their images' 
                : 'Upload your first image to get started!'}
            </p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {displayedImages.map((image) => (
                <div
                  key={image.assetid}
                  onClick={() => handleImageClick(image)}
                  className="border border-gray-700 bg-transparent rounded-lg overflow-hidden hover:border-indigo-500 transition-colors cursor-pointer"
                >
                  <div className="aspect-video bg-gray-800 relative overflow-hidden">
                    <img
                      src={getImageUrl(image.assetid, true)}
                      alt={image.localname}
                      className="w-full h-full object-cover transition-opacity duration-300"
                      loading="lazy"
                      decoding="async"
                      onLoad={(e) => e.currentTarget.style.opacity = '1'}
                      style={{ opacity: 0 }}
                    />
                  </div>
                  <div className="p-4">
                    <h3 className="font-semibold text-gray-900 dark:text-white truncate">
                      {image.localname}
                    </h3>
                    <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                      Asset ID: {image.assetid}
                    </p>
                  </div>
                </div>
              ))}
            </div>
            
            {/* Infinite scroll trigger */}
            {displayedImages.length < images.length && (
              <div ref={observerTarget} className="text-center py-8">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                <p className="mt-2 text-gray-600 dark:text-gray-400">Loading more images...</p>
              </div>
            )}
          </>
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
                    onClick={() => handleDownload(selectedImage)}
                    disabled={downloading || deletingSingleImage}
                    className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors disabled:opacity-50"
                  >
                    {downloading ? 'Downloading...' : 'Download Image'}
                  </button>
                  <button
                    onClick={() => handleDeleteSingleImage(selectedImage)}
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
                  {labels.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {labels.map((label, idx) => (
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

export default function ImagesPage() {
  return (
    <ProtectedRoute>
      <ImagesPageContent />
    </ProtectedRoute>
  );
}