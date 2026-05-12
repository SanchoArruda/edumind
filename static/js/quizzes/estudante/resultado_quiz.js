document.addEventListener("DOMContentLoaded", function () {
    mostrarConfetes();
    tocarSomConclusao();
});

function tocarSomConclusao() {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;

    if (!AudioContextClass) {
        return;
    }

    const audioContext = new AudioContextClass();

    const notas = [523.25, 659.25, 783.99];
    const tempoInicial = audioContext.currentTime;

    notas.forEach(function (frequencia, index) {
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        const inicio = tempoInicial + index * 0.15;
        const fim = inicio + 0.25;

        oscillator.type = "sine";
        oscillator.frequency.setValueAtTime(frequencia, inicio);

        gainNode.gain.setValueAtTime(0.15, inicio);
        gainNode.gain.exponentialRampToValueAtTime(0.001, fim);

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.start(inicio);
        oscillator.stop(fim);
    });
}

function mostrarConfetes() {
    const container = document.getElementById("confetti-container");

    if (!container) {
        console.log("Container de confetes não encontrado.");
        return;
    }

    const quantidadeConfetes = 100;
    const cores = ["#5b4ee6", "#4ea8ff", "#ffcc33", "#ff6b6b", "#2ecc71", "#ff8a00"];

    for (let i = 0; i < quantidadeConfetes; i++) {
        const confete = document.createElement("span");

        confete.classList.add("confetti");
        confete.style.left = Math.random() * 100 + "vw";
        confete.style.backgroundColor = cores[Math.floor(Math.random() * cores.length)];
        confete.style.animationDelay = Math.random() * 0.5 + "s";
        confete.style.animationDuration = 2.5 + Math.random() * 2 + "s";

        container.appendChild(confete);

        setTimeout(function () {
            confete.remove();
        }, 5000);
    }
}