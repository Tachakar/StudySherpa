import { Link } from "react-router";
import { Glow } from "./Glow";
import { TextField } from "./TextField";
type AuthFormProps = {
  title: string;
  email: string;
  setEmail: React.Dispatch<React.SetStateAction<string>>;
  password: string;
  setPassword: React.Dispatch<React.SetStateAction<string>>;
  handler: (event: React.FormEvent<HTMLFormElement>) => void;
  msg: string;
  submitLabel: string;
  passwordAutoComplete: "current-password" | "new-password";
};
export function AuthForm(props: AuthFormProps) {
  const {
    title,
    email,
    setEmail,
    password,
    setPassword,
    handler,
    msg,
    submitLabel,
    passwordAutoComplete,
  } = props;
  return (
    <div className="min-h-dvh flex flex-col items-center justify-center-safe bg-charcoal px-4">
      <div className="relative w-full max-w-sm">
        <h1 className="absolute text-ink text-5xl bottom-full w-full mb-20 text-center">
          {title}
        </h1>
        <Glow className="inset-0 absolute" />
        <form
          onSubmit={handler}
          className="bg-panel w-full p-8 rounded-2xl shadow-xl shadow-black/30 flex flex-col gap-4 relative"
        >
          <TextField
            required={true}
            id="email"
            label="Email"
            value={email}
            type="email"
            autoComplete="email"
            onChange={setEmail}
          />
          <TextField
            required={true}
            id="password"
            label="Password"
            value={password}
            type="password"
            autoComplete={passwordAutoComplete}
            onChange={setPassword}
          />
          <div className="flex gap-4">
            <Link
              to={"/"}
              className="w-full bg-muted text-charcoal font-semibold rounded-lg py-2.5 hover:bg-muted/90 transition-colors focus-visible:ring-2 focus-visible:ring-accent/50 text-center cursor-pointer"
            >
              Home
            </Link>
            <button
              type="submit"
              className="w-full bg-accent text-charcoal font-semibold rounded-lg py-2.5 hover:bg-accent/90 transition-colors focus-visible:ring-2 focus-visible:ring-accent/50 cursor-pointer"
            >
              {submitLabel}
            </button>
          </div>
          <div role="alert" className="text-red-400">
            {msg}
          </div>
        </form>
      </div>
    </div>
  );
}
