// Login and Registration
document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit",handleLogin);
    }
    const registerForm =document.getElementById("registerForm");
    if (registerForm) {registerForm.addEventListener("submit",handleRegister);
    }
});
// LOGIN
async function handleLogin(event) {
    event.preventDefault();
    const email =
        document.getElementById("email").value.trim();
    const password =
        document.getElementById("password").value;
    const loginBtn =
        document.getElementById("loginBtn");
    const message =
        document.getElementById("loginMessage");
    message.textContent = "";
    message.className = "message";
    loginBtn.disabled = true;
    loginBtn.textContent = "Logging in...";
    try {const data = await login(email,password);
        saveAuth(data);
        message.textContent =
            "Login successful.";
        message.classList.add("success");
        // Go to dashboard
        setTimeout(() => {window.location.href ="dashboard.html";}, 500);
    } catch (error) {
        console.error("Login failed:",error);
        message.textContent =error.message;
        message.classList.add("error");
    } finally {
        loginBtn.disabled = false;
        loginBtn.textContent = "Login";
    }
}
// REGISTER
async function handleRegister(event) {
    event.preventDefault();
    const registerBtn =
        document.getElementById("registerBtn");
    const message =
        document.getElementById("registerMessage");
    message.textContent = "";
    message.className = "message";
    registerBtn.disabled = true;
    registerBtn.textContent ="Creating account...";
    try {
        const formData = new FormData();
        formData.append("name",
            document.getElementById("name").value.trim());
        formData.append("email",
            document.getElementById("email").value.trim()
        );
        formData.append("password",
            document.getElementById("password").value
        );
        formData.append("target_role",
            document.getElementById("target_role").value.trim()
        );
        const resumeInput =document.getElementById("resume");
        if (!resumeInput.files ||resumeInput.files.length === 0) {
            throw new Error("Please select a resume.");

        }
        formData.append("resume",
            resumeInput.files[0]
        );
        const data =await registerCandidate(formData);
        console.log("Candidate registered:",data);
        message.textContent ="Account created successfully.";
        message.classList.add("success");
        setTimeout(() => {window.location.href ="login.html";}, 800);
    } catch (error) {
        console.error("Registration failed:", error);
        message.textContent =error.message;
        message.classList.add("error");
    } finally {
        registerBtn.disabled = false;
        registerBtn.textContent ="Create Account";
    }
}