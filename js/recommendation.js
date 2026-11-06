const API_BASE = window.NUTRIORDER_API_BASE || `http://${window.location.hostname}:5000`;
const STEPS = [
    { key: "goal", title: "Your food goal", subtitle: "Pick one primary goal for this meal discovery.", type: "single", options: [["weight_loss", "Weight loss", "Portion-aware menu matches"], ["weight_gain", "Weight gain", "Explore energy-containing dishes"], ["muscle_building", "Muscle building", "Compare listed protein values"], ["weight_maintenance", "Weight maintenance", "Everyday balance"], ["healthy_eating", "Healthy eating", "A thoughtful all-round choice"], ["high_protein", "High protein", "Prioritise menu protein data"], ["heart_healthy", "Heart-conscious eating", "General information; not medical advice"], ["balanced_nutrition", "Balanced nutrition", "Explore variety from the menu"]] },
    { key: "health_considerations", title: "Health considerations", subtitle: "Optional and private to this session. Skip or choose prefer not to say.", type: "multi", options: [["diabetes", "Diabetes"], ["high_blood_pressure", "High blood pressure"], ["low_blood_pressure", "Low blood pressure"], ["heart_disease", "Heart disease"], ["high_cholesterol", "High cholesterol"], ["thyroid_conditions", "Thyroid conditions"], ["other", "Other dietary considerations"], ["none", "None"], ["prefer_not_to_say", "Prefer not to say"]] },
    { key: "dietary_preference", title: "How do you like to eat?", subtitle: "Choose your dietary pattern. Unconfirmed recipes are sent to the verification list, not treated as safe.", type: "single", options: [["vegetarian", "Vegetarian"], ["non_vegetarian", "Non-vegetarian"], ["eggetarian", "Eggetarian"], ["vegan", "Vegan"], ["pescatarian", "Pescatarian"], ["no_preference", "No preference"]] },
    { key: "cuisine_preferences", title: "Cuisine mood", subtitle: "Choose one or more cuisine preferences.", type: "multi", options: [["tamil_nadu", "Tamil Nadu traditional"], ["south_indian", "South Indian"], ["north_indian", "North Indian"], ["continental", "Continental"], ["chinese", "Chinese"], ["all_cuisines", "All cuisines"]] },
    { key: "allergies", title: "Allergies & ingredients", subtitle: "Select known allergies. Unknown ingredients and cross-contact are never assumed safe.", type: "multi", options: [["peanuts", "Peanuts"], ["tree_nuts", "Tree nuts"], ["dairy", "Milk / dairy"], ["egg", "Egg"], ["fish", "Fish"], ["shellfish", "Shellfish"], ["soy", "Soy"], ["gluten", "Gluten"], ["sesame", "Sesame"], ["other", "Other allergy"], ["no_known_allergies", "No known allergies"]], other: true },
    { key: "nutrition_preferences", title: "Nutrition preferences", subtitle: "These are menu filters—not medical targets. Values are estimates unless explicitly verified.", type: "multi", options: [["low_calorie", "Lower calorie"], ["high_protein", "Higher protein"], ["high_fibre", "Higher fibre"], ["lower_carbohydrate", "Lower carbohydrate"], ["less_oil", "Less oil"], ["less_salt", "Less salt"], ["balanced_nutrition", "Balanced nutrition"]] },
    { key: "taste_preferences", title: "Taste preferences", subtitle: "Choose what sounds good today.", type: "multi", options: [["spicy", "Spicy"], ["mild", "Mild"], ["sweet", "Sweet"], ["less_oily", "Less oily"], ["less_salty", "Less salty"], ["no_preference", "No preference"]] },
    { key: "meal_preferences", title: "When are you eating?", subtitle: "We’ll use meal types listed in the current restaurant menu.", type: "multi", options: [["breakfast", "Breakfast"], ["lunch", "Lunch"], ["evening_snacks", "Evening snacks"], ["dinner", "Dinner"], ["anytime", "Anytime"]] },
    { key: "budget", title: "Your budget", subtitle: "Prices are taken from the live menu. Choose a range or skip for any budget.", type: "single", options: [["under_50", "Under ₹50"], ["50_100", "₹50 to under ₹100"], ["100_200", "₹100 to under ₹200"], ["200_300", "₹200–₹300"], ["above_300", "Above ₹300"], ["no_limit", "No budget preference"]] },
    { key: "personal", title: "Optional personal details", subtitle: "Not needed for recommendations. Measurements are not stored or used to prescribe calorie targets.", type: "personal" }
];

const defaults = () => ({ goal: null, secondary_goals: [], health_considerations: [], dietary_preference: "no_preference", cuisine_preferences: [], allergies: [], other_allergies: "", nutrition_preferences: [], taste_preferences: [], meal_preferences: [], budget: "no_limit" });
let profile = defaults();
let stepIndex = 0;
let latestRecommendations = [];

const stepContent = document.getElementById("stepContent");
const progressFill = document.getElementById("progressFill");
const wizard = document.getElementById("preferenceWizard");
const results = document.getElementById("recommendationResults");
const previousButton = document.getElementById("previousStep");
const nextButton = document.getElementById("nextStep");
const skipButton = document.getElementById("skipStep");

function selectedValues(step) {
    if (step.key === "personal") return [];
    if (step.type === "single") return profile[step.key] ? [profile[step.key]] : [];
    return profile[step.key] || [];
}

function renderStep() {
    const step = STEPS[stepIndex];
    document.getElementById("stepCount").textContent = `Step ${stepIndex + 1} of ${STEPS.length}`;
    document.getElementById("stepName").textContent = step.title;
    document.querySelector(".nm-progress-track").setAttribute("aria-valuenow", String(stepIndex + 1));
    progressFill.style.width = `${((stepIndex + 1) / STEPS.length) * 100}%`;
    previousButton.disabled = stepIndex === 0;
    nextButton.textContent = stepIndex === STEPS.length - 1 ? "Find my matches →" : "Continue →";
    skipButton.textContent = stepIndex === 0 ? "Skip all preferences" : "Skip this step";
    stepContent.replaceChildren();

    const heading = document.createElement("div");
    heading.className = "nm-step-title";
    const title = document.createElement("h3");
    title.textContent = step.title;
    const subtitle = document.createElement("p");
    subtitle.textContent = step.subtitle;
    heading.append(title, subtitle);
    stepContent.appendChild(heading);

    if (step.type === "personal") {
        const note = document.createElement("div");
        note.className = "nm-personal-note";
        note.textContent = "Personal measurements are not needed. If you choose to enter them below, they stay only in this page session and are not submitted to the recommendation API.";
        stepContent.appendChild(note);
        const grid = document.createElement("div");
        grid.className = "nm-personal-grid";
        [["Age", "age", "years"], ["Height", "height", "cm"], ["Weight", "weight", "kg"]].forEach(([label, key, unit]) => {
            const wrapper = document.createElement("label");
            wrapper.className = "nm-input-label";
            wrapper.textContent = label;
            const input = document.createElement("input");
            input.type = "number";
            input.min = "1";
            input.max = "250";
            input.placeholder = unit;
            input.autocomplete = "off";
            input.dataset.personal = key;
            wrapper.appendChild(input);
            grid.appendChild(wrapper);
        });
        const activity = document.createElement("label");
        activity.className = "nm-input-label nm-activity-label";
        activity.textContent = "Activity level (optional)";
        const select = document.createElement("select");
        select.dataset.personal = "activity";
        [["", "Prefer not to say"], ["low", "Mostly seated"], ["moderate", "Moderately active"], ["high", "Very active"]].forEach(([value, label]) => {
            const option = document.createElement("option"); option.value = value; option.textContent = label; select.appendChild(option);
        });
        activity.appendChild(select); grid.append(activity);
        stepContent.appendChild(grid);
    } else {
        const grid = document.createElement("div");
        grid.className = `nm-option-grid ${step.key === "health_considerations" || step.key === "allergies" ? "nm-option-grid-compact" : ""}`;
        step.options.forEach(([value, label, description]) => {
            const button = document.createElement("button");
            button.type = "button";
            button.className = "nm-option-card";
            button.dataset.value = value;
            button.setAttribute("aria-pressed", String(selectedValues(step).includes(value)));
            const mark = document.createElement("span"); mark.className = "nm-option-mark"; mark.setAttribute("aria-hidden", "true"); mark.textContent = selectedValues(step).includes(value) ? "✓" : "+";
            const copy = document.createElement("span"); copy.className = "nm-option-copy";
            const strong = document.createElement("strong"); strong.textContent = label; copy.appendChild(strong);
            if (description) { const detail = document.createElement("small"); detail.textContent = description; copy.appendChild(detail); }
            button.append(mark, copy);
            button.addEventListener("click", () => toggleOption(step, value, button));
            grid.appendChild(button);
        });
        stepContent.appendChild(grid);
        if (step.key === "goal") {
            const secondary = document.createElement("fieldset");
            secondary.className = "nm-secondary-goals";
            const legend = document.createElement("legend"); legend.textContent = "Optional secondary goals"; secondary.appendChild(legend);
            const secondaryGrid = document.createElement("div"); secondaryGrid.className = "nm-secondary-goal-options";
            step.options.forEach(([value, label]) => {
                const wrapper = document.createElement("label"); wrapper.className = "nm-check-option";
                const checkbox = document.createElement("input"); checkbox.type = "checkbox"; checkbox.value = value; checkbox.checked = profile.secondary_goals.includes(value);
                checkbox.addEventListener("change", () => { profile.secondary_goals = checkbox.checked ? [...new Set([...profile.secondary_goals, value])] : profile.secondary_goals.filter(item => item !== value); });
                const text = document.createElement("span"); text.textContent = label; wrapper.append(checkbox, text); secondaryGrid.appendChild(wrapper);
            });
            secondary.appendChild(secondaryGrid); stepContent.appendChild(secondary);
        }
        if (step.other) {
            const other = document.createElement("label");
            other.className = "nm-input-label nm-other-allergy";
            other.textContent = "Other allergy details (optional)";
            const input = document.createElement("input"); input.maxLength = 160; input.placeholder = "Enter a food or ingredient"; input.value = profile.other_allergies;
            input.addEventListener("input", () => { profile.other_allergies = input.value; });
            other.appendChild(input); stepContent.appendChild(other);
        }
    }
}

function toggleOption(step, value, button) {
    if (step.type === "single") {
        profile[step.key] = profile[step.key] === value ? null : value;
        stepContent.querySelectorAll(".nm-option-card").forEach(card => {
            const active = card.dataset.value === profile[step.key];
            card.setAttribute("aria-pressed", String(active));
            card.querySelector(".nm-option-mark").textContent = active ? "✓" : "+";
        });
        return;
    }
    let values = profile[step.key];
    const exclusive = step.key === "health_considerations" ? ["none", "prefer_not_to_say"] : step.key === "allergies" ? ["no_known_allergies"] : step.key === "cuisine_preferences" ? ["all_cuisines"] : step.key === "taste_preferences" ? ["no_preference"] : step.key === "meal_preferences" ? ["anytime"] : [];
    if (values.includes(value)) values = values.filter(item => item !== value);
    else if (exclusive.includes(value)) values = [value];
    else values = [...values.filter(item => !exclusive.includes(item)), value];
    profile[step.key] = values;
    const active = values.includes(value);
    button.setAttribute("aria-pressed", String(active));
    button.querySelector(".nm-option-mark").textContent = active ? "✓" : "+";
    stepContent.querySelectorAll(".nm-option-card").forEach(card => {
        const isActive = values.includes(card.dataset.value);
        card.setAttribute("aria-pressed", String(isActive));
        card.querySelector(".nm-option-mark").textContent = isActive ? "✓" : "+";
    });
}

async function postJson(path, payload) {
    const response = await fetch(`${API_BASE}${path}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    const data = await response.json();
    if (!response.ok || !data.success) throw new Error(data.message || "NutriMatch could not complete that request.");
    return data;
}

function setLoading(loading) {
    nextButton.disabled = loading;
    skipButton.disabled = loading;
    previousButton.disabled = loading || stepIndex === 0;
    nextButton.innerHTML = loading ? '<span class="nm-spinner" aria-hidden="true"></span> Finding thoughtful picks…' : (stepIndex === STEPS.length - 1 ? "Find my matches →" : "Continue →");
    stepContent.setAttribute("aria-busy", String(loading));
}

async function finishQuestionnaire() {
    setLoading(true);
    try {
        // Profile endpoint validates and echoes only request data; optional measurements are excluded.
        const { age, height, weight, activity, ...shareableProfile } = profile;
        const validated = await postJson("/api/nutrimatch/profile", shareableProfile);
        const result = await postJson("/api/nutrimatch/recommendations", validated.profile);
        renderResults(result);
        wizard.hidden = true;
        results.hidden = false;
        results.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (error) {
        showWizardError(error.message || "Recommendations could not be loaded. Please try again.");
    } finally { setLoading(false); }
}

function showWizardError(message) {
    let error = document.getElementById("nmWizardError");
    if (!error) { error = document.createElement("p"); error.id = "nmWizardError"; error.className = "nm-inline-error"; error.setAttribute("role", "alert"); stepContent.appendChild(error); }
    error.textContent = message;
}

function clearWizardError() { document.getElementById("nmWizardError")?.remove(); }

function renderResults(data) {
    latestRecommendations = [...(data.best_matches || []), ...(data.alternative_choices || [])];
    document.getElementById("matchingMethod").textContent = `Match score = goal 30% + nutrition 25% + cuisine 15% + taste 10% + budget 10% + meal 10%. Allergy and strict dietary filters are applied before scoring. Unknown nutrition earns no assumed advantage. Method: ${data.recommendation_method}.`;
    document.getElementById("resultsDisclaimer").textContent = data.disclaimer || "General food information only; confirm ingredients and allergies with the restaurant.";
    const notices = document.getElementById("healthNotices"); notices.replaceChildren();
    (data.health_notices || []).forEach(text => { const p = document.createElement("p"); p.textContent = text; notices.appendChild(p); });
    const guidance = document.getElementById("ragGuidance"); guidance.replaceChildren();
    if (data.rag_guidance?.length) {
        guidance.hidden = false;
        const title = document.createElement("h3"); title.textContent = "A little more context"; guidance.appendChild(title);
        const intro = document.createElement("p"); intro.className = "nm-rag-intro"; intro.textContent = "Retrieved from NutriOrder’s curated food notes. These general references do not override the live menu or provide medical advice."; guidance.appendChild(intro);
        const list = document.createElement("ul");
        data.rag_guidance.forEach(item => { const row = document.createElement("li"); const text = document.createElement("p"); text.textContent = item.excerpt; const source = document.createElement("span"); source.textContent = item.source; row.append(text, source); list.appendChild(row); });
        guidance.appendChild(list);
    } else { guidance.hidden = true; }
    renderFoodGroup("bestMatches", data.best_matches || [], "No best matches in the current menu for those filters.");
    renderFoodGroup("alternativeChoices", data.alternative_choices || [], "No additional eligible alternatives were found.");
    const verification = document.getElementById("verificationFoods"); verification.replaceChildren();
    (data.requiring_verification || []).forEach(food => verification.appendChild(createVerificationCard(food)));
    document.getElementById("verificationSection").hidden = !(data.requiring_verification || []).length;
    document.getElementById("resultsSummary").textContent = `${(data.best_matches || []).length + (data.alternative_choices || []).length} eligible menu match${(data.best_matches || []).length + (data.alternative_choices || []).length === 1 ? "" : "es"}; ${data.filtered_count || 0} excluded by selected restrictions, menu, budget, or meal filters.`;
}

function renderFoodGroup(id, foods, emptyText) {
    const container = document.getElementById(id); container.replaceChildren();
    if (!foods.length) { const empty = document.createElement("div"); empty.className = "nm-empty-state"; empty.textContent = emptyText; container.appendChild(empty); return; }
    foods.forEach((food, index) => container.appendChild(createFoodCard(food, index)));
}

function createFoodCard(food, index = 0) {
    const card = document.createElement("article"); card.className = "nm-food-card"; card.style.setProperty("--card-order", index);
    const media = document.createElement("div"); media.className = "nm-food-media";
    const hasLocalImage = typeof food.image_url === "string" && food.image_url.startsWith("/images/");
    const image = document.createElement("img"); image.src = hasLocalImage ? food.image_url : "/images/food-fallback.svg"; image.alt = hasLocalImage ? `${food.name} representative food photo; not restaurant-verified` : `${food.name}; exact dish photograph not verified`; image.loading = "lazy"; image.onerror = () => { image.onerror = null; image.src = "/images/food-fallback.svg"; }; media.appendChild(image);
    const score = document.createElement("span"); score.className = "nm-match-badge"; score.textContent = `${food.match_percentage}% match`; media.appendChild(score); card.appendChild(media);
    const body = document.createElement("div"); body.className = "nm-food-card-body";
    const tags = document.createElement("div"); tags.className = "nm-food-tags";
    [food.food_type, food.meal_type, food.cuisine].filter(Boolean).forEach(tag => { const pill = document.createElement("span"); pill.textContent = tag.replaceAll("_", " "); tags.appendChild(pill); });
    const title = document.createElement("h4"); title.textContent = food.name;
    const restaurant = document.createElement("p"); restaurant.className = "nm-restaurant-name"; restaurant.textContent = `${food.restaurant_name || "NutriOrder AI"} · ${food.category || "Menu item"}`;
    const metrics = document.createElement("div"); metrics.className = "nm-food-metrics";
    const n = food.nutrition || {};
    metrics.append(metric(n.calories == null ? "Calories N/A" : `~${n.calories} kcal`), metric(n.protein == null ? "Protein N/A" : `~${n.protein} g protein`));
    const nutritionStatus = document.createElement("p"); nutritionStatus.className = "nm-nutrition-status"; nutritionStatus.textContent = `Nutrition: ${n.status || "not recorded"}`;
    const explanation = document.createElement("ul"); explanation.className = "nm-match-reasons";
    (food.match_explanation || []).slice(0, 2).forEach(text => { const li = document.createElement("li"); li.textContent = text; explanation.appendChild(li); });
    const availability = document.createElement("p"); availability.className = "nm-availability"; availability.textContent = `Availability: ${food.availability || "not tracked"}`;
    const footer = document.createElement("div"); footer.className = "nm-food-card-footer";
    const price = document.createElement("strong"); price.textContent = food.price == null ? "Price unavailable" : `₹${Number(food.price).toFixed(0)}`;
    const actions = document.createElement("div"); actions.className = "nm-food-actions";
    const detail = document.createElement("button"); detail.type = "button"; detail.className = "nm-detail-button"; detail.textContent = "View details"; detail.addEventListener("click", () => showFoodDetail(food));
    const add = document.createElement("button"); add.type = "button"; add.className = "nm-add-button"; add.textContent = "+ Add"; add.addEventListener("click", () => addRecommendedFood(food, add));
    actions.append(detail, add); footer.append(price, actions);
    body.append(tags, title, restaurant, metrics, nutritionStatus, explanation, availability, footer); card.appendChild(body);
    const allergen = document.createElement("p"); allergen.className = "nm-allergen-note"; allergen.textContent = `Allergens: ${food.allergens?.length ? food.allergens.join(", ") : "not recorded"}. ${food.allergen_status || "Confirm ingredients and cross-contact with the restaurant."}`; card.appendChild(allergen);
    return card;
}

function metric(text) { const span = document.createElement("span"); span.textContent = text; return span; }

function createVerificationCard(food) {
    const card = document.createElement("article"); card.className = "nm-verification-card";
    const image = document.createElement("img"); image.src = food.image_url || "/images/food-fallback.svg"; image.alt = ""; image.loading = "lazy"; image.onerror = () => { image.onerror = null; image.src = "/images/food-fallback.svg"; };
    const info = document.createElement("div"); const title = document.createElement("h4"); title.textContent = food.name;
    const detail = document.createElement("button"); detail.type = "button"; detail.className = "nm-detail-button"; detail.textContent = "View details"; detail.addEventListener("click", async () => {
        try { const data = await fetch(`${API_BASE}/api/nutrimatch/foods/${food.id}`).then(response => response.json()); if (!data.success) throw new Error(data.message); showFoodDetail(_foodFromApi(data.food)); }
        catch (_) { showFoodDetail({ ...food, ingredients: [], allergens: [], nutrition: {}, health_notice: "This item needs confirmation before ordering." }); }
    });
    const reason = document.createElement("p"); reason.textContent = food.reason;
    const price = document.createElement("span"); price.textContent = food.price == null ? "Price unavailable" : `₹${Number(food.price).toFixed(0)}`;
    info.append(title, reason, price, detail); card.append(image, info); return card;
}

function _foodFromApi(food) {
    return { ...food, image_url: typeof food.image_url === "string" && food.image_url.startsWith("/images/") ? food.image_url : null, restaurant_name: food.restaurant_name || "NutriOrder AI", match_percentage: 0, match_explanation: [], health_notice: "General food information only. Confirm ingredients and allergy cross-contact with the restaurant." };
}

function showFoodDetail(food) {
    const dialog = document.getElementById("foodDetailDialog"); const content = document.getElementById("foodDetailContent"); content.replaceChildren();
    const image = document.createElement("img"); image.className = "nm-detail-image"; image.src = food.image_url || "/images/food-fallback.svg"; image.alt = `${food.name} dish`; image.onerror = () => { image.onerror = null; image.src = "/images/food-fallback.svg"; };
    const title = document.createElement("h2"); title.id = "detailFoodName"; title.textContent = food.name;
    const restaurant = document.createElement("p"); restaurant.textContent = `${food.restaurant_name || "NutriOrder AI"} · ${food.category || "Menu item"} · ${food.price == null ? "Price not available" : `₹${Number(food.price).toFixed(0)}`}`;
    const details = document.createElement("div"); details.className = "nm-detail-grid";
    const nutrition = food.nutrition || {};
    [["Serving size", food.serving_size], ["Calories", nutrition.calories == null ? null : `${nutrition.calories} kcal`], ["Protein", nutrition.protein == null ? null : `${nutrition.protein} g`], ["Carbohydrates", nutrition.carbohydrates == null ? null : `${nutrition.carbohydrates} g`], ["Fat", nutrition.fat == null ? null : `${nutrition.fat} g`], ["Fibre", nutrition.fiber == null ? null : `${nutrition.fiber} g`], ["Sodium", nutrition.sodium == null ? null : `${nutrition.sodium} mg`], ["Data status", nutrition.status]].forEach(([label, value]) => { const box = document.createElement("div"); const small = document.createElement("small"); small.textContent = label; const strong = document.createElement("strong"); strong.textContent = value || "Not available"; box.append(small, strong); details.appendChild(box); });
    const ingredients = document.createElement("p"); ingredients.textContent = `Ingredients: ${food.ingredients?.length ? food.ingredients.join(", ") : "not recorded; confirm with restaurant"}`;
    const allergen = document.createElement("p"); allergen.textContent = `Allergens: ${food.allergens?.length ? food.allergens.join(", ") : "not recorded; cross-contact unknown"}`;
    const notice = document.createElement("p"); notice.className = "nm-disclaimer"; notice.textContent = food.health_notice;
    content.append(image, title, restaurant, details, ingredients, allergen, notice);
    if (typeof dialog.showModal === "function") dialog.showModal(); else alert(`${food.name}\n${ingredients.textContent}\n${allergen.textContent}`);
}

function addRecommendedFood(food, button) {
    const cart = JSON.parse(localStorage.getItem("cart") || "[]");
    const existing = cart.find(item => item.id === food.id);
    if (existing) existing.quantity++;
    else cart.push({ id: food.id, name: food.name, price: food.price, quantity: 1 });
    localStorage.setItem("cart", JSON.stringify(cart));
    const original = button.textContent; button.textContent = "Added ✓"; button.disabled = true;
    window.setTimeout(() => { button.textContent = original; button.disabled = false; }, 1200);
}

async function submitChat(message) {
    const list = document.getElementById("nmChatMessages"); const status = document.getElementById("nmChatStatus");
    const user = document.createElement("li"); user.className = "nm-chat-user"; user.textContent = message; list.appendChild(user);
    status.textContent = "Checking the current menu…";
    try {
        const response = await postJson("/api/nutrimatch/chat", { message, preferences: profile });
        const assistant = document.createElement("li"); assistant.className = "nm-chat-assistant"; assistant.textContent = response.answer; list.appendChild(assistant);
        if (response.sources?.length) {
            const sources = document.createElement("li"); sources.className = "nm-chat-source"; sources.textContent = `Context: ${response.sources.join(" · ")}`; list.appendChild(sources);
        }
        const recs = response.recommendations;
        if (recs) {
            latestRecommendations = [...(recs.best_matches || []), ...(recs.alternative_choices || [])];
            if (latestRecommendations.length) {
                const cards = document.createElement("div"); cards.className = "nm-chat-recommendations";
                latestRecommendations.slice(0, 3).forEach(food => cards.appendChild(createFoodCard(food)));
                const resultItem = document.createElement("li"); resultItem.className = "nm-chat-result-cards"; resultItem.appendChild(cards); list.appendChild(resultItem);
            }
        }
        status.textContent = "Menu information retrieved; verify ingredients with restaurant staff.";
    } catch (error) { const assistant = document.createElement("li"); assistant.className = "nm-chat-assistant"; assistant.textContent = error.message || "NutriMatch chat is unavailable. Try again."; list.appendChild(assistant); status.textContent = "Could not reach NutriMatch."; }
    list.lastElementChild?.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

document.getElementById("nutriMatchForm").addEventListener("submit", event => event.preventDefault());
previousButton.addEventListener("click", () => { if (stepIndex > 0) { stepIndex--; clearWizardError(); renderStep(); } });
nextButton.addEventListener("click", async () => {
    clearWizardError();
    if (stepIndex < STEPS.length - 1) { stepIndex++; renderStep(); stepContent.scrollIntoView({ behavior: "smooth", block: "nearest" }); }
    else await finishQuestionnaire();
});
skipButton.addEventListener("click", async () => {
    clearWizardError();
    if (stepIndex === 0) { stepIndex = STEPS.length - 1; renderStep(); }
    else if (stepIndex < STEPS.length - 1) { stepIndex++; renderStep(); }
    else await finishQuestionnaire();
});
document.getElementById("editPreferences").addEventListener("click", () => { results.hidden = true; wizard.hidden = false; stepIndex = 0; renderStep(); wizard.scrollIntoView({ behavior: "smooth", block: "start" }); });
document.getElementById("nmChatForm").addEventListener("submit", event => { event.preventDefault(); const input = document.getElementById("nmChatInput"); const message = input.value.trim(); if (!message) return; input.value = ""; submitChat(message); });
renderStep();
