    document.addEventListener("DOMContentLoaded", function () {
        const urlParams = new URLSearchParams(window.location.search);

        const lat = urlParams.get("lat");
        const lon = urlParams.get("lon");
        const localizacao = urlParams.get("localizacao");

        const temLatitude = lat !== null && lat.trim() !== "";
        const temLongitude = lon !== null && lon.trim() !== "";

        if (!temLatitude && !temLongitude && !localizacao && navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function (position) {
                    urlParams.set("lat", position.coords.latitude);
                    urlParams.set("lon", position.coords.longitude);
                    urlParams.set("localizacao", "ok");

                    window.location.search = urlParams.toString();
                },
                function () {
                    urlParams.set("localizacao", "negada");

                    window.location.search = urlParams.toString();
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 60000
                }
            );
        }
    });