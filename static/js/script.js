document.addEventListener("DOMContentLoaded", function () {
    const formTitle = document.getElementById("form-title");
    const authForm = document.getElementById("auth-form");
    const toggleFormLink = document.getElementById("toggle-form");

    const signupFields = document.getElementById("signup-fields");
    const loginFields = document.getElementById("login-fields");
    const generatedIdMessage = document.getElementById("generated-id-message");

    let isSignup = false;

    function generateAppID() {
        return "APP-" + Math.floor(100000 + Math.random() * 900000);
    }

    toggleFormLink.addEventListener("click", function (e) {
        e.preventDefault();
        isSignup = !isSignup;

        if (isSignup) {
            formTitle.textContent = "Signup";
            toggleFormLink.textContent = "Already have an account? Login";
            signupFields.classList.remove("hidden");
            loginFields.classList.add("hidden");
        } else {
            formTitle.textContent = "Login";
            toggleFormLink.textContent = "Don't have an account? Signup";
            signupFields.classList.add("hidden");
            loginFields.classList.remove("hidden");
            generatedIdMessage.classList.add("hidden");
        }
    });

    authForm.addEventListener("submit", function (e) {
        e.preventDefault();

        if (isSignup) {
            const name = document.getElementById("name").value;
            const role = document.getElementById("role").value;
            const password = document.getElementById("signup-password").value;
            const newAppID = generateAppID();

            if (!name || !password) {
                alert("Please fill all fields!");
                return;
            }

            let users = JSON.parse(localStorage.getItem("users")) || [];
            users.push({ name, appID: newAppID, password, role });
            localStorage.setItem("users", JSON.stringify(users));

            generatedIdMessage.textContent = `Signup Successful! Your Application ID: ${newAppID}`;
            generatedIdMessage.classList.remove("hidden");

            isSignup = false;
            signupFields.classList.add("hidden");
            loginFields.classList.remove("hidden");
            formTitle.textContent = "Login";
            toggleFormLink.textContent = "Don't have an account? Signup";
        } else {
            const appID = document.getElementById("appID").value;
            const password = document.getElementById("login-password").value;

            let users = JSON.parse(localStorage.getItem("users")) || [];
            let user = users.find(u => u.appID === appID && u.password === password);

            if (user) {
                alert(`Login Successful! Welcome ${user.name} (${user.role})`);
                sessionStorage.setItem("loggedInUser", JSON.stringify(user));

                if (user.role === "admin") {
                    window.location.href = "admin-dashboard.html";
                } else if (user.role === "teacher") {
                    window.location.href = "teacher-dashboard.html";
                } else {
                    window.location.href = "student-dashboard.html";
                }
            } else {
                alert("Invalid Application ID or Password!");
            }
        }
    });
});
