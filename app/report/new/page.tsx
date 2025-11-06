"use client";

import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { ArrowLeft } from "lucide-react";

export default function NewReportPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [config, setConfig] = useState({
    reportTitle: "",
    claimantGender: "male",
    claimantFirstName: "",
    claimantLastName: "",
    perspective: "third",
    specialtyType: "",
  });

  const specialtyTypes = [
    "Administrative",
    "Anesthesiology",
    "Cardiology",
    "Dermatology",
    "Emergency Medicine",
    "Family Medicine",
    "Internal Medicine",
    "Neurology",
    "Obstetrics and Gynecology",
    "Oncology",
    "Ophthalmology",
    "Orthopedic Surgery",
    "Pediatrics",
    "Physical Medicine and Rehabilitation",
    "Psychiatry",
    "Psychology",
    "Radiology",
    "Surgery",
    "Urology",
  ];

  useEffect(() => {
    const userData = localStorage.getItem("user");
    if (!userData) {
      router.push("/");
    } else {
      const parsedUser = JSON.parse(userData);
      setUser(parsedUser);
      setConfig((prev) => ({
        ...prev,
        specialtyType:
          parsedUser.specialtyType === "Administrative"
            ? ""
            : parsedUser.specialtyType,
      }));
    }
  }, [router]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    localStorage.setItem("reportConfig", JSON.stringify(config));
    router.push("/report/generate");
  };

  if (!user) return null;

  const isAdmin = user.specialtyType === "Administrative";

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <nav className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center h-16">
            <button
              onClick={() => router.push("/dashboard")}
              className="flex items-center gap-2 text-gray-700 hover:text-primary-600 transition-colors"
            >
              <ArrowLeft size={20} />
              Back to Dashboard
            </button>
          </div>
        </div>
      </nav>

      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-6">
            Configure New Report
          </h2>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Report Save Title
              </label>
              <input
                type="text"
                required
                value={config.reportTitle}
                onChange={(e) =>
                  setConfig({ ...config, reportTitle: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Enter a title for this report"
              />
            </div>

            {isAdmin && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Type of Report (Specialty)
                </label>
                <select
                  required
                  value={config.specialtyType}
                  onChange={(e) =>
                    setConfig({ ...config, specialtyType: e.target.value })
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="">Select Specialty</option>
                  {specialtyTypes
                    .filter((s) => s !== "Administrative")
                    .map((specialty) => (
                      <option key={specialty} value={specialty}>
                        {specialty}
                      </option>
                    ))}
                </select>
              </div>
            )}

            {!isAdmin && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Type of Report
                </label>
                <input
                  type="text"
                  disabled
                  value={config.specialtyType || user.specialtyType}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-100"
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Claimant Gender
              </label>
              <div className="flex gap-4">
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="male"
                    checked={config.claimantGender === "male"}
                    onChange={(e) =>
                      setConfig({ ...config, claimantGender: e.target.value })
                    }
                    className="mr-2"
                  />
                  Male
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="female"
                    checked={config.claimantGender === "female"}
                    onChange={(e) =>
                      setConfig({ ...config, claimantGender: e.target.value })
                    }
                    className="mr-2"
                  />
                  Female
                </label>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Claimant First Name
                </label>
                <input
                  type="text"
                  required
                  value={config.claimantFirstName}
                  onChange={(e) =>
                    setConfig({ ...config, claimantFirstName: e.target.value })
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Claimant Last Name
                </label>
                <input
                  type="text"
                  required
                  value={config.claimantLastName}
                  onChange={(e) =>
                    setConfig({ ...config, claimantLastName: e.target.value })
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Report Perspective
              </label>
              <div className="flex gap-4">
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="first"
                    checked={config.perspective === "first"}
                    onChange={(e) =>
                      setConfig({ ...config, perspective: e.target.value })
                    }
                    className="mr-2"
                  />
                  First Person
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="third"
                    checked={config.perspective === "third"}
                    onChange={(e) =>
                      setConfig({ ...config, perspective: e.target.value })
                    }
                    className="mr-2"
                  />
                  Third Person
                </label>
              </div>
            </div>

            <button
              type="submit"
              className="w-full bg-primary-600 text-white py-3 rounded-lg font-semibold hover:bg-primary-700 transition-colors shadow-lg"
            >
              Continue to Report Generation
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
