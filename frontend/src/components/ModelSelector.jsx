import React from "react";
import "./ModelSelector.css";

const MODEL_OPTIONS = [
  { id: "openai:gpt-4o", label: "GPT-4o (OpenAI)" },
  {
    id: "openai:gpt-5.1",
    label: "GPT-5.1 (OpenAI)*",
    badge: "New",
  },
  {
    id: "gemini:gemini-3-pro-preview",
    label: "Gemini 3 Pro Preview",
    badge: "Gemini",
  },
  {
    id: "huggingface+together:deepseek-ai/DeepSeek-V3",
    label: "DeepSeek-V3.1 (HF via Together)",
    badge: "HF",
  },
  {
    id: "huggingface+fireworks-ai:Qwen/Qwen3-235B-A22B",
    label: "Qwen3-235B-A22B (HF via Fireworks)",
    badge: "HF",
  },
  {
    id: "huggingface+groq:openai/gpt-oss-120b",
    label: "GPT-OSS-120B (HF via Groq)",
    badge: "Groq",
  },
];

function ModelSelector({ selectedModels, onChange }) {
  const handleToggle = (modelId) => {
    if (selectedModels.includes(modelId)) {
      // Prevent deselecting all models
      if (selectedModels.length === 1) {
        return;
      }
      onChange(selectedModels.filter((id) => id !== modelId));
    } else {
      onChange([...selectedModels, modelId]);
    }
  };

  return (
    <div className="model-selector">
      <div className="model-selector-header">
        <h3>Choose Models</h3>
        <span>Select 1-3 models to compare</span>
      </div>
      <div className="model-options">
        {MODEL_OPTIONS.map((option) => (
          <label
            key={option.id}
            className={`model-option ${
              selectedModels.includes(option.id) ? "selected" : ""
            }`}
          >
            <input
              type="checkbox"
              checked={selectedModels.includes(option.id)}
              onChange={() => handleToggle(option.id)}
            />
            <div>
              <span className="model-label">{option.label}</span>
              {option.badge && (
                <span className="model-badge">{option.badge}</span>
              )}
            </div>
          </label>
        ))}
      </div>
      <p className="model-note">
        * GPT-5.1 availability depends on your OpenAI account. Hugging Face
        models require HUGGINGFACE_API_KEY in backend/.env.
      </p>
    </div>
  );
}

export default ModelSelector;
