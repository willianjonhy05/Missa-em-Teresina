// Dados simulados de igrejas
const igrejas = [
    {
        nome: "Catedral Metropolitana",
        lat: -23.5505, // Exemplo: Centro de SP
        lng: -46.6333,
        missas: ["07:00", "12:00", "18:00", "19:30"],
        endereco: "Praça da Sé, s/n"
    },
    {
        nome: "Paróquia Santo Antônio",
        lat: -23.5610,
        lng: -46.6550,
        missas: ["08:00", "15:00", "19:00"],
        endereco: "Av. Paulista, 1000"
    },
    {
        nome: "Igreja de São Francisco",
        lat: -23.5400,
        lng: -46.6400,
        missas: ["06:30", "10:00", "17:30"],
        endereco: "Largo de São Francisco"
    }
];

const btnLocalizar = document.getElementById('btnLocalizar');
const statusTxt = document.getElementById('status');
const resultadosArea = document.getElementById('resultados');

btnLocalizar.addEventListener('click', () => {
    if (navigator.geolocation) {
        statusTxt.innerText = "Localizando sua posição...";
        navigator.geolocation.getCurrentPosition(processarPosicao, erroLocalizacao);
    } else {
        statusTxt.innerText = "Geolocalização não suportada pelo seu navegador.";
    }
});

function processarPosicao(posicao) {
    const userLat = posicao.coords.latitude;
    const userLng = posicao.coords.longitude;
    statusTxt.innerText = "Localizado com sucesso!";
    
    // 1. Calcular distâncias
    const igrejasComDistancia = igrejas.map(igreja => {
        const d = calcularDistancia(userLat, userLng, igreja.lat, igreja.lng);
        return { ...igreja, distancia: d };
    }).sort((a, b) => a.distancia - b.distancia);

    exibirResultados(igrejasComDistancia);
}

function erroLocalizacao() {
    statusTxt.innerText = "Não foi possível obter sua localização. Verifique as permissões.";
}

// Fórmula de Haversine para calcular distância entre dois pontos (km)
function calcularDistancia(lat1, lon1, lat2, lon2) {
    const R = 6371;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

function buscarProximaMissa(horarios) {
    const agora = new Date();
    const horaAtual = agora.getHours() * 60 + agora.getMinutes();

    for (let h of horarios) {
        const [hora, min] = h.split(':').map(Number);
        const horaMissa = hora * 60 + min;
        if (horaMissa > horaAtual) return h;
    }
    return horarios[0]; // Retorna a primeira do dia seguinte se não houver mais hoje
}

function exibirResultados(lista) {
    resultadosArea.classList.remove('hidden');
    const proximaCard = document.getElementById('proxima-missa-card');
    const listaDiv = document.getElementById('lista-igrejas');
    
    listaDiv.innerHTML = "";

    // A mais próxima (primeira da lista ordenada)
    const principal = lista[0];
    const proxHora = buscarProximaMissa(principal.missas);

    proximaCard.innerHTML = `
        <h3>${principal.nome}</h3>
        <p><i class="fas fa-map-marker-alt"></i> ${principal.endereco}</p>
        <p class="distancia">A apenas ${principal.distancia.toFixed(2)} km de você</p>
        <span class="horario"><i class="far fa-clock"></i> Próxima Missa: ${proxHora}</span>
    `;

    // Outras igrejas
    lista.forEach((igreja, index) => {
        if (index === 0) return;
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
            <h4>${igreja.nome}</h4>
            <p>${igreja.endereco}</p>
            <p class="distancia">${igreja.distancia.toFixed(2)} km</p>
            <p>Horários: ${igreja.missas.join(' | ')}</p>
        `;
        listaDiv.appendChild(card);
    });
}