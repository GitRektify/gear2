let selectedPromptKeys = {};
let kvStore = {{ prompt_config | tojson }};
let originalKVStore = JSON.parse(JSON.stringify(kvStore));
let selectedKey = null;

function toggleSettings() {
    const panel = document.getElementById("settingsPanel");
    const overlay = document.getElementById("settingsOverlay");
    const isVisible = panel.style.display === "block";

    if (!isVisible) {
        resetFormToOriginal();
        populateKeyList();
        const keys = Object.keys(kvStore);
        if (keys.length > 0) {
            loadKeyValue(keys[0]);
        }
    }

    panel.style.display = isVisible ? "none" : "block";
    overlay.style.display = isVisible ? "none" : "block";
}

function resetFormToOriginal() {
    kvStore = JSON.parse(JSON.stringify(originalKVStore));
    selectedKey = null;
    document.getElementById("saveBtn").disabled = true;
}

function populateKeyList() {
    const list = document.getElementById("keyList");
    list.innerHTML = "";

    Object.keys(kvStore).forEach(key => {
        const li = document.createElement("li");
        li.textContent = key;
        li.className = "key-item";
        li.onclick = () => loadKeyValue(key);
        li.onmouseenter = () => li.style.background = "#eee";
        li.onmouseleave = () => li.style.background = "";
        if (key === selectedKey) li.classList.add("active");
        list.appendChild(li);
    });

    const newLi = document.createElement("li");
    newLi.textContent = "➕ New Key";
    newLi.className = "key-item new-key";
    newLi.onclick = () => addNewKey();
    newLi.onmouseenter = () => newLi.style.background = "#eee";
    newLi.onmouseleave = () => newLi.style.background = "";
    list.appendChild(newLi);
}

function loadKeyValue(key) {
    selectedKey = key;
    const value = kvStore[key];
    document.getElementById("editKey").value = key;
    document.getElementById("editValue").value = value;
    document.getElementById("saveBtn").disabled = true;

    document.getElementById("editKey").oninput = checkChanges;
    document.getElementById("editValue").oninput = checkChanges;

    populateKeyList();
}

function checkChanges() {
    const newKey = document.getElementById("editKey").value;
    const newValue = document.getElementById("editValue").value;
    const originalValue = originalKVStore[selectedKey];
    const changed = newKey !== selectedKey || newValue !== originalValue;
    document.getElementById("saveBtn").disabled = !changed;
}

function saveSelectedKV() {
    const newKey = document.getElementById("editKey").value.trim();
    const newValue = document.getElementById("editValue").value.trim();

    if (!newKey || !newValue) {
        alert("Both fields are required.");
        return;
    }

    if ((!selectedKey || newKey !== selectedKey) && kvStore.hasOwnProperty(newKey)) {
        alert("Key already exists.");
        return;
    }

    if (newKey !== selectedKey && selectedKey !== null) {
        delete kvStore[selectedKey];
    }

    kvStore[newKey] = newValue;

    fetch("/save-config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(kvStore)
    }).then(res => {
        if (res.ok) {
            alert("Settings saved!");
            originalKVStore = JSON.parse(JSON.stringify(kvStore));
            populateKeyList();
            loadKeyValue(newKey);
        } else {
            alert("Failed to save settings.");
        }
    });
}

function cancelSettings() {
    toggleSettings();
}

function addNewKey() {
    selectedKey = null;
    document.getElementById("editKey").value = "";
    document.getElementById("editValue").value = "";
    document.getElementById("saveBtn").disabled = false;
}

function deleteCurrentKey() {
    if (selectedKey && confirm(`Are you sure you want to delete "${selectedKey}"?`)) {
        delete kvStore[selectedKey];

        fetch("/save-config", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(kvStore)
        }).then(res => {
            if (res.ok) {
                originalKVStore = JSON.parse(JSON.stringify(kvStore));
                populateKeyList();
                const firstKey = Object.keys(kvStore)[0];
                if (firstKey) {
                    loadKeyValue(firstKey);
                } else {
                    addNewKey();
                }
                document.getElementById("saveBtn").disabled = true;
            } else {
                alert("Failed to delete and save.");
            }
        });
    }
}

function showFileNameAndButton() {
    const fileInput = document.getElementById("file-input");
    const fileName = document.getElementById("file-name");
    const importBtn = document.getElementById("import-btn");

    if (fileInput.files.length > 0) {
        fileName.textContent = fileInput.files[0].name;
        fileName.style.display = "block";
        importBtn.style.display = "inline-block";
    } else {
        fileName.style.display = "none";
        importBtn.style.display = "none";
    }
}

function showPromptOptions(event, index) {
    const container = event.target.closest(".prompt-dropdown-container");
    const select = container.querySelector(".prompt-select");
    const button = container.querySelector(".prompt-btn");

    select.innerHTML = "";

    Object.keys(kvStore).forEach(key => {
        const option = document.createElement("option");
        option.value = key;
        option.textContent = key;
        if (selectedPromptKeys[index] === key) {
            option.selected = true;
        }
        select.appendChild(option);
    });

    select.style.display = "inline-block";
    button.style.display = "none";
}

function setPromptKey(selectEl, index) {
    const selectedKey = selectEl.value;
    const container = selectEl.closest(".prompt-dropdown-container");
    const button = container.querySelector(".prompt-btn");

    button.textContent = selectedKey;
    button.style.display = "inline-block";
    selectEl.style.display = "none";

    selectedPromptKeys[index] = selectedKey;

    const hiddenInput = document.querySelector(`#prompt-key-${index}`);
    if (hiddenInput) {
        hiddenInput.value = selectedKey;
    }
}