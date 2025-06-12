"use client";

import { DeepDiveSections } from '@/types/api';

interface SummarySectionProps {
  deepDiveSections: DeepDiveSections;
}

const sectionOrder = [
  'Executive Summary',
  'Key Insights',
  'Key Risks',
  'Team Info',
  'Problem & Market',
  'Solution & Product',
  'Competition',
  'Business Model',
  'Traction',
  'Funding and Investors',
  'Conclusion'
] as const;

const sectionIcons: Record<string, string> = {
  'Executive Summary': '',
  'Key Insights': '',
  'Key Risks': '',
  'Team Info': '',
  'Problem & Market': '',
  'Solution & Product': '',
  'Competition': '',
  'Business Model': '',
  'Traction': '',
  'Funding and Investors': '',
  'Conclusion': ''
};

export default function SummarySection({ deepDiveSections }: SummarySectionProps) {
  if (!deepDiveSections) {
    return null;
  }

  return (
    <div className="space-y-8">
      <h2 className="text-lg font-medium text-gray-900 mb-4">Startup Analysis</h2>
      
      {sectionOrder.map(sectionName => {
        const content = deepDiveSections[sectionName];
        if (!content) return null;

        return (
          <div key={sectionName} className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
            <div className="p-6">
              <h3 className="text-md font-medium text-gray-800 mb-3">
                {sectionIcons[sectionName]} {sectionName}
              </h3>
              <div className="prose max-w-none">
                <p className="text-sm text-gray-600 whitespace-pre-line">{content}</p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
