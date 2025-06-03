import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { analyzeStartup, handleApiError } from '../../utils/api';
import { DATA_SOURCES, ANALYSIS_TYPES, AnalysisResult } from '../../utils/analysisTypes';

type FormData = {
  url: string;
  data_sources: string[];
  analysis_types: string[];
};

type AnalysisFormProps = {
  onAnalysisComplete: (result: AnalysisResult) => void;
  onAnalysisStart?: () => void;
};

export { AnalysisResult };

export default function AnalysisForm({ onAnalysisComplete, onAnalysisStart }: AnalysisFormProps) {
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    defaultValues: {
      data_sources: DATA_SOURCES.filter(source => source.default).map(source => source.id),
      analysis_types: ANALYSIS_TYPES.filter(type => type.default).map(type => type.id)
    }
  });
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (data: FormData) => {
    setIsSubmitting(true);
    setError(null);
    
    if (onAnalysisStart) {
      onAnalysisStart();
    }
    
    try {
      const result = await analyzeStartup(data.url, data.data_sources, data.analysis_types);
      onAnalysisComplete(result);
    } catch (err) {
      setError(handleApiError(err));
      console.error('Analysis error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="card">
      {/* URL Input */}
      <div className="mb-6">
        <label htmlFor="url" className="form-label">
          Startup Website URL
        </label>
        <input
          id="url"
          type="url"
          placeholder="https://example.com"
          className="input-field"
          {...register("url", { 
            required: "URL is required",
            pattern: {
              value: /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/,
              message: "Please enter a valid URL"
            }
          })}
        />
        {errors.url && (
          <p className="form-error">{errors.url.message}</p>
        )}
      </div>

      {/* Data Sources Selection */}
      <div className="mb-6">
        <label className="form-label">
          Data Sources
          <span className="text-xs text-gray-500 ml-2">(Select at least one)</span>
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {DATA_SOURCES.map((source) => (
            <div key={source.id} className="flex items-center">
              <input
                type="checkbox"
                id={`data-source-${source.id}`}
                value={source.id}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                {...register("data_sources", { 
                  required: "Select at least one data source",
                  validate: value => value.length > 0 || "Select at least one data source"
                })}
              />
              <label htmlFor={`data-source-${source.id}`} className="ml-2 text-sm text-gray-700">
                {source.label}
              </label>
            </div>
          ))}
        </div>
        {errors.data_sources && (
          <p className="form-error">{errors.data_sources.message}</p>
        )}
      </div>

      {/* Analysis Types Selection */}
      <div className="mb-6">
        <label className="form-label">
          Analysis Types
          <span className="text-xs text-gray-500 ml-2">(Select at least one)</span>
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {ANALYSIS_TYPES.map((type) => (
            <div key={type.id} className="flex items-center">
              <input
                type="checkbox"
                id={`analysis-type-${type.id}`}
                value={type.id}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                {...register("analysis_types", { 
                  required: "Select at least one analysis type",
                  validate: value => value.length > 0 || "Select at least one analysis type"
                })}
              />
              <label htmlFor={`analysis-type-${type.id}`} className="ml-2 text-sm text-gray-700">
                {type.label}
              </label>
            </div>
          ))}
        </div>
        {errors.analysis_types && (
          <p className="form-error">{errors.analysis_types.message}</p>
        )}
      </div>

      {/* Error message */}
      {error && (
        <div className="mb-6 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md">
          {error}
        </div>
      )}

      {/* Submit Button */}
      <div className="flex justify-end">
        <button 
          type="submit" 
          className="btn-primary"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Analyzing...' : 'Analyze Startup'}
        </button>
      </div>
    </form>
  );
}
