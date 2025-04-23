console.log("⚡ JS chargé");

document.addEventListener('DOMContentLoaded', () => {
    console.log("📦 DOM prêt");

    if (window.formHandlerInitialized) {
        console.log("⛔ Handler déjà initialisé");
        return;
    }
    window.formHandlerInitialized = true;
    console.log("✅ Handler attaché");

    // Préremplir si URL contient ?id=...
    const urlParams = new URLSearchParams(window.location.search);
    const presetId = urlParams.get('id');
    if (presetId) {
        document.getElementById('order-id').value = presetId;
    }

    const form = document.getElementById('complete-form');
    const messageDiv = document.getElementById('message');
    const submitBtn = form.querySelector('button[type="submit"]');

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        console.log("📨 Formulaire soumis");

        submitBtn.disabled = true;

        const orderId = document.getElementById('order-id').value;
        const email = document.getElementById('email').value;
        const address = document.getElementById('address').value;
        const city = document.getElementById('city').value;
        const province = document.getElementById('province').value;
        const postal_code = document.getElementById('postal_code').value;
        const country = document.getElementById('country').value;

        if (!orderId || !email || !address || !city || !province || !postal_code || !country) {
            messageDiv.innerText = "Tous les champs sont obligatoires.";
            submitBtn.disabled = false;
            return;
        }

        const payload = {
            order: {
                email,
                shipping_information: {
                    address,
                    city,
                    province,
                    postal_code,
                    country
                }
            }
        };

        console.log("🚀 Requête envoyée pour orderId :", orderId);

        fetch(`/order/${orderId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(res => {
            if (res.ok) {
                messageDiv.innerText = "Commande complétée avec succès ✅";
                messageDiv.style.color = "green";
            
                // Redirection vers la vue commande après 2.5s
                setTimeout(() => {
                    window.location.href = `/home/view_order.html?id=${orderId}`;
                }, 2500);
            } else {
                res.text().then(msg => {
                    messageDiv.innerText = "Erreur : " + msg;
                    messageDiv.style.color = "red";
                });
            }
        })
        .catch(err => {
            messageDiv.innerText = "Erreur réseau ou serveur.";
            console.error("💥 Erreur JS complète :", err);
        })
        .finally(() => {
            submitBtn.disabled = false;
        });
    });
});
