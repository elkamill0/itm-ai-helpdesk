const form = document.getElementById('uploadForm');
const loader = document.getElementById('loader');
const responseContainer = document.getElementById('responseContainer');
const responseElement = document.getElementById('response');
const imageInput = document.getElementById('image');
const imagePreview = document.getElementById('imagePreview');
const fileName = document.getElementById('fileName');
const clearButton = document.getElementById('clearButton');
const dropArea = document.getElementById('dropArea');
const cropButton = document.getElementById('cropButton');
const confirmCrop = document.getElementById('confirmCrop');
let cropper = null;

function getTypoCheckFlag() {
    const saved = localStorage.getItem("check_typos");
    return saved === null ? true : saved === "true";
}

function getMinSimilarity() {
    const saved = localStorage.getItem("min_similarity");
    return saved || "40";
}

function getSelectedColumns() {
    const saved = localStorage.getItem("selected_columns");
    try {
        const parsed = JSON.parse(saved);
        return Array.isArray(parsed) ? parsed : [];
    } catch {
        return [];
    }
}

imageInput.addEventListener('change', function (e) {
    const file = e.target.files[0];
    if (file) {
        fileName.textContent = file.name;
        clearButton.classList.remove('hidden');
        const reader = new FileReader();
        reader.onload = function (e) {
            imagePreview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
            imagePreview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    } else {
        fileName.textContent = 'Obrazek jeszcze nie jest wybrany';
        imagePreview.style.display = 'none';
        imagePreview.innerHTML = '';
        clearButton.classList.add('hidden');
    }
});

cropButton.addEventListener('click', () => {
    const img = imagePreview.querySelector('img');
    if (!img) {
        alert("Najpierw wybierz obrazek.");
        return;
    }

    if (cropper) cropper.destroy();

    cropper = new Cropper(img, {
        viewMode: 1,
        background: false,
        aspectRatio: NaN,
        autoCropArea: 0.8,
        dragMode: 'none',
    });

    confirmCrop.classList.remove('hidden');
});

let isRightMouseDragging = false;
let startX = 0;
let startY = 0;

imagePreview.addEventListener('contextmenu', e => e.preventDefault());

imagePreview.addEventListener('mousedown', (e) => {
    if (e.button === 2 && cropper) {
        isRightMouseDragging = true;
        startX = e.clientX;
        startY = e.clientY;
    }
});

window.addEventListener('mousemove', (e) => {
    if (isRightMouseDragging && cropper) {
        const deltaX = e.clientX - startX;
        const deltaY = e.clientY - startY;
        cropper.move(deltaX, deltaY);
        startX = e.clientX;
        startY = e.clientY;
    }
});

window.addEventListener('mouseup', (e) => {
    if (e.button === 2) {
        isRightMouseDragging = false;
    }
});

confirmCrop.addEventListener('click', () => {
    const canvas = cropper.getCroppedCanvas();
    const croppedDataUrl = canvas.toDataURL();

    imagePreview.innerHTML = `<img src="${croppedDataUrl}" alt="Cropped">`;
    fileName.textContent = "Wycięty fragment";
    confirmCrop.classList.add('hidden');

    fetch(croppedDataUrl)
        .then(res => res.blob())
        .then(blob => {
            const croppedFile = new File([blob], "cropped.png", { type: "image/png" });
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(croppedFile);
            imageInput.files = dataTransfer.files;
        });

    cropper.destroy();
});

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const submitButton = form.querySelector('button');
    submitButton.disabled = true;
    loader.style.display = 'block';
    responseContainer.classList.add('hidden');
    responseElement.classList.remove('error');

    const formData = new FormData(form);
    formData.append("check_typos", getTypoCheckFlag());
    formData.append("min_similarity", getMinSimilarity());

    // ✅ добавляем выбранные колонки
    const selectedColumns = getSelectedColumns();
    selectedColumns.forEach(col => formData.append("columns", col));

    try {
        const response = await fetch('http://127.0.0.1:8000/api/ask/', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Server error');
        }

        if (Array.isArray(data.answers)) {
            responseElement.innerHTML = data.answers.map((row, i) => `
                <div style="margin-bottom: 1rem;">
                    <strong>#${i + 1}: ${row[2] || 'Brak tytułu'}</strong><br/>
                    <em>${row[3] || ''}</em><br/>
                    <p>${row[5] || 'Brak rozwiązania'}</p>
                    <hr/>
                </div>
            `).join("");
        } else {
            responseElement.textContent = "Brak odpowiedzi.";
        }

        responseContainer.classList.remove('hidden');

    } catch (error) {
        responseElement.textContent = `Błąd: ${error.message}`;
        responseElement.classList.add('error');
        responseContainer.classList.remove('hidden');
    } finally {
        submitButton.disabled = false;
        loader.style.display = 'none';
    }
});

clearButton.addEventListener('click', () => {
    imageInput.value = '';
    fileName.textContent = 'Obrazek jeszcze nie jest wybrany';
    imagePreview.style.display = 'none';
    imagePreview.innerHTML = '';
    clearButton.classList.add('hidden');
    confirmCrop.classList.add('hidden');
    if (cropper) cropper.destroy();
});

['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropArea.classList.add('dragover');
    }, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropArea.classList.remove('dragover');
    }, false);
});

dropArea.addEventListener('drop', (e) => {
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        imageInput.files = e.dataTransfer.files;
        fileName.textContent = file.name;
        clearButton.classList.remove('hidden');

        const reader = new FileReader();
        reader.onload = function (e) {
            imagePreview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
            imagePreview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    } else {
        alert("Wybierz poprawny plik graficzny.");
    }
});

document.addEventListener('paste', (e) => {
    const items = e.clipboardData.items;
    for (let i = 0; i < items.length; i++) {
        const item = items[i];
        if (item.type.indexOf('image') !== -1) {
            const file = item.getAsFile();
            if (file) {
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                imageInput.files = dataTransfer.files;

                fileName.textContent = file.name || 'Wklejony obrazek';
                clearButton.classList.remove('hidden');

                const reader = new FileReader();
                reader.onload = function (event) {
                    imagePreview.innerHTML = `<img src="${event.target.result}" alt="Pasted Image">`;
                    imagePreview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        }
    }
});
