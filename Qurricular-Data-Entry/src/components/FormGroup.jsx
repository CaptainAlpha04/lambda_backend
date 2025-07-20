export default function FormGroup({ label, children, required = false }) {
  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-dark-purple">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      {children}
    </div>
  );
}