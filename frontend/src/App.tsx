import { Link, Outlet } from "react-router-dom";

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="font-semibold text-slate-900">
            Mini-Headway
          </Link>
          <span className="text-sm text-slate-500">Logged in as Dr. Adams</span>
        </div>
      </header>
      <main className="flex-1">
        <div className="max-w-4xl mx-auto px-6 py-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
