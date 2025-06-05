import { ReactNode } from 'react';

interface Tab {
  id: string;
  label: string;
  icon?: ReactNode;
}

interface TabNavigationProps {
  tabs: Tab[];
  activeTab: string;
  onTabChange: (tabId: string) => void;
  className?: string;
}

const TabNavigation = ({ tabs, activeTab, onTabChange, className = '' }: TabNavigationProps) => {
  return (
    <div className={`border-b border-gray-200 dark:border-secondary-700 ${className}`}>
      <nav className="-mb-px flex space-x-8">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`
              py-4 px-1 border-b-2 font-medium text-sm flex items-center
              ${
                activeTab === tab.id
                  ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:border-secondary-300 dark:text-secondary-400 dark:hover:text-secondary-300'
              }
            `}
          >
            {tab.icon && <span className="mr-2">{tab.icon}</span>}
            {tab.label}
          </button>
        ))}
      </nav>
    </div>
  );
};

export default TabNavigation;
