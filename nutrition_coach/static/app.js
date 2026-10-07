// Shows a preview of the chosen image and a loading message while the model works.
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("analyze-form");
    const fileInput = document.getElementById("file");
    const preview = document.getElementById("uploaded-image");
    const loading = document.getElementById("loading-message");
    const submitBtn = document.getElementById("submit-btn");

    fileInput.addEventListener("change", () => {
        preview.replaceChildren();
        const file = fileInput.files[0];
        if (!file) return;

        const img = document.createElement("img");
        img.className = "uploaded-image-preview";
        img.alt = "Selected meal";
        img.src = URL.createObjectURL(file);
        img.onload = () => URL.revokeObjectURL(img.src);
        preview.appendChild(img);
    });

    form.addEventListener("submit", () => {
        loading.hidden = false;
        submitBtn.disabled = true;
    });
});
