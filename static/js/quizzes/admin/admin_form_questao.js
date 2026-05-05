document.addEventListener("DOMContentLoaded", function () {
    const container = document.getElementById("alternativas-container");
    const btnAdicionar = document.getElementById("adicionar-alternativa");
    const letras = ["A", "B", "C", "D", "E"];

    if (!container || !btnAdicionar) {
        return;
    }

    function atualizarLetras() {
        const itens = container.querySelectorAll(".alternativa-item");

        itens.forEach((item, index) => {
            const letra = letras[index];

            const letraAlternativa = item.querySelector(".letra-alternativa");
            const inputLetra = item.querySelector("input[name='letra[]']");
            const inputTexto = item.querySelector("input[name='texto[]']");
            const radioCorreta = item.querySelector("input[name='correta']");

            if (letraAlternativa) {
                letraAlternativa.textContent = letra + ")";
            }

            if (inputLetra) {
                inputLetra.value = letra;
            }

            if (inputTexto) {
                inputTexto.placeholder = "Alternativa " + letra;
            }

            if (radioCorreta) {
                radioCorreta.value = letra;
            }
        });

        btnAdicionar.disabled = itens.length >= 5;

        const botoesRemover = container.querySelectorAll(".remover-alternativa");

        botoesRemover.forEach((botao) => {
            botao.disabled = itens.length <= 2;
        });
    }

    btnAdicionar.addEventListener("click", function () {
        const total = container.querySelectorAll(".alternativa-item").length;

        if (total >= 5) {
            return;
        }

        const proximaLetra = letras[total];

        const html = `
            <div class="border rounded p-3 mb-3 alternativa-item">
                <div class="row align-items-center">
                    <div class="col-md-1 col-2">
                        <strong class="letra-alternativa">${proximaLetra})</strong>
                        <input type="hidden" name="letra[]" value="${proximaLetra}">
                    </div>

                    <div class="col-md-8 col-10">
                        <input
                            type="text"
                            name="texto[]"
                            class="form-control"
                            placeholder="Alternativa ${proximaLetra}"
                        >
                    </div>

                    <div class="col-md-2 col-8 mt-3 mt-md-0">
                        <label class="mb-0">
                            <input
                                type="radio"
                                name="correta"
                                value="${proximaLetra}"
                                required
                            >
                            Correta
                        </label>
                    </div>

                    <div class="col-md-1 col-4 mt-3 mt-md-0 text-right">
                        <button type="button" class="btn btn-sm btn-light border text-danger remover-alternativa">
                            ×
                        </button>
                    </div>
                </div>
            </div>
        `;

        container.insertAdjacentHTML("beforeend", html);
        atualizarLetras();
    });

    container.addEventListener("click", function (event) {
        if (event.target.classList.contains("remover-alternativa")) {
            const itens = container.querySelectorAll(".alternativa-item");

            if (itens.length <= 2) {
                return;
            }

            event.target.closest(".alternativa-item").remove();
            atualizarLetras();
        }
    });

    atualizarLetras();
});