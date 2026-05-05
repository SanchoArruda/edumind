document.addEventListener("DOMContentLoaded", function () {
    const radios = document.querySelectorAll(".desafio-radio-input");
    const form = document.getElementById("formEscolhaProva");

    function limparSelecao() {
        radios.forEach(function (radio) {
            radio.checked = false;
        });
    }

    limparSelecao();

    window.addEventListener("pageshow", function () {
        limparSelecao();
    });

    radios.forEach(function (radio) {
        radio.addEventListener("change", function () {
            setTimeout(function () {
                form.submit();
            }, 70);
        });
    });
});