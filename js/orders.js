const API_BASE_URL = window.NUTRIORDER_API_BASE || `http://${window.location.hostname}:5000`;

async function loadOrders() {

    const user =
        JSON.parse(
            localStorage.getItem("user")
        );


    const container =
        document.getElementById(
            "ordersContainer"
        );


    if (!user) {

        container.innerHTML =
            `<p>Please login to view orders.</p>`;

        return;
    }


    try {

        const response = await fetch(
            `${API_BASE_URL}/api/orders/customer/${user.id}`,
            { credentials: "include" }
        );


        const orders =
            await response.json();


        if (orders.length === 0) {

            container.innerHTML =
                "<p>No orders yet.</p>";

            return;
        }


        container.innerHTML = "";


        orders.forEach(order => {

            const card =
                document.createElement("div");


            card.className =
                "order-card";


            let itemsHTML = "";


            order.items.forEach(item => {

                itemsHTML += `
                    <p>
                        ${item.name}
                        × ${item.quantity}
                        — ₹${item.price}
                    </p>
                `;

            });


            card.innerHTML = `

                <h2>
                    Order ID:
                    ${order.order_id}
                </h2>

                <br>

                ${itemsHTML}

                <br>

                <p>
                    <strong>
                        Total:
                        ₹${order.total}
                    </strong>
                </p>

                <br>

                <span class="status">
                    ${order.status}
                </span>

                <br><br>

                <small>
                    ${order.created_at}
                </small>

            `;


            container.appendChild(card);

        });


    } catch (error) {

        console.error(error);

        container.innerHTML =
            "<p>Unable to load orders.</p>";

    }

}


loadOrders();