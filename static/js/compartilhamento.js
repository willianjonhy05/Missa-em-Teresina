document.addEventListener("DOMContentLoaded", function () {

    const url = window.location.href;
    const text = document.querySelector(".church-name")?.innerText || "Confira esta igreja";

    // WhatsApp
    document.getElementById("share-whatsapp").href =
        `https://wa.me/?text=${encodeURIComponent(text + " - " + url)}`;

    // Facebook
    document.getElementById("share-facebook").href =
        `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;

    // Copiar link
    document.getElementById("share-copy").addEventListener("click", function () {
        navigator.clipboard.writeText(url).then(() => {
            this.innerHTML = '<i class="fa-solid fa-check"></i>';
            setTimeout(() => {
                this.innerHTML = '<i class="fa-solid fa-link"></i>';
            }, 2000);
        });
    });

});