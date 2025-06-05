import { useState } from 'react';
import { FaChartLine, FaExternalLinkAlt } from 'react-icons/fa';
import { formatDate, extractDomain, formatSuccessPrediction, getSuccessPredictionColor } from '@/utils/helpers';
import { AnalysisResponse } from '@/types/api';

interface RecentAnalysesProps {
  analyses: AnalysisResponse[];
  onSelectAnalysis: (analysis: AnalysisResponse) => void;
}

const RecentAnalyses = ({ analyses, onSelectAnalysis }: RecentAnalysesProps) => {
  if (!analyses || analyses.length === 0) {
    return (
      <div className="card p-6 text-center">
        <FaChartLine className="mx-auto text-4xl text-secondary-300 dark:text-secondary-600 mb-4" />
        <h3 className="text-lg font-medium mb-2">No Recent Analyses</h3>
        <p className="text-secondary-500 dark:text-secondary-400">
          Your recent startup analyses will appear here.
        </p>
      </div>
    );
  }

  return (
    <div className="card">
      <h3 className="section-title">Recent Analyses</h3>
      
      <div className="divide-y divide-gray-200 dark:divide-secondary-700">
        {analyses.map((analysis) => (
          <div 
            key={analysis.id} 
            className="py-4 first:pt-0 last:pb-0 cursor-pointer hover:bg-gray-50 dark:hover:bg-secondary-800/50 px-2 -mx-2 rounded-md"
            onClick={() => onSelectAnalysis(analysis)}
          >
            <div className="flex justify-between items-start mb-1">
              <h4 className="font-medium">{analysis.company_name}</h4>
              {analysis.success_prediction !== undefined && (
                <span className={`text-sm font-medium ${getSuccessPredictionColor(analysis.success_prediction)}`}>
                  {formatSuccessPrediction(analysis.success_prediction)}
                </span>
              )}
            </div>
            
            {analysis.url && (
              <div className="text-xs text-primary-600 dark:text-primary-400 mb-2 flex items-center">
                <FaExternalLinkAlt className="mr-1" size={10} />
                {extractDomain(analysis.url)}
              </div>
            )}
            
            {analysis.timestamp && (
              <div className="text-xs text-secondary-500 dark:text-secondary-500">
                {formatDate(analysis.timestamp)}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecentAnalyses;
