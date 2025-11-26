import React, { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import "./FileUpload.css";

function FileUpload({ onFileUpload, loading, acceptedTypes }) {
  const onDrop = useCallback(
    (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        onFileUpload(acceptedFiles[0]);
      }
    },
    [onFileUpload]
  );

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/msword": [".doc"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        [".docx"],
      "text/plain": [".txt"],
    },
    multiple: false,
    disabled: loading,
    noClick: true,
    noKeyboard: true,
  });

  return (
    <div className="file-upload-container">
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? "active" : ""} ${
          loading ? "loading" : ""
        }`}
      >
        <input {...getInputProps()} />
        {loading ? (
          <div className="upload-content">
            <div className="spinner"></div>
            <p>Parsing resume...</p>
          </div>
        ) : (
          <div className="upload-content">
            <svg
              width="64"
              height="64"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="17 8 12 3 7 8"></polyline>
              <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
            <p className="upload-text">
              {isDragActive
                ? "Drop the file here"
                : "Drag & drop a resume file here"}
            </p>
            <p className="upload-hint">
              Supported formats: PDF, DOC, DOCX, TXT
            </p>
            <button
              type="button"
              className="browse-btn"
              onClick={open}
              disabled={loading}
            >
              Browse files
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default FileUpload;
