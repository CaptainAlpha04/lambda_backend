import { useState, useEffect } from "react";
import { CheckCircle, XCircle, Info, X } from "lucide-react";

export default function ResponseBox({ type, message, onClose }) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (message) {
      setIsVisible(true);
    }
  }, [message]);

  const handleClose = () => {
    setIsVisible(false);
    setTimeout(() => {
      if (onClose) onClose();
    }, 300);
  };

  if (!message) return null;

  const styles = {
    success: "bg-green-100 text-green-800 border-green-200",
    error: "bg-red-100 text-red-800 border-red-200",
    info: "bg-blue-100 text-blue-800 border-blue-200",
  };

  const icons = {
    success: <CheckCircle className="w-6 h-6 text-green-600" />,
    error: <XCircle className="w-6 h-6 text-red-600" />,
    info: <Info className="w-6 h-6 text-blue-600" />,
  };

  return (
    <div
      className={`transition-all duration-300 transform ${
        isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-2"
      }`}
    >
      <div className={`p-4 rounded-lg border ${styles[type]} relative`}>
        <div className="flex items-start gap-3">
          <span className="text-lg">{icons[type]}</span>
          <div className="flex-1">
            <p className="font-medium whitespace-pre-wrap">{message}</p>
          </div>
          <button
            onClick={handleClose}
            className="text-gray-500 hover:text-gray-700 transition-colors ml-2"
          >
            ✕
          </button>
        </div>
      </div>
    </div>
  );
}
