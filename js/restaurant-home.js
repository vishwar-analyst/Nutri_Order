const homeApi = window.NUTRIORDER_API_BASE || `http://${window.location.hostname}:5000`;
const featuredFoods = document.getElementById("featuredFoods");
const featuredImages = {
    "Chettinad Chicken Biryani": "/images/chettinad-chicken-biryani.jpg",
    "Ghee Roast Dosa": "/images/ghee-roast-dosa.png",
    "Traditional Banana Leaf Meals": "/images/banana-leaf-meals.jpg",
    "Parotta with Salna": "/images/parotta-with-salna.jpg",
    "Chicken 65": "/images/chicken-65.jpg",
    "Ven Pongal": "/images/ven-pongal.jpg"
};

const navToggle = document.getElementById("navToggle");
const mainNav = document.getElementById("mainNav");
const siteHeader = document.getElementById("siteHeader");

navToggle.addEventListener("click", () => {
    const expanded = navToggle.getAttribute("aria-expanded") === "true";
    navToggle.setAttribute("aria-expanded", String(!expanded));
    navToggle.setAttribute("aria-label", expanded ? "Open navigation" : "Close navigation");
    mainNav.classList.toggle("is-open", !expanded);
});

mainNav.querySelectorAll("a").forEach(link => link.addEventListener("click", () => {
    navToggle.setAttribute("aria-expanded", "false");
    mainNav.classList.remove("is-open");
}));

window.addEventListener("scroll", () => {
    siteHeader.classList.toggle("is-scrolled", window.scrollY > 24);
}, { passive: true });

const revealObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            revealObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.12 });
document.querySelectorAll("[data-reveal]").forEach(element => revealObserver.observe(element));

function formatPrice(price) {
    const amount = Number(price);
    return Number.isFinite(amount) ? `₹${amount.toFixed(0)}` : "Price unavailable";
}

function renderDishes(foods) {
    featuredFoods.replaceChildren();
    const picks = foods.filter(food => featuredImages[food.name]).slice(0, 4);
    if (!picks.length) {
        const message = document.createElement("p");
        message.className = "home-menu-status";
        message.textContent = "Our featured menu is temporarily unavailable. Please visit the full menu.";
        featuredFoods.appendChild(message);
        return;
    }

    picks.forEach((food, index) => {
        const card = document.createElement("article");
        card.className = "dish-card";
        card.dataset.reveal = "";
        card.style.setProperty("--card-order", index);

        const media = document.createElement("div");
        media.className = "dish-media";
        const image = document.createElement("img");
        const localImage = typeof food.image_url === "string" && food.image_url.startsWith("/images/");
        image.src = localImage ? food.image_url : featuredImages[food.name] || "/images/food-fallback.svg";
        image.alt = `${food.name}, representative food photo; not restaurant-verified`;
        image.loading = "lazy";
        image.onerror = () => { image.onerror = null; image.src = "/images/food-fallback.svg"; };
        media.appendChild(image);

        const tag = document.createElement("span");
        tag.className = `dish-tag ${food.food_type === "non-vegetarian" ? "non-veg" : "veg"}`;
        tag.textContent = food.food_type === "non-vegetarian" ? "NON-VEGETARIAN" : "VEGETARIAN";
        media.appendChild(tag);

        const details = document.createElement("div");
        details.className = "dish-copy";
        const category = document.createElement("p");
        category.className = "dish-category";
        category.textContent = food.category || "Tamil Kitchen";
        const title = document.createElement("h3");
        title.textContent = food.name;
        const description = document.createElement("p");
        description.className = "dish-description";
        description.textContent = food.description || "A much-loved Tamil Nadu favourite, prepared fresh.";
        const meta = document.createElement("div");
        meta.className = "dish-meta";
        const rating = document.createElement("span");
        rating.textContent = `★ ${Number(food.rating || 0).toFixed(1)}`;
        const calories = document.createElement("span");
        calories.textContent = food.calories == null ? "Calories not listed" : `~${food.calories} kcal`;
        meta.append(rating, calories);
        const footer = document.createElement("div");
        footer.className = "dish-footer";
        const price = document.createElement("strong");
        price.textContent = formatPrice(food.price);
        const addButton = document.createElement("button");
        addButton.className = "dish-add";
        addButton.type = "button";
        addButton.textContent = "+ Add";
        addButton.addEventListener("click", () => addFoodToCart(food, addButton));
        footer.append(price, addButton);
        details.append(category, title, description, meta, footer);
        card.append(media, details);
        featuredFoods.appendChild(card);
        requestAnimationFrame(() => card.classList.add("is-visible"));
    });
}

function addFoodToCart(food, button) {
    let cart;
    try { cart = JSON.parse(localStorage.getItem("cart")) || []; } catch { cart = []; }
    const existing = cart.find(item => Number(item.id) === Number(food.id));
    if (existing) existing.quantity += 1;
    else cart.push({ id: food.id, name: food.name, price: Number(food.price), quantity: 1 });
    localStorage.setItem("cart", JSON.stringify(cart));
    button.textContent = "Added ✓";
    window.setTimeout(() => { button.textContent = "+ Add"; }, 1200);
}

async function loadFeaturedFoods() {
    try {
        const response = await fetch(`${homeApi}/api/foods`);
        if (!response.ok) throw new Error("Menu request failed");
        const foods = await response.json();
        renderDishes(foods);
    } catch (error) {
        console.error("Unable to load featured restaurant dishes:", error);
        featuredFoods.replaceChildren();
        const message = document.createElement("p");
        message.className = "home-menu-status";
        message.textContent = "Start the Flask backend to load today's featured dishes.";
        featuredFoods.appendChild(message);
    }
}

loadFeaturedFoods();
