export default function StatusIndicator({ hasBook, isLoading }) {
  if (isLoading) {
    return (
      <div className="flex items-center gap-2 px-4 py-2 bg-blue-100 text-blue-800 rounded-lg border border-blue-200">
        <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
        <span className="font-medium">Processing book...</span>
      </div>
    );
  }

  return (
    <div
      className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-all duration-300 ${
        hasBook
          ? "bg-green-100 text-green-800 border-green-200"
          : "bg-gray-100 text-gray-600 border-gray-200"
      }`}
    >
      <div
        className={`w-3 h-3 rounded-full ${
          hasBook ? "bg-green-500" : "bg-gray-400"
        }`}
      ></div>
      <span className="font-medium">{hasBook ? "Book Ready" : "No Book"}</span>
    </div>
  );
}
