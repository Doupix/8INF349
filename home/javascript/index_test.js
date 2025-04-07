const productList = document.getElementById("product-list");
const cartPanel = document.getElementById("cart-panel");
const cartItemsContainer = document.getElementById("cart-items");
const cartTotal = document.getElementById("cart-total");
const cartCount = document.getElementById("cart-count");
const closeCart = document.getElementById("close-cart");
const clearCart = document.getElementById("clear-cart");
const cartButton = document.getElementById("cart-button");

// Produits de test
const fakeProducts = [
    {
        name: "Clavier mécanique",
        price: 89.99,
        quantity: 15,
        image: "https://ca.hyperx.com/cdn/shop/files/hyperx_alloy_origins_65_english_us_1_top_down.jpg?v=1741695682"
    },
    {
        name: "Casque sans fil",
        price: 59.99,
        quantity: 23,
        image: "https://m.media-amazon.com/images/I/41SkA5j2l-L._AC_SR300,300.jpg"
    },
    {
        name: "Souris gaming",
        price: 39.99,
        quantity: 8,
        image: "https://m.media-amazon.com/images/I/51pnw-Y7YaL._AC_UF1000,1000_QL80_.jpg"
    }
];

// Afficher les produits
fakeProducts.forEach(product => {
    const card = document.createElement("div");
    card.className = "product-card";
    card.innerHTML = `
        <img src="${product.image}" alt="${product.name}">
        <h3>${product.name}</h3>
        <p><strong>Prix :</strong> ${product.price} $</p>
        <p><strong>Quantité :</strong> ${product.quantity}</p>
        <button onclick='addToCart("${product.name}")'>Ajouter au panier</button>
    `;
    productList.appendChild(card);
});

// Ajouter au panier
function addToCart(name) {
    let cart = JSON.parse(localStorage.getItem("panier")) || [];
    const product = fakeProducts.find(p => p.name === name);
    const item = cart.find(i => i.name === name);

    if (item) {
        item.quantity += 1;
    } else {
        cart.push({ ...product, quantity: 1 });
    }

    localStorage.setItem("panier", JSON.stringify(cart));
    updateCartCount();
    updateCartPanel();
}

// Mettre à jour le compteur
function updateCartCount() {
    const cart = JSON.parse(localStorage.getItem("panier")) || [];
    const total = cart.reduce((sum, item) => sum + item.quantity, 0);
    cartCount.textContent = total;
}

// Mettre à jour le panneau du panier
function updateCartPanel() {
    const cart = JSON.parse(localStorage.getItem("panier")) || [];
    cartItemsContainer.innerHTML = "";
    let total = 0;

    cart.forEach(item => {
        total += item.price * item.quantity;

        const li = document.createElement("li");
        li.innerHTML = `
            <div class="cart-line">
                <div class="cart-details">
                    <img src="${item.image}" alt="${item.name}">
                    <div>
                        <strong>${item.name}</strong><br>
                        <div class="cart-controls">
                            ${item.price} $ ×
                            <button onclick="changeQuantity('${item.name}', -1)">−</button>
                            ${item.quantity}
                            <button onclick="changeQuantity('${item.name}', 1)">+</button>
                        </div>
                    </div>
                </div>
                <span class="remove-item" onclick="removeItem('${item.name}')">Retirer l'article</span>
            </div>
        `;
        cartItemsContainer.appendChild(li);
    });

    cartTotal.textContent = `Total : ${total.toFixed(2)} $`;
}

// Modifier la quantité
function changeQuantity(name, delta) {
    let cart = JSON.parse(localStorage.getItem("panier")) || [];
    const item = cart.find(p => p.name === name);

    if (item) {
        item.quantity += delta;
        if (item.quantity <= 0) {
            cart = cart.filter(p => p.name !== name);
        }
        localStorage.setItem("panier", JSON.stringify(cart));
        updateCartCount();
        updateCartPanel();
    }
}

// Supprimer un article
function removeItem(name) {
    let cart = JSON.parse(localStorage.getItem("panier")) || [];
    cart = cart.filter(p => p.name !== name);
    localStorage.setItem("panier", JSON.stringify(cart));
    updateCartCount();
    updateCartPanel();
}

// Vider le panier
clearCart.addEventListener("click", () => {
    localStorage.removeItem("panier");
    updateCartCount();
    updateCartPanel();
});

// Ouvrir/Fermer panier
cartButton.addEventListener("click", () => {
    cartPanel.classList.toggle("show");
    updateCartPanel();
});
closeCart.addEventListener("click", () => {
    cartPanel.classList.remove("show");
});

// Initialisation
updateCartCount();
