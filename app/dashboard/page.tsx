"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { FileText, Library, LogOut } from "lucide-react";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const userData = localStorage.getItem("user");
    if (!userData) {
      router.push("/");
    } else {
      setUser(JSON.parse(userData));
    }
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem("user");
    router.push("/");
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <nav className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div>
              <h1 className="text-2xl font-bold text-primary-600">MedXM.ai</h1>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-gray-700">
                Welcome, {user.firstName} {user.lastName}
              </span>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:text-red-600 transition-colors"
              >
                <LogOut size={20} />
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">Dashboard</h2>
          <p className="text-gray-600">
            Select an option below to get started
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          <button
            onClick={() => router.push("/report/new")}
            className="bg-white rounded-2xl shadow-xl p-8 hover:shadow-2xl transition-all transform hover:scale-105 group"
          >
            <div className="flex flex-col items-center text-center">
              <div className="bg-primary-100 p-6 rounded-full mb-4 group-hover:bg-primary-200 transition-colors">
                <FileText size={48} className="text-primary-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">
                Generate New Report
              </h3>
              <p className="text-gray-600">
                Create a new medical/legal report using AI
              </p>
            </div>
          </button>

          <button
            onClick={() => router.push("/library")}
            className="bg-white rounded-2xl shadow-xl p-8 hover:shadow-2xl transition-all transform hover:scale-105 group"
          >
            <div className="flex flex-col items-center text-center">
              <div className="bg-indigo-100 p-6 rounded-full mb-4 group-hover:bg-indigo-200 transition-colors">
                <Library size={48} className="text-indigo-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">
                Report Library
              </h3>
              <p className="text-gray-600">
                View and manage your previously generated reports
              </p>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
}
