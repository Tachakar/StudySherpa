function Glow({ className }: { className: string }) {
  const classes = `absolute bg-accent opacity-30 blur-3xl rounded-3xl pointer-events-none ${className}`;
  return <div className={classes} />;
}
export default Glow;
