import { FaExclamationTriangle } from 'react-icons/fa';

interface ErrorMessageProps {
  title?: string;
  message: string;
  suggestion?: string;
}

const ErrorMessage = ({ 
  title = 'Error', 
  message, 
  suggestion 
}: ErrorMessageProps) => {
  return (
    <div className="card border-l-4 border-red-500">
      <div className="flex items-start">
        <FaExclamationTriangle className="text-red-500 text-xl mt-1 mr-4" />
        <div>
          <h3 className="text-xl font-medium mb-2">{title}</h3>
          <p className="text-secondary-600 dark:text-secondary-400">{message}</p>
          {suggestion && (
            <p className="mt-4 text-sm">{suggestion}</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default ErrorMessage;
