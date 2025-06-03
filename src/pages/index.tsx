import { useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import Layout from '../components/layout/Layout';
import AnalysisForm, { AnalysisResult as AnalysisResultType } from '../components/analysis/AnalysisForm';
import AnalysisResult from '../components/analysis/AnalysisResult';

export default function Home() {
  const [analysisResult, setAnalysisResult] = useState<AnalysisResultType | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleAnalysisStart = () => {
    setIsAnalyzing(true);
  };

  const handleAnalysisComplete = (result: AnalysisResultType) => {
    setAnalysisResult(result);
    setIsAnalyzing(false);
  };

  const handleReset = () => {
    setAnalysisResult(null);
  };

  return (
    <Layout
      title="VC Copilot - AI-Powered Startup Analyzer"
      description="Analyze startups with AI-powered insights. Get SWOT analysis, funding recommendations, and more."
    >
      <div className="page-container">
        {!analysisResult ? (
          <>
            <div className="text-center mb-12">
              <h1 className="text-4xl font-bold text-gray-900 mb-4">
                Analyze Any Startup in Seconds
              </h1>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                Enter a startup's website URL to get AI-powered insights, SWOT analysis, 
                and investment recommendations.
              </p>
            </div>

            <div className="max-w-3xl mx-auto">
              <AnalysisForm 
                onAnalysisComplete={handleAnalysisComplete}
                onAnalysisStart={handleAnalysisStart}
              />
            </div>

            {isAnalyzing && (
              <div className="max-w-3xl mx-auto mt-8 text-center">
                <div className="animate-pulse">
                  <p className="text-lg text-gray-600 mb-2">Analyzing startup data...</p>
                  <p className="text-sm text-gray-500">This may take a few moments</p>
                </div>
              </div>
            )}

            <div className="mt-16 max-w-4xl mx-auto">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
                How It Works
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="card-compact text-center">
                  <div className="bg-primary-100 text-primary-700 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-4">
                    <span className="text-xl font-bold">1</span>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Enter URL</h3>
                  <p className="text-gray-600">
                    Provide the website URL of the startup you want to analyze
                  </p>
                </div>
                <div className="card-compact text-center">
                  <div className="bg-primary-100 text-primary-700 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-4">
                    <span className="text-xl font-bold">2</span>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">AI Analysis</h3>
                  <p className="text-gray-600">
                    Our AI scrapes and analyzes the startup's data from various sources
                  </p>
                </div>
                <div className="card-compact text-center">
                  <div className="bg-primary-100 text-primary-700 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-4">
                    <span className="text-xl font-bold">3</span>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Get Insights</h3>
                  <p className="text-gray-600">
                    Receive comprehensive analysis, SWOT, and recommendations
                  </p>
                </div>
              </div>
            </div>

            <div className="mt-16 max-w-4xl mx-auto">
              <div className="bg-gray-50 rounded-lg p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">
                  About VC Copilot
                </h2>
                <p className="text-gray-600 mb-4">
                  VC Copilot is an AI-powered tool designed to help venture capitalists, 
                  angel investors, and startup enthusiasts quickly analyze startups and make 
                  informed decisions. Our platform combines web scraping, AI analysis, and 
                  industry expertise to provide valuable insights.
                </p>
                <p className="text-gray-600">
                  This is a Minimal Viable Product (MVP) with basic functionality. 
                  We're constantly improving our algorithms and adding new features.
                </p>
              </div>
            </div>
          </>
        ) : (
          <div className="max-w-4xl mx-auto">
            <AnalysisResult 
              result={analysisResult}
              onReset={handleReset}
            />
          </div>
        )}

        <div className="mt-16 text-center">
          <Link href="/history" className="text-primary-600 hover:text-primary-800">
            View Analysis History →
          </Link>
        </div>
      </div>
    </Layout>
  );
}
