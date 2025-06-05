'use client';

import { useState } from 'react';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import AnalysisForm from '@/components/AnalysisForm';
import AnalysisResults from '@/components/AnalysisResults';
import { useAppStore } from '@/lib/store';

export default function Home() {
  const {
    isAnalyzing,
    analysisResults,
    analysisError,
    activeTab,
    setActiveTab,
  } = useAppStore();

  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      
      <main className="flex-grow container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-10">
            <h1 className="text-4xl font-bold mb-4">VC Copilot</h1>
            <p className="text-xl text-secondary-600 dark:text-secondary-400 max-w-3xl mx-auto">
              AI-powered startup analysis tool for venture capitalists and investors.
              Get deep insights and success predictions for any startup in minutes.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="md:col-span-1">
              <AnalysisForm />
            </div>
            
            <div className="md:col-span-2">
              <AnalysisResults 
                results={analysisResults}
                isLoading={isAnalyzing}
                error={analysisError}
              />
            </div>
          </div>
        </div>
      </main>
      
      <Footer />
    </div>
  );
}
