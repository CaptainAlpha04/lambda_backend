export default function Spinner({ size = "md", text = "" }) {
  const sizeClasses = {
    sm: "w-4 h-4 border-2",
    md: "w-6 h-6 border-2",
    lg: "w-8 h-8 border-3"
  };

  return (
    <div className="flex items-center justify-center gap-3">
      <div className={`${sizeClasses[size]} border-primary-purple border-t-transparent rounded-full animate-spin`}></div>
      {text && <span className="text-dark-purple font-medium">{text}</span>}
    </div>
  );
}