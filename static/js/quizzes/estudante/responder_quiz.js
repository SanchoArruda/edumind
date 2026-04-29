document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("quizForm");
    if (!form) return;

    const steps = Array.from(document.querySelectorAll(".quiz-step"));
    const prevBtn = document.getElementById("prevQuestionBtn");
    const nextBtn = document.getElementById("nextQuestionBtn");
    const currentQuestionNumber = document.getElementById("currentQuestionNumber");
    const answeredCounter = document.getElementById("answeredCounter");
    const progressFill = document.getElementById("quizProgressFill");
    const quizTimer = document.getElementById("quizTimer");
    const tempoGastoSegundosInput = document.getElementById("tempoGastoSegundos");

    const totalQuestions = parseInt(form.dataset.totalQuestions, 10);

    let currentStep = 0;
    let elapsedSeconds = 0;

    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${String(minutes).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
    }

    function getAnsweredCount() {
        const answeredNames = new Set();

        document.querySelectorAll(".quiz-option__input:checked").forEach((input) => {
            answeredNames.add(input.name);
        });

        return answeredNames.size;
    }

    function updateAnsweredCounter() {
        answeredCounter.textContent = getAnsweredCount();
    }

    function updateProgress() {
        const percentage = ((currentStep + 1) / totalQuestions) * 100;
        progressFill.style.width = `${percentage}%`;
    }

    function updateStep() {
        steps.forEach((step, index) => {
            step.classList.toggle("active", index === currentStep);
        });

        currentQuestionNumber.textContent = currentStep + 1;
        prevBtn.disabled = currentStep === 0;

        if (currentStep === totalQuestions - 1) {
            nextBtn.innerHTML = '<span>Finalizar</span><i class="icon-check"></i>';
        } else {
            nextBtn.innerHTML = '<span>Próxima</span><i class="icon-arrow-right"></i>';
        }

        updateProgress();
        updateAnsweredCounter();
    }

    function saveElapsedTime() {
        tempoGastoSegundosInput.value = elapsedSeconds;
    }

    prevBtn.addEventListener("click", function () {
        if (currentStep > 0) {
            currentStep--;
            updateStep();
        }
    });

    nextBtn.addEventListener("click", function () {
        if (currentStep < totalQuestions - 1) {
            currentStep++;
            updateStep();
            return;
        }

        const unanswered = totalQuestions - getAnsweredCount();

        if (unanswered > 0) {
            const confirmar = window.confirm(
                `Ainda existem ${unanswered} questão(ões) sem resposta. Deseja finalizar mesmo assim?`
            );

            if (!confirmar) {
                return;
            }
        }

        saveElapsedTime();
        form.submit();
    });

    document.querySelectorAll(".quiz-option__input").forEach((input) => {
        input.addEventListener("change", function () {
            updateAnsweredCounter();
        });
    });

    const timerInterval = setInterval(function () {
        elapsedSeconds++;
        quizTimer.textContent = formatTime(elapsedSeconds);
        saveElapsedTime();
    }, 1000);

    quizTimer.textContent = formatTime(elapsedSeconds);
    updateStep();

    form.addEventListener("submit", function () {
        saveElapsedTime();
        clearInterval(timerInterval);
    });
});