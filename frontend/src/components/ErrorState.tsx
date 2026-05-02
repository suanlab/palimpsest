interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="flex-1 flex items-center justify-center">
      <div className="text-center max-w-sm">
        <div className="w-12 h-12 rounded-full bg-[#ff4757]/10 flex items-center justify-center mx-auto">
          <svg
            className="w-6 h-6 text-[#ff4757]"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <title>Error indicator</title>
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"
            />
          </svg>
        </div>
        <p className="font-[Outfit] text-sm text-gray-400 mt-3">{message}</p>
        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="mt-4 px-4 py-2 bg-[#2a2a4a] hover:bg-[#3a3a5a] text-gray-300 hover:text-white font-[Outfit] text-sm rounded-lg transition-colors"
          >
            Try Again
          </button>
        )}
      </div>
    </div>
  );
}
