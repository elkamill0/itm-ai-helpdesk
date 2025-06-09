const excelUploadForm = document.getElementById('excelUploadForm');
const excelFileInput = document.getElementById('excelFile');
const excelFileNameDisplay = document.getElementById('excelFileName');
const successMessage = document.getElementById('successMessage');

function loadSelectedColumns() {
    const saved = JSON.parse(localStorage.getItem("selected_columns") || "[]");
    const checkboxes = document.querySelectorAll('input[name="columns"]');
    checkboxes.forEach(cb => {
        cb.checked = saved.includes(cb.value);
        cb.addEventListener("change", saveSelectedColumns);
    });
}
function saveSelectedColumns() {
    const checkboxes = document.querySelectorAll('input[name="columns"]');
    const selected = Array.from(checkboxes).filter(ch => ch.checked).map(ch => ch.value);
    localStorage.setItem("selected_columns", JSON.stringify(selected));
}

function loadTypoCheck() {
    const typoCheckbox = document.getElementById("typoCheck");
    const saved = localStorage.getItem("check_typos");
    typoCheckbox.checked = saved === null ? true : saved === "true";
    typoCheckbox.addEventListener("change", () => {
        localStorage.setItem("check_typos", typoCheckbox.checked);
    });
}

function loadSimilaritySlider() {
    const slider = document.getElementById("similaritySlider");
    const label = document.getElementById("similarityValue");
    const saved = localStorage.getItem("min_similarity") || "40";

    slider.value = saved;
    label.textContent = `${saved}%`;

    slider.addEventListener("input", () => {
        localStorage.setItem("min_similarity", slider.value);
        label.textContent = `${slider.value}%`;
    });
}

excelFileInput.addEventListener('change', (event) => {
    const file = event.target.files[0];
    excelFileNameDisplay.textContent = file ? file.name : "Plik nie został wybrany";
});

excelUploadForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    saveSelectedColumns();

    const file = excelFileInput.files[0];
    if (!file) {
        alert("Wybierz plik przed wysłaniem.");
        return;
    }

    const formData = new FormData();
    formData.append('excelFile', file);

    try {
        const response = await fetch('http://127.0.0.1:8000/api/errors/upload-excel/', {
            method: 'POST',
            body: formData,
        });
        const data = await response.json();
        if (response.ok) {
            successMessage.textContent = data.message;
            successMessage.classList.remove('hidden');
            successMessage.classList.add('success-message');
            loadBackupList();
        } else {
            alert(data.error || "Błąd podczas przesyłania pliku.");
        }
    } catch (error) {
        console.error("Błąd:", error);
        alert("Wystąpił błąd podczas wysyłania pliku.");
    }
});

const excelDropArea = document.getElementById("excelDropArea");

["dragenter", "dragover"].forEach(eventName => {
    excelDropArea.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        excelDropArea.classList.add('dragover');
    }, false);
});

["dragleave", "drop"].forEach(eventName => {
    excelDropArea.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        excelDropArea.classList.remove('dragover');
    }, false);
});

excelDropArea.addEventListener("drop", (e) => {
    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith(".xlsx")) {
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        excelFileInput.files = dataTransfer.files;
        excelFileNameDisplay.textContent = file.name;
    } else {
        alert("Wybierz poprawny plik Excel (.xlsx)");
    }
});


async function loadBackupList() {
    try {
        const response = await fetch("http://127.0.0.1:8000/api/errors/backups/");
        const data = await response.json();

        const backupList = document.getElementById("backupList");
        backupList.innerHTML = "";

        const active = data.active;

        data.backups.forEach(file => {
            const row = document.createElement("div");
            row.className = "backup-row";
            
            const fileName = document.createElement("span");
            fileName.className = "backup-filename";
            fileName.textContent = file;
            
            if (file === active) {
                const activeBadge = document.createElement("span");
                activeBadge.className = "active-badge";
                activeBadge.textContent = "Aktywne";
                fileName.appendChild(activeBadge);
            }
            
            const btn = document.createElement("button");
            btn.textContent = "Aktywuj";
            btn.className = "small-button";
            btn.disabled = (file === active);

            btn.onclick = async () => {
                if (!confirm(`Czy na pewno chcesz ustawić plik "${file}" jako aktywny?`)) return;

                const res = await fetch("http://127.0.0.1:8000/api/errors/select-backup/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ filename: file })
                });

                if (res.ok) {
                    alert("Plik został ustawiony jako aktywny.");
                    loadBackupList();
                } else {
                    alert("Wystąpił błąd.");
                }
            };

            row.appendChild(fileName);
            row.appendChild(btn);
            backupList.appendChild(row);
        });

    } catch (err) {
        console.error("Błąd przy pobieraniu kopii zapasowych:", err);
        backupList.innerHTML = `<p class="error">Błąd przy pobieraniu listy plików</p>`;
    }
}

