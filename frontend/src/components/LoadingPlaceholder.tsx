interface LoadingPlaceholderProps {
  height?: string;
  className?: string;
}

export default function LoadingPlaceholder({ height = "h-24", className = "" }: LoadingPlaceholderProps) {
  return (
    <div className={`animate-pulse bg-gray-200 rounded-md ${height} ${className}`} />
  );
}
