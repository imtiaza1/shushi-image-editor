const upload = document.getElementById("upload");
const preview = document.getElementById("preview");
const themeToggle = document.getElementById("theme-toggle");

let imageFile = null;
let options = {
  brightness: 100,
  contrast: 100,
  grayscale: 0,
  rotate: 0,
  flip: false,
};

// 🌙 Theme toggle
themeToggle.addEventListener("click", () => {
  document.body.classList.toggle("dark");
  themeToggle.textContent = document.body.classList.contains("dark")
    ? "☀️ Light Mode"
    : "🌙 Dark Mode";
});

// File Upload Preview
upload.addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (!file) return;
  imageFile = file;
  preview.src = URL.createObjectURL(file);
});

// Controls
document.getElementById("brightness").oninput = (e) =>
  (options.brightness = e.target.value);
document.getElementById("contrast").oninput = (e) =>
  (options.contrast = e.target.value);
document.getElementById("grayscale").oninput = (e) =>
  (options.grayscale = e.target.value);

document.getElementById("rotate").onclick = () => {
  options.rotate += 90;
};
document.getElementById("flip").onclick = () => {
  options.flip = !options.flip;
};

// Apply Filters via Flask API
document.getElementById("apply").onclick = async () => {
  if (!imageFile) {
    alert("Please upload an image first!");
    return;
  }

  const formData = new FormData();
  formData.append("image", imageFile);
  formData.append("options", JSON.stringify(options));

  try {
    const res = await fetch("/api/edit", {
      method: "POST",
      body: formData,
    });

    if (!res.ok) throw new Error("Failed to process image");
    const blob = await res.blob();
    preview.src = URL.createObjectURL(blob);
    imageFile = new File([blob], "edited.png", { type: "image/png" });
  } catch (err) {
    console.error(err);
    alert("Error editing image!");
  }
};

// Download
document.getElementById("download").onclick = () => {
  if (!imageFile) {
    alert("No image to download!");
    return;
  }
  const link = document.createElement("a");
  link.download = "edited-image.png";
  link.href = preview.src;
  link.click();
};
