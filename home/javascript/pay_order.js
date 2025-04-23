// /home/javascript/pay_order.js

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('pay-form');
    const message = document.getElementById('message');
    const btn = form.querySelector('button');

    // Préremplir l'ID à partir de l'URL
    const id = new URLSearchParams(window.location.search).get('id');
    if (id) document.getElementById('order-id').value = id;

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        btn.disabled = true;

        const orderId = document.getElementById('order-id').value;
        const number = document.getElementById('card-number').value;
        const expiration = document.getElementById('expiry').value; // Format MM/AA
        const cvc = document.getElementById('cvc').value;

        if (!number || !expiration || !cvc) {
            message.innerText = "Tous les champs sont requis.";
            btn.disabled = false;
            return;
        }

        const [month, yearSuffix] = expiration.split('/');
        const year = "20" + yearSuffix;

        const payload = {
            credit_card: {
                name: "Max Gambier", // Nom factice (obligatoire pour l’API externe)
                number: number,
                expiration_month: parseInt(month),
                expiration_year: parseInt(year),
                cvv: cvc
            }
        };

        fetch(`/order/${orderId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(res => {
            if (res.ok) {
                message.innerText = "✅ Paiement effectué avec succès !";
                message.style.color = "green";

                // Redirection vers la page de la commande après 2s
                setTimeout(() => {
                    window.location.href = `/home/view_order.html?id=${orderId}`;
                }, 2000);
            } else {
                res.text().then(text => {
                    message.innerText = "Erreur : " + text;
                    message.style.color = "red";
                });
            }
        })
        .catch(err => {
            message.innerText = "Erreur réseau.";
            console.error(err);
        })
        .finally(() => {
            btn.disabled = false;
        });
    });
});
