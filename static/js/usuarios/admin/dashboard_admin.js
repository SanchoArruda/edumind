document.addEventListener("DOMContentLoaded", function () {
    const shortcutCards = document.querySelectorAll(".admin-shortcut-card");

    shortcutCards.forEach(function (card) {
        card.addEventListener("mouseenter", function () {
            card.classList.add("shadow-sm");
        });

        card.addEventListener("mouseleave", function () {
            card.classList.remove("shadow-sm");
        });
    });
});