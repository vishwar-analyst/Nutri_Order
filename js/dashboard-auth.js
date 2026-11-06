const dashboardApi = window.NUTRIORDER_API_BASE || `http://${window.location.hostname}:5000`;

async function requireRole(allowedRoles) {
    try {
        const response = await fetch(`${dashboardApi}/api/me`, { credentials: "include" });
        if (!response.ok) throw new Error("Sign in required");
        const data = await response.json();
        if (!data.success || !allowedRoles.includes(data.user.role)) throw new Error("Role not permitted");
        localStorage.setItem("user", JSON.stringify(data.user));
        return data.user;
    } catch {
        localStorage.removeItem("user");
        window.location.replace("/frontend/login.html");
        return null;
    }
}

async function signOut() {
    try {
        await fetch(`${dashboardApi}/api/logout`, { method: "POST", credentials: "include" });
    } finally {
        localStorage.removeItem("user");
        window.location.assign("/frontend/login.html");
    }
}
