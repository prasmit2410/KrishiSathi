// results.js - Display recommendation results on results.html
// Reads the stored recommendation JSON from sessionStorage and populates the UI.

let translations = {};

async function loadTranslations() {
  const res = await fetch("/translations.json");
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  translations = await res.json();
}

function applyTranslations(lang) {
  if (!lang || lang === "en") return;
  const langMap = translations[lang] || {};
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (langMap[key]) {
      el.textContent = langMap[key];
    }
  });
}

function formatRecommendation(rec, lang) {
  const { rank, crop_name, suitability, suitability_score, estimated_risk, estimated_return_potential, explanation, method, images } = rec;
  const labelSuitability = (translations[lang] && translations[lang].label_suitability) || "Suitability";
  const labelRisk = (translations[lang] && translations[lang].label_risk) || "Risk";
  const labelReturn = (translations[lang] && translations[lang].label_return) || "Return Potential";
  const labelMethod = (translations[lang] && translations[lang].label_method) || "Method";

  let imagesHtml = '';
  if (Array.isArray(images) && images.length > 0) {
    imagesHtml = `
      <div class="crop-images">
        ${images.map(img => `<img src="${img}" alt="${crop_name}" class="crop-image" onerror="this.style.display='none'">`).join('')}
      </div>
    `;
  }

  return `
    <div class="crop-card rank-${rank}">
      <div class="crop-header">
        <span class="crop-name">#${rank} ${crop_name}</span>
        <span class="crop-rank">Rank ${rank}</span>
      </div>
      <div class="score-bar">
        <div class="score-fill" style="width: ${suitability_score}%"></div>
      </div>
      <div class="badges">
        <span class="badge badge-high">${labelSuitability}: ${suitability} (${suitability_score}%)</span>
        <span class="badge badge-risk">${labelRisk}: ${estimated_risk}</span>
        <span class="badge badge-return">${labelReturn}: ${estimated_return_potential}</span>
        <span class="badge badge-moderate">${labelMethod}: ${method}</span>
      </div>
      <p class="crop-explanation">${explanation}</p>
      ${imagesHtml}
    </div>
  `;
}

async function renderResults() {
  try {
    await loadTranslations();
  } catch (e) {
    console.error("Failed to load translations:", e);
  }

  const raw = sessionStorage.getItem('krishi_result');
  if (!raw) {
    document.getElementById('results-container').innerHTML = '<p class="error">No results found. Please complete a recommendation first.</p>';
    return;
  }
  const data = JSON.parse(raw);
  const lang = data._lang || "en";

  applyTranslations(lang);

  const container = document.getElementById('results-container');
  
  // Summary text
  const summaryEl = document.getElementById('summary-text');
  if (summaryEl && data.summary) {
    summaryEl.textContent = data.summary;
  }
  
  // Recommendations list
  if (Array.isArray(data.recommendations) && data.recommendations.length) {
    container.innerHTML = data.recommendations.map(rec => formatRecommendation(rec, lang)).join('');
  } else {
    container.innerHTML = '<p>No recommendations returned.</p>';
  }
  
  // Meta info
  const metaInfo = document.getElementById('meta-info');
  if (metaInfo) {
    const meta = data.metadata || {};
    metaInfo.textContent = `Generated at ${meta.generated_at || ''} – Model ${meta.llm_model || ''} (v${meta.model_version})`;
  }
  
  // Disclaimer
  const disclaimerEl = document.getElementById('disclaimer');
  if (disclaimerEl && data.disclaimer) {
    disclaimerEl.textContent = data.disclaimer;
  }

  // Populate Input Summary
  const inputSummaryEl = document.getElementById('input-summary');
  if (inputSummaryEl && data.farmer_inputs) {
    const i = data.farmer_inputs;
    const langMap = translations[lang] || {};
    const labelTitle = lang === "hi" ? "कृषि विवरण" : (lang === "mr" ? "शेताचा तपशील" : "Farm Details");
    const lblState = langMap.label_state ? langMap.label_state.replace('*', '').trim() : 'State';
    const lblDistrict = langMap.label_district ? langMap.label_district.replace('*', '').trim() : 'District';
    const lblVillage = langMap.label_village || 'Village/Town';
    const lblLand = lang === "hi" ? "भूमि क्षेत्र" : (lang === "mr" ? "जमीन क्षेत्र" : "Land Area");
    const lblSoil = langMap.label_soil ? langMap.label_soil.replace('*', '').trim() : 'Soil Type';
    const lblSeason = langMap.label_season || 'Season';
    const lblIrrigation = langMap.label_irrigation || 'Irrigation';
    const valIrrigation = i.irrigation_available 
      ? (langMap.label_yes || 'Yes') 
      : (langMap.label_no || 'No');

    inputSummaryEl.innerHTML = `
      <h3>${labelTitle}</h3>
      <ul>
        <li><span>${lblState}:</span> ${i.state || 'N/A'}</li>
        <li><span>${lblDistrict}:</span> ${i.district || 'N/A'}</li>
        <li><span>${lblVillage}:</span> ${i.village || 'N/A'}</li>
        <li><span>${lblLand}:</span> ${i.land_area || 'N/A'} ${i.land_unit || ''}</li>
        <li><span>${lblSoil}:</span> ${i.soil_type || 'N/A'}</li>
        <li><span>${lblSeason}:</span> ${i.season || 'N/A'}</li>
        <li><span>${lblIrrigation}:</span> ${valIrrigation}</li>
      </ul>
    `;
    inputSummaryEl.classList.remove('hidden');
  }


}

// Run when DOM is ready
if (document.readyState !== 'loading') {
  renderResults();
} else {
  document.addEventListener('DOMContentLoaded', renderResults);
}
