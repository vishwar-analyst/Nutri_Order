const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const chatMessages = document.getElementById("chatMessages");
const chatStatus = document.getElementById("chatStatus");
const sendButton = document.getElementById("sendButton");
const CHAT_API_URL = `${window.NUTRIORDER_API_BASE || `http://${window.location.hostname}:5000`}/api/chat`;

const STATUS_LABELS = {
	generally_suitable: "Generally suitable",
	portion_control: "Suitable with portion awareness",
	preparation_matters: "Preparation matters",
	check_ingredients: "Check ingredients",
	limited_information: "Limited information",
	seek_professional_advice: "Seek professional advice"
};

function appendText(parent, tag, className, text) {
	const element = document.createElement(tag);
	if (className) element.className = className;
	element.textContent = text;
	parent.appendChild(element);
	return element;
}

function renderList(parent, title, values, emptyText = "Not available") {
	const section = document.createElement("section");
	section.className = "analysis-section";
	appendText(section, "h3", "analysis-subtitle", title);
	if (!values || values.length === 0) {
		appendText(section, "p", "analysis-muted", emptyText);
	} else {
		const list = document.createElement("ul");
		values.forEach(value => appendText(list, "li", "", typeof value === "string" ? value : JSON.stringify(value)));
		section.appendChild(list);
	}
	return section;
}

function renderHealthAnalysis(analysis, sources = [], mode = "") {
	const item = document.createElement("li");
	item.className = "chat-message assistant-message analysis-message";
	const card = document.createElement("article");
	card.className = "health-analysis-card";
	card.setAttribute("aria-label", `Health analysis for ${analysis.food_name || "menu food"}`);

	const header = document.createElement("header");
	header.className = "analysis-food-header";
	const image = document.createElement("img");
	image.className = "analysis-food-image";
	image.src = analysis.image_url || "/images/food-fallback.svg";
	image.alt = analysis.image_url ? `${analysis.food_name || "Food"} dish` : `${analysis.food_name || "Food"}; exact dish photo not verified`;
	image.loading = "lazy";
	image.onerror = () => { image.onerror = null; image.src = "/images/food-fallback.svg"; };
	header.appendChild(image);
	const headingGroup = document.createElement("div");
	appendText(headingGroup, "p", "analysis-kicker", "NUTRIORDER · FOOD INSIGHT");
	appendText(headingGroup, "h2", "analysis-food-name", analysis.food_name || "Food health analysis");
	const meta = [analysis.tamil_name, analysis.food_category, analysis.cuisine, analysis.serving_size].filter(Boolean).join(" · ");
	appendText(headingGroup, "p", "analysis-muted", meta || "Serving size not available");
	header.appendChild(headingGroup);
	card.appendChild(header);

	const assessmentGrid = document.createElement("div");
	assessmentGrid.className = "assessment-grid";
	(analysis.health_assessments || []).forEach(assessment => {
		const assessmentCard = document.createElement("section");
		assessmentCard.className = `assessment-card status-${assessment.status || "limited_information"}`;
		appendText(assessmentCard, "p", "assessment-label", assessment.condition || "Health consideration");
		appendText(assessmentCard, "span", "assessment-status", STATUS_LABELS[assessment.status] || "Limited information");
		appendText(assessmentCard, "p", "assessment-summary", assessment.summary || "Information is limited.");
		(assessment.reason || []).forEach(reason => appendText(assessmentCard, "p", "assessment-detail", reason));
		(assessment.considerations || []).forEach(note => appendText(assessmentCard, "p", "assessment-detail", `• ${note}`));
		assessmentGrid.appendChild(assessmentCard);
	});
	card.appendChild(assessmentGrid);

	const nutrition = analysis.nutrition || {};
	const nutritionSection = document.createElement("section");
	nutritionSection.className = "analysis-section";
	appendText(nutritionSection, "h3", "analysis-subtitle", "Nutrition snapshot");
	const nutritionGrid = document.createElement("div");
	nutritionGrid.className = "nutrition-grid";
	[
		["Calories", nutrition.calories, "kcal"],
		["Protein", nutrition.protein, "g"],
		["Carbohydrates", nutrition.carbohydrates, "g"],
		["Total fat", nutrition.fat, "g"],
		["Fibre", nutrition.fiber, "g"],
		["Sodium", nutrition.sodium, "mg"]
	].forEach(([label, value, unit]) => {
		const stat = document.createElement("div");
		stat.className = "nutrition-stat";
		appendText(stat, "span", "nutrition-label", label);
		appendText(stat, "strong", "nutrition-value", value === null || value === undefined ? "Not available" : `${value} ${unit}`);
		nutritionGrid.appendChild(stat);
	});
	nutritionSection.appendChild(nutritionGrid);
	appendText(nutritionSection, "p", "analysis-muted", `Data status: ${nutrition.status || "not recorded"}. Estimates are not verified measurements.`);
	card.appendChild(nutritionSection);

	if (analysis.ingredients?.length) card.appendChild(renderList(card, "Listed ingredients", analysis.ingredients));
	if (analysis.preparation_method) appendText(card, "p", "analysis-muted", `Preparation reference: ${analysis.preparation_method}`);
	if (analysis.dietary_type) appendText(card, "p", "analysis-muted", `Dietary type: ${analysis.dietary_type}${analysis.catalog_status === "reference_pending_restaurant_confirmation" ? " · not restaurant-verified" : ""}`);
	if (analysis.availability_status) appendText(card, "p", "analysis-muted", `Menu status: ${analysis.availability_status}`);
	if (analysis.allergens?.length) card.appendChild(renderList(card, "Potential allergen ingredients", analysis.allergens));
	if (analysis.warnings?.length) card.appendChild(renderList(card, "Important considerations", analysis.warnings));
	if (analysis.comparison_items?.length) {
		const comparison = document.createElement("section");
		comparison.className = "analysis-section";
		appendText(comparison, "h3", "analysis-subtitle", "Side-by-side menu facts");
		appendText(comparison, "p", "analysis-muted", "Menu comparison only—not a health ranking. Nutrition may be estimated; sodium and fibre are unavailable unless verified.");
		const comparisonGrid = document.createElement("div");
		comparisonGrid.className = "alternative-grid";
		analysis.comparison_items.forEach(food => {
			const comparisonCard = document.createElement("article");
			comparisonCard.className = "alternative-card";
			if (food.image_url) {
				const image = document.createElement("img");
				image.src = food.image_url;
				image.alt = "";
				image.loading = "lazy";
				image.onerror = () => image.remove();
				comparisonCard.appendChild(image);
			}
			appendText(comparisonCard, "h4", "", food.name || "Menu item");
			const facts = food.nutrition || {};
			appendText(comparisonCard, "p", "analysis-muted", `${facts.calories ?? "Not available"} kcal · ${facts.carbohydrates ?? "Not available"} g carbs`);
			appendText(comparisonCard, "p", "analysis-muted", `${facts.protein ?? "Not available"} g protein · ${facts.fat ?? "Not available"} g fat`);
			comparisonGrid.appendChild(comparisonCard);
		});
		comparison.appendChild(comparisonGrid);
		card.appendChild(comparison);
	}

	if (analysis.alternatives?.length) {
		const alternatives = document.createElement("section");
		alternatives.className = "analysis-section";
		appendText(alternatives, "h3", "analysis-subtitle", "From the current restaurant menu");
		const alternativeGrid = document.createElement("div");
		alternativeGrid.className = "alternative-grid";
		analysis.alternatives.forEach(alternative => {
			const alternativeCard = document.createElement("article");
			alternativeCard.className = "alternative-card";
			if (alternative.image_url) {
				const image = document.createElement("img");
				image.src = alternative.image_url;
				image.alt = "";
				image.loading = "lazy";
				image.onerror = () => image.remove();
				alternativeCard.appendChild(image);
			}
			appendText(alternativeCard, "h4", "", alternative.name || "Menu item");
			const facts = alternative.nutrition || {};
			appendText(alternativeCard, "p", "analysis-muted", `₹${alternative.price ?? "Not available"} · ${facts.calories ?? "Not available"} kcal · ${facts.protein ?? "Not available"} g protein`);
			appendText(alternativeCard, "p", "alternative-reason", alternative.reason || "Menu comparison only.");
			alternativeGrid.appendChild(alternativeCard);
		});
		alternatives.appendChild(alternativeGrid);
		card.appendChild(alternatives);
	}

	appendText(card, "p", "analysis-disclaimer", analysis.disclaimer || "General nutrition information only—not medical advice.");
	item.appendChild(card);
	if (sources.length) appendText(item, "p", "message-sources", `Sources: ${sources.map(source => source.label).join(" · ")}`);
	if (mode.startsWith("local_")) appendText(item, "p", "message-mode", "Source-based response · Gemini is not configured or available.");
	chatMessages.appendChild(item);
	item.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function addMessage(text, kind, sources = [], mode = "") {
	const item = document.createElement("li");
	item.className = `chat-message ${kind}-message`;

	const bubble = document.createElement("div");
	bubble.className = "message-bubble";
	bubble.textContent = text;
	item.appendChild(bubble);

	if (kind === "assistant" && sources.length > 0) {
		const sourceList = document.createElement("p");
		sourceList.className = "message-sources";
		sourceList.textContent = `Sources: ${sources.map(source => source.label).join(" · ")}`;
		item.appendChild(sourceList);
	}

	if (kind === "assistant" && mode.startsWith("local_")) {
		const modeNote = document.createElement("p");
		modeNote.className = "message-mode";
		modeNote.textContent = "Source-based response · Gemini is not configured or unavailable.";
		item.appendChild(modeNote);
	}

	chatMessages.appendChild(item);
	item.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

async function submitQuestion(question) {
	const trimmedQuestion = question.trim();
	if (!trimmedQuestion) return;

	addMessage(trimmedQuestion, "user");
	chatInput.value = "";
	chatInput.disabled = true;
	sendButton.disabled = true;
	chatStatus.textContent = "Searching NutriOrder sources…";

	try {
		const response = await fetch(CHAT_API_URL, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ message: trimmedQuestion })
		});
		const data = await response.json();
		if (!response.ok || !data.success) {
			throw new Error(data.message || "NutriBot could not answer right now.");
		}
		if (data.health_analysis?.response_type === "health_suitability") {
			renderHealthAnalysis(data.health_analysis, data.sources || [], data.mode || "");
		} else if (data.food_information?.response_type === "food_information") {
			renderHealthAnalysis(data.food_information, data.sources || [], data.mode || "");
		} else {
			addMessage(data.answer, "assistant", data.sources || [], data.mode || "");
		}
		chatStatus.textContent = data.grounded
			? "Answer retrieved from available sources."
			: "No supporting source was found.";
	} catch (error) {
		addMessage(error.message || "Could not connect to NutriBot. Check that the Flask server is running.", "assistant");
		chatStatus.textContent = "Connection or service error.";
	} finally {
		chatInput.disabled = false;
		sendButton.disabled = false;
		chatInput.focus();
	}
}

chatForm.addEventListener("submit", event => {
	event.preventDefault();
	submitQuestion(chatInput.value);
});

document.querySelectorAll("[data-prompt]").forEach(button => {
	button.addEventListener("click", () => submitQuestion(button.dataset.prompt));
});
