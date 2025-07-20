import { useState } from "react";
import { BookOpen, Upload } from "lucide-react";
import FormGroup from "./FormGroup";
import Spinner from "./Spinner";
import ResponseBox from "./ResponseBox";
import { uploadBook } from "../api";

export default function BookUpload({
  onBookUploaded,
  isUploading,
  setIsUploading,
}) { 
  const [userId, setUserId] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [response, setResponse] = useState(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === "application/pdf") {
      setSelectedFile(file);
      setResponse(null);
    } else {
      setSelectedFile(null);
      setResponse({
        type: "error",
        message: "Please select a valid PDF file.",
      });
    }
  };

  const handleUpload = async () => {
    if (!userId || !selectedFile) {
      setResponse({
        type: "error",
        message: "Please fill in all required fields.",
      });
      return;
    }

    setIsUploading(true);
    setResponse(null);

    try {
      const result = await uploadBook(userId, selectedFile);
      setResponse({ type: "success", message: result.message });
      onBookUploaded(true);
      // Reset form
      setUserId("");
      setSelectedFile(null);
      // Reset file input
      document.getElementById("pdf-upload").value = "";
    } catch (error) {
      setResponse({ type: "error", message: error.message });
      onBookUploaded(false);
    } finally {
      setIsUploading(false);
    }
  };

  const isValid = userId.trim() && selectedFile;

  return (
    <div className="bg-white rounded-2xl shadow-md p-6 border border-gray-100">
      <div className="flex items-center gap-3 mb-6">
        <BookOpen className="w-6 h-6 text-primary-purple" />
        <h2 className="text-xl font-semibold text-dark-purple">
          Upload and Process a Book
        </h2>
      </div>

      <div className="space-y-6">
        <FormGroup label="User ID" required>
          <input
            type="text"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-light-purple focus:border-transparent transition-all duration-200"
            placeholder="Enter your user ID"
            disabled={isUploading}
          />
        </FormGroup>

        <FormGroup label="PDF Upload" required>
          <div className="relative">
            <input
              id="pdf-upload"
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-light-purple focus:border-transparent transition-all duration-200 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-medium file:bg-light-purple file:text-white hover:file:bg-primary-purple"
              disabled={isUploading}
            />
            {selectedFile && (
              <p className="mt-2 text-sm text-green-600">
                ✓ Selected: {selectedFile.name}
              </p>
            )}
          </div>
        </FormGroup>

        <button
          onClick={handleUpload}
          disabled={!isValid || isUploading}
          className="w-full bg-primary-purple text-white py-3 px-6 rounded-lg font-medium hover:bg-light-purple focus:outline-none focus:ring-2 focus:ring-light-purple focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3"
        >
          {isUploading ? (
            <Spinner size="sm" text="Uploading and Processing..." />
          ) : (
            <>
              <Upload className="w-5 h-5" />
              Upload and Process Book
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
      </div>
    </div>
  );
}
