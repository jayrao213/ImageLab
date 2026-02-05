'use client';

import { useState } from 'react';
import { uploadImage } from '@/lib/api';
import { useAuth } from '@/lib/auth';
import ProtectedRoute from '@/components/ProtectedRoute';

function UploadPageContent() {
  const { user: authUser } = useAuth();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
      
      setError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!authUser) {
      setError('Please log in to upload');
      return;
    }

    if (!selectedFile) {
      setError('Please select an image file');
      return;
    }

    try {
      setUploading(true);
      setError(null);

      const result = await uploadImage(authUser.userid, selectedFile);
      
      alert(`Image uploaded successfully!\nAsset ID: ${result.assetid}\n${result.message}`);
      
      // Reset form to default state
      setSelectedFile(null);
      setPreview(null);
      
      // Reset the file input element
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileInput) {
        fileInput.value = '';
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload image');
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-4xl font-bold mb-8 text-gray-900 dark:text-white">
          Upload Image
        </h1>

        <div className="border border-gray-700 bg-transparent rounded-lg p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* File Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Select Image *
              </label>
              <input
                type="file"
                accept="image/png, image/jpeg"
                onChange={handleFileChange}
                required
                className="w-full px-4 py-2 border border-gray-700 rounded-lg bg-transparent text-white file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-700 file:cursor-pointer"
              />
              <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                Supported formats: PNG, JPG
              </p>
            </div>

            {/* Preview */}
            {preview && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Preview
                </label>
                <div className="border border-gray-300 dark:border-gray-600 rounded-lg overflow-hidden">
                  <img
                    src={preview}
                    alt="Preview"
                    className="w-full h-auto max-h-96 object-contain bg-gray-100 dark:bg-gray-900"
                  />
                </div>
                {selectedFile && (
                  <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                    Filename: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                  </p>
                )}
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                <p className="text-red-800 dark:text-red-200">{error}</p>
              </div>
            )}

            {/* Info Box */}
            <div className="border border-gray-700 bg-transparent rounded-lg p-4">
              <h3 className="font-semibold text-indigo-200 mb-2">
                What happens when you upload?
              </h3>
              <ul className="text-sm text-indigo-300 space-y-1">
                <li>Image is stored securely in AWS S3</li>
                <li>Database record is created</li>
                <li>AWS Rekognition analyzes the image</li>
                <li>AI-detected labels are saved for search</li>
              </ul>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={uploading || !selectedFile}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {uploading ? (
                <span className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Uploading...
                </span>
              ) : (
                'Upload Image'
              )}
            </button>
          </form>
        </div>

        {/* Additional Info */}
        <div className="mt-6 border border-gray-700 bg-transparent rounded-lg p-6">
          <h2 className="font-semibold text-gray-900 dark:text-white mb-3">
            Tips for best results:
          </h2>
          <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-2">
            <li>• Use clear, high-quality images for better AI label detection</li>
            <li>• Supported formats: JPEG, PNG, GIF</li>
            <li>• The AI will automatically detect objects, scenes, and activities</li>
            <li>• Labels with confidence &gt; 80% are saved</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default function UploadPage() {
  return (
    <ProtectedRoute>
      <UploadPageContent />
    </ProtectedRoute>
  );
}
