/**
 * Helper functions for the VC Copilot frontend
 */

// Format date string to a readable format
export const formatDate = (dateString: string): string => {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

// Validate URL format
export const isValidUrl = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch (e) {
    return false;
  }
};

// Add http:// prefix if missing
export const normalizeUrl = (url: string): string => {
  if (!url) return '';
  
  if (!url.match(/^https?:\/\//i)) {
    return `https://${url}`;
  }
  return url;
};

// Truncate text with ellipsis
export const truncateText = (text: string, maxLength: number): string => {
  if (!text || text.length <= maxLength) return text;
  return `${text.substring(0, maxLength)}...`;
};

// Extract domain from URL
export const extractDomain = (url: string): string => {
  try {
    const { hostname } = new URL(normalizeUrl(url));
    return hostname.replace('www.', '');
  } catch (e) {
    return url;
  }
};

// Convert success prediction to readable format
export const formatSuccessPrediction = (prediction: boolean | null | undefined): string => {
  if (prediction === true) return 'High Potential';
  if (prediction === false) return 'Needs Improvement';
  return 'Not Evaluated';
};

// Get color class based on success prediction
export const getSuccessPredictionColor = (prediction: boolean | null | undefined): string => {
  if (prediction === true) return 'text-green-600';
  if (prediction === false) return 'text-amber-600';
  return 'text-gray-500';
};
