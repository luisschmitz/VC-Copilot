import ReactMarkdown from 'react-markdown';

interface MarkdownContentProps {
  content: string;
  className?: string;
}

const MarkdownContent = ({ content, className = '' }: MarkdownContentProps) => {
  if (!content) {
    return null;
  }

  return (
    <div className={`prose dark:prose-invert max-w-none markdown-content ${className}`}>
      <ReactMarkdown>{content}</ReactMarkdown>
    </div>
  );
};

export default MarkdownContent;
