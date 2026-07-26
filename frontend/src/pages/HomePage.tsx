import Glow from "../components/Glow";
function HomePage() {
  return (
    <div className="relative">
      <Glow className="w-135 h-45 left-1/2 -translate-x-1/2 -top-7.5 rounded-full" />
      <h1 className="tracking-tight text-7xl font-semibold text-ink text-center relative">
        StudySherpa
      </h1>
      <p className="text-muted text-sm py-2.5 font-medium text-center relative">
        Learn faster with your sherpa.
      </p>
    </div>
  );
}

export default HomePage;
