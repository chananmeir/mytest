"use client";

import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { ArrowLeft, Upload, Mic, FileText, Loader2 } from "lucide-react";

interface ReportSection {
  id: string;
  title: string;
  showForMentalHealth: boolean;
  content: string;
  inputMethod: "upload-transcription" | "upload-notes" | "live-transcription" | "live-notes" | null;
  inputData: string;
}

export default function GenerateReportPage() {
  const router = useRouter();
  const [config, setConfig] = useState<any>(null);
  const [currentSectionIndex, setCurrentSectionIndex] = useState(0);
  const [isGenerating, setIsGenerating] = useState(false);
  const [showRefinement, setShowRefinement] = useState(false);
  const [refinementCommand, setRefinementCommand] = useState("");

  const allSections: ReportSection[] = [
    { id: "accident_details", title: "Accident Details", showForMentalHealth: false, content: "", inputMethod: null, inputData: "" },
    { id: "initial_complaints", title: "Initial Accident Complaints", showForMentalHealth: false, content: "", inputMethod: null, inputData: "" },
    { id: "current_complaints", title: "Current Complaints", showForMentalHealth: false, content: "", inputMethod: null, inputData: "" },
    { id: "course_treatment", title: "Course of Treatment", showForMentalHealth: false, content: "", inputMethod: null, inputData: "" },
    { id: "past_medical", title: "Past Medical History", showForMentalHealth: false, content: "", inputMethod: null, inputData: "" },
    { id: "medications", title: "Medications", showForMentalHealth: false, content: "", inputMethod: null, inputData: "" },
    { id: "childhood_education", title: "Childhood/Educational History", showForMentalHealth: false, content: "", inputMethod: null, inputData: "" },
    { id: "social_history", title: "Social History", showForMentalHealth: false, content: "", inputMethod: null, inputData: "" },
    { id: "functional_status", title: "Functional Status (Pre and Post Accident)", showForMentalHealth: false, content: "", inputMethod: null, inputData: "" },
    { id: "substance_use", title: "Substance Use (Pre and Post Accident)", showForMentalHealth: false, content: "", inputMethod: null, inputData: "" },
    { id: "occupational_history", title: "Occupational History (Pre and Post Accident)", showForMentalHealth: false, content: "", inputMethod: null, inputData: "" },
    { id: "past_psychiatric", title: "Past Psychiatric History", showForMentalHealth: true, content: "", inputMethod: null, inputData: "" },
    { id: "family_psychiatric", title: "Family Psychiatric History", showForMentalHealth: true, content: "", inputMethod: null, inputData: "" },
    { id: "mental_health_screening", title: "Mental Health Screening", showForMentalHealth: true, content: "", inputMethod: null, inputData: "" },
    { id: "clinical_examination", title: "Clinical Examination", showForMentalHealth: false, content: "", inputMethod: null, inputData: "" },
    { id: "question_answer", title: "Question and Answer Section", showForMentalHealth: false, content: "", inputMethod: null, inputData: "" },
  ];

  const [sections, setSections] = useState<ReportSection[]>(allSections);

  useEffect(() => {
    const reportConfig = localStorage.getItem("reportConfig");
    if (!reportConfig) {
      router.push("/dashboard");
    } else {
      const parsedConfig = JSON.parse(reportConfig);
      setConfig(parsedConfig);

      // Filter sections based on specialty
      const isMentalHealth =
        parsedConfig.specialtyType === "Psychiatry" ||
        parsedConfig.specialtyType === "Psychology";

      if (!isMentalHealth) {
        setSections(allSections.filter(s => !s.showForMentalHealth));
      }
    }
  }, [router]);

  const currentSection = sections[currentSectionIndex];

  const handleInputMethodSelect = (method: ReportSection["inputMethod"]) => {
    setSections(sections.map((s, i) =>
      i === currentSectionIndex ? { ...s, inputMethod: method } : s
    ));
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const text = await file.text();
    setSections(sections.map((s, i) =>
      i === currentSectionIndex ? { ...s, inputData: text } : s
    ));
  };

  const handleGenerate = async () => {
    if (!currentSection.inputData) {
      alert("Please provide input data first");
      return;
    }

    setIsGenerating(true);

    try {
      const response = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sectionId: currentSection.id,
          inputMethod: currentSection.inputMethod,
          inputData: currentSection.inputData,
          config: config,
        }),
      });

      const data = await response.json();

      setSections(sections.map((s, i) =>
        i === currentSectionIndex ? { ...s, content: data.content } : s
      ));

      setShowRefinement(true);
    } catch (error) {
      alert("Failed to generate content. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleRefinement = async () => {
    if (!refinementCommand) return;

    setIsGenerating(true);

    try {
      const response = await fetch("/api/refine", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content: currentSection.content,
          command: refinementCommand,
          config: config,
        }),
      });

      const data = await response.json();

      setSections(sections.map((s, i) =>
        i === currentSectionIndex ? { ...s, content: data.content } : s
      ));

      setRefinementCommand("");
    } catch (error) {
      alert("Failed to refine content. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleNext = () => {
    if (currentSectionIndex < sections.length - 1) {
      setCurrentSectionIndex(currentSectionIndex + 1);
      setShowRefinement(false);
      setRefinementCommand("");
    } else {
      // All sections complete, save and go to process page
      localStorage.setItem("reportSections", JSON.stringify(sections));
      router.push("/report/process");
    }
  };

  const handlePrevious = () => {
    if (currentSectionIndex > 0) {
      setCurrentSectionIndex(currentSectionIndex - 1);
      setShowRefinement(sections[currentSectionIndex - 1].content !== "");
    }
  };

  if (!config) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <nav className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <button
              onClick={() => router.push("/dashboard")}
              className="flex items-center gap-2 text-gray-700 hover:text-primary-600 transition-colors"
            >
              <ArrowLeft size={20} />
              Back to Dashboard
            </button>
            <div className="text-sm text-gray-600">
              Section {currentSectionIndex + 1} of {sections.length}
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-3xl font-bold text-gray-900">
                {currentSection.title}
              </h2>
            </div>

            <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
              <div
                className="bg-primary-600 h-2 rounded-full transition-all"
                style={{ width: `${((currentSectionIndex + 1) / sections.length) * 100}%` }}
              />
            </div>
          </div>

          {!currentSection.inputMethod && (
            <div>
              <h3 className="text-lg font-semibold text-gray-700 mb-4">
                How would you like to provide information for this section?
              </h3>
              <div className="grid md:grid-cols-2 gap-4">
                <button
                  onClick={() => handleInputMethodSelect("upload-transcription")}
                  className="p-6 border-2 border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-all"
                >
                  <Upload className="mx-auto mb-3 text-primary-600" size={32} />
                  <h4 className="font-semibold mb-2">Upload Transcription</h4>
                  <p className="text-sm text-gray-600">Upload an existing transcription file</p>
                </button>

                <button
                  onClick={() => handleInputMethodSelect("upload-notes")}
                  className="p-6 border-2 border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-all"
                >
                  <FileText className="mx-auto mb-3 text-primary-600" size={32} />
                  <h4 className="font-semibold mb-2">Upload Notes</h4>
                  <p className="text-sm text-gray-600">Upload existing point-form notes</p>
                </button>

                <button
                  onClick={() => handleInputMethodSelect("live-transcription")}
                  className="p-6 border-2 border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-all"
                >
                  <Mic className="mx-auto mb-3 text-primary-600" size={32} />
                  <h4 className="font-semibold mb-2">Live Transcription</h4>
                  <p className="text-sm text-gray-600">Record interview in real-time</p>
                </button>

                <button
                  onClick={() => handleInputMethodSelect("live-notes")}
                  className="p-6 border-2 border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-all"
                >
                  <FileText className="mx-auto mb-3 text-primary-600" size={32} />
                  <h4 className="font-semibold mb-2">Live Notes</h4>
                  <p className="text-sm text-gray-600">Take notes directly in the app</p>
                </button>
              </div>
            </div>
          )}

          {currentSection.inputMethod && !currentSection.content && (
            <div className="space-y-4">
              {(currentSection.inputMethod === "upload-transcription" ||
                currentSection.inputMethod === "upload-notes") && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Upload File
                  </label>
                  <input
                    type="file"
                    accept=".txt,.doc,.docx"
                    onChange={handleFileUpload}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  />
                  {currentSection.inputData && (
                    <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-600 mb-2">File content:</p>
                      <pre className="text-xs whitespace-pre-wrap">{currentSection.inputData.substring(0, 200)}...</pre>
                    </div>
                  )}
                </div>
              )}

              {(currentSection.inputMethod === "live-transcription" ||
                currentSection.inputMethod === "live-notes") && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {currentSection.inputMethod === "live-transcription"
                      ? "Transcription (Live recording to be implemented)"
                      : "Enter your notes"}
                  </label>
                  <textarea
                    value={currentSection.inputData}
                    onChange={(e) => setSections(sections.map((s, i) =>
                      i === currentSectionIndex ? { ...s, inputData: e.target.value } : s
                    ))}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg h-64"
                    placeholder="Enter information here..."
                  />
                </div>
              )}

              <div className="flex gap-4">
                <button
                  onClick={() => handleInputMethodSelect(null)}
                  className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Change Input Method
                </button>
                <button
                  onClick={handleGenerate}
                  disabled={isGenerating || !currentSection.inputData}
                  className="flex-1 bg-primary-600 text-white py-2 rounded-lg font-semibold hover:bg-primary-700 transition-colors disabled:bg-gray-400 flex items-center justify-center gap-2"
                >
                  {isGenerating ? (
                    <>
                      <Loader2 className="animate-spin" size={20} />
                      Generating...
                    </>
                  ) : (
                    "Generate Content"
                  )}
                </button>
              </div>
            </div>
          )}

          {currentSection.content && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Generated Content
                </label>
                <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <p className="whitespace-pre-wrap">{currentSection.content}</p>
                </div>
              </div>

              {showRefinement && (
                <div className="space-y-4 p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-semibold text-gray-900">Refine Content (Optional)</h4>
                  <div className="space-y-2">
                    <button
                      onClick={() => setRefinementCommand("Reword paragraph to make it sound more formal.")}
                      className="w-full text-left px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
                    >
                      Make it more formal
                    </button>
                    <button
                      onClick={() => setRefinementCommand("Always refer to the patient as claimant")}
                      className="w-full text-left px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
                    >
                      Always refer to patient as claimant
                    </button>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Custom refinement command
                    </label>
                    <textarea
                      value={refinementCommand}
                      onChange={(e) => setRefinementCommand(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                      rows={3}
                      placeholder="Enter custom refinement instructions..."
                    />
                  </div>

                  <button
                    onClick={handleRefinement}
                    disabled={isGenerating || !refinementCommand}
                    className="w-full bg-blue-600 text-white py-2 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:bg-gray-400 flex items-center justify-center gap-2"
                  >
                    {isGenerating ? (
                      <>
                        <Loader2 className="animate-spin" size={20} />
                        Refining...
                      </>
                    ) : (
                      "Apply Refinement"
                    )}
                  </button>
                </div>
              )}

              <div className="flex gap-4 pt-4">
                <button
                  onClick={handlePrevious}
                  disabled={currentSectionIndex === 0}
                  className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
                >
                  Previous
                </button>
                <button
                  onClick={handleNext}
                  className="flex-1 bg-green-600 text-white py-2 rounded-lg font-semibold hover:bg-green-700 transition-colors"
                >
                  {currentSectionIndex === sections.length - 1 ? "Finish & Process Report" : "Save & Continue to Next Section"}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
