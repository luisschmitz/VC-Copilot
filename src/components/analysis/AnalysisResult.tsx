import { useState } from 'react';
import { AnalysisResult as AnalysisResultType } from './AnalysisForm';
import { jsPDF } from 'jspdf';
import html2canvas from 'html2canvas';

type AnalysisResultProps = {
  result: AnalysisResultType;
  onReset?: () => void;
};

export default function AnalysisResult({ result, onReset }: AnalysisResultProps) {
  const [activeTab, setActiveTab] = useState('overview');
  const [exportLoading, setExportLoading] = useState(false);

  // Tabs can be dynamically generated based on available analysis types
  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'swot', label: 'SWOT Analysis' },
    ...(result.analysis_types?.includes('founder_evaluation') ? [{ id: 'founder_evaluation', label: 'Founder Evaluation' }] : []),
    ...(result.analysis_types?.includes('market') ? [{ id: 'market', label: 'Market Analysis' }] : []),
    ...(result.analysis_types?.includes('team') ? [{ id: 'team', label: 'Team Assessment' }] : []),
  ];

  const handleExportPDF = async () => {
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
      pdf.save(`${result.company_name.replace(/\s+/g, '-').toLowerCase()}-analysis.pdf`);
    } catch (err) {
      console.error('Error generating PDF:', err);
      alert('Failed to generate PDF. Please try again.');
    } finally {
      setExportLoading(false);
    }
  };

  const handleExportJSON = () => {
    const dataStr = JSON.stringify(result, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `${result.company_name.replace(/\s+/g, '-').toLowerCase()}-analysis.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  // Display data sources used for the analysis
  const renderDataSources = () => {
    if (!result.data_sources || result.data_sources.length === 0) {
      return null;
    }

    return (
      <div className="flex flex-wrap gap-2 mt-2">
        {result.data_sources.map(source => (
          <span key={source} className="data-source-badge">
            {source === 'website' ? 'Website' : 
             source === 'crunchbase' ? 'Crunchbase' : 
             source === 'linkedin' ? 'LinkedIn' : source}
          </span>
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{result.company_name}</h2>
          <p className="text-gray-500">
            <a href={result.url} target="_blank" rel="noopener noreferrer" className="hover:underline">
              {result.url}
            </a>
          </p>
          {renderDataSources()}
        </div>
        <div className="flex items-center space-x-3">
          <button 
            onClick={handleExportPDF}
            disabled={exportLoading}
            className="btn-outline"
          >
            {exportLoading ? 'Exporting...' : 'Export PDF'}
          </button>
          <button 
            onClick={handleExportJSON}
            className="btn-outline"
          >
            Export JSON
          </button>
          {onReset && (
            <button 
              onClick={onReset}
              className="btn-outline"
            >
              New Analysis
            </button>
          )}
        </div>
      </div>

      {/* Tab navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm
                ${activeTab === tab.id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}
              `}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab content */}
      <div id="analysis-report" className="card">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="analysis-section">
            <div className="analysis-header">
              <div>
                <h3 className="analysis-title">Company Overview</h3>
              </div>
              <div className="analysis-score">
                Score: {result.score}/10
              </div>
            </div>

            <p className="text-gray-700 mb-6">{result.description}</p>
            
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
              <div className="bg-gray-50 p-4 rounded-md">
                <p className="text-sm text-gray-500 mb-1">Industry</p>
                <p className="font-medium">{result.industry}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-md">
                <p className="text-sm text-gray-500 mb-1">Team Size</p>
                <p className="font-medium">{result.team_size}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-md">
                <p className="text-sm text-gray-500 mb-1">Funding Stage</p>
                <p className="font-medium">{result.funding_stage}</p>
              </div>
            </div>

            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">Recommendation</h3>
              <div className="bg-gray-50 p-4 rounded-md">
                <p className="text-gray-700">{result.recommendation}</p>
              </div>
            </div>
          </div>
        )}

        {/* SWOT Analysis Tab */}
        {activeTab === 'swot' && (
          <div className="analysis-section">
            <h3 className="analysis-title mb-6">SWOT Analysis</h3>
            <div className="swot-grid">
              <div className="swot-item swot-strengths">
                <h4 className="font-bold text-green-800 mb-2">Strengths</h4>
                <ul className="text-green-700 list-disc list-inside space-y-1">
                  {result.strengths.map((item, i) => (
                    <li key={`strength-${i}`}>{item}</li>
                  ))}
                </ul>
              </div>
              <div className="swot-item swot-weaknesses">
                <h4 className="font-bold text-red-800 mb-2">Weaknesses</h4>
                <ul className="text-red-700 list-disc list-inside space-y-1">
                  {result.weaknesses.map((item, i) => (
                    <li key={`weakness-${i}`}>{item}</li>
                  ))}
                </ul>
              </div>
              <div className="swot-item swot-opportunities">
                <h4 className="font-bold text-blue-800 mb-2">Opportunities</h4>
                <ul className="text-blue-700 list-disc list-inside space-y-1">
                  {result.opportunities.map((item, i) => (
                    <li key={`opportunity-${i}`}>{item}</li>
                  ))}
                </ul>
              </div>
              <div className="swot-item swot-threats">
                <h4 className="font-bold text-yellow-800 mb-2">Threats</h4>
                <ul className="text-yellow-700 list-disc list-inside space-y-1">
                  {result.threats.map((item, i) => (
                    <li key={`threat-${i}`}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Market Analysis Tab - Placeholder for future extension */}
        {activeTab === 'market' && (
          <div className="analysis-section">
            <h3 className="analysis-title mb-4">Market Analysis</h3>
            <div className="plugin-container">
              <p className="text-gray-500 text-center py-8">
                Market analysis module is not yet available in the MVP version.
                <br />
                This section will include market size, trends, competition, and growth projections.
              </p>
            </div>
          </div>
        )}

        {/* Team Assessment Tab - Placeholder for future extension */}
        {activeTab === 'team' && (
          <div className="analysis-section">
            <h3 className="analysis-title mb-4">Team Assessment</h3>
            <div className="plugin-container">
              <p className="text-gray-500 text-center py-8">
                Team assessment module is not yet available in the MVP version.
                <br />
                This section will include founder background, experience, team composition, and skills analysis.
              </p>
            </div>
          </div>
        )}

        {/* Founder Evaluation Tab */}
        {activeTab === 'founder_evaluation' && result.founder_evaluation && (
          <div className="analysis-section">
            <div className="analysis-header">
              <h3 className="analysis-title mb-4">Founder Evaluation</h3>
              <div className="analysis-score">
                Success Prediction: 
                <span className={result.founder_evaluation.success_prediction ? "text-green-600 font-bold" : "text-red-600 font-bold"}>
                  {result.founder_evaluation.success_prediction ? "True" : "False"}
                </span>
              </div>
            </div>
            
            <div className="mb-6">
              <h4 className="text-lg font-semibold mb-2">Overall Assessment</h4>
              <div className="bg-gray-50 p-4 rounded-md">
                <p className="text-gray-700">{result.founder_evaluation.overall_assessment}</p>
              </div>
            </div>
            
            <h4 className="text-lg font-semibold mb-4">Evaluation Criteria</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {result.founder_evaluation.evaluation_criteria && Object.entries(result.founder_evaluation.evaluation_criteria).map(([key, value]: [string, any]) => (
                <div key={key} className="bg-gray-50 p-4 rounded-md">
                  <div className="flex justify-between items-center mb-2">
                    <h5 className="font-medium capitalize">{key.replace(/_/g, ' ')}</h5>
                    <span 
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        value.score >= 7 ? 'bg-green-100 text-green-800' :
                        value.score >= 4 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}
                    >
                      Score: {value.score}/10
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">{value.assessment}</p>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Extension point for future analysis types */}
        {/* Additional tabs can be added here as the application evolves */}
      </div>
    </div>
  );
}
