import Link from 'next/link';
import { FaChartLine, FaChartBar, FaCog } from 'react-icons/fa';

const Header = () => {
  return (
    <header className="bg-white dark:bg-secondary-800 shadow-sm">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <Link href="/" className="flex items-center space-x-2">
          <FaChartLine className="text-primary-600 text-2xl" />
          <span className="text-xl font-bold text-secondary-900 dark:text-white">VC Copilot</span>
        </Link>
        
        <nav>
          <ul className="flex space-x-6">
            <li>
              <Link href="/" className="text-secondary-600 hover:text-primary-600 dark:text-secondary-300 dark:hover:text-primary-400">
                Home
              </Link>
            </li>
            <li>
              <Link href="/dashboard" className="text-secondary-600 hover:text-primary-600 dark:text-secondary-300 dark:hover:text-primary-400 flex items-center">
                <FaChartBar className="mr-1" />
                Dashboard
              </Link>
            </li>
            <li>
              <Link href="/about" className="text-secondary-600 hover:text-primary-600 dark:text-secondary-300 dark:hover:text-primary-400">
                About
              </Link>
            </li>
            <li>
              <Link href="/settings" className="text-secondary-600 hover:text-primary-600 dark:text-secondary-300 dark:hover:text-primary-400 flex items-center">
                <FaCog className="mr-1" />
                Settings
              </Link>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
};

export default Header;
