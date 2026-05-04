    const anoEl = document.getElementById("ano-atual");
    if (anoEl) {
        anoEl.textContent = new Date().getFullYear();
    }