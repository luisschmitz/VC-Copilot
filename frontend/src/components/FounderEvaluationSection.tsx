"use client";

interface FounderEvaluationProps {
  evaluation: {
    overall_assessment: string;
    success_prediction: boolean;
  };
}

export default function FounderEvaluationSection({ evaluation }: FounderEvaluationProps) {
  const { overall_assessment, success_prediction } = evaluation;

  return (
    <div>
      <h2 className="text-lg font-medium text-gray-900 mb-4">🎯 Founder Evaluation</h2>
      
      <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
        <div className="p-6">
          {/* Success Prediction Badge */}
          <div className="mb-4">
            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
              success_prediction 
                ? 'bg-green-100 text-green-800' 
                : 'bg-yellow-100 text-yellow-800'
            }`}>
              {success_prediction ? '✨ High Potential' : '⚠️ Needs Further Evaluation'}
            </span>
          </div>

          {/* Overall Assessment */}
          <div>
            <h3 className="text-md font-medium text-gray-800 mb-3">Assessment</h3>
            <div className="prose prose-sm max-w-none">
              <p className="text-sm text-gray-600 whitespace-pre-line">{overall_assessment}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
