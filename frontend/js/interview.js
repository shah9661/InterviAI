let sessionId = null;
let questions = [];
let currentQuestionIndex = 0;
let questionStartTime = null;
let timerInterval = null;
document.addEventListener("DOMContentLoaded", async () => {
    sessionId = localStorage.getItem("session_id");
    if (!sessionId) {showMessage("Interview session not found.", "error");
        return;
    }
    setupButtons();
    await loadQuestions();
});
// BUTTONS
function setupButtons() {
    const submitButton =document.getElementById("submitAnswerBtn");
    const startRecordingButton =document.getElementById("startRecordingBtn");
    const stopRecordingButton =document.getElementById("stopRecordingBtn");
    if (submitButton) {
        submitButton.addEventListener("click",submitCurrentAnswer);
    }
    if (startRecordingButton) {startRecordingButton.addEventListener("click",
            startAnswerTimer);
    }
    if (stopRecordingButton) {stopRecordingButton.addEventListener(
            "click",stopAnswerTimer);
    }
}
// LOAD QUESTIONS
async function loadQuestions() {
    try {showMessage("Loading questions...", "");
        const data = await getQuestions(sessionId);
        if (!Array.isArray(data)) {throw new Error("Invalid questions response."
            );
        }
        questions = data;
        if (questions.length === 0) {throw new Error("No questions found for this interview.");
        }
        currentQuestionIndex = 0;
        showQuestion();
        showMessage("", "");
    } catch (error) {
        console.error("Failed to load questions:",error);
        showMessage(error.message,"error");
    }
}
// SHOW CURRENT QUESTION
function showQuestion() {
    const question =questions[currentQuestionIndex];
    if (!question) {finishInterview();
        return;
    }
    document.getElementById("questionText").textContent = question.q_text;
    document.getElementById("questionType").textContent = question.q_type;
    document.getElementById("questionProgress").textContent =`${currentQuestionIndex + 1} / ${questions.length}`;
    document.getElementById("transcript").value = "";
    resetTimer();
    startAnswerTimer();
}
// SUBMIT CURRENT ANSWER
async function submitCurrentAnswer() {
    const question =questions[currentQuestionIndex];
    if (!question) {
        return;
    }
    const transcript =document.getElementById("transcript").value.trim();
    if (!transcript) {showMessage("Please enter your answer.","error");
        return;
    }
    stopAnswerTimer();
    const duration =
        getElapsedSeconds();
    const submitButton =document.getElementById("submitAnswerBtn");
    submitButton.disabled = true;
    submitButton.textContent ="Submitting...";
    try {
        await submitAnswer(question.id,transcript,duration);
        showMessage( "Answer submitted successfully.", "success"
        );
        currentQuestionIndex++;
        if (currentQuestionIndex >=questions.length) {finishInterview();
            return;
        }
        setTimeout(() => {showQuestion();}, 500);
    } catch (error) {console.error("Answer submission failed:",error
        );
        showMessage(error.message,"error"
        );
        startAnswerTimer();
    } finally {submitButton.disabled = false;submitButton.textContent =
            "Submit Answer";
    }
}
// TIMER
function startAnswerTimer() {
    if (timerInterval) {
        return;
    }
    if (!questionStartTime) {
        questionStartTime =Date.now();
    }
    const startButton =document.getElementById("startRecordingBtn"
        );
    const stopButton =document.getElementById( "stopRecordingBtn"
        );
    if (startButton) {startButton.disabled = true;
    }
    if (stopButton) {stopButton.disabled = false;
    }
    timerInterval =setInterval(updateTimer, 1000);
    updateTimer();
}
function stopAnswerTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
    const startButton =document.getElementById("startRecordingBtn"
        );
    const stopButton =document.getElementById( "stopRecordingBtn"
        );
    if (startButton) {startButton.disabled = false;
    }
    if (stopButton) {
        stopButton.disabled = true;
    }
}
function updateTimer() {
    const duration = getElapsedSeconds();
    document.getElementById("duration"
    ).textContent = duration;
}
function getElapsedSeconds() {
    if (!questionStartTime) {
        return 0;
    }
    return Math.floor(
        (Date.now() - questionStartTime) / 1000
    );
}
function resetTimer() {
    stopAnswerTimer();
    questionStartTime = null;
    document.getElementById("duration"
    ).textContent = "0";
}
// INTERVIEW FINISHED
function finishInterview() {
    stopAnswerTimer();
    showMessage("Interview completed.","success"
    );
    setTimeout(() => {
        window.location.href =`report.html?session_id=${sessionId}`;
    }, 1000);
}
// MESSAGE
function showMessage(text, type) {
    const message = document.getElementById( "interviewMessage"
        );
    if (!message) {
        return;
    }
    message.textContent = text;
    message.className = "message";
    if (type) {
        message.classList.add(type);
    }
}