"use client";

import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { FileDown, Loader2, CheckCircle } from "lucide-react";

export default function ProcessReportPage() {
  const router = useRouter();
  const [config, setConfig] = useState<any>(null);
  const [sections, setSections] = useState<any[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [reportId, setReportId] = useState<string>("");

  useEffect(() => {
    const reportConfig = localStorage.getItem("reportConfig");
    const reportSections = localStorage.getItem("reportSections");

    if (!reportConfig || !reportSections) {
      router.push("/dashboard");
    } else {
      setConfig(JSON.parse(reportConfig));
      setSections(JSON.parse(reportSections));
    }
  }, [router]);

  const handleProcessReport = async () => {
    setIsProcessing(true);

    try {
      const response = await fetch("/api/report/process", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          config,
          sections,
        }),
      });

      const data = await response.json();
      setReportId(data.reportId);
      setIsComplete(true);
    } catch (error) {
      alert("Failed to process report. Please try again.");
      setIsProcessing(false);
    }
  };

  const handleDownload = async () => {
    const response = await fetch(`/api/report/download/${reportId}`);
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${config.reportTitle}.docx`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  if (!config) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <nav className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center h-16">
            <h1 className="text-2xl font-bold text-primary-600">MedXM.ai</h1>
          </div>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {!isComplete ? (
            <>
              <h2 className="text-3xl font-bold text-gray-900 mb-6">
                Process Report
              </h2>

              <div className="mb-8">
                <h3 className="text-lg font-semibold text-gray-700 mb-4">
                  Report Summary
                </h3>
                <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                  <p>
                    <span className="font-semibold">Title:</span> {config.reportTitle}
                  </p>
                  <p>
                    <span className="font-semibold">Specialty:</span>{" "}
                    {config.specialtyType}
                  </p>
                  <p>
                    <span className="font-semibold">Claimant:</span>{" "}
                    {config.claimantFirstName} {config.claimantLastName} (
                    {config.claimantGender})
                  </p>
                  <p>
                    <span className="font-semibold">Perspective:</span>{" "}
                    {config.perspective} person
                  </p>
                  <p>
                    <span className="font-semibold">Sections completed:</span>{" "}
                    {sections.length}
                  </p>
                </div>
              </div>

              <div className="space-y-4">
                <p className="text-gray-600">
                  Click the button below to generate your final report in Microsoft
                  Word format. The report will be saved to your library and ready for
                  download.
                </p>

                <button
                  onClick={handleProcessReport}
                  disabled={isProcessing}
                  className="w-full bg-primary-600 text-white py-4 rounded-lg font-semibold hover:bg-primary-700 transition-colors disabled:bg-gray-400 flex items-center justify-center gap-2 text-lg"
                >
                  {isProcessing ? (
                    <>
                      <Loader2 className="animate-spin" size={24} />
                      Processing Report...
                    </>
                  ) : (
                    <>
                      <FileDown size={24} />
                      Process Report
                    </>
                  )}
                </button>
              </div>
            </>
          ) : (
            <div className="text-center py-8">
              <CheckCircle className="mx-auto mb-4 text-green-600" size={64} />
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Report Generated Successfully!
              </h2>
              <p className="text-gray-600 mb-8">
                Your report has been generated and saved to your library.
              </p>

              <div className="space-y-4">
                <button
                  onClick={handleDownload}
                  className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
                >
                  <FileDown size={20} />
                  Download Report
                </button>

                <button
                  onClick={() => router.push("/library")}
                  className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
                >
                  Go to Library
                </button>

                <button
                  onClick={() => router.push("/dashboard")}
                  className="w-full border border-gray-300 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
                >
                  Return to Dashboard
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
