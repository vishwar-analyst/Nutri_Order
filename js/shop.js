function loadDashboard() {

    const orders =
        JSON.parse(
            localStorage.getItem("orders")
        ) || [];


    let totalOrders = orders.length;

    let pendingOrders = 0;

    let foodsSold = 0;

    let totalSales = 0;


    orders.forEach(order => {

        if (order.status === "Pending") {

            pendingOrders++;

        }


        order.items.forEach(item => {

            foodsSold += item.quantity;

        });


        totalSales += order.total;

    });


    document.getElementById("totalOrders")
        .textContent = totalOrders;


    document.getElementById("pendingOrders")
        .textContent = pendingOrders;


    document.getElementById("foodsSold")
        .textContent = foodsSold;


    document.getElementById("totalSales")
        .textContent = "₹" + totalSales;


    displayRecentOrders(orders);
}


function displayRecentOrders(orders) {

    const container =
        document.getElementById("recentOrders");


    container.innerHTML = "";


    if (orders.length === 0) {

        container.innerHTML = `

            <div class="no-orders">

                <div>
                    📦
                </div>

                <h3>
                    No orders yet
                </h3>

                <p>
                    New customer orders will
                    appear here.
                </p>

            </div>

        `;

        return;
    }


    const recentOrders =
        [...orders].reverse().slice(0, 5);


    recentOrders.forEach(order => {

        let items = "";

        order.items.forEach(item => {

            items +=
                `${item.name} × ${item.quantity}, `;

        });


        const orderCard =
            document.createElement("div");


        orderCard.className =
            "bakery-order-card";


        orderCard.innerHTML = `

            <div class="bakery-order-info">

                <p class="order-label">
                    ORDER ID
                </p>

                <h3>
                    ${order.orderId}
                </h3>

                <p>
                    ${items}
                </p>

                <small>
                    ${order.date}
                </small>

            </div>


            <div class="bakery-order-right">

                <strong>
                    ₹${order.total}
                </strong>

                <span class="order-status">
                    ${order.status}
                </span>

            </div>

        `;


        container.appendChild(orderCard);

    });

}


loadDashboard();
function displayBakeryOrders(orderList = null) {

    const container =
        document.getElementById("bakeryOrders");

    if (!container) {
        return;
    }

    const orders =
        orderList ||
        JSON.parse(localStorage.getItem("orders")) ||
        [];

    container.innerHTML = "";

    if (orders.length === 0) {

        container.innerHTML = `
            <div class="no-orders">
                <div>📦</div>
                <h3>No orders found</h3>
                <p>Customer orders will appear here.</p>
            </div>
        `;

        return;
    }

    [...orders].reverse().forEach(order => {

        let itemsHTML = "";

        order.items.forEach(item => {

            itemsHTML += `
                <div class="bakery-item-row">
                    <span>
                        ${item.name} × ${item.quantity}
                    </span>

                    <strong>
                        ₹${item.price * item.quantity}
                    </strong>
                </div>
            `;

        });

        const card =
            document.createElement("div");

        card.className =
            "bakery-full-order";

        card.innerHTML = `

            <div class="full-order-header">

                <div>

                    <p class="order-label">
                        ORDER ID
                    </p>

                    <h2>
                        ${order.orderId}
                    </h2>

                    <small>
                        ${order.date}
                    </small>

                </div>

                <span class="order-status">
                    ${order.status}
                </span>

            </div>


            <div class="bakery-items">

                <h3>
                    Ordered Items
                </h3>

                ${itemsHTML}

            </div>


            <div class="full-order-footer">

                <strong>
                    Total: ₹${order.total}
                </strong>

                <div class="status-buttons">

                    <button
                        onclick="updateOrderStatus('${order.orderId}', 'Accepted')"
                    >
                        Accept
                    </button>

                    <button
                        onclick="updateOrderStatus('${order.orderId}', 'Preparing')"
                    >
                        Preparing
                    </button>

                    <button
                        onclick="updateOrderStatus('${order.orderId}', 'Ready')"
                    >
                        Ready
                    </button>

                    <button
                        onclick="updateOrderStatus('${order.orderId}', 'Completed')"
                    >
                        Completed
                    </button>

                </div>

            </div>

        `;

        container.appendChild(card);

    });
}


function searchOrder() {

    const search =
        document
        .getElementById("orderSearch")
        .value
        .trim()
        .toUpperCase();

    const orders =
        JSON.parse(
            localStorage.getItem("orders")
        ) || [];

    if (search === "") {

        displayBakeryOrders();

        return;
    }

    const result =
        orders.filter(order =>
            order.orderId
            .toUpperCase()
            .includes(search)
        );

    displayBakeryOrders(result);
}


function updateOrderStatus(orderId, newStatus) {

    let orders =
        JSON.parse(
            localStorage.getItem("orders")
        ) || [];

    orders = orders.map(order => {

        if (order.orderId === orderId) {

            order.status = newStatus;

        }

        return order;

    });

    localStorage.setItem(
        "orders",
        JSON.stringify(orders)
    );

    displayBakeryOrders();

    alert(
        "Order " +
        orderId +
        " updated to " +
        newStatus
    );
}


/*
   Automatically load bakery orders
   when orders.html is opened.
*/

if (document.getElementById("bakeryOrders")) {

    displayBakeryOrders();

}