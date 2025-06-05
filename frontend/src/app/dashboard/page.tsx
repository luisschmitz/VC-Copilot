'use client';

import { useState, useEffect } from 'react';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import TabNavigation from '@/components/TabNavigation';
import RecentAnalyses from '@/components/RecentAnalyses';
import AnalysisResults from '@/components/AnalysisResults';
import { FaChartBar, FaHistory, FaStar } from 'react-icons/fa';
import { AnalysisResponse } from '@/types/api';
import { useAppStore } from '@/lib/store';

// Mock data for demonstration - in a real app, this would come from an API or local storage
const mockAnalyses: AnalysisResponse[] = [
  {
    id: '1',
    company_name: 'TechStartup Inc.',
    url: 'https://techstartup.com',
    success_prediction: true,
    overall_assessment: 'Strong potential with innovative technology and experienced team.',
    timestamp: new Date().toISOString(),
    sections: {
      'Executive Summary': 'TechStartup Inc. is developing a revolutionary AI platform...',
      'Key Insights': '- Strong technical team\n- Innovative product\n- Growing market',
      'Key Risks': '- Competitive landscape\n- Funding challenges\n- Regulatory concerns'
    }
  },
  {
    id: '2',
    company_name: 'GreenEnergy Solutions',
    url: 'https://greenenergy.io',
    success_prediction: true,
    overall_assessment: 'Promising clean energy startup with solid market traction.',
    timestamp: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
    sections: {
      'Executive Summary': 'GreenEnergy Solutions is pioneering sustainable energy solutions...',
      'Market Analysis': 'The clean energy market is growing at 15% annually...',
      'Team Assessment': 'The founding team has strong technical and business backgrounds...'
    }
  },
  {
    id: '3',
    company_name: 'HealthTech Innovations',
    url: 'https://healthtech.co',
    success_prediction: false,
    overall_assessment: 'Interesting concept but faces significant regulatory challenges.',
    timestamp: new Date(Date.now() - 172800000).toISOString(), // 2 days ago
    sections: {
      'Executive Summary': 'HealthTech Innovations aims to revolutionize patient care...',
      'Regulatory Challenges': 'The healthcare industry has strict regulatory requirements...',
      'Competition': 'Several established players already offer similar solutions...'
    }
  }
];

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('recent');
  const [selectedAnalysis, setSelectedAnalysis] = useState<AnalysisResponse | null>(null);
  const { analysisResults } = useAppStore();
  
  // Combine mock analyses with any real analysis from the store
  const allAnalyses = [...(analysisResults ? [analysisResults] : []), ...mockAnalyses];
  
  // Filter analyses based on active tab
  const filteredAnalyses = activeTab === 'favorites' 
    ? allAnalyses.filter((_, index) => index < 2) // Mock favorite filter
    : allAnalyses;
  
  const handleSelectAnalysis = (analysis: AnalysisResponse) => {
    setSelectedAnalysis(analysis);
  };
  
  const tabs = [
    { id: 'recent', label: 'Recent', icon: <FaHistory /> },
    { id: 'favorites', label: 'Favorites', icon: <FaStar /> },
    { id: 'all', label: 'All Analyses', icon: <FaChartBar /> }
  ];
  
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      
      <main className="flex-grow container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
          
          <TabNavigation 
            tabs={tabs} 
            activeTab={activeTab} 
            onTabChange={setActiveTab} 
            className="mb-6"
          />
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="md:col-span-1">
              <RecentAnalyses 
                analyses={filteredAnalyses} 
                onSelectAnalysis={handleSelectAnalysis}
              />
            </div>
            
            <div className="md:col-span-2">
              {selectedAnalysis ? (
                <AnalysisResults 
                  results={selectedAnalysis}
                  isLoading={false}
                  error={null}
                />
              ) : (
                <div className="card p-8 text-center">
                  <FaChartBar className="mx-auto text-5xl text-secondary-300 dark:text-secondary-600 mb-4" />
                  <h3 className="text-xl font-medium mb-2">Select an Analysis</h3>
                  <p className="text-secondary-500 dark:text-secondary-400">
                    Choose a startup analysis from the list to view detailed results.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
      
      <Footer />
    </div>
  );
}
