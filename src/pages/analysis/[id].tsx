import Head from 'next/head';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import axios from 'axios';
import { jsPDF } from 'jspdf';
import html2canvas from 'html2canvas';

type StartupAnalysis = {
  id: number;
  url: string;
  company_name: string;
  description: string;
  industry: string;
  team_size: string;
  funding_stage: string;
  strengths: string[];
  weaknesses: string[];
  opportunities: string[];
  threats: string[];
  score: number;
  recommendation: string;
  created_at: string;
  updated_at: string;
};

export default function AnalysisDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [analysis, setAnalysis] = useState<StartupAnalysis | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [exportLoading, setExportLoading] = useState<boolean>(false);

  useEffect(() => {
    if (id) {
      fetchAnalysis();
    }
  }, [id]);

  const fetchAnalysis = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`/api/analyses/${id}`);
      setAnalysis(response.data);
    } catch (err) {
      setError('Failed to load analysis. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleExportPDF = async () => {
    if (!analysis) return;
    
    setExportLoading(true);
    
    try {
      const reportElement = document.getElementById('analysis-report');
      if (!reportElement) return;
      
      const canvas = await html2canvas(reportElement, {
        scale: 2,
        logging: false,
        useCORS: true
      });
      
      const imgData = canvas.toDataURL('image/png');
      
      // A4 size: 210 x 297 mm
      const pdf = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'a4'
      });
      
      const imgWidth = 210;
      const imgHeight = canvas.height * imgWidth / canvas.width;
      
      pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);
      pdf.save(`${analysis.company_name.replace(/\s+/g, '-').toLowerCase()}-analysis.pdf`);
    } catch (err) {
      console.error('Error generating PDF:', err);
      alert('Failed to generate PDF. Please try again.');
    } finally {
      setExportLoading(false);
    }
  };

  const handleExportJSON = () => {
    if (!analysis) return;
    
    const dataStr = JSON.stringify(analysis, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `${analysis.company_name.replace(/\s+/g, '-').toLowerCase()}-analysis.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-600">Loading analysis...</p>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-8">
            {error || 'Analysis not found'}
          </div>
          <Link href="/history" className="text-primary-600 hover:text-primary-700">
            Back to History
          </Link>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>{analysis.company_name} Analysis | Minimal Viable Startup Analyzer</title>
        <meta name="description" content={`Startup analysis for ${analysis.company_name}`} />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <header className="mb-8">
            <div className="flex justify-between items-center mb-6">
              <div>
                <Link href="/history" className="text-primary-600 hover:text-primary-700 mb-2 inline-block">
                  ← Back to History
                </Link>
                <h1 className="text-3xl font-bold text-gray-900">{analysis.company_name}</h1>
                <p className="text-gray-500">
                  <a href={analysis.url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                    {analysis.url}
                  </a>
                </p>
              </div>
              <div className="flex gap-2">
                <button 
                  onClick={handleExportPDF}
                  disabled={exportLoading}
                  className="bg-gray-100 hover:bg-gray-200 text-gray-800 font-medium py-2 px-4 rounded-md transition-colors"
                >
                  {exportLoading ? 'Exporting...' : 'Export PDF'}
                </button>
                <button 
                  onClick={handleExportJSON}
                  className="bg-gray-100 hover:bg-gray-200 text-gray-800 font-medium py-2 px-4 rounded-md transition-colors"
                >
                  Export JSON
                </button>
              </div>
            </div>
          </header>

          <main>
            <div id="analysis-report" className="card mb-8">
              <div className="mb-8">
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">Company Overview</h2>
                    <p className="text-sm text-gray-500">Analyzed on {formatDate(analysis.created_at)}</p>
                  </div>
                  <div className="bg-primary-50 border border-primary-200 text-primary-700 px-4 py-2 rounded-md">
                    <span className="font-bold">Score: {analysis.score}/10</span>
                  </div>
                </div>

                <p className="text-gray-700 mb-6">{analysis.description}</p>
                
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
                  <div className="bg-gray-50 p-4 rounded-md">
                    <p className="text-sm text-gray-500 mb-1">Industry</p>
                    <p className="font-medium">{analysis.industry}</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-md">
                    <p className="text-sm text-gray-500 mb-1">Team Size</p>
                    <p className="font-medium">{analysis.team_size}</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-md">
                    <p className="text-sm text-gray-500 mb-1">Funding Stage</p>
                    <p className="font-medium">{analysis.funding_stage}</p>
                  </div>
                </div>
              </div>

              <div className="mb-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">SWOT Analysis</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-green-50 p-4 rounded-md">
                    <h3 className="font-bold text-green-800 mb-2">Strengths</h3>
                    <ul className="text-green-700 list-disc list-inside space-y-1">
                      {analysis.strengths.map((item, i) => (
                        <li key={`strength-${i}`}>{item}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="bg-red-50 p-4 rounded-md">
                    <h3 className="font-bold text-red-800 mb-2">Weaknesses</h3>
                    <ul className="text-red-700 list-disc list-inside space-y-1">
                      {analysis.weaknesses.map((item, i) => (
                        <li key={`weakness-${i}`}>{item}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="bg-blue-50 p-4 rounded-md">
                    <h3 className="font-bold text-blue-800 mb-2">Opportunities</h3>
                    <ul className="text-blue-700 list-disc list-inside space-y-1">
                      {analysis.opportunities.map((item, i) => (
                        <li key={`opportunity-${i}`}>{item}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="bg-yellow-50 p-4 rounded-md">
                    <h3 className="font-bold text-yellow-800 mb-2">Threats</h3>
                    <ul className="text-yellow-700 list-disc list-inside space-y-1">
                      {analysis.threats.map((item, i) => (
                        <li key={`threat-${i}`}>{item}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>

              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Recommendation</h2>
                <div className="bg-gray-50 p-4 rounded-md">
                  <p className="text-gray-700">{analysis.recommendation}</p>
                </div>
              </div>
            </div>
          </main>
        </div>
      </div>
    </>
  );
}
