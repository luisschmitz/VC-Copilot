"use client";

import LoadingSpinner from '@/components/LoadingSpinner';

interface ProgressIndicatorProps {
  currentStep: 'idle' | 'analyzing' | 'founders' | 'funding' | 'deep_dive' | 'evaluation' | 'complete';
  isLoading: boolean;
}

interface Step {
  id: string;
  name: string;
  description: string;
  status: 'upcoming' | 'in_progress' | 'complete';
}

export default function ProgressIndicator({ currentStep, isLoading }: ProgressIndicatorProps) {
  const getStepStatus = (stepId: string): 'upcoming' | 'in_progress' | 'complete' => {
    if (currentStep === 'idle') return 'upcoming';
    if (currentStep === 'complete') return 'complete';
    
    // During analysis, show steps in sequence
    const analysisSteps = ['analyzing', 'founders', 'funding', 'deep_dive', 'evaluation'];
    const currentStepIndex = analysisSteps.indexOf(currentStep);
    const stepIndex = analysisSteps.indexOf(stepId);
    
    if (stepIndex === -1) return 'upcoming';
    
    if (stepIndex < currentStepIndex) return 'complete';
    if (stepIndex === currentStepIndex) return 'in_progress';
    return 'upcoming';
  };

  const steps: Step[] = [
    { 
      id: 'analyzing',
      name: 'Website Data',
      description: 'Fetching website information',
      status: getStepStatus('analyzing')
    },
    {
      id: 'founders',
      name: 'Founder Data',
      description: 'Gathering founder information',
      status: getStepStatus('founders')
    },
    {
      id: 'funding',
      name: 'Funding & News',
      description: 'Collecting funding history and news',
      status: getStepStatus('funding')
    },
    {
      id: 'deep_dive',
      name: 'Deep Dive',
      description: 'Analyzing startup details',
      status: getStepStatus('deep_dive')
    },
    {
      id: 'evaluation',
      name: 'Evaluation',
      description: 'Evaluating founder profiles',
      status: getStepStatus('evaluation')
    }
  ];

  return (
    <div>
      <h2 className="text-lg font-medium text-gray-900 mb-4">Analysis Progress</h2>
      <div className="relative">
        {/* Progress bar */}
        <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-gray-200">
          <div 
            className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-indigo-600 transition-all duration-500"
            style={{ 
              width: `${(() => {
                if (currentStep === 'idle') return '0%';
                if (currentStep === 'complete') return '100%';
                const steps = ['analyzing', 'founders', 'funding', 'deep_dive', 'evaluation'];
                const currentIndex = steps.indexOf(currentStep);
                return `${Math.round((currentIndex + 1) / steps.length * 100)}%`;
              })()}`
            }}
          />
        </div>

        {/* Step indicator */}
        <div className="space-y-4">
          {steps.map((step) => {
            const isActive = step.status === 'in_progress';
            const isComplete = step.status === 'complete' || currentStep === 'complete';
            const isUpcoming = step.status === 'upcoming';

            return (
              <div key={step.id} className="flex items-center">
                <div className="relative flex items-center justify-center">
                  <span className={`h-6 w-6 rounded-full ${
                    isComplete ? 'bg-green-500' : 
                    isActive ? 'bg-indigo-600' : 
                    'bg-gray-300'
                  } flex items-center justify-center`}>
                    {isComplete ? (
                      <svg className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    ) : isActive && isLoading ? (
                      <LoadingSpinner className="h-4 w-4 text-white" />
                    ) : (
                      <span className="text-white text-xs">{steps.findIndex(s => s.id === step.id) + 1}</span>
                    )}
                  </span>
                </div>
                <div className="ml-4">
                  <p className={`text-sm font-medium ${
                    isComplete ? 'text-green-600' : 
                    isActive ? 'text-indigo-600' : 
                    'text-gray-500'
                  }`}>
                    {step.name}
                  </p>
                  <p className="text-sm text-gray-500">{step.description}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
