// frontend/js/app.js
// API_BASE is defined in config.js (loaded before this script)


let translations = {};
let selectedLanguage = "en";

async function loadTranslations() {
  const res = await fetchJSON("/translations.json");
  translations = res;
}

function getTranslation(key) {
  if (selectedLanguage === "en") return key;
  const langMap = translations[selectedLanguage] || {};
  const optionsMap = langMap.options || {};
  return optionsMap[key] || key;
}

function translateStaticOptions() {
  document.querySelectorAll("select:not(#language) option").forEach((opt) => {
    const val = opt.value;
    if (val) {
      opt.textContent = getTranslation(val);
    } else if (opt.textContent) {
      opt.textContent = getTranslation(opt.textContent.trim());
    }
  });
}

function applyTranslations() {
  if (selectedLanguage !== "en") {
    const langMap = translations[selectedLanguage] || {};
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      if (langMap[key]) {
        el.textContent = langMap[key];
      }
    });
  }
  translateStaticOptions();
}

function initLanguageSelector() {
  const selector = document.getElementById("language");
  if (!selector) return;
  const stored = localStorage.getItem("selectedLanguage");
  if (stored) {
    selectedLanguage = stored;
    selector.value = stored;
  }
  selector.addEventListener("change", () => {
    selectedLanguage = selector.value;
    localStorage.setItem("selectedLanguage", selectedLanguage);
    window.location.reload();
  });
}

async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

async function loadFormOptions() {
  const [statesData, soilData] = await Promise.all([
    fetchJSON(`${API_BASE}/api/v1/locations/states?lang=${selectedLanguage}`),
    fetchJSON(`${API_BASE}/api/v1/soil-types`),
  ]);

  const stateSelect = document.getElementById("state");
  stateSelect.innerHTML = "";
  const placeholderState = document.createElement("option");
  placeholderState.value = "";
  placeholderState.textContent = getTranslation("Select state");
  stateSelect.appendChild(placeholderState);
  statesData.states.forEach((state) => {
    const opt = document.createElement("option");
    opt.value = state.id;
    opt.textContent = state.name;
    stateSelect.appendChild(opt);
  });

  const soilSelect = document.getElementById("soil_type");
  soilSelect.innerHTML = "";
  const placeholderSoil = document.createElement("option");
  placeholderSoil.value = "";
  placeholderSoil.textContent = getTranslation("Select soil type");
  soilSelect.appendChild(placeholderSoil);
  soilData.soil_types.forEach((soil) => {
    const opt = document.createElement("option");
    opt.value = soil;
    opt.textContent = getTranslation(soil);
    soilSelect.appendChild(opt);
  });

  stateSelect.addEventListener("change", async () => {
    const districtSelect = document.getElementById("district");
    districtSelect.innerHTML = "";
    if (!stateSelect.value) {
      districtSelect.disabled = true;
      const placeholderDistrict = document.createElement("option");
      placeholderDistrict.value = "";
      placeholderDistrict.textContent = getTranslation("Select state first");
      districtSelect.appendChild(placeholderDistrict);
      return;
    }
    const placeholderDistrict = document.createElement("option");
    placeholderDistrict.value = "";
    placeholderDistrict.textContent = getTranslation("Select district");
    districtSelect.appendChild(placeholderDistrict);

    const data = await fetchJSON(
      `${API_BASE}/api/v1/locations/districts?state=${encodeURIComponent(stateSelect.value)}&lang=${selectedLanguage}`
    );
    data.districts.forEach((d) => {
      const opt = document.createElement("option");
      opt.value = d.id;
      opt.textContent = d.name;
      districtSelect.appendChild(opt);
    });
    districtSelect.disabled = false;
  });

  stateSelect.dispatchEvent(new Event("change"));
}

document.getElementById("recommendation-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const form = e.target;
  const loading = document.getElementById("loading");
  const errorEl = document.getElementById("error");
  const submitBtn = document.getElementById("submit-btn");

  errorEl.classList.add("hidden");
  loading.classList.remove("hidden");
  submitBtn.disabled = true;

  const payload = {
    state: form.state.value,
    district: form.district.value,
    village: form.village.value || null,
    land_area: parseFloat(form.land_area.value),
    land_unit: form.land_unit.value,
    soil_type: form.soil_type.value,
    season: form.season.value,
    irrigation_available: form.irrigation_available.value === "true",
    language: selectedLanguage,
  };

  try {
    const res = await fetch(`${API_BASE}/api/v1/recommendations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) {
      const msg = data.details
        ? data.details.map((d) => d.msg || JSON.stringify(d)).join("; ")
        : data.message || "Request failed";
      throw new Error(msg);
    }

    // Store language preference with result
    data._lang = selectedLanguage;
    sessionStorage.setItem("krishi_result", JSON.stringify(data));
    window.location.href = "/results.html"; // Redirect to results page
  } catch (err) {
    errorEl.textContent = err.message || "Something went wrong. Please try again.";
    errorEl.classList.remove("hidden");
  } finally {
    loading.classList.add("hidden");
    submitBtn.disabled = false;
  }
});

// Initialize on load
(async () => {
  try {
    await loadTranslations();
    initLanguageSelector();
    applyTranslations();
    await loadFormOptions();
  } catch (err) {
    document.getElementById("error").textContent = "Could not load form options. Is the server running?";
    document.getElementById("error").classList.remove("hidden");
  }
})();
