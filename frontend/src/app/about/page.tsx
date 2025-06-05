'use client';

import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { FaRocket, FaChartBar, FaUserTie, FaBrain } from 'react-icons/fa';

export default function About() {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      
      <main className="flex-grow container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-6">About VC Copilot</h1>
          
          <div className="card mb-8">
            <h2 className="text-2xl font-semibold mb-4">Our Mission</h2>
            <p className="mb-4">
              VC Copilot is designed to revolutionize the way venture capitalists and investors 
              evaluate startups. By leveraging advanced AI and natural language processing, we 
              provide deep insights and data-driven analysis to help you make better investment decisions.
            </p>
            <p>
              Our goal is to reduce the time spent on initial research while increasing the quality 
              of analysis, allowing you to focus on what matters most: building relationships with 
              promising founders and making strategic investment decisions.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="card">
              <div className="flex items-center mb-4">
                <FaRocket className="text-primary-600 text-2xl mr-3" />
                <h3 className="text-xl font-semibold">Startup Analysis</h3>
              </div>
              <p>
                Our AI analyzes startup websites and available data to provide 
                comprehensive insights into business models, market positioning, 
                competitive advantages, and potential risks.
              </p>
            </div>
            
            <div className="card">
              <div className="flex items-center mb-4">
                <FaUserTie className="text-primary-600 text-2xl mr-3" />
                <h3 className="text-xl font-semibold">Founder Evaluation</h3>
              </div>
              <p>
                We evaluate founding teams based on scientific criteria correlated 
                with startup success, helping you identify high-potential founders 
                and teams with the right mix of skills and experience.
              </p>
            </div>
            
            <div className="card">
              <div className="flex items-center mb-4">
                <FaChartBar className="text-primary-600 text-2xl mr-3" />
                <h3 className="text-xl font-semibold">Success Prediction</h3>
              </div>
              <p>
                Using machine learning models trained on thousands of successful 
                and unsuccessful startups, we provide data-backed predictions 
                about a startup's potential for success.
              </p>
            </div>
            
            <div className="card">
              <div className="flex items-center mb-4">
                <FaBrain className="text-primary-600 text-2xl mr-3" />
                <h3 className="text-xl font-semibold">AI-Powered Insights</h3>
              </div>
              <p>
                Our system continuously learns from new data and user feedback, 
                improving its analysis capabilities over time to provide increasingly 
                accurate and valuable insights.
              </p>
            </div>
          </div>
          
          <div className="card">
            <h2 className="text-2xl font-semibold mb-4">How It Works</h2>
            <ol className="list-decimal pl-5 space-y-3">
              <li>
                <strong>Website Scraping:</strong> Enter a startup's website URL, and our system 
                intelligently scrapes relevant information about the company, products, team, and more.
              </li>
              <li>
                <strong>Deep Analysis:</strong> Our AI analyzes the collected data, identifying 
                key strengths, weaknesses, opportunities, and threats.
              </li>
              <li>
                <strong>Founder Evaluation:</strong> The system evaluates the founding team based 
                on criteria scientifically correlated with startup success.
              </li>
              <li>
                <strong>Success Prediction:</strong> Using all available data, our AI provides a 
                prediction about the startup's potential for success.
              </li>
              <li>
                <strong>Comprehensive Report:</strong> You receive a detailed report with actionable 
                insights to inform your investment decisions.
              </li>
            </ol>
          </div>
        </div>
      </main>
      
      <Footer />
    </div>
  );
}
