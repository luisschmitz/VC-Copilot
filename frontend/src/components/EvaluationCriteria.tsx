interface CriterionData {
  score?: number;
  assessment?: string;
  details?: string;
}

interface EvaluationCriteriaProps {
  criteria: Record<string, CriterionData>;
}

const EvaluationCriteria = ({ criteria }: EvaluationCriteriaProps) => {
  if (!criteria || Object.keys(criteria).length === 0) {
    return (
      <div className="text-center py-6 text-secondary-500">
        No evaluation criteria available
      </div>
    );
  }

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'bg-green-500';
    if (score >= 6) return 'bg-green-400';
    if (score >= 4) return 'bg-yellow-400';
    if (score >= 2) return 'bg-orange-400';
    return 'bg-red-500';
  };

  return (
    <div className="space-y-6">
      {Object.entries(criteria).map(([criterion, data]) => (
        <div key={criterion} className="card">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-medium text-lg">{criterion}</h3>
            {data.score !== undefined && (
              <div className="flex items-center">
                <div className="w-16 h-2 bg-gray-200 dark:bg-secondary-700 rounded-full overflow-hidden mr-2">
                  <div 
                    className={`h-full ${getScoreColor(data.score)}`} 
                    style={{ width: `${(data.score / 10) * 100}%` }}
                  ></div>
                </div>
                <span className="font-medium">{data.score}/10</span>
              </div>
            )}
          </div>
          
          {data.assessment && (
            <p className="text-secondary-600 dark:text-secondary-400 mb-3">
              {data.assessment}
            </p>
          )}
          
          {data.details && (
            <div className="mt-3 text-sm bg-gray-50 dark:bg-secondary-700/50 p-3 rounded-md">
              {data.details}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default EvaluationCriteria;
