"use client";

import { useState } from 'react';
import LoadingSpinner from '@/components/LoadingSpinner';

interface UrlInputProps {
  onSubmit: (url: string) => Promise<void>;
  isLoading: boolean;
}

export default function UrlInput({ onSubmit, isLoading }: UrlInputProps) {
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!url) {
      setError('Please enter a startup URL');
      return;
    }
    
    // Basic URL validation
    try {
      new URL(url);
      setError('');
      await onSubmit(url);
    } catch (e) {
      setError('Please enter a valid URL (include https://)');
    }
  };

  return (
    <div>
      <h2 className="text-lg font-medium text-gray-900 mb-4">Enter Startup URL</h2>
      <form onSubmit={handleSubmit} className="sm:flex sm:items-center">
        <div className="w-full">
          <label htmlFor="url" className="sr-only">
            Startup URL
          </label>
          <input
            type="text"
            id="url"
            placeholder="https://example-startup.com"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={isLoading}
            className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
          />
          {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
        </div>
        <button
          type="submit"
          disabled={isLoading || !url}
          className="mt-3 w-full inline-flex items-center justify-center px-4 py-2 border border-transparent shadow-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <>
              <LoadingSpinner className="h-4 w-4 mr-2" />
              Gathering Data...
            </>
          ) : (
            'Gather Data'
          )}
        </button>
      </form>
    </div>
  );
}
