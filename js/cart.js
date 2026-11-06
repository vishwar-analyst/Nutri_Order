function loadCart() {

    const cart =
        JSON.parse(
            localStorage.getItem("cart")
        ) || [];


    const container =
        document.getElementById(
            "cartContainer"
        );


    const totalBox =
        document.getElementById(
            "cartTotal"
        );


    container.innerHTML = "";


    if (cart.length === 0) {

        container.innerHTML = `
            <section class="cart-empty-state">
                <span aria-hidden="true">✳</span>
                <h2>Your table is waiting.</h2>
                <p>Your cart is empty for now. Browse the menu and find something you’ll love.</p>
                <a class="primary-btn" href="menu.html">Explore the menu <span aria-hidden="true">↗</span></a>
            </section>
        `;

        totalBox.innerHTML = "";

        return;
    }


    let total = 0;


    cart.forEach((item, index) => {

        const itemTotal =
            item.price * item.quantity;


        total += itemTotal;


        const div =
            document.createElement("div");


        div.className =
            "cart-item";


        div.innerHTML = `

            <div>

                <h3>
                    ${item.name}
                </h3>

                <p>
                    ₹${item.price}
                    ×
                    ${item.quantity}
                </p>

            </div>


            <div>

                <strong>
                    ₹${itemTotal}
                </strong>

                <button
                    onclick="removeItem(${index})">

                    Remove

                </button>

            </div>

        `;


        container.appendChild(div);

    });


    totalBox.innerHTML = `

        <h2>
            Total: ₹${total}
        </h2>

        <br>

        <button
            class="primary-btn"
            onclick="placeOrder()">

            Place Order

        </button>

    `;

}

const API_BASE_URL = window.NUTRIORDER_API_BASE || `http://${window.location.hostname}:5000`;


function removeItem(index) {

    let cart =
        JSON.parse(
            localStorage.getItem("cart")
        ) || [];


    cart.splice(index, 1);


    localStorage.setItem(
        "cart",
        JSON.stringify(cart)
    );


    loadCart();

}


async function placeOrder() {

    const user =
        JSON.parse(
            localStorage.getItem("user")
        );


    if (!user) {

        alert(
            "Please login before placing an order."
        );

        window.location.href =
            "login.html";

        return;
    }


    const cart =
        JSON.parse(
            localStorage.getItem("cart")
        ) || [];


    if (cart.length === 0) {

        alert("Your cart is empty.");

        return;
    }


    try {

        const response = await fetch(
            `${API_BASE_URL}/api/orders`,
            {
                method: "POST",
                credentials: "include",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    customer_id: user.id,

                    items: cart

                })

            }
        );


        const data =
            await response.json();


        if (!data.success) {

            alert(data.message);

            return;

        }


        localStorage.removeItem("cart");


        localStorage.setItem(
            "lastOrder",
            JSON.stringify(data)
        );


        window.location.href =
            "orders.html";

    } catch (error) {

        console.error(error);

        alert(
            "Could not place order."
        );

    }

}


loadCart();