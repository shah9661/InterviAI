document.addEventListener("DOMContentLoaded", () => {
    if (!isLoggedIn()) {
        window.location.href = "login.html";
        return;
    }
    loadCandidateInfo();
    setupDashboard();
});
// CANDIDATE INFO
function loadCandidateInfo() {
    const candidateName =getCandidateName();
    const nameElement =document.getElementById("candidateName");
    if (nameElement && candidateName) {
        nameElement.textContent = candidateName;
    }
}
// DASHBOARD EVENTS
function setupDashboard() {
    const startButton = document.getElementById("startInterviewBtn"
        );
    const logoutButton =document.getElementById("logoutBtn"
        );
    if (startButton) {
        startButton.addEventListener("click",handleStartInterview
        );
    }
    if (logoutButton) {
        logoutButton.addEventListener("click",logout
        );
    }
}
// START INTERVIEW
async function handleStartInterview() {
    const candidateId =getCandidateId();
    const numQuestions =Number(document.getElementById("numQuestions").value
        );
    const startButton =document.getElementById("startInterviewBtn"
        );
    if (!candidateId) {
        showDashboardMessage("Candidate information not found.","error"
        );
        return;
    }
    if (!numQuestions) {
        showDashboardMessage("Please select number of questions.","error"
        );
        return;
    }
    startButton.disabled = true;
    startButton.textContent ="Starting Interview...";
    try {
        const session =await startInterview(candidateId,numQuestions
            );
        if (!session || !session.id) {
            throw new Error("Invalid interview session response."
            );
        }
        localStorage.setItem("session_id",session.id
        );
        showDashboardMessage("Generating interview questions...",""
        );
        await generateQuestions(session.id,candidateId,numQuestions
        );
        window.location.href ="interview.html";
    } catch (error) {
        console.error("Failed to start interview:",error
        );
        showDashboardMessage(error.message,"error"
        );
        startButton.disabled = false;
        startButton.textContent = "Start Interview";
    }
}
// MESSAGE
function showDashboardMessage(text,type) {
    const message =document.getElementById("dashboardMessage"
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