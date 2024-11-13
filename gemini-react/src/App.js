import React, { useState } from 'react';

function App() {
  const [image, setImage] = useState(null);
  const [responseData, setResponseData] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");

  // Handle file selection
  const handleFileChange = (e) => {
    setImage(e.target.files[0]);
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!image) {
      alert("Please select an image file.");
      return;
    }

    const formData = new FormData();
    formData.append("image", image);

    try {
      const response = await fetch("https://rishbh.pythonanywhere.com/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to upload image. Please try again.");
      }

      const data = await response.json();

      // Check if the response contains the expected data
      if (data.captions && data.songs) {
        setResponseData(data);
        setErrorMessage("");
      } else {
        setErrorMessage("Unexpected response format.");
        setResponseData(null);
      }
    } catch (error) {
      console.error("Error:", error);
      setErrorMessage("Error uploading file or processing the response.");
      setResponseData(null);
    }
  };

  return (
    <div className="App">
      <h1>React Image Upload</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" accept="image/*" onChange={handleFileChange} required />
        <button type="submit">Upload</button>
      </form>

      {errorMessage && <p style={{ color: "red" }}>{errorMessage}</p>}

      {responseData && (
        <div>
          <h2>Captions</h2>
          <ul>
            {responseData.captions.map((caption, index) => (
              <li key={index}>{caption}</li>
            ))}
          </ul>
          <h2>Suggested Songs</h2>
          <ul>
            {responseData.songs.map((song, index) => (
              <li key={index}>{song}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
