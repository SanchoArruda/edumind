
document.addEventListener("DOMContentLoaded", function () {
    const passwordInputs = document.querySelectorAll(".js-password-input");

    passwordInputs.forEach(function (input) {
        input.addEventListener("input", function () {
            input.classList.remove("is-invalid");
        });
    });
});