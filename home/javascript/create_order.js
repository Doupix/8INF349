document.addEventListener('DOMContentLoaded', () => {
    const productList = document.getElementById('product-list');
    const form = document.getElementById('order-form');
    const messageDiv = document.getElementById('message');

    fetch('/')
        .then(res => res.json())
        .then(data => {
            data.products.forEach(product => {
                const container = document.createElement('div');
                container.className = 'product-entry';

                const disabled = product.in_stock ? '' : 'disabled';
                const labelStyle = product.in_stock ? '' : 'style="opacity: 0.5;"';
                const note = product.in_stock ? '' : ' (Rupture de stock)';

                container.innerHTML = `
                    <label ${labelStyle}>
                        <input type="number" min="0" value="0" name="product-${product.id}" ${disabled} />
                        ${product.name} (${product.price.toFixed(2)}$) ${note}
                    </label>
                `;

                productList.appendChild(container);
            });
        })
        .catch(err => {
            messageDiv.innerText = 'Erreur de chargement des produits.';
            console.error(err);
        });

    form.addEventListener('submit', (e) => {
        e.preventDefault();

        const inputs = form.querySelectorAll('input[type="number"]');
        const products = [];

        inputs.forEach(input => {
            const quantity = parseInt(input.value);
            const id = parseInt(input.name.replace('product-', ''));

            if (quantity > 0) {
                products.push({ id, quantity });
            }
        });

        if (products.length === 0) {
            messageDiv.innerText = "Veuillez sélectionner au moins un produit.";
            return;
        }

        fetch('/order', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ products })
        })
        .then(res => {
            if (res.redirected) {
                const orderId = res.url.split('/').pop();
                window.location.href = `/home/view_order.html?id=${orderId}`;
            } else if (res.headers.get("Content-Type")?.includes("application/json")) {
                return res.json().then(data => {
                    if (data.order?.id) {
                        window.location.href = `/home/view_order.html?id=${data.order.id}`;
                    } else {
                        messageDiv.innerText = "Erreur : commande invalide.";
                    }
                });
            } else {
                return res.text().then(msg => {
                    messageDiv.innerText = "Erreur : " + msg;
                });
            }
        })
        .catch(err => {
            messageDiv.innerText = "Erreur lors de la création de la commande.";
            console.error(err);
        });
    });
});
