"use client";

import { useState } from "react";
import Link from "next/link";

export default function EmailVerifier() {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<string | null>(null);
  const [progress, setProgress] = useState<number>(0); // Percentage progress
  const [showModal, setShowModal] = useState<boolean>(false); // Show or hide the modal

  const handleDrop = async (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && (droppedFile.type === "text/csv" || droppedFile.type === "text/plain")) {
      setFile(droppedFile);
      setShowModal(true);
      await uploadFile(droppedFile);
    } else {
      alert("Please drop a CSV or TXT file.");
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile && (selectedFile.type === "text/csv" || selectedFile.type === "text/plain")) {
      setFile(selectedFile);
      setShowModal(true);
      await uploadFile(selectedFile);
    } else {
      alert("Please select a CSV or TXT file.");
    }
  };

  const uploadFile = async (file: File) => {
    setUploading(true);
    setUploadResult(null);

    const formData = new FormData();
    formData.append("file", file);

    // Simulate progress
    const interval = setInterval(() => {
      setProgress((oldProgress) => {
        if (oldProgress === 100) {
          clearInterval(interval);
          return oldProgress;
        }
        return oldProgress + 10;
      });
    }, 300); // Update every 300ms

    try {
      const response = await fetch("/api/verify-email", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setUploadResult(`Success: ${result.message}`);
      } else {
        setUploadResult("Failed to upload file.");
      }
    } catch (error) {
      setUploadResult("An error occurred while uploading the file.");
    } finally {
      setUploading(false);
      setShowModal(false); // Hide modal after upload
      setProgress(0); // Reset progress
    }
  };

  return (
    <main className="flex flex-col items-center justify-center min-h-screen p-8 bg-gray-100">
      <div className="max-w-lg w-full bg-white p-8 rounded-lg shadow-lg">
        <h1 className="text-3xl font-bold mb-6 text-gray-800">Email Verifier</h1>
        <p className="text-lg mb-8 text-gray-600 text-center">Upload a CSV or TXT file to verify emails.</p>

        <div
          className={`border-2 border-dashed p-6 rounded-lg ${isDragging ? "border-blue-500" : "border-gray-300"} ${uploading ? "opacity-50" : ""} mb-6`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
        >
          <p className="text-lg mb-4">Drag and drop a CSV or TXT file here</p>
          <p className="text-sm text-gray-500 mb-4">or click to select a file</p>
          <input
            type="file"
            accept=".csv, .txt"
            className="hidden"
            onChange={handleFileSelect}
            id="file-input"
          />
          <label htmlFor="file-input" className="cursor-pointer text-blue-500 underline">
            Choose file
          </label>
        </div>

        {uploadResult && (
          <p className={`mt-4 text-lg ${uploadResult.startsWith("Success") ? "text-green-500" : "text-red-500"}`}>
            {uploadResult}
          </p>
        )}

        <Link href="/" className="text-blue-500 hover:underline mt-6 block text-center">
          Go back to Home
        </Link>
      </div>

      {/* Modal for Upload Progress */}
      {showModal && (
        <div className="fixed inset-0 bg-gray-700 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg max-w-sm w-full">
            <h2 className="text-lg font-bold mb-4">Uploading File</h2>
            <div className="mb-4">
              <div className="relative pt-1">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold inline-block py-1 px-2 rounded text-blue-600 bg-blue-200 uppercase last:mr-0 mr-1">
                    {progress}%
                  </span>
                </div>
                <div className="flex">
                  <div
                    style={{ width: `${progress}%` }}
                    className="bg-blue-500 text-xs leading-none py-1 text-center text-white rounded-r"
                  >
                  </div>
                </div>
              </div>
            </div>
            <p className="text-sm text-gray-500">Please wait while we process your file.</p>
          </div>
        </div>
      )}
    </main>
  );
}
