interface EmptyGraphStateProps {
  seedId: string | null;
  message: string;
}

export function EmptyGraphState({ seedId, message }: EmptyGraphStateProps) {
  if (!seedId) return null;

  return (
    <div className="flex-1 flex items-center justify-center">
      <div className="text-center max-w-sm">
        <div className="w-12 h-12 rounded-full bg-[#ffa502]/10 flex items-center justify-center mx-auto">
          <svg
            className="w-6 h-6 text-[#ffa502]"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={1.5}
          >
            <title>No results</title>
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5m6 4.125l2.25 2.25m0 0l2.25 2.25M12 13.875l2.25-2.25M12 13.875l-2.25 2.25M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z"
            />
          </svg>
        </div>
        <p className="font-[Outfit] text-sm text-gray-500 mt-3">{message}</p>
        <p className="font-[JetBrains_Mono] text-xs text-gray-600 mt-1">
          Try a different search or adjust filters
        </p>
      </div>
    </div>
  );
}
