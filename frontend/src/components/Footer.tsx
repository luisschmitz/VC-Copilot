import Link from 'next/link';

const Footer = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="bg-white dark:bg-secondary-800 shadow-inner mt-auto">
      <div className="container mx-auto px-4 py-6">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-4 md:mb-0">
            <p className="text-sm text-secondary-600 dark:text-secondary-400">
              &copy; {currentYear} VC Copilot. All rights reserved.
            </p>
          </div>
          
          <div className="flex space-x-4">
            <Link href="/privacy" className="text-sm text-secondary-600 hover:text-primary-600 dark:text-secondary-400 dark:hover:text-primary-400">
              Privacy Policy
            </Link>
            <Link href="/terms" className="text-sm text-secondary-600 hover:text-primary-600 dark:text-secondary-400 dark:hover:text-primary-400">
              Terms of Service
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
