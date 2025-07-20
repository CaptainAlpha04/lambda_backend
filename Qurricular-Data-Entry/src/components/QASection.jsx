import { useState } from "react";
import { HelpCircle, MessageSquare } from "lucide-react";
import FormGroup from "./FormGroup";
import Spinner from "./Spinner";
import ResponseBox from "./ResponseBox";
import { askQuestion } from "../api";

export default function QASection({ hasBook, userId }) {
  const [question, setQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [answer, setAnswer] = useState(null);

  const handleAsk = async () => {
    if (!question.trim()) {
      setResponse({ type: "error", message: "Please enter a question." });
      return;
    }

    if (!hasBook) {
      setResponse({
        type: "error",
        message: "Please upload a book first to ask questions about it.",
      });
      return;
    }

    setIsLoading(true);
    setResponse(null);
    setAnswer(null);

    try {
      const result = await askQuestion(userId, question);
      setAnswer(result.answer);
      setResponse({
        type: "success",
        message: "Question answered successfully!",
      });
    } catch (error) {
      setResponse({ type: "error", message: error.message });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && e.ctrlKey) {
      handleAsk();
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-md p-6 border border-gray-100">
      <div className="flex items-center gap-3 mb-6">
        <HelpCircle className="w-6 h-6 text-primary-purple" />
        <h2 className="text-xl font-semibold text-dark-purple">
          Q&A About Your Book
        </h2>
        {!hasBook && (
          <span className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
            Book required
          </span>
        )}
      </div>

      <div className="space-y-6">
        <FormGroup label="Your Question" required>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyPress={handleKeyPress}
            className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-light-purple focus:border-transparent transition-all duration-200 resize-none"
            rows="4"
            placeholder={
              hasBook
                ? "Ask any question about the uploaded book..."
                : "Upload a book first to ask questions"
            }
            disabled={isLoading || !hasBook}
          />
          <p className="text-xs text-gray-500 mt-1">
            Tip: Press Ctrl + Enter to submit quickly
          </p>
        </FormGroup>

        <button
          onClick={handleAsk}
          disabled={isLoading || !question.trim() || !hasBook}
          className="w-full bg-primary-purple text-white py-3 px-6 rounded-lg font-medium hover:bg-light-purple focus:outline-none focus:ring-2 focus:ring-light-purple focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3"
        >
          {isLoading ? (
            <Spinner size="sm" text="Processing question..." />
          ) : (
            <>
              <MessageSquare className="w-5 h-5" />
              Ask Question
            </>
          )}
        </button>

        {response && (
          <ResponseBox
            type={response.type}
            message={response.message}
            onClose={() => setResponse(null)}
          />
        )}

        {answer && !isLoading && (
          <div className="mt-6">
            <h3 className="text-lg font-semibold text-dark-purple mb-4">
              Answer
            </h3>
            <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
              <div className="prose prose-sm max-w-none text-dark-purple">
                <p className="whitespace-pre-wrap leading-relaxed">{answer}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
