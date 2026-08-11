// ======================================================
// REPORT.JS
// ======================================================

document.addEventListener("DOMContentLoaded", async () => {

    if (!isLoggedIn()) {
        window.location.href = "login.html";
        return;
    }

    setupLogout();

    const sessionId = getSessionIdFromUrl();

    if (!sessionId) {
        showReportMessage(
            "Session ID not found.",
            "error"
        );
        return;
    }

    await loadFullReport(sessionId);
});


// ======================================================
// SESSION ID
// ======================================================

function getSessionIdFromUrl() {

    const params =
        new URLSearchParams(
            window.location.search
        );

    return params.get("session_id");
}


// ======================================================
// LOAD FULL REPORT
// ======================================================

async function loadFullReport(sessionId) {

    try {

        showReportMessage(
            "Loading report...",
            ""
        );


        const data =
            await getFullReport(sessionId);


        if (!data) {
            throw new Error(
                "Empty report response."
            );
        }


        renderCandidate(data.candidate);

        renderSession(data.session);

        renderReport(data.report);

        renderQuestions(data.questions);


        showReportMessage("", "");


    } catch (error) {

        console.error(
            "Failed to load report:",
            error
        );


        showReportMessage(
            error.message,
            "error"
        );
    }
}


// ======================================================
// CANDIDATE
// ======================================================

function renderCandidate(candidate) {

    if (!candidate) {
        return;
    }


    const name =
        document.getElementById(
            "candidateName"
        );

    const email =
        document.getElementById(
            "candidateEmail"
        );


    if (name) {
        name.textContent =
            candidate.name ?? "--";
    }


    if (email) {
        email.textContent =
            candidate.email ?? "--";
    }
}


// ======================================================
// SESSION
// ======================================================

function renderSession(session) {

    if (!session) {
        return;
    }


    const sessionId =
        document.getElementById(
            "sessionId"
        );

    const status =
        document.getElementById(
            "sessionStatus"
        );

    const questions =
        document.getElementById(
            "sessionQuestions"
        );

    const score =
        document.getElementById(
            "sessionScore"
        );

    const startedAt =
        document.getElementById(
            "startedAt"
        );

    const completedAt =
        document.getElementById(
            "completedAt"
        );


    if (sessionId) {
        sessionId.textContent =
            session.id ?? "--";
    }


    if (status) {
        status.textContent =
            session.status ?? "--";
    }


    if (questions) {
        questions.textContent =
            session.num_questions ?? "--";
    }


    if (score) {
        score.textContent =
            session.total_score ?? "--";
    }


    if (startedAt) {
        startedAt.textContent =
            formatDate(session.started_at);
    }


    if (completedAt) {
        completedAt.textContent =
            formatDate(session.completed_at);
    }
}


// ======================================================
// REPORT
// ======================================================

function renderReport(report) {

    if (!report) {
        return;
    }


    const avgScore =
        document.getElementById(
            "avgScore"
        );

    const totalQuestions =
        document.getElementById(
            "totalQuestions"
        );

    const answered =
        document.getElementById(
            "answered"
        );

    const strengths =
        document.getElementById(
            "strengthsSummary"
        );

    const weaknesses =
        document.getElementById(
            "weaknessesSummary"
        );

    const recommendation =
        document.getElementById(
            "hiringRecommendation"
        );

    const feedback =
        document.getElementById(
            "overallFeedback"
        );


    if (avgScore) {
        avgScore.textContent =
            report.avg_score ?? "--";
    }


    if (totalQuestions) {
        totalQuestions.textContent =
            report.total_questions ?? "--";
    }


    if (answered) {
        answered.textContent =
            report.answered ?? "--";
    }


    if (strengths) {
        strengths.textContent =
            report.strengths_summary ?? "--";
    }


    if (weaknesses) {
        weaknesses.textContent =
            report.weaknesses_summary ?? "--";
    }


    if (recommendation) {
        recommendation.textContent =
            report.hiring_recommendation ?? "--";
    }


    if (feedback) {
        feedback.textContent =
            report.overall_feedback ?? "--";
    }
}


// ======================================================
// QUESTIONS
// ======================================================

function renderQuestions(questions) {

    const container =
        document.getElementById(
            "questionsContainer"
        );


    if (!container) {
        return;
    }


    container.innerHTML = "";


    if (
        !Array.isArray(questions) ||
        questions.length === 0
    ) {

        container.innerHTML =
            "<p>No questions found.</p>";

        return;
    }


    questions.forEach(
        (question, index) => {

            const questionCard =
                document.createElement(
                    "div"
                );


            questionCard.className =
                "question-report-card";


            questionCard.innerHTML = `
                <div class="question-report-header">

                    <h3>
                        Question ${question.q_index ?? index + 1}
                    </h3>

                    <span>
                        ${escapeHtml(question.q_type ?? "")}
                    </span>

                </div>

                <p class="report-question">
                    ${escapeHtml(question.q_text ?? "")}
                </p>

                <div class="answers-container">
                </div>
            `;


            const answersContainer =
                questionCard.querySelector(
                    ".answers-container"
                );


            const answers =
                question.answers_with_evals;


            if (
                !Array.isArray(answers) ||
                answers.length === 0
            ) {

                answersContainer.innerHTML =
                    "<p>No answer submitted.</p>";

            } else {

                answers.forEach(
                    answerWithEval => {

                        renderAnswer(
                            answerWithEval,
                            answersContainer
                        );

                    }
                );
            }


            container.appendChild(
                questionCard
            );
        }
    );
}


// ======================================================
// ANSWER + EVALUATION
// ======================================================

function renderAnswer(
    answerWithEval,
    container
) {

    const answer =
        answerWithEval.answer;

    const evaluation =
        answerWithEval.evaluation;


    const answerElement =
        document.createElement(
            "div"
        );


    answerElement.className =
        "answer-report";


    let evaluationHTML =
        "<p>No evaluation available.</p>";


    if (evaluation) {

        evaluationHTML = `
            <div class="evaluation">

                <p>
                    <strong>Score:</strong>
                    ${evaluation.score ?? "--"}
                </p>

                <p>
                    <strong>Rating:</strong>
                    ${escapeHtml(evaluation.rating ?? "--")}
                </p>

                <p>
                    <strong>Feedback:</strong>
                    ${escapeHtml(evaluation.feedback ?? "--")}
                </p>

                <p>
                    <strong>Strengths:</strong>
                    ${escapeHtml(evaluation.strengths ?? "--")}
                </p>

                <p>
                    <strong>Improvements:</strong>
                    ${escapeHtml(evaluation.improvements ?? "--")}
                </p>

            </div>
        `;
    }


    answerElement.innerHTML = `

        <div class="answer">

            <h4>Your Answer</h4>

            <p>
                ${escapeHtml(answer?.transcript ?? "--")}
            </p>

            <p>
                <strong>Duration:</strong>
                ${answer?.duration_s ?? "--"} seconds
            </p>

            <p>
                <strong>Submitted:</strong>
                ${formatDate(answer?.submitted_at)}
            </p>

        </div>

        ${evaluationHTML}
    `;


    container.appendChild(
        answerElement
    );
}


// ======================================================
// DATE FORMAT
// ======================================================

function formatDate(value) {

    if (!value) {
        return "--";
    }


    const date =
        new Date(value);


    if (Number.isNaN(date.getTime())) {
        return value;
    }


    return date.toLocaleString();
}


// ======================================================
// HTML ESCAPE
// ======================================================

function escapeHtml(value) {

    const div =
        document.createElement("div");

    div.textContent =
        String(value);

    return div.innerHTML;
}


// ======================================================
// LOGOUT
// ======================================================

function setupLogout() {

    const logoutButton =
        document.getElementById(
            "logoutBtn"
        );


    if (logoutButton) {

        logoutButton.addEventListener(
            "click",
            logout
        );
    }
}


// ======================================================
// MESSAGE
// ======================================================

function showReportMessage(
    text,
    type
) {

    const message =
        document.getElementById(
            "reportMessage"
        );


    if (!message) {
        return;
    }


    message.textContent =
        text;

    message.className =
        "message";


    if (type) {
        message.classList.add(type);
    }
}