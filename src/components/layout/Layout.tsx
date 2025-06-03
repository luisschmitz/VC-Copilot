import { ReactNode } from 'react';
import Head from 'next/head';
import Header from './Header';

type LayoutProps = {
  children: ReactNode;
  title?: string;
  description?: string;
};

export default function Layout({ 
  children, 
  title = 'VC Copilot - Startup Analyzer', 
  description = 'Analyze startups with AI-powered insights'
}: LayoutProps) {
  return (
    <>
      <Head>
        <title>{title}</title>
        <meta name="description" content={description} />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      
      <div className="min-h-screen flex flex-col">
        <Header />
        
        <main className="flex-grow">
          {children}
        </main>
        
        <footer className="bg-white border-t border-gray-200 py-6">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center">
              <p className="text-sm text-gray-500">
                &copy; {new Date().getFullYear()} VC Copilot. All rights reserved.
              </p>
              <div className="flex space-x-6">
                {/* Placeholder for future social links or other footer content */}
                <a href="#" className="text-gray-400 hover:text-gray-500">
                  Terms
                </a>
                <a href="#" className="text-gray-400 hover:text-gray-500">
                  Privacy
                </a>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
}
