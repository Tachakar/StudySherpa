type TextFieldProps = {
  required?: boolean;
  id: string;
  label: string;
  value: string;
  type: "email" | "password" | "text";
  autoComplete: "email" | "new-password" | "current-password";
  onChange: (value: string) => void;
};
export function TextField(props: TextFieldProps) {
  const { required, id, label, value, type, autoComplete, onChange } = props;
  return (
    <div>
      <label
        htmlFor={id}
        className="text-muted text-xl font-medium mb-1.5 block"
      >
        {label}
      </label>
      <input
        required={required}
        value={value}
        id={id}
        type={type}
        autoComplete={autoComplete}
        className="bg-charcoal w-full rounded-lg px-3 py-2 text-ink focus:outline-none focus:ring-2 focus:ring-accent/40 transition-colors"
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}
