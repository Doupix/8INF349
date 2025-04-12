document.addEventListener('DOMContentLoaded', () => {
    fetch('/')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('products');
            data.products.forEach(product => {
                const card = document.createElement('div');
                card.className = 'product-card';

                const inStock = product.in_stock;
                const stockClass = inStock ? 'stock-ok' : 'stock-out';
                const stockText = inStock ? 'En stock' : 'Rupture de stock';
                const buttonHTML = inStock
                    ? `<a href="/home/create_order.html" class="btn">Commander</a>`
                    : `<button class="btn" disabled>Commander</button>`;

                card.innerHTML = `
                    <img src="/static/images/${product.image}" alt="${product.name}" class="product-image">
                    <h2 class="product-title">${product.name}</h2>
                    <p class="product-description">${product.description}</p>
                    <p><strong>Prix:</strong> ${product.price} $</p>
                    <p><strong>Poids:</strong> ${product.weight} g</p>
                    <p class="${stockClass}">${stockText}</p>
                    <div class="product-actions">${buttonHTML}</div>
                `;
                container.appendChild(card);
            });
        })
        .catch(err => {
            document.getElementById('products').innerHTML = "<p>Erreur lors du chargement des produits.</p>";
            console.error(err);
        });
});
