"use client";

import UrlInput from '@/components/UrlInput';
import ProgressIndicator from '@/components/ProgressIndicator';
import FounderSection from '@/components/FounderSection';
import FundingSection from '@/components/FundingSection';
import SummarySection from '@/components/SummarySection';
import FounderEvaluationSection from '@/components/FounderEvaluationSection';
import ErrorDisplay from '@/components/ErrorDisplay';
import LoadingPlaceholder from '@/components/LoadingPlaceholder';
import { useVCCopilotStore } from '@/lib/store';

export default function Home() {
  const {
    url,
    currentStep,
    isLoading,
    error,
    analysisData,
    analyzeStartup,
    reset,
    summaryLoaded,
    foundersLoaded,
    fundingLoaded,
    evaluationLoaded
  } = useVCCopilotStore();

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 sm:text-4xl">
            VC Copilot Analysis
          </h1>
          <p className="mt-3 text-lg text-gray-600">
            AI-powered startup analysis for venture capitalists
          </p>
        </div>

        <div className="bg-white shadow rounded-lg overflow-hidden mb-8">
          <div className="p-6">
            <UrlInput 
              onSubmit={analyzeStartup} 
              isLoading={isLoading} 
            />
          </div>
        </div>

        <div className="bg-white shadow rounded-lg overflow-hidden mb-8">
          <div className="p-6">
            <ProgressIndicator 
              currentStep={currentStep}
              isLoading={isLoading}
            />
          </div>
        </div>

        {error && (
          <ErrorDisplay 
            error={error}
            onReset={reset}
          />
        )}

        <div className="space-y-8">
            {/* Founder Section */}
            <div className="bg-white shadow rounded-lg overflow-hidden">
              <div className="p-6">
                {analysisData?.founder_data ? (
                  <FounderSection 
                    founderData={{
                      founders: analysisData.founder_data,
                      founding_story: analysisData.founding_story || '',
                      company_name: analysisData.company_name || '',
                      url: analysisData.url || ''
                    }}
                  />
                ) : (
                  <div>
                    <h2 className="text-lg font-medium text-gray-900 mb-4">Founder Information</h2>
                    {currentStep === 'founders' ? <LoadingPlaceholder /> : 
                      <p className="text-gray-500 italic">
                        {currentStep === 'analyzing' ? 'Fetching website data...' : 'Enter a startup URL above to begin analysis'}
                      </p>
                    }
                  </div>
                )}
              </div>
            </div>

            {/* Funding Section */}
            <div className="bg-white shadow rounded-lg overflow-hidden">
              <div className="p-6">
                {analysisData?.funding_data ? (
                  <FundingSection 
                    fundingData={analysisData.funding_data}
                  />
                ) : (
                  <div>
                    <h2 className="text-lg font-medium text-gray-900 mb-4">Funding History</h2>
                    {currentStep === 'funding' ? <LoadingPlaceholder /> : 
                      <p className="text-gray-500 italic">
                        {['analyzing', 'founders'].includes(currentStep) ? 'Processing previous steps...' : 'Enter a startup URL above to begin analysis'}
                      </p>
                    }
                  </div>
                )}
              </div>
            </div>

            {/* Summary Section */}
            <div className="bg-white shadow rounded-lg overflow-hidden">
              <div className="p-6">
                {currentStep !== 'idle' && summaryLoaded && analysisData?.deep_dive_sections ? (
                  <SummarySection 
                    deepDiveSections={analysisData.deep_dive_sections}
                  />
                ) : (
                  <div>
                    <h2 className="text-lg font-medium text-gray-900 mb-4">Deep Dive Analysis</h2>
                    {currentStep === 'deep_dive' ? <LoadingPlaceholder /> : 
                      <p className="text-gray-500 italic">
                        {['analyzing', 'founders', 'funding'].includes(currentStep) ? 'Gathering data...' : 'Enter a startup URL above to begin analysis'}
                      </p>
                    }
                  </div>
                )}
              </div>
            </div>

            {/* Founder Evaluation Section */}
            <div className="bg-white shadow rounded-lg overflow-hidden">
              <div className="p-6">
                {currentStep !== 'idle' && evaluationLoaded && analysisData?.founder_evaluation ? (
                  <FounderEvaluationSection 
                    evaluation={analysisData.founder_evaluation}
                  />
                ) : (
                  <div>
                    <h2 className="text-lg font-medium text-gray-900 mb-4">Founder Evaluation</h2>
                    {currentStep !== 'idle' ? <LoadingPlaceholder /> : 
                      <p className="text-gray-500 italic">Enter a startup URL above to begin analysis</p>
                    }
                  </div>
                )}
              </div>
            </div>
          </div>
        )


        {(currentStep === 'complete' || error) && (
          <div className="text-center mt-8">
            <button
              onClick={reset}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Start New Analysis
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
