const menuContainer = document.getElementById("menuContainer");
const resultCount = document.getElementById("menuResultCount");
const API_BASE_URL = window.NUTRIORDER_API_BASE || `http://${window.location.hostname}:5000`;
let allFoods = [];
let selectedCategory = "all";
let selectedDiet = "all";
let searchQuery = "";
let selectedBudget = "all";

async function loadFoods() {
    menuContainer.setAttribute("aria-busy", "true");
    try {
        const response = await fetch(`${API_BASE_URL}/api/foods`);
        if (!response.ok) throw new Error("Could not load the restaurant menu.");
        allFoods = await response.json();
        renderMenu();
    } catch (error) {
        console.error(error);
        menuContainer.replaceChildren();
        const message = document.createElement("p");
        message.className = "menu-empty-state";
        message.textContent = "Unable to load today's dishes. Please check that the Flask backend is running.";
        menuContainer.appendChild(message);
        resultCount.textContent = "Menu temporarily unavailable";
    } finally {
        menuContainer.setAttribute("aria-busy", "false");
    }
}

function renderMenu() {
    const sortMode = document.getElementById("foodSort").value;
    const query = searchQuery.toLowerCase();
    let foods = allFoods.filter(food => {
        const matchesCategory = selectedCategory === "all" || food.category === selectedCategory || food.meal_type === selectedCategory;
        const matchesDiet = selectedDiet === "all" || food.food_type === selectedDiet;
        const searchable = `${food.name} ${food.tamil_name || ""} ${food.description || ""} ${food.ingredients || ""} ${food.category || ""} ${food.cuisine || ""}`.toLowerCase();
        const price = food.price == null ? null : Number(food.price);
        const matchesBudget = selectedBudget === "all" || (price !== null && Number.isFinite(price) && (
            selectedBudget === "under-50" ? price < 50 :
            selectedBudget === "50-100" ? price >= 50 && price < 100 :
            selectedBudget === "100-200" ? price >= 100 && price < 200 :
            selectedBudget === "200-300" ? price >= 200 && price <= 300 : price > 300
        ));
        return matchesCategory && matchesDiet && matchesBudget && searchable.includes(query);
    });

    if (sortMode === "price-low") foods.sort((a, b) => (a.price == null) - (b.price == null) || Number(a.price || 0) - Number(b.price || 0));
    if (sortMode === "price-high") foods.sort((a, b) => (a.price == null) - (b.price == null) || Number(b.price || 0) - Number(a.price || 0));
    if (sortMode === "popular") foods.sort((a, b) => Number(b.rating || 0) - Number(a.rating || 0));

    menuContainer.replaceChildren();
    resultCount.textContent = `${foods.length} ${foods.length === 1 ? "dish" : "dishes"} to savour`;
    if (!foods.length) {
        const empty = document.createElement("p");
        empty.className = "menu-empty-state";
        empty.textContent = "No dishes match those filters. Try another category or search.";
        menuContainer.appendChild(empty);
        return;
    }
    foods.forEach((food, index) => menuContainer.appendChild(createFoodCard(food, index)));
}

function createFoodCard(food, index) {
    const card = document.createElement("article");
    card.className = "restaurant-food-card";
    card.style.setProperty("--card-order", index);

    const imageWrap = document.createElement("div");
    imageWrap.className = "restaurant-food-image";
    const image = document.createElement("img");
    const localImage = typeof food.image_url === "string" && food.image_url.startsWith("/images/");
    image.src = localImage ? food.image_url : "/images/food-fallback.svg";
    image.alt = localImage ? `${food.name} — representative food photo; not restaurant-verified` : `${food.name} — exact dish photograph not verified`;
    image.loading = "lazy";
    image.onerror = () => { image.onerror = null; image.src = "/images/food-fallback.svg"; };
    imageWrap.appendChild(image);

    const badge = document.createElement("span");
    badge.className = `dish-tag ${food.food_type === "non-vegetarian" ? "non-veg" : "veg"}`;
    badge.textContent = food.food_type === "non-vegetarian" ? "NON-VEGETARIAN" : food.food_type === "egg" ? "EGG" : "VEGETARIAN · VERIFY RECIPE";
    imageWrap.appendChild(badge);

    const body = document.createElement("div");
    body.className = "restaurant-food-copy";
    const category = document.createElement("p");
    category.className = "dish-category";
    category.textContent = food.category || food.meal_type || "Tamil Kitchen";
    const title = document.createElement("h2");
    title.textContent = food.name;
    if (food.tamil_name) {
        const tamil = document.createElement("p");
        tamil.className = "dish-tamil-name";
        tamil.lang = "ta";
        tamil.textContent = food.tamil_name;
        body.appendChild(tamil);
    }
    const description = document.createElement("p");
    description.className = "dish-description";
    description.textContent = food.description || "Prepared fresh with care in our Tamil kitchen.";
    const stats = document.createElement("div");
    stats.className = "menu-food-stats";
    const rating = document.createElement("span");
    rating.textContent = `★ ${Number(food.rating || 0).toFixed(1)}`;
    const calories = document.createElement("span");
    calories.textContent = food.calories == null ? "Calories not available" : `~${food.calories} kcal · ${food.nutrition_status === "verified" ? "verified" : "estimate"}`;
    stats.append(rating, calories);
    const ingredients = document.createElement("p");
    ingredients.className = "menu-ingredients";
    ingredients.textContent = food.ingredients ? `Common recipe ingredients: ${food.ingredients}` : "Recipe ingredients are not confirmed; please ask the restaurant.";
    const bottom = document.createElement("div");
    bottom.className = "restaurant-food-bottom";
    const price = document.createElement("strong");
    price.textContent = food.price == null ? "Price not set" : `₹${Number(food.price).toFixed(0)}`;
    const details = document.createElement("button");
    details.className = "dish-add dish-detail-trigger";
    details.type = "button";
    details.textContent = "View details";
    details.addEventListener("click", () => showMenuFoodDetail(food));
    const isPending = food.catalog_status === "reference_pending_restaurant_confirmation" || food.availability_status === "pending_confirmation";
    if (isPending) {
        const pending = document.createElement("p");
        pending.className = "menu-pending-note";
        pending.textContent = "Dish reference · restaurant offering, price, preparation and availability need confirmation.";
        body.appendChild(pending);
    }
    const add = document.createElement("button");
    add.className = "dish-add";
    add.type = "button";
    add.textContent = "Add to cart +";
    add.disabled = isPending || food.price == null || ["unavailable", "out_of_stock", "disabled"].includes(String(food.availability_status || "").toLowerCase());
    if (isPending) add.title = "Not orderable until confirmed by the restaurant";
    add.addEventListener("click", () => addToCart(food, add));
    bottom.append(price, details, add);
    body.append(category, title, description, stats, ingredients, bottom);
    card.append(imageWrap, body);
    return card;
}

function addToCart(food, button) {
    let cart;
    try { cart = JSON.parse(localStorage.getItem("cart")) || []; } catch { cart = []; }
    const existing = cart.find(item => Number(item.id) === Number(food.id));
    if (existing) existing.quantity += 1;
    else cart.push({ id: food.id, name: food.name, price: Number(food.price), quantity: 1 });
    localStorage.setItem("cart", JSON.stringify(cart));
    const originalText = button.textContent;
    button.textContent = "Added ✓";
    window.setTimeout(() => { button.textContent = originalText; }, 1200);
}

function showMenuFoodDetail(food) {
    const dialog = document.getElementById("menuFoodDialog");
    const content = document.getElementById("menuFoodDetail");
    content.replaceChildren();
    const image = document.createElement("img");
    image.className = "nm-detail-image";
    const localImage = typeof food.image_url === "string" && food.image_url.startsWith("/images/");
    image.src = localImage ? food.image_url : "/images/food-fallback.svg";
    image.alt = localImage ? `${food.name} representative photo; not restaurant-verified` : `${food.name}; exact dish photo not verified`;
    image.onerror = () => { image.onerror = null; image.src = "/images/food-fallback.svg"; };
    const title = document.createElement("h2"); title.id = "menuDetailName"; title.textContent = food.name;
    const tamil = document.createElement("p"); tamil.lang = "ta"; tamil.textContent = food.tamil_name || "Tamil name not recorded";
    const intro = document.createElement("p"); intro.textContent = food.description || "Traditional dish reference; restaurant recipe details are not confirmed.";
    const details = document.createElement("div"); details.className = "nm-detail-grid";
    [["Category", food.category], ["Cuisine", food.cuisine], ["Dietary type", food.food_type], ["Price", food.price == null ? null : `₹${food.price}`], ["Serving size", food.serving_size], ["Calories", food.calories == null ? null : `${food.calories} kcal`], ["Protein", food.protein == null ? null : `${food.protein} g`], ["Carbohydrates", food.carbs == null ? null : `${food.carbs} g`], ["Fat", food.fat == null ? null : `${food.fat} g`], ["Fibre", food.fiber == null ? null : `${food.fiber} g`], ["Sodium", food.sodium == null ? null : `${food.sodium} mg`], ["Nutrition source", food.nutrition_source], ["Data status", food.nutrition_status], ["Availability", food.availability_status]].forEach(([label, value]) => { const box = document.createElement("div"); const small = document.createElement("small"); small.textContent = label; const strong = document.createElement("strong"); strong.textContent = value || "Not available"; box.append(small, strong); details.appendChild(box); });
    const ingredients = document.createElement("p"); ingredients.textContent = `Common recipe ingredients (not restaurant-verified): ${food.ingredients || "not available"}`;
    const preparation = document.createElement("p"); preparation.textContent = `Preparation reference: ${food.preparation_method || food.cooking_method || "not available"}`;
    const allergens = document.createElement("p"); allergens.textContent = `Allergens: ${food.allergens || "not recorded; confirm ingredients and cross-contact with the restaurant"}`;
    content.append(image, title, tamil, intro, details, ingredients, preparation, allergens);
    if (typeof dialog.showModal === "function") dialog.showModal();
}

document.getElementById("foodSearch").addEventListener("input", event => {
    searchQuery = event.target.value.trim();
    renderMenu();
});

document.getElementById("foodSort").addEventListener("change", renderMenu);
document.getElementById("foodBudget").addEventListener("change", event => { selectedBudget = event.target.value; renderMenu(); });
document.querySelectorAll("[data-category]").forEach(button => button.addEventListener("click", () => {
    selectedCategory = button.dataset.category;
    document.querySelectorAll("[data-category]").forEach(item => {
        const active = item === button;
        item.classList.toggle("active", active);
        item.setAttribute("aria-pressed", String(active));
    });
    renderMenu();
}));

document.querySelectorAll("[data-diet]").forEach(button => button.addEventListener("click", () => {
    const diet = button.dataset.diet;
    selectedDiet = selectedDiet === diet ? "all" : diet;
    document.querySelectorAll("[data-diet]").forEach(item => {
        const active = item.dataset.diet === selectedDiet;
        item.classList.toggle("active", active);
        item.setAttribute("aria-pressed", String(active));
    });
    renderMenu();
}));

const menuToggle = document.getElementById("menuNavToggle");
const menuNav = document.getElementById("menuNav");
menuToggle.addEventListener("click", () => {
    const expanded = menuToggle.getAttribute("aria-expanded") === "true";
    menuToggle.setAttribute("aria-expanded", String(!expanded));
    menuNav.classList.toggle("is-open", !expanded);
});
menuNav.querySelectorAll("a").forEach(link => link.addEventListener("click", () => {
    menuToggle.setAttribute("aria-expanded", "false");
    menuNav.classList.remove("is-open");
}));

loadFoods();