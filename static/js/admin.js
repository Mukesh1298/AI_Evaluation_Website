document.addEventListener("DOMContentLoaded", function () {
    const userTable = document.getElementById("userTable");
    const logoutBtn = document.getElementById("logoutBtn");

    let users = JSON.parse(localStorage.getItem("users")) || [
        { id: 1, name: "Alice Johnson", role: "Teacher" },
        { id: 2, name: "Bob Smith", role: "Student" },
        { id: 3, name: "Charlie Brown", role: "Student" }
    ];

    if (!localStorage.getItem("users")) {
        localStorage.setItem("users", JSON.stringify(users));
    }

    function loadUsers() {
        userTable.innerHTML = "";
        users.forEach((user, index) => {
            let row = document.createElement("tr");
            row.innerHTML = `
                <td class="border p-2">${user.id}</td>
                <td class="border p-2">${user.name}</td>
                <td class="border p-2">${user.role}</td>
                <td class="border p-2">
                    <button onclick="removeUser(${index})" class="bg-red-500 px-2 py-1 text-white rounded">Remove</button>
                </td>
            `;
            userTable.appendChild(row);
        });
    }

    window.removeUser = function (index) {
        if (confirm("Are you sure you want to remove this user?")) {
            users.splice(index, 1);
            localStorage.setItem("users", JSON.stringify(users));
            loadUsers();
        }
    };

    logoutBtn.addEventListener("click", function () {
        sessionStorage.removeItem("loggedInUser");
        window.location.href = "index.html";
    });

    loadUsers();
});
