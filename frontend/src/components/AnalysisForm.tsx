import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { FaSearch, FaSpinner } from 'react-icons/fa';
import { isValidUrl, normalizeUrl } from '@/utils/helpers';
import { useAppStore } from '@/lib/store';
import apiService from '@/lib/api';
import { AnalysisRequest } from '@/types/api';

interface FormInputs {
  url: string;
  scrapeDepth: string;
  analysisTypes: string[];
}

const AnalysisForm = () => {
  const { register, handleSubmit, formState: { errors } } = useForm<FormInputs>();
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const {
    setIsAnalyzing,
    setAnalysisResults,
    setAnalysisError,
    setIsScraping,
    setScrapedData,
    setScrapingError,
    resetState,
  } = useAppStore();
  
  const onSubmit = async (data: FormInputs) => {
    try {
      setIsSubmitting(true);
      resetState();
      
      // Normalize URL
      const normalizedUrl = normalizeUrl(data.url);
      
      // Prepare analysis request
      const request: AnalysisRequest = {
        url: normalizedUrl,
        analysis_types: data.analysisTypes,
        scrape_depth: data.scrapeDepth,
      };
      
      // Set analyzing state
      setIsAnalyzing(true);
      
      // Call API to analyze startup
      const results = await apiService.analyzeStartup(request);
      
      // Update state with results
      setAnalysisResults(results);
      setAnalysisError(null);
    } catch (error) {
      console.error('Analysis error:', error);
      setAnalysisError(error instanceof Error ? error.message : 'An error occurred during analysis');
      setAnalysisResults(null);
    } finally {
      setIsAnalyzing(false);
      setIsSubmitting(false);
    }
  };
  
  return (
    <div className="card">
      <h2 className="section-title">Analyze Startup</h2>
      
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label htmlFor="url" className="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-1">
            Startup Website URL
          </label>
          <div className="relative">
            <input
              id="url"
              type="text"
              placeholder="https://example.com"
              className={`input-field pl-10 ${errors.url ? 'border-red-500' : ''}`}
              {...register('url', { 
                required: 'URL is required',
                validate: (value) => isValidUrl(normalizeUrl(value)) || 'Please enter a valid URL'
              })}
            />
            <FaSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary-400" />
          </div>
          {errors.url && (
            <p className="mt-1 text-sm text-red-500">{errors.url.message}</p>
          )}
        </div>
        
        <div>
          <label htmlFor="scrapeDepth" className="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-1">
            Scrape Depth
          </label>
          <select
            id="scrapeDepth"
            className="input-field"
            {...register('scrapeDepth')}
            defaultValue="standard"
          >
            <option value="standard">Standard</option>
            <option value="deep">Deep</option>
            <option value="custom">Custom</option>
          </select>
        </div>
        
        <div>
          <p className="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-1">
            Analysis Types
          </p>
          <div className="space-y-2">
            <div className="flex items-center">
              <input
                id="executiveSummary"
                type="checkbox"
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                {...register('analysisTypes')}
                value="executive_summary"
                defaultChecked
              />
              <label htmlFor="executiveSummary" className="ml-2 text-sm text-secondary-700 dark:text-secondary-300">
                Executive Summary
              </label>
            </div>
            
            <div className="flex items-center">
              <input
                id="successPrediction"
                type="checkbox"
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                {...register('analysisTypes')}
                value="success_prediction"
                defaultChecked
              />
              <label htmlFor="successPrediction" className="ml-2 text-sm text-secondary-700 dark:text-secondary-300">
                Success Prediction
              </label>
            </div>
          </div>
        </div>
        
        <div className="pt-2">
          <button
            type="submit"
            className="btn-primary w-full flex justify-center items-center"
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <>
                <FaSpinner className="animate-spin mr-2" />
                Analyzing...
              </>
            ) : (
              'Analyze Startup'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AnalysisForm;
