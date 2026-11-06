const API_BASE_URL = window.NUTRIORDER_API_BASE || `http://${window.location.hostname}:5000`;
const customerName = document.getElementById("customerName");
const recentOrders = document.getElementById("recentOrders");
const currentUser = (() => {
    try {
        return JSON.parse(localStorage.getItem("user"));
    } catch {
        return null;
    }
})();

let verifiedUser = null;
verifyCustomerSession();

document.getElementById("logoutButton").addEventListener("click", async () => {
    try {
        await fetch(`${API_BASE_URL}/api/logout`, { method: "POST", credentials: "include" });
    } finally {
        localStorage.removeItem("user");
        window.location.assign("login.html");
    }
});

async function verifyCustomerSession() {
    if (!currentUser || currentUser.role !== "customer") {
        window.location.replace("login.html");
        return;
    }
    try {
        const response = await fetch(`${API_BASE_URL}/api/me`, { credentials: "include" });
        if (!response.ok) throw new Error("Session expired");
        const data = await response.json();
        if (!data.success || data.user.role !== "customer") throw new Error("Customer session required");
        verifiedUser = data.user;
        localStorage.setItem("user", JSON.stringify(verifiedUser));
        customerName.textContent = verifiedUser.full_name || verifiedUser.username || "food lover";
        loadRecentOrders();
    } catch {
        localStorage.removeItem("user");
        window.location.replace("login.html");
    }
}

async function loadRecentOrders() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/orders/customer/${encodeURIComponent(verifiedUser.id)}`, { credentials: "include" });
        if (!response.ok) throw new Error("Orders could not be loaded.");
        const orders = await response.json();
        renderRecentOrders(Array.isArray(orders) ? orders.slice(0, 3) : []);
    } catch (error) {
        console.error("Could not load customer orders:", error);
        recentOrders.replaceChildren();
        const message = document.createElement("p");
        message.className = "dashboard-empty";
        message.textContent = "Your dashboard is ready, but recent orders are unavailable. Check that the Flask backend is running.";
        recentOrders.appendChild(message);
    }
}

function renderRecentOrders(orders) {
    recentOrders.replaceChildren();
    if (orders.length === 0) {
        const empty = document.createElement("div");
        empty.className = "dashboard-empty";
        empty.innerHTML = "<span aria-hidden=\"true\">📦</span><strong>No orders yet</strong><p>Your placed orders will appear here.</p><a href=\"menu.html\">Find your first favourite →</a>";
        recentOrders.appendChild(empty);
        return;
    }

    orders.forEach(order => {
        const card = document.createElement("article");
        card.className = "recent-order-card";

        const heading = document.createElement("div");
        heading.className = "recent-order-heading";
        const orderName = document.createElement("strong");
        orderName.textContent = order.order_id || "Order";
        const status = document.createElement("span");
        status.className = "order-status-pill";
        status.textContent = order.status || "Pending";
        heading.append(orderName, status);

        const detail = document.createElement("p");
        const items = Array.isArray(order.items) ? order.items : [];
        detail.textContent = items.map(item => `${item.name} × ${item.quantity}`).join(" · ") || "Order details";

        const total = document.createElement("strong");
        const amount = Number(order.total);
        total.textContent = Number.isFinite(amount) ? `₹${amount.toFixed(2)}` : "Total unavailable";

        card.append(heading, detail, total);
        recentOrders.appendChild(card);
    });
}
