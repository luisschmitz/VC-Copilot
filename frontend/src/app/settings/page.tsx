'use client';

import { useState } from 'react';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { FaCog, FaCheck, FaMoon, FaSun, FaDatabase, FaKey } from 'react-icons/fa';

export default function Settings() {
  const [darkMode, setDarkMode] = useState(true);
  const [apiUrl, setApiUrl] = useState(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000');
  const [openaiKey, setOpenaiKey] = useState('');
  const [maxScrapeDepth, setMaxScrapeDepth] = useState(3);
  const [savedSuccess, setSavedSuccess] = useState(false);
  
  const handleSaveSettings = () => {
    // In a real app, this would save to localStorage or a backend API
    localStorage.setItem('vc_copilot_settings', JSON.stringify({
      darkMode,
      apiUrl,
      openaiKey,
      maxScrapeDepth
    }));
    
    // Show success message
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };
  
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      
      <main className="flex-grow container mx-auto px-4 py-8">
        <div className="max-w-3xl mx-auto">
          <div className="flex items-center mb-6">
            <FaCog className="text-primary-600 text-2xl mr-3" />
            <h1 className="text-3xl font-bold">Settings</h1>
          </div>
          
          <div className="card mb-6">
            <h2 className="text-xl font-semibold mb-4">Appearance</h2>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                {darkMode ? (
                  <FaMoon className="text-primary-600 mr-3" />
                ) : (
                  <FaSun className="text-amber-500 mr-3" />
                )}
                <div>
                  <h3 className="font-medium">Dark Mode</h3>
                  <p className="text-sm text-secondary-500">Enable dark mode for a better viewing experience at night</p>
                </div>
              </div>
              
              <label className="relative inline-flex items-center cursor-pointer">
                <input 
                  type="checkbox" 
                  className="sr-only peer" 
                  checked={darkMode}
                  onChange={() => setDarkMode(!darkMode)}
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-secondary-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
              </label>
            </div>
          </div>
          
          <div className="card mb-6">
            <h2 className="text-xl font-semibold mb-4">API Configuration</h2>
            
            <div className="mb-4">
              <div className="flex items-center mb-2">
                <FaDatabase className="text-primary-600 mr-2" />
                <label htmlFor="apiUrl" className="font-medium">Backend API URL</label>
              </div>
              <input
                id="apiUrl"
                type="text"
                className="w-full p-2 border border-gray-300 dark:border-secondary-700 rounded-md bg-white dark:bg-secondary-800"
                value={apiUrl}
                onChange={(e) => setApiUrl(e.target.value)}
                placeholder="http://localhost:8000"
              />
              <p className="text-xs text-secondary-500 mt-1">
                The URL of your VC Copilot backend API
              </p>
            </div>
            
            <div className="mb-4">
              <div className="flex items-center mb-2">
                <FaKey className="text-primary-600 mr-2" />
                <label htmlFor="openaiKey" className="font-medium">OpenAI API Key (Optional)</label>
              </div>
              <input
                id="openaiKey"
                type="password"
                className="w-full p-2 border border-gray-300 dark:border-secondary-700 rounded-md bg-white dark:bg-secondary-800"
                value={openaiKey}
                onChange={(e) => setOpenaiKey(e.target.value)}
                placeholder="sk-..."
              />
              <p className="text-xs text-secondary-500 mt-1">
                Your OpenAI API key for direct integration (optional, can be handled by backend)
              </p>
            </div>
          </div>
          
          <div className="card mb-6">
            <h2 className="text-xl font-semibold mb-4">Analysis Settings</h2>
            
            <div className="mb-4">
              <label htmlFor="maxScrapeDepth" className="font-medium block mb-2">
                Maximum Scrape Depth
              </label>
              <input
                id="maxScrapeDepth"
                type="range"
                min="1"
                max="5"
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-secondary-700"
                value={maxScrapeDepth}
                onChange={(e) => setMaxScrapeDepth(parseInt(e.target.value))}
              />
              <div className="flex justify-between text-xs text-secondary-500 mt-1">
                <span>Minimal (1)</span>
                <span>Default (3)</span>
                <span>Deep (5)</span>
              </div>
              <p className="text-sm text-secondary-500 mt-2">
                Current value: {maxScrapeDepth} - {maxScrapeDepth === 1 ? 'Minimal scraping' : maxScrapeDepth === 5 ? 'Deep scraping' : 'Standard scraping'}
              </p>
            </div>
          </div>
          
          <div className="flex justify-end">
            {savedSuccess && (
              <div className="flex items-center text-green-500 mr-4">
                <FaCheck className="mr-1" />
                <span>Settings saved!</span>
              </div>
            )}
            <button 
              className="btn-primary"
              onClick={handleSaveSettings}
            >
              Save Settings
            </button>
          </div>
        </div>
      </main>
      
      <Footer />
    </div>
  );
}
