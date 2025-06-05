import { FaGlobe, FaInfoCircle } from 'react-icons/fa';
import { extractDomain } from '@/utils/helpers';

interface CompanyInfoProps {
  companyName: string;
  url?: string;
  description?: string;
  className?: string;
}

const CompanyInfo = ({ companyName, url, description, className = '' }: CompanyInfoProps) => {
  return (
    <div className={`card ${className}`}>
      <div className="flex items-center mb-4">
        <div className="w-12 h-12 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center mr-4">
          <span className="text-xl font-bold text-primary-600 dark:text-primary-300">
            {companyName.charAt(0).toUpperCase()}
          </span>
        </div>
        
        <div>
          <h2 className="text-2xl font-bold">{companyName}</h2>
          {url && (
            <a 
              href={url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-primary-600 hover:underline text-sm flex items-center"
            >
              <FaGlobe className="mr-1" size={12} />
              {extractDomain(url)}
            </a>
          )}
        </div>
      </div>
      
      {description && (
        <div className="mt-4">
          <div className="flex items-center mb-2">
            <FaInfoCircle className="text-secondary-500 mr-2" />
            <h3 className="text-lg font-medium">Company Description</h3>
          </div>
          <p className="text-secondary-600 dark:text-secondary-400">
            {description}
          </p>
        </div>
      )}
    </div>
  );
};

export default CompanyInfo;
