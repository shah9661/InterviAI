const API_BASE_URL = "http://127.0.0.1:8000";
// COMMON API REQUEST
async function apiRequest(endpoint, options = {}) {
    const token = localStorage.getItem("access_token");
    const headers = {...options.headers};
    if (options.body &&!(options.body instanceof FormData)) {
        headers["Content-Type"] = "application/json";
    }
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }
    const response = await fetch(`${API_BASE_URL}${endpoint}`,{...options,headers});
    const data = await response.json().catch(() => null);
    if (!response.ok) {throw new Error(
            data?.detail || `Request failed: ${response.status}`);
    }
    return data;
}
// AUTH
async function login(email, password) {
    return await apiRequest("/auth/login", {method: "POST",
        body: JSON.stringify({email: email,password: password})});
}
function saveAuth(tokenData) {
    localStorage.setItem("access_token",tokenData.access_token);
    localStorage.setItem("token_type",tokenData.token_type);
    localStorage.setItem("candidate_id",tokenData.candidate_id);
    localStorage.setItem("candidate_name",tokenData.name);
}


function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("token_type");
    localStorage.removeItem("candidate_id");
    localStorage.removeItem("candidate_name");
    window.location.href = "login.html";
}

function getToken() {return localStorage.getItem("access_token");}
function getCandidateId() {
    return localStorage.getItem("candidate_id");}
function getCandidateName() {
    return localStorage.getItem("candidate_name");}

function isLoggedIn() {
    return !!getToken();
}

// CANDIDATE REGISTRATION
async function registerCandidate(formData) {
    return await apiRequest("/candidates", {method: "POST",body: formData});
}
// INTERVIEW
async function startInterview(candidateId,numQuestions
) {
    const params = new URLSearchParams({candidate_id: candidateId, num_questions: numQuestions});
    return await apiRequest(`/interviews/start?${params.toString()}`,{method: "POST"});
}
// GENERATE QUESTIONS
async function generateQuestions(sessionId,candidateId,numQuestions
) {const params = new URLSearchParams({candidate_id: candidateId,num_questions: numQuestions});
    return await apiRequest(
        `/sessions/${sessionId}/generate-questions?${params.toString()}`,{
            method: "POST"}
    );
}
// GET SESSION QUESTIONS
async function getQuestions(sessionId) {
    return await apiRequest( `/sessions/${sessionId}/questions`,{method: "GET"});
}
// SUBMIT ANSWER
async function submitAnswer(questionId,transcript,durationSeconds
) {return await apiRequest("/answers/submit",{
            method: "POST",
            body: JSON.stringify({
                question_id: questionId,
                transcript: transcript,
                duration_s: durationSeconds
            })
        }
    );
}
// REPORT
async function getReport(sessionId) {
    return await apiRequest(`/interviews/${sessionId}/report`,
        {
            method: "GET"
        }
    );
}
async function getFullReport(sessionId) {
    return await apiRequest(`/interviews/${sessionId}/report/full`,
        {
            method: "GET"
        }
    );
}

// SUBMIT VOICE ANSWER
async function submitVoiceAnswer(audioBlob,questionId,durationSeconds) {
    const formData = new FormData();
    formData.append("file",audioBlob,"answer.webm");
    formData.append("question_id",questionId);
    formData.append("duration_s",durationSeconds);
    return await apiRequest("/voice/submit",
        {
            method: "POST",
            body: formData
        }
    );
}