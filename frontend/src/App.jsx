import React, { useState } from "react";
import FileUpload from "./components/FileUpload";
import ResumeDisplay from "./components/ResumeDisplay";
import ModelSelector from "./components/ModelSelector";
import "./App.css";

const DEFAULT_MODELS = ["openai:gpt-4o", "openai:gpt-5.1"];

function App() {
  const [resumeData, setResumeData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedModels, setSelectedModels] = useState(DEFAULT_MODELS);

  const handleFileUpload = async (file) => {
    setLoading(true);
    setError(null);
    setResumeData(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const params = new URLSearchParams();
      if (selectedModels.length) {
        params.append("models", selectedModels.join(","));
      }
      const apiUrl = import.meta.env.VITE_API_URL || "";
      const response = await fetch(`${apiUrl}/api/parse?${params.toString()}`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to parse resume");
      }

      const data = await response.json();
      setResumeData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>Resume Parser</h1>
          <p>Upload your resume to extract structured information</p>
        </header>

        <ModelSelector
          selectedModels={selectedModels}
          onChange={setSelectedModels}
        />

        <FileUpload
          onFileUpload={handleFileUpload}
          loading={loading}
          acceptedTypes=".pdf,.doc,.docx,.txt"
        />

        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
          </div>
        )}

        {resumeData && <ResumeDisplay data={resumeData} />}
      </div>
    </div>
  );
}

export default App;
