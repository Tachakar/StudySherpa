import { Glow } from "../components/Glow";
export function HomePage() {
  return (
    <div className="relative text-center">
      <h1 className="text-6xl sm:text-7xl font-semibold text-ink">
        StudySherpa
      </h1>
      <Glow className="absolute inset-0" />
      <p className="text-muted text-sm py-2.5 font-medium ">
        Learn faster with your sherpa.
      </p>
    </div>
  );
}
