import { useState } from "react";
import StatusIndicator from "./components/StatusIndicator";
import BookUpload from "./components/BookUpload";
import ExerciseGeneration from "./components/ExerciseGeneration";
import QASection from "./components/QASection";

function App() {
  const [hasBook, setHasBook] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [userId, setUserId] = useState("demo-user-123");

  const handleBookUploaded = (success) => {
    if (success) {
      setHasBook(true);
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
          <div className="flex items-center gap-4">
            <img
              src="/Qurricular.svg"
              alt="Qurricular"
              className="h-14 w-14 object-contain"
            />
            <div>
              <h1 className="text-3xl font-bold text-dark-purple mb-1">
                Qurricular Data Entry
              </h1>
              <p className="text-gray-600 text-sm sm:text-base">
                Upload books, generate exercises, and get answers with AI
                assistance
              </p>
            </div>
          </div>

          <StatusIndicator hasBook={hasBook} isLoading={isUploading} />
        </div>

        {/* Main Content */}
        <div className="space-y-8">
          {/* Book Upload Section */}
          <BookUpload
            onBookUploaded={handleBookUploaded}
            isUploading={isUploading}
            setIsUploading={setIsUploading}
          />

          {/* Exercise Generation Section */}
          <ExerciseGeneration hasBook={hasBook} userId={userId} />

          {/* Q&A Section */}
          <QASection hasBook={hasBook} userId={userId} />
        </div>
      </div>
    </div>
  );
}

export default App;
