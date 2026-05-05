document.addEventListener("DOMContentLoaded", function () {
    const tipoProvaSelect = document.getElementById("tipoProvaSelect");
    const mostrarAmbosCheckbox = document.getElementById("mostrarAmbos");
    const filtrosNivel = document.querySelectorAll(".filtro-nivel");
    const questoes = document.querySelectorAll(".questao-item");
    const nenhumaQuestaoMsg = document.getElementById("nenhumaQuestaoDesafioMsg");

    const quantidadeQuestoesInput = document.getElementById("quantidadeQuestoesInput");
    const tempoTotalFormatadoInput = document.getElementById("tempoTotalFormatadoInput");
    const tempoTotalSegundosInput = document.getElementById("tempoTotalSegundosInput");

    function getNiveisSelecionados() {
        const niveis = [];

        filtrosNivel.forEach(function (checkbox) {
            if (checkbox.checked) {
                niveis.push(checkbox.value);
            }
        });

        return niveis;
    }

    function getQuestoesSelecionadas() {
        return document.querySelectorAll('input[name="questoes"]:checked').length;
    }

    function calcularTempoPorQuestaoEmSegundos(tipoProva) {
        if (tipoProva === "ENADE") {
            return 5 * 60;
        }

        if (tipoProva === "POSCOMP") {
            return (3 * 60) + 17;
        }

        return 0;
    }

    function formatarTempo(segundosTotais) {
        const minutos = Math.floor(segundosTotais / 60);
        const segundos = segundosTotais % 60;

        if (segundos === 0) {
            return `${minutos} min`;
        }

        return `${minutos} min e ${segundos} seg`;
    }

    function atualizarResumoDesafio() {
        const tipoProva = tipoProvaSelect ? tipoProvaSelect.value : "";
        const quantidadeSelecionada = getQuestoesSelecionadas();
        const tempoPorQuestaoSegundos = calcularTempoPorQuestaoEmSegundos(tipoProva);
        const tempoTotalSegundos = quantidadeSelecionada * tempoPorQuestaoSegundos;

        if (quantidadeQuestoesInput) {
            quantidadeQuestoesInput.value = quantidadeSelecionada;
        }

        if (tempoTotalFormatadoInput) {
            tempoTotalFormatadoInput.value = quantidadeSelecionada > 0
                ? formatarTempo(tempoTotalSegundos)
                : "";
        }

        if (tempoTotalSegundosInput) {
            tempoTotalSegundosInput.value = tempoTotalSegundos;
        }
    }

    function filtrarQuestoes() {
        const tipoProva = tipoProvaSelect ? tipoProvaSelect.value : "";
        const incluirAmbos = mostrarAmbosCheckbox ? mostrarAmbosCheckbox.checked : false;
        const niveisSelecionados = getNiveisSelecionados();

        let quantidadeVisivel = 0;

        questoes.forEach(function (item) {
            const itemTipoProva = item.dataset.tipoProva;
            const itemNivel = item.dataset.nivel;

            let bateTipoProva = false;

            if (tipoProva) {
                if (incluirAmbos) {
                    bateTipoProva = itemTipoProva === tipoProva || itemTipoProva === "AMBOS";
                } else {
                    bateTipoProva = itemTipoProva === tipoProva;
                }
            }

            let bateNivel = true;

            if (niveisSelecionados.length > 0) {
                bateNivel = niveisSelecionados.includes(itemNivel);
            }

            if (tipoProva && bateTipoProva && bateNivel) {
                item.classList.remove("d-none");
                quantidadeVisivel++;
            } else {
                item.classList.add("d-none");
            }
        });

        if (!tipoProva) {
            nenhumaQuestaoMsg.textContent = "Selecione o tipo de prova para visualizar as questões.";
            nenhumaQuestaoMsg.classList.remove("d-none");
        } else if (quantidadeVisivel === 0) {
            nenhumaQuestaoMsg.textContent = "Nenhuma questão encontrada para esse filtro.";
            nenhumaQuestaoMsg.classList.remove("d-none");
        } else {
            nenhumaQuestaoMsg.classList.add("d-none");
        }

        atualizarResumoDesafio();
    }

    if (tipoProvaSelect) {
        tipoProvaSelect.addEventListener("change", function () {
            filtrarQuestoes();
            atualizarResumoDesafio();
        });
    }

    if (mostrarAmbosCheckbox) {
        mostrarAmbosCheckbox.addEventListener("change", filtrarQuestoes);
    }

    filtrosNivel.forEach(function (checkbox) {
        checkbox.addEventListener("change", filtrarQuestoes);
    });

    document.querySelectorAll('input[name="questoes"]').forEach(function (checkbox) {
        checkbox.addEventListener("change", atualizarResumoDesafio);
    });

    filtrarQuestoes();
    atualizarResumoDesafio();
});