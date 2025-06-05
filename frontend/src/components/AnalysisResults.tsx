import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { FaCheckCircle, FaExclamationTriangle, FaSpinner } from 'react-icons/fa';
import { AnalysisResponse } from '@/types/api';
import { formatDate, formatSuccessPrediction, getSuccessPredictionColor } from '@/utils/helpers';

interface AnalysisResultsProps {
  results: AnalysisResponse | null;
  isLoading: boolean;
  error: string | null;
}

const AnalysisResults = ({ results, isLoading, error }: AnalysisResultsProps) => {
  const [activeSection, setActiveSection] = useState<string | null>(
    results?.sections && Object.keys(results.sections).length > 0 
      ? Object.keys(results.sections)[0] 
      : null
  );
  
  if (isLoading) {
    return (
      <div className="card flex flex-col items-center justify-center py-12">
        <FaSpinner className="text-4xl text-primary-600 animate-spin mb-4" />
        <h3 className="text-xl font-medium">Analyzing startup...</h3>
        <p className="text-secondary-600 dark:text-secondary-400 mt-2">
          This may take a minute or two. We're scraping the website and running AI analysis.
        </p>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="card border-l-4 border-red-500">
        <div className="flex items-start">
          <FaExclamationTriangle className="text-red-500 text-xl mt-1 mr-4" />
          <div>
            <h3 className="text-xl font-medium mb-2">Analysis Error</h3>
            <p className="text-secondary-600 dark:text-secondary-400">{error}</p>
            <p className="mt-4 text-sm">
              Please check the URL and try again. If the problem persists, the website might be blocking our scraper
              or there might be an issue with our analysis service.
            </p>
          </div>
        </div>
      </div>
    );
  }
  
  if (!results) {
    return null;
  }
  
  const handleSectionClick = (section: string) => {
    setActiveSection(section);
  };
  
  return (
    <div className="space-y-6">
      <div className="card">
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-2xl font-bold">{results.company_name}</h2>
            {results.url && (
              <a 
                href={results.url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-primary-600 hover:underline text-sm"
              >
                {results.url}
              </a>
            )}
          </div>
          
          {results.success_prediction !== undefined && (
            <div className="flex flex-col items-end">
              <span className="text-sm text-secondary-600 dark:text-secondary-400">
                Success Prediction
              </span>
              <span className={`font-medium ${getSuccessPredictionColor(results.success_prediction)}`}>
                {formatSuccessPrediction(results.success_prediction)}
              </span>
            </div>
          )}
        </div>
        
        {results.timestamp && (
          <div className="mt-4 text-xs text-secondary-500 dark:text-secondary-500">
            Analysis completed on {formatDate(results.timestamp)}
          </div>
        )}
      </div>
      
      {results.overall_assessment && (
        <div className="card">
          <h3 className="section-title">Overall Assessment</h3>
          <p>{results.overall_assessment}</p>
        </div>
      )}
      
      {results.sections && Object.keys(results.sections).length > 0 && (
        <div className="card">
          <h3 className="section-title">Analysis Sections</h3>
          
          <div className="flex flex-col md:flex-row">
            <div className="md:w-1/4 mb-4 md:mb-0 md:pr-4">
              <ul className="space-y-1">
                {Object.keys(results.sections).map((section) => (
                  <li key={section}>
                    <button
                      onClick={() => handleSectionClick(section)}
                      className={`w-full text-left px-3 py-2 rounded-md text-sm ${
                        activeSection === section
                          ? 'bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200'
                          : 'hover:bg-gray-100 dark:hover:bg-secondary-700'
                      }`}
                    >
                      {section}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
            
            <div className="md:w-3/4 md:pl-4 md:border-l border-gray-200 dark:border-secondary-700">
              {activeSection && results.sections[activeSection] && (
                <div className="prose dark:prose-invert max-w-none markdown-content">
                  <ReactMarkdown>
                    {results.sections[activeSection]}
                  </ReactMarkdown>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      
      {results.evaluation_criteria && Object.keys(results.evaluation_criteria).length > 0 && (
        <div className="card">
          <h3 className="section-title">Evaluation Criteria</h3>
          
          <div className="space-y-4">
            {Object.entries(results.evaluation_criteria).map(([criterion, data]) => (
              <div key={criterion} className="border-b border-gray-200 dark:border-secondary-700 pb-4 last:border-0">
                <div className="flex justify-between items-center mb-2">
                  <h4 className="font-medium">{criterion}</h4>
                  {typeof data === 'object' && 'score' in data && (
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      (data.score as number) >= 7 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' 
                        : (data.score as number) >= 4
                          ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                          : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                    }`}>
                      {data.score}/10
                    </span>
                  )}
                </div>
                
                {typeof data === 'object' && 'assessment' in data && (
                  <p className="text-sm text-secondary-600 dark:text-secondary-400">
                    {data.assessment as string}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalysisResults;
