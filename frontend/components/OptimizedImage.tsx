'use client';

import { useState } from 'react';

interface OptimizedImageProps {
  src: string;
  alt: string;
  className?: string;
  style?: React.CSSProperties;
  onClick?: () => void;
}

/**
 * Optimized image component with:
 * - Smooth fade-in on load
 * - Background placeholder
 * - Lazy loading
 * - Async decoding
 */
export default function OptimizedImage({ 
  src, 
  alt, 
  className = '', 
  style,
  onClick 
}: OptimizedImageProps) {
  const [loaded, setLoaded] = useState(false);

  return (
    <div className={`relative overflow-hidden ${onClick ? 'cursor-pointer' : ''}`} onClick={onClick}>
      {/* Placeholder background */}
      <div 
        className={`absolute inset-0 bg-gray-800 transition-opacity duration-300 ${loaded ? 'opacity-0' : 'opacity-100'}`}
      />
      <img
        src={src}
        alt={alt}
        className={`transition-opacity duration-300 ${loaded ? 'opacity-100' : 'opacity-0'} ${className}`}
        style={style}
        loading="lazy"
        decoding="async"
        onLoad={() => setLoaded(true)}
        fetchPriority="low"
      />
    </div>
  );
}
