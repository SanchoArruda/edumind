document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("quizForm");
    const steps = document.querySelectorAll(".quiz-step");
    const prevBtn = document.getElementById("prevQuestionBtn");
    const nextBtn = document.getElementById("nextQuestionBtn");
    const currentQuestionNumber = document.getElementById("currentQuestionNumber");
    const answeredCounter = document.getElementById("answeredCounter");
    const progressFill = document.getElementById("quizProgressFill");
    const timerEl = document.getElementById("quizTimer");
    const tempoGastoInput = document.getElementById("tempoGastoSegundos");
    const tempoTotalInput = document.getElementById("tempoTotalSegundos");

    if (!form || !steps.length) {
        return;
    }

    let currentStep = 0;
    const totalSteps = steps.length;

    let tempoTotal = parseInt(tempoTotalInput?.value || "0", 10);
    let tempoRestante = tempoTotal;
    let tempoGasto = 0;

    function formatTime(totalSeconds) {
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = totalSeconds % 60;

        if (hours > 0) {
            return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
        }

        return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
    }

    function updateTimer() {
        if (timerEl) {
            timerEl.textContent = formatTime(Math.max(tempoRestante, 0));
        }

        if (tempoGastoInput) {
            tempoGastoInput.value = tempoGasto;
        }
    }

    function updateAnsweredCounter() {
        let answered = 0;

        form.querySelectorAll('input[type="radio"]:checked').forEach(() => {
            answered += 1;
        });

        if (answeredCounter) {
            answeredCounter.textContent = answered;
        }
    }

    function updateProgress() {
        const progress = ((currentStep + 1) / totalSteps) * 100;

        if (progressFill) {
            progressFill.style.width = `${progress}%`;
        }
    }

    function showStep(index) {
        steps.forEach((step, i) => {
            if (i === index) {
                step.classList.add("active");
            } else {
                step.classList.remove("active");
            }
        });

        if (currentQuestionNumber) {
            currentQuestionNumber.textContent = index + 1;
        }

        if (prevBtn) {
            prevBtn.style.visibility = index === 0 ? "hidden" : "visible";
        }

        if (nextBtn) {
            if (index === totalSteps - 1) {
                nextBtn.innerHTML = '<span>Finalizar</span><i class="icon-check"></i>';
            } else {
                nextBtn.innerHTML = '<span>Próxima</span><i class="icon-arrow-right"></i>';
            }
        }

        updateProgress();
        updateAnsweredCounter();
    }

    form.querySelectorAll('input[type="radio"]').forEach((input) => {
        input.addEventListener("change", function () {
            updateAnsweredCounter();
        });
    });

    if (prevBtn) {
        prevBtn.addEventListener("click", function () {
            if (currentStep > 0) {
                currentStep--;
                showStep(currentStep);
            }
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener("click", function () {
            if (currentStep < totalSteps - 1) {
                currentStep++;
                showStep(currentStep);
            } else {
                form.submit();
            }
        });
    }

    updateTimer();
    showStep(0);

    const timerInterval = setInterval(function () {
        tempoRestante--;
        tempoGasto++;

        updateTimer();

        if (tempoRestante <= 0) {
            clearInterval(timerInterval);
            tempoRestante = 0;
            updateTimer();
            form.submit();
        }
    }, 1000);
});