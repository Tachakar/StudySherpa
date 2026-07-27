export function Glow({ className }: { className: string }) {
  const classes = `bg-accent opacity-30 blur-3xl rounded-full pointer-events-none ${className}`;
  return <div className={classes} />;
}
