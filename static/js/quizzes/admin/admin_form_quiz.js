document.addEventListener("DOMContentLoaded", function () {
    const disciplinaSelect = document.getElementById("id_disciplina");
    const tipoProvaSelect = document.getElementById("id_tipo_prova");
    const incluirAmbosSelect = document.getElementById("incluirAmbos");
    const questoes = document.querySelectorAll(".questao-item");
    const nenhumaQuestaoMsg = document.getElementById("nenhumaQuestaoMsg");

    function filtrarQuestoes() {
        const disciplinaId = disciplinaSelect ? disciplinaSelect.value : "";
        const tipoProva = tipoProvaSelect ? tipoProvaSelect.value : "";
        const incluirAmbos = incluirAmbosSelect ? incluirAmbosSelect.value === "sim" : true;

        let quantidadeVisivel = 0;

        questoes.forEach(function (item) {
            const itemDisciplina = item.dataset.disciplina;
            const itemTipoProva = item.dataset.tipoProva;

            const bateDisciplina = disciplinaId && itemDisciplina === disciplinaId;

            let bateTipoProva = false;

            if (tipoProva) {
                if (incluirAmbos) {
                    bateTipoProva = itemTipoProva === tipoProva || itemTipoProva === "AMBOS";
                } else {
                    bateTipoProva = itemTipoProva === tipoProva;
                }
            }

            if (disciplinaId && tipoProva && bateDisciplina && bateTipoProva) {
                item.classList.remove("d-none");
                item.classList.add("d-flex");
                quantidadeVisivel++;
            } else {
                item.classList.add("d-none");
                item.classList.remove("d-flex");
            }
        });

        if (!disciplinaId || !tipoProva) {
            nenhumaQuestaoMsg.textContent = "Selecione a disciplina e o tipo de prova para visualizar as questões disponíveis.";
            nenhumaQuestaoMsg.classList.remove("d-none");
        } else if (quantidadeVisivel === 0) {
            nenhumaQuestaoMsg.textContent = "Nenhuma questão cadastrada para essa combinação.";
            nenhumaQuestaoMsg.classList.remove("d-none");
        } else {
            nenhumaQuestaoMsg.classList.add("d-none");
        }
    }

    if (disciplinaSelect) {
        disciplinaSelect.addEventListener("change", filtrarQuestoes);
    }

    if (tipoProvaSelect) {
        tipoProvaSelect.addEventListener("change", filtrarQuestoes);
    }

    if (incluirAmbosSelect) {
        incluirAmbosSelect.addEventListener("change", filtrarQuestoes);
    }

    filtrarQuestoes();
});