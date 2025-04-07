const productList = document.getElementById("product-list");

fetch('http://localhost:5000/')
  .then(response => response.json())
  .then(data => {
    data.products.forEach(product => {
      const card = document.createElement("div");
      card.className = "product-card";
      card.innerHTML = `
        <h3>${product.name}</h3>
        <p><strong>Prix :</strong> ${product.price} $</p>
        <p><strong>Quantité :</strong> ${product.quantity}</p>
        <button>Commander</button>
      `;
      productList.appendChild(card);
    });
  })
  .catch(error => console.error('Erreur lors du chargement des produits:', error));

// Initialiser le compteur panier au démarrage
function updateCartCount() {
    const cart = JSON.parse(localStorage.getItem('panier')) || [];
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    document.getElementById("cart-count").textContent = totalItems;
  }
  
  // Appel au chargement
  updateCartCount();
  