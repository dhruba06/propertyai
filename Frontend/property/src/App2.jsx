import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState("");
  const [caption, setCaption] = useState("");
  const [loading, setLoading] = useState(false);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
      setPreview(URL.createObjectURL(file));
      setCaption("");
    }
  };

  const handleSubmit = async () => {
    if (!image) return alert("Please select an image first!");

    setLoading(true);
    const formData = new FormData();
    formData.append("image", image);

    try {
      const res = await axios.post("http://127.0.0.1:5000/generate_caption", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setCaption(res.data.caption);
    } catch (err) {
      console.error(err);
      alert("Error generating caption.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>🏠 Property Caption Generator</h1>

      <input type="file" accept="image/*" onChange={handleImageChange} />
      {preview && <img src={preview} alt="Preview" className="preview" />}

      <button onClick={handleSubmit} disabled={loading}>
        {loading ? "Generating..." : "Generate Caption"}
      </button>

      {caption && (
        <div className="caption-box">
          <h3>Generated Caption:</h3>
          <p>{caption}</p>
        </div>
      )}
    </div>
  );
}

export default App;
