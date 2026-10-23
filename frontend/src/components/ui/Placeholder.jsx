function Placeholder({ title }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
      <h2 className="text-xl font-bold text-slate-900">{title}</h2>
      <p className="mt-2 text-sm text-slate-500">
        Module foundation created. Backend integration will be connected next.
      </p>
    </div>
  );
}

export default Placeholder;

