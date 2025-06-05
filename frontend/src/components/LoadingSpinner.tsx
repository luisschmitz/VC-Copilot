import { FaSpinner } from 'react-icons/fa';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  message?: string;
}

const LoadingSpinner = ({ size = 'md', message = 'Loading...' }: LoadingSpinnerProps) => {
  const sizeClasses = {
    sm: 'text-xl',
    md: 'text-3xl',
    lg: 'text-5xl',
  };

  return (
    <div className="flex flex-col items-center justify-center py-8">
      <FaSpinner className={`${sizeClasses[size]} text-primary-600 animate-spin mb-4`} />
      {message && <p className="text-secondary-600 dark:text-secondary-400">{message}</p>}
    </div>
  );
};

export default LoadingSpinner;
