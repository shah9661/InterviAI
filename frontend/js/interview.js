let sessionId = null;
let questions = [];
let currentQuestionIndex = 0;
let questionStartTime = null;
let timerInterval = null;


let mediaRecorder = null;
let audioChunks = [];
let audioBlob = null;
let mediaStream = null;

document.addEventListener("DOMContentLoaded", async () => {
    sessionId = localStorage.getItem("session_id");
    if (!sessionId) {
        showMessage("Interview session not found.", "error");
        return;
    }
    setupButtons();
    await loadQuestions();
});


function setupButtons() {
    const submitButton =document.getElementById("submitAnswerBtn");
    const startRecordingButton =
        document.getElementById("startRecordingBtn");
    const stopRecordingButton =
        document.getElementById("stopRecordingBtn");

    if (submitButton) {
        submitButton.addEventListener("click",submitCurrentAnswer);
    }

    if (startRecordingButton) {
        startRecordingButton.addEventListener("click",startRecording);
    }

    if (stopRecordingButton) {
        stopRecordingButton.addEventListener("click", stopRecording);
    }
}

async function loadQuestions() {
    try {
        showMessage("Loading questions...", "");
        const data = await getQuestions(sessionId);
        if (!Array.isArray(data)) {
            throw new Error("Invalid questions response.");
        }
        questions = data;
        if (questions.length === 0) {
            throw new Error("No questions found for this interview.");
        }

        // Restore progress instead of always resetting to 0
        const savedIndex = Number(localStorage.getItem(`qidx_${sessionId}`));
        currentQuestionIndex = (savedIndex >= 0 && savedIndex < questions.length) ? savedIndex : 0;

        showQuestion();
        showMessage("", "");
    } catch (error) {
        console.error("Failed to load questions:", error);
        showMessage(error.message, "error");
    }
}

function showQuestion() {
    const question =questions[currentQuestionIndex];
    if (!question) {
        finishInterview();
        return;
    }

    document.getElementById("questionText").textContent = question.q_text;

    document.getElementById("questionType").textContent = question.q_type;

    document.getElementById("questionProgress").textContent =
        `${currentQuestionIndex + 1} / ${questions.length}`;
    audioChunks = [];
    audioBlob = null;

    resetTimer();
    showMessage("", "");
}

async function startRecording() {
    try {
        mediaStream =await navigator.mediaDevices.getUserMedia({
                audio: true
            });
        audioChunks = [];
        audioBlob = null;
        mediaRecorder = new MediaRecorder(
            mediaStream,
            {
                mimeType: "audio/webm;codecs=opus"
            }
        );

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };
        mediaRecorder.onstop = () => {
            audioBlob = new Blob(
                audioChunks,
                {
                    type: "audio/webm;codecs=opus"
                }
            );


            console.log(
                "Audio recorded:",
                audioBlob.size,
                "bytes"
            );
            if (mediaStream) {
                mediaStream.getTracks().forEach(track => track.stop());
            }
            showMessage(
                "Recording ready. Submit your answer.",
                "success"
            );
        };
        mediaRecorder.start();
        startAnswerTimer();
        const startButton =
            document.getElementById("startRecordingBtn");
        const stopButton =
            document.getElementById("stopRecordingBtn");

        startButton.disabled = true;
        stopButton.disabled = false;

        showMessage("Recording...","");
    } catch (error) {
        console.error("Microphone error:",
            error
        );
        showMessage(
            "Unable to access microphone.",
            "error"
        );
    }
}
function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
        mediaRecorder.stop();
    }
    stopAnswerTimer();
    const startButton =document.getElementById("startRecordingBtn");
    const stopButton =document.getElementById("stopRecordingBtn");
    startButton.disabled = false;
    stopButton.disabled = true;
}
async function submitCurrentAnswer() {
    const question = questions[currentQuestionIndex];

    if (!question) {
        return;
    }

    if (!audioBlob) {
        showMessage(
            "Please record your answer first.",
            "error"
        );
        return;
    }

    stopRecording();

    const duration = getElapsedSeconds();

    const submitButton = document.getElementById("submitAnswerBtn");

    submitButton.disabled = true;
    submitButton.textContent = "Transcribing...";

    try {
        console.log("Submitting question ID:", question.id);
        console.log(
            "Current index BEFORE submit:",
            currentQuestionIndex
        );

        // Submit answer to backend
        const data = await submitVoiceAnswer(
            audioBlob,
            question.id,
            duration
        );

        console.log("Answer submitted successfully:", data);

        // Move to next question
        currentQuestionIndex++;
        localStorage.setItem(`qidx_${sessionId}`, currentQuestionIndex); 

        console.log("Current index AFTER submit:", currentQuestionIndex);

        console.log(
            "Current index AFTER submit:",
            currentQuestionIndex
        );

        console.log(
            "Next question:",
            questions[currentQuestionIndex]
        );

        showMessage(
            "Answer submitted successfully.",
            "success"
        );

        // All questions completed
        if (currentQuestionIndex >= questions.length) {
            finishInterview();
            return;
        }

        // Show next question
        setTimeout(() => {
            showQuestion();
        }, 500);

    } catch (error) {
        console.error(
            "Voice answer submission failed:",
            error
        );

        showMessage(
            error.message || "Failed to submit answer.",
            "error"
        );

    } finally {
        submitButton.disabled = false;
        submitButton.textContent = "Submit Answer";
    }
}
function startAnswerTimer() {
    if (timerInterval) {
        return;
    }
    if (!questionStartTime) {
        questionStartTime =Date.now();
    }
    const startButton =document.getElementById("startRecordingBtn");
    const stopButton =document.getElementById("stopRecordingBtn");
    if (startButton) {startButton.disabled = true;}
    if (stopButton) {stopButton.disabled = false;
    }
    timerInterval =setInterval(updateTimer,1000);
    updateTimer();
}
function stopAnswerTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
    const startButton =document.getElementById("startRecordingBtn");
    const stopButton =document.getElementById("stopRecordingBtn");
    if (startButton) {startButton.disabled = false;
    }
    if (stopButton) {stopButton.disabled = true;
    }
}
function updateTimer() {
    const duration =getElapsedSeconds();
    document.getElementById("duration").textContent = duration;
}
function getElapsedSeconds() {
    if (!questionStartTime) {
        return 0;
    }
    return Math.floor(
        (Date.now() - questionStartTime) /
        1000
    );
}
function resetTimer() {
    stopAnswerTimer();
    questionStartTime = null;
    document.getElementById("duration").textContent = "0";
}
function finishInterview() {
    stopRecording();
    localStorage.removeItem(`qidx_${sessionId}`)
    showMessage("Interview completed.","success");
    setTimeout(() => {
        window.location.href =`report.html?session_id=${sessionId}`;
    }, 1000);
}
function showMessage(text, type) {
    const message =document.getElementById("interviewMessage" );
    if (!message) {
        return;
    }
    message.textContent = text;
    message.className = "message";
    if (type) {
        message.classList.add(type);
    }
}