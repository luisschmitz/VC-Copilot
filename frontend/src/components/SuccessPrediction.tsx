import { FaCheckCircle, FaTimesCircle, FaQuestionCircle } from 'react-icons/fa';

interface SuccessPredictionProps {
  prediction: boolean | null | undefined;
  score?: number;
  className?: string;
}

const SuccessPrediction = ({ prediction, score, className = '' }: SuccessPredictionProps) => {
  const getIcon = () => {
    if (prediction === true) return <FaCheckCircle className="text-green-500 text-2xl" />;
    if (prediction === false) return <FaTimesCircle className="text-amber-500 text-2xl" />;
    return <FaQuestionCircle className="text-gray-400 text-2xl" />;
  };

  const getLabel = () => {
    if (prediction === true) return 'High Potential';
    if (prediction === false) return 'Needs Improvement';
    return 'Not Evaluated';
  };

  const getDescription = () => {
    if (prediction === true) {
      return 'This startup shows strong indicators of success based on our analysis.';
    }
    if (prediction === false) {
      return 'This startup has some challenges that may impact its success potential.';
    }
    return 'We have not evaluated this startup\'s success potential yet.';
  };

  return (
    <div className={`flex flex-col items-center p-4 ${className}`}>
      <div className="mb-2">{getIcon()}</div>
      <h4 className="text-lg font-medium mb-1">{getLabel()}</h4>
      <p className="text-sm text-center text-secondary-600 dark:text-secondary-400">
        {getDescription()}
      </p>
      {score !== undefined && (
        <div className="mt-3 text-center">
          <span className="text-sm text-secondary-500 dark:text-secondary-500">
            Confidence Score
          </span>
          <div className="mt-1 font-medium text-lg">
            {score}/10
          </div>
        </div>
      )}
    </div>
  );
};

export default SuccessPrediction;
