import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState("");
  const [postData, setPostData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      alert("Please select an image file.");
      return;
    }
    if (file.size > 5 * 1024 * 1024) {  // 5 MB limit
      alert("Image must be less than 5 MB.");
      return;
    }

    setImage(file);
    const objectUrl = URL.createObjectURL(file);
    setPreview(objectUrl);
    setPostData(null);
    setError("");
  };

  const handleSubmit = async () => {
    if (!image) {
      alert("Please select an image first!");
      return;
    }

    setLoading(true);
    setError("");
    const formData = new FormData();
    formData.append("image", image);

    try {
      const res = await axios.post("http://127.0.0.1:5000/generate_caption", formData);
      if (res.data.post) {
        setPostData(res.data.post);
      } else {
        setError("No post data returned.");
      }
    } catch (err) {
      console.error(err);
      setError("Error generating caption or preparing post.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Cleanup object URL when component unmounts or preview changes
    return () => {
      if (preview) {
        URL.revokeObjectURL(preview);
      }
    };
  }, [preview]);

  return (
    <div className="container">
      <h1>🏠 Property Caption & Post‑Prep Generator</h1>

      <input type="file" accept="image/*" onChange={handleImageChange} />

      {preview && (
        <div className="preview-container">
          <img src={preview} alt="Preview" className="preview" />
        </div>
      )}

      <button className="generate-post" onClick={handleSubmit} disabled={loading || !image}>
        {loading ? "Processing…" : "Generate Caption & Post Data"}
      </button>

      {error && <p className="error">{error}</p>}

      {postData && (
        <div className="post-box">
          <h3>Generated Caption:</h3>
          <p>{postData.caption}</p>

          <h4>Scheduled Platforms & Time:</h4>
          <p><strong>Platforms:</strong> {postData.platforms.join(", ")}</p>
          <p><strong>Scheduled Time (UTC):</strong> {postData.scheduled_time}</p>

          <button
            onClick={() => {
              const csvContent =
                `Image Filename,Caption,Platforms,ScheduledTime\n` +
                `"${postData.image_filename}","${postData.caption}","${postData.platforms.join(";")}","${postData.scheduled_time}"`;
              const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
              const url = URL.createObjectURL(blob);
              const link = document.createElement("a");
              link.setAttribute("href", url);
              link.setAttribute("download", "post_data.csv");
              link.click();
            }}
          >
            Download CSV
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
