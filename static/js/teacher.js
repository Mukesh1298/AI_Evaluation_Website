// document.addEventListener("DOMContentLoaded", function () {
//     const questionInput = document.getElementById("questionInput");
//     const addQuestionForm = document.getElementById("addQuestionForm");
//     const questionSelect = document.getElementById("questionSelect");
//     const questionList = document.getElementById("questionList");

//     let questions = JSON.parse(localStorage.getItem("questions")) || [];

//     function loadQuestions() {
//         questionList.innerHTML = "";
//         questionSelect.innerHTML = `<option value="">Select a Question</option>`;

//         questions.forEach((question, index) => {
         
//             let option = document.createElement("option");
//             option.value = question.id;
//             option.textContent = question.text;
//             questionSelect.appendChild(option);

//             let questionDiv = document.createElement("div");
//             questionDiv.classList.add("flex", "justify-between", "items-center", "p-2", "border", "rounded", "mb-2", "bg-gray-100");

//             questionDiv.innerHTML = `
//                 <input type="text" id="editQuestion-${question.id}" value="${question.text}" class="border p-1 rounded w-3/4">
//                 <div>
//                     <button onclick="editQuestion(${question.id})" class="bg-yellow-500 text-white px-3 py-1 rounded mr-2">Edit</button>
//                     <button onclick="deleteQuestion(${question.id})" class="bg-red-500 text-white px-3 py-1 rounded">Delete</button>
//                 </div>
//             `;

//             questionList.appendChild(questionDiv);
//         });

//         localStorage.setItem("questions", JSON.stringify(questions));
//     }

//     addQuestionForm.addEventListener("submit", function (e) {
//         e.preventDefault();
//         let questionText = questionInput.value.trim();

//         if (!questionText) {
//             alert("Please enter a question.");
//             return;
//         }

//         let newQuestion = { id: Date.now(), text: questionText };
//         questions.push(newQuestion);

//         localStorage.setItem("questions", JSON.stringify(questions));
//         questionInput.value = "";
//         loadQuestions();
//     });

//     window.editQuestion = function (questionId) {
//         let editInput = document.getElementById(`editQuestion-${questionId}`);
//         let updatedText = editInput.value.trim();

//         if (!updatedText) {
//             alert("Question cannot be empty.");
//             return;
//         }

//         let questionIndex = questions.findIndex(q => q.id === questionId);
//         if (questionIndex !== -1) {
//             questions[questionIndex].text = updatedText;
//             localStorage.setItem("questions", JSON.stringify(questions));
//             alert("Question updated successfully!");
//             loadQuestions();
//         }
//     };

//         logoutBtn.addEventListener("click", function () {
//             sessionStorage.removeItem("loggedInUser");
//             window.location.href = "index.html";
//         });

//     window.deleteQuestion = function (questionId) {
//         if (confirm("Are you sure you want to delete this question?")) {
//             questions = questions.filter(q => q.id !== questionId);
//             localStorage.setItem("questions", JSON.stringify(questions));
//             loadQuestions();
//         }
//     };

//     loadQuestions();
// });
// app.js (Teacher Page - teacher.html)
document.addEventListener('DOMContentLoaded', function() {
    // Add event listener to the form for adding questions
    document.getElementById('question-form').addEventListener('submit', function(event) {
        event.preventDefault();

        let question = document.getElementById('question-input').value;
        let answer = document.getElementById('answer-input').value;

        // Send data to backend using Fetch API
        fetch('/teacher', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question: question,
                answer: answer
            })
        })
        .then(response => response.json())
        .then(data => {
            // Clear the form and update the list of questions
            document.getElementById('question-input').value = '';
            document.getElementById('answer-input').value = '';
            loadQuestions();  // Reload questions from the server
        })
        .catch(error => console.error('Error:', error));
    });

    // Load questions dynamically
    function loadQuestions() {
        fetch('/teacher')
            .then(response => response.json())
            .then(data => {
                let questionsList = document.getElementById('questions-list');
                questionsList.innerHTML = '';
                data.forEach(question => {
                    let li = document.createElement('li');
                    li.textContent = `${question.question} - Answer: ${question.answer}`;
                    questionsList.appendChild(li);
                });
            })
            .catch(error => console.error('Error:', error));
    }

    loadQuestions();
});

