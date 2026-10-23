import { Bell, Menu, Search } from "lucide-react";

function Topbar({
  onMenuClick,
  onSearchFocus,
  onSearchBlur,
}) {
  return (
    <header className="sticky top-0 z-30 h-[72px] border-b border-slate-200 bg-white/95 backdrop-blur">
      <div className="flex h-full items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">

        <div className="flex min-w-0 items-center gap-3">

          <button
            type="button"
            onClick={onMenuClick}
            className="rounded-xl border border-slate-200 p-2 text-slate-600 hover:bg-slate-50 lg:hidden"
          >
            <Menu size={20} />
          </button>

          <div
            className="
              flex min-w-0 items-center gap-2
              rounded-xl border border-slate-200
              bg-slate-50 px-3 py-2
              transition
              focus-within:border-[#9db9d7]
              focus-within:bg-white
              focus-within:ring-2
              focus-within:ring-[#173b67]/10
              w-[220px] sm:w-72 lg:w-[360px]
            "
          >
            <Search size={17} className="shrink-0 text-slate-400" />

            <input
              type="text"
              placeholder="Search customers, calls, products..."
              onFocus={onSearchFocus}
              onBlur={onSearchBlur}
              className="w-full bg-transparent text-sm text-slate-700 outline-none placeholder:text-slate-400"
            />
          </div>
        </div>

        <div className="flex shrink-0 items-center gap-2 sm:gap-3">

          <button
            type="button"
            className="relative rounded-xl p-2.5 text-slate-500 hover:bg-slate-100"
          >
            <Bell size={19} />

            <span className="absolute right-2 top-2 h-1.5 w-1.5 rounded-full bg-red-500" />
          </button>

          <div className="flex items-center gap-3 border-l border-slate-200 pl-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[#eaf2fb] text-xs font-bold text-[#173b67]">
              AD
            </div>

            <div className="hidden sm:block">
              <p className="text-sm font-semibold text-slate-800">
                Admin User
              </p>

              <p className="text-xs text-slate-500">
                Service Administrator
              </p>
            </div>
          </div>
        </div>

      </div>
    </header>
  );
}

export default Topbar;
