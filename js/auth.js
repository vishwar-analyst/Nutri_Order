const API_BASE_URL = window.NUTRIORDER_API_BASE || `http://${window.location.hostname}:5000`;
const authMessage = document.getElementById("authMessage");

function showAuthMessage(text, kind = "") {
    if (!authMessage) return;
    authMessage.textContent = text;
    authMessage.className = `auth-message ${kind}`.trim();
}

function setBusy(button, busy, label) {
    if (!button) return;
    button.disabled = busy;
    button.classList.toggle("is-loading", busy);
    button.querySelector("span").textContent = busy ? "Please wait…" : label;
}

async function sendJson(path, payload) {
    const response = await fetch(`${API_BASE_URL}${path}`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok || !data.success) {
        const error = new Error(data.message || "Something went wrong. Please try again.");
        error.status = response.status;
        throw error;
    }
    return data;
}

function saveUserAndRedirect(data) {
    if (data.user) localStorage.setItem("user", JSON.stringify(data.user));
    window.location.assign(data.redirect_url || "/frontend/customer.html");
}

function setError(error) {
    showAuthMessage(error.status === 0
        ? `Cannot connect to NutriOrder at ${API_BASE_URL}. Start the Flask server and try again.`
        : error.message, "error");
}

function configurePasswordToggles() {
    document.querySelectorAll("[data-password-toggle]").forEach(button => {
        button.addEventListener("click", () => {
            const input = document.getElementById(button.dataset.passwordToggle);
            if (!input) return;
            const show = input.type === "password";
            input.type = show ? "text" : "password";
            button.setAttribute("aria-pressed", String(show));
            button.setAttribute("aria-label", show ? "Hide password" : "Show password");
        });
    });
}

function validEmail(value) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

function configureLogin() {
    const form = document.getElementById("loginForm");
    form.addEventListener("submit", async event => {
        event.preventDefault();
        const identifier = document.getElementById("identifier").value.trim();
        const password = document.getElementById("password").value;
        const remember = document.getElementById("rememberMe")?.checked || false;
        const button = document.getElementById("loginButton");
        if (!identifier || identifier.length > 254) return showAuthMessage("Enter your email address or username.", "error");
        if (!password) return showAuthMessage("Enter your password.", "error");

        setBusy(button, true, "Sign in");
        showAuthMessage("Signing you in securely…", "pending");
        try {
            const data = await sendJson("/api/login", { identifier, password, remember });
            saveUserAndRedirect(data);
        } catch (error) {
            error.status = error.status || 0;
            setError(error);
        } finally {
            setBusy(button, false, "Sign in");
        }
    });
}

function configureRegister() {
    const form = document.getElementById("registerForm");
    form.addEventListener("submit", async event => {
        event.preventDefault();
        const full_name = document.getElementById("fullName").value.trim();
        const email = document.getElementById("email").value.trim().toLowerCase();
        const phone = document.getElementById("phone").value.trim();
        const password = document.getElementById("password").value;
        const confirmPassword = document.getElementById("confirmPassword").value;
        const button = document.getElementById("registerButton");

        if (!full_name) return showAuthMessage("Enter your full name.", "error");
        if (!validEmail(email)) return showAuthMessage("Enter a valid email address.", "error");
        if (!/^[+0-9()\-\s]{7,20}$/.test(phone)) return showAuthMessage("Enter a valid phone number.", "error");
        if (password.length < 10 || !/[A-Za-z]/.test(password) || !/[0-9]/.test(password)) {
            return showAuthMessage("Use at least 10 characters with a letter and a number.", "error");
        }
        if (password !== confirmPassword) return showAuthMessage("Your passwords do not match.", "error");
        if (!document.getElementById("termsAccepted").checked) return showAuthMessage("Please accept the Terms and Privacy Policy to continue.", "error");

        setBusy(button, true, "Create account");
        showAuthMessage("Creating your NutriOrder account…", "pending");
        try {
            const data = await sendJson("/api/register", { full_name, email, phone, password });
            saveUserAndRedirect(data);
        } catch (error) {
            error.status = error.status || 0;
            setError(error);
        } finally {
            setBusy(button, false, "Create account");
        }
    });
}

function configureForgotPassword() {
    document.getElementById("forgotForm").addEventListener("submit", async event => {
        event.preventDefault();
        const email = document.getElementById("email").value.trim().toLowerCase();
        const button = document.getElementById("forgotButton");
        if (!validEmail(email)) return showAuthMessage("Enter a valid email address.", "error");
        setBusy(button, true, "Send reset link");
        showAuthMessage("Requesting password reset…", "pending");
        try {
            const data = await sendJson("/api/forgot-password", { email });
            showAuthMessage(data.message, "success");
        } catch (error) {
            error.status = error.status || 0;
            setError(error);
        } finally {
            setBusy(button, false, "Send reset link");
        }
    });
}

function configureResetPassword() {
    const form = document.getElementById("resetForm");
    const token = new URLSearchParams(window.location.search).get("token");
    if (!token) {
        showAuthMessage("This reset link is invalid or missing. Request a new one.", "error");
        document.getElementById("resetButton").disabled = true;
    }
    form.addEventListener("submit", async event => {
        event.preventDefault();
        const password = document.getElementById("password").value;
        const confirmPassword = document.getElementById("confirmPassword").value;
        const button = document.getElementById("resetButton");
        if (!token) return showAuthMessage("Request a new password reset link.", "error");
        if (password.length < 10 || !/[A-Za-z]/.test(password) || !/[0-9]/.test(password)) {
            return showAuthMessage("Use at least 10 characters with a letter and a number.", "error");
        }
        if (password !== confirmPassword) return showAuthMessage("Your passwords do not match.", "error");
        setBusy(button, true, "Update password");
        showAuthMessage("Updating your password securely…", "pending");
        try {
            const data = await sendJson("/api/reset-password", { token, password });
            showAuthMessage(data.message, "success");
            window.setTimeout(() => window.location.assign("login.html"), 1500);
        } catch (error) {
            error.status = error.status || 0;
            setError(error);
        } finally {
            setBusy(button, false, "Update password");
        }
    });
}

configurePasswordToggles();
const authPage = document.body.dataset.authPage;
if (authPage === "login") configureLogin();
if (authPage === "register") configureRegister();
if (authPage === "forgot") configureForgotPassword();
if (authPage === "reset") configureResetPassword();