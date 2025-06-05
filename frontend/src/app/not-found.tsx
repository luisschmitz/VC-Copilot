'use client';

import Link from 'next/link';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

export default function NotFound() {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      
      <main className="flex-grow container mx-auto px-4 py-12 flex flex-col items-center justify-center">
        <h1 className="text-4xl font-bold mb-4">404 - Page Not Found</h1>
        <p className="text-xl text-secondary-600 dark:text-secondary-400 mb-8">
          The page you are looking for does not exist.
        </p>
        <Link href="/" className="btn-primary">
          Return to Home
        </Link>
      </main>
      
      <Footer />
    </div>
  );
}
