const API_BASE_URL = window.NUTRIORDER_API_BASE || `http://${window.location.hostname}:5000`;

async function loadBakeryOrders() {
    const container = document.getElementById("ordersContainer");
    try {
        const response = await fetch(`${API_BASE_URL}/api/bakery/orders`, {
            credentials: "include"
        });
        if (!response.ok) throw new Error("Could not load customer orders.");

        const orders = await response.json();
        container.replaceChildren();
        if (!Array.isArray(orders) || orders.length === 0) {
            const empty = document.createElement("p");
            empty.textContent = "No customer orders yet.";
            container.appendChild(empty);
            return;
        }

        orders.forEach(order => {
            const card = document.createElement("article");
            card.className = "bakery-order";

            const heading = document.createElement("div");
            heading.className = "bakery-order-heading";
            const orderId = document.createElement("h2");
            orderId.textContent = order.order_id;
            const created = document.createElement("time");
            created.className = "bakery-order-date";
            created.textContent = order.created_at || "Date unavailable";
            heading.append(orderId, created);

            const customer = order.customer || {};
            const customerPanel = document.createElement("section");
            customerPanel.className = "bakery-order-customer";
            const customerLabel = document.createElement("p");
            customerLabel.className = "bakery-order-label";
            customerLabel.textContent = "CUSTOMER";
            const customerName = document.createElement("h3");
            customerName.textContent = customer.name || "Customer details unavailable";
            customerPanel.append(customerLabel, customerName);

            const appendContact = (label, value, scheme) => {
                const row = document.createElement("p");
                const labelNode = document.createElement("span");
                labelNode.textContent = `${label}: `;
                row.appendChild(labelNode);
                if (value && scheme) {
                    const link = document.createElement("a");
                    link.href = `${scheme}:${value}`;
                    link.textContent = value;
                    row.appendChild(link);
                } else {
                    const valueNode = document.createElement("span");
                    valueNode.textContent = value || "Not provided";
                    row.appendChild(valueNode);
                }
                customerPanel.appendChild(row);
            };
            appendContact("Email", customer.email, "mailto");
            appendContact("Phone", customer.phone, "tel");

            const itemsList = document.createElement("ul");
            itemsList.className = "bakery-order-items";
            (Array.isArray(order.items) ? order.items : []).forEach(item => {
                const row = document.createElement("li");
                const name = document.createElement("span");
                name.textContent = `${item.name} × ${item.quantity}`;
                const price = document.createElement("strong");
                price.textContent = `₹${Number(item.price || 0).toFixed(0)}`;
                row.append(name, price);
                itemsList.appendChild(row);
            });

            const total = document.createElement("p");
            total.className = "bakery-order-total";
            total.textContent = `Order total: ₹${Number(order.total || 0).toFixed(0)}`;

            const statusRow = document.createElement("label");
            statusRow.className = "bakery-order-status";
            statusRow.textContent = "Update status";
            const statusSelect = document.createElement("select");
            statusSelect.setAttribute("aria-label", `Update status for ${order.order_id}`);
            const statuses = ["Pending", "Accepted", "Preparing", "Ready", "Completed"];
            statuses.forEach(status => {
                const option = document.createElement("option");
                option.value = status;
                option.textContent = status;
                option.selected = status === order.status;
                statusSelect.appendChild(option);
            });
            statusRow.appendChild(statusSelect);
            statusSelect.addEventListener("change", () => {
                updateStatus(order.order_id, statusSelect.value, statusSelect, order.status);
            });

            card.append(heading, customerPanel, itemsList, total, statusRow);
            container.appendChild(card);
        });
    } catch (error) {
        console.error(error);
        container.replaceChildren();
        const message = document.createElement("p");
        message.textContent = "Unable to load orders. Please refresh and try again.";
        container.appendChild(message);
    }
}


async function updateStatus(orderId, status, select, previousStatus) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/orders/${encodeURIComponent(orderId)}/status`, {
            method: "PUT",
            credentials: "include",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status })
        });
        if (!response.ok) throw new Error("Status update failed.");
        loadBakeryOrders();
    } catch (error) {
        console.error(error);
        if (select) select.value = previousStatus;
        alert("Could not update order status. Please try again.");
    }
}


loadBakeryOrders();