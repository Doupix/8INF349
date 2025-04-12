document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('lookup-form');
    const result = document.getElementById('result');
    const urlParams = new URLSearchParams(window.location.search);
    const presetId = urlParams.get('id');
    if (presetId) {
        document.getElementById('order-id').value = presetId;
        form.dispatchEvent(new Event('submit')); // auto-chargement
    }

    form.addEventListener('submit', (e) => {
        e.preventDefault();

        const orderId = document.getElementById('order-id').value;
        if (!orderId) return;

        fetch(`/order/${orderId}`)
            .then(res => {
                if (res.status === 200) {
                    return res.json();
                } else if (res.status === 202) {
                    result.innerHTML = `<p>Commande en cours de traitement...</p>`;
                    throw new Error("En traitement");
                } else if (res.status === 404) {
                    result.innerHTML = `<p>Commande non trouvée.</p>`;
                    throw new Error("Not found");
                } else {
                    return res.text().then(text => {
                        result.innerHTML = `<p>Erreur : ${text}</p>`;
                        throw new Error(text);
                    });
                }
            })
            .then(async data => {
                const order = data.order;
            
                // 👇 On récupère la liste de tous les produits
                const productListResponse = await fetch('/');
                const allProductsData = await productListResponse.json();
            
                // 👇 On fait un dictionnaire id → nom
                const idToName = {};
                allProductsData.products.forEach(p => {
                    idToName[p.id] = p.name;
                });
            
                // 👇 Affichage des produits de la commande
                const productsHTML = order.products.map(p => {
                    const name = idToName[p.id] || `Produit #${p.id}`;
                    return `<li>${name} × ${p.quantity}</li>`;
                }).join('');
            
                result.innerHTML = `
                    <h2>Commande #${order.id}</h2>

                    <p><strong>Email :</strong> ${order.email || "Non fourni"}</p>
                    <p><strong>Sous-total :</strong> ${order.total_price.toFixed(2)} $</p>
                    ${order.email ? `<p><strong>Total avec taxes :</strong> ${order.total_price_tax.toFixed(2)} $</p>` : ""}
                    <p><strong>Frais d'expédition :</strong> ${order.shipping_price.toFixed(2)} $</p>

                    <hr>

                    <p><strong>Statut :</strong> ${order.paid ? "Payée" : "Non payée"}</p>
                    ${order.paid ? `<p><strong>ID de transaction :</strong> ${order.transaction.id}</p>` : ""}
                    ${order.paid ? `<p><strong>Montant total facturé :</strong> ${order.transaction.amount_charged.toFixed(2)} $</p>` : ""}

                    <hr>

                    <h3>Produits :</h3>
                    <ul>${productsHTML}</ul>

                    <hr>

                    ${order.transaction?.error ? `<p style="color:red"><strong>Erreur paiement :</strong> ${order.transaction.error.name}</p>` : ""}

                    ${order.email ? "" : `<a href="/home/complete_order.html?id=${order.id}" class="btn">Compléter les informations de commande</a>`}
                    ${!order.paid ? `<a href="/home/pay_order.html?id=${order.id}" class="btn">Payer la commande</a>` : ""}
                `;
            })            
            .catch(err => {
                console.warn("Erreur affichage commande :", err.message);
            });
    });
});