// document.addEventListener("DOMContentLoaded", function () {
//     const questionsContainer = document.getElementById("questionsContainer");
//     const answersTable = document.getElementById("answersTable");
//     const logoutBtn = document.getElementById("logoutBtn");
//     const token = sessionStorage.getItem("accessToken");
  
//     // Load Questions Based on User Selection
//     window.loadQuestions = async function () {
//       const limitInput = document.getElementById("numQuestions");
//       const limit = parseInt(limitInput.value);
  
//       if (isNaN(limit) || limit < 1 || limit > 50) {
//         alert("Please select a valid number between 1 and 50.");
//         return;
//       }
  
//       questionsContainer.innerHTML = `<p class="text-gray-500">Loading ${limit} questions...</p>`;
  
//       try {
//         const response = await fetch(`/api/questions/?limit=${limit}`, {
//           headers: {
//             "Authorization": "Bearer " + token
//           },
//         });
  
//         if (response.ok) {
//           const questions = await response.json();
//           questionsContainer.innerHTML = "";
  
//           questions.forEach((question) => {
//             const div = document.createElement("div");
//             div.className = "mb-4 p-4 border rounded bg-gray-100";
//             div.innerHTML = `
//               <p class="font-semibold">${question.text}</p>
//               <textarea id="answer-${question.id}" placeholder="Enter your answer" class="w-full p-2 border rounded mt-2"></textarea>
//               <button onclick="submitAnswer(${question.id})" class="bg-blue-500 text-white px-4 py-2 rounded mt-2 hover:bg-blue-600 transition">Submit</button>
//             `;
//             questionsContainer.appendChild(div);
//           });
  
//           if (questions.length === 0) {
//             questionsContainer.innerHTML = "<p class='text-gray-500'>No questions found.</p>";
//           }
  
//         } else {
//           questionsContainer.innerHTML = "<p class='text-red-500'>Failed to load questions.</p>";
//         }
//       } catch (err) {
//         questionsContainer.innerHTML = "<p class='text-red-500'>Error loading questions.</p>";
//         console.error(err);
//       }
//     };
  
//     // Load Submitted Answers
//     async function loadAnswers() {
//       try {
//         const response = await fetch("/api/submitted-answers/", {
//           headers: { "Authorization": "Bearer " + token },
//         });
  
//         if (response.ok) {
//           const answers = await response.json();
//           answersTable.innerHTML = "";
  
//           answers.forEach((ans) => {
//             const row = document.createElement("tr");
//             row.innerHTML = `
//               <td class="border p-2">${ans.question_text}</td>
//               <td class="border p-2">${ans.answer_text}</td>
//               <td class="border p-2 text-blue-700">${ans.ai_feedback || "Pending"}</td>
//               <td class="border p-2 text-green-700">${ans.teacher_feedback || "Not Reviewed"}</td>
//               <td class="border p-2 font-semibold">${ans.grade || "N/A"}</td>
//             `;
//             answersTable.appendChild(row);
//           });
  
//         } else {
//           answersTable.innerHTML = "<tr><td colspan='5' class='p-2 text-red-500'>Failed to load answers.</td></tr>";
//         }
//       } catch (err) {
//         answersTable.innerHTML = "<tr><td colspan='5' class='p-2 text-red-500'>Error loading answers.</td></tr>";
//         console.error(err);
//       }
//     }
  
//     // Submit Answer
//     window.submitAnswer = async function (questionId) {
//       const answerInput = document.getElementById(`answer-${questionId}`);
//       const answerText = answerInput.value.trim();
  
//       if (!answerText) {
//         alert("Please enter an answer before submitting.");
//         return;
//       }
  
//       try {
//         const response = await fetch("/api/submitted-answers/", {
//           method: "POST",
//           headers: {
//             "Content-Type": "application/json",
//             "Authorization": "Bearer " + token
//           },
//           body: JSON.stringify({
//             question: questionId,
//             answer_text: answerText,
//           }),
//         });
  
//         if (response.ok) {
//           alert("Answer submitted successfully!");
//           answerInput.value = "";
//           loadAnswers();
//         } else {
//           alert("Submission failed.");
//         }
//       } catch (err) {
//         alert("Error: " + err);
//       }
//     };
  
//     // Logout
//     logoutBtn.addEventListener("click", function () {
//       sessionStorage.clear();
//       window.location.href = "/";
//     });
  
//     // Initial load of previously submitted answers
//     loadAnswers();
//   });
// app.js (Student Page - student.html)
document.addEventListener('DOMContentLoaded', function() {
    // Add event listener to the form for submitting answers
    document.getElementById('student-form').addEventListener('submit', function(event) {
        event.preventDefault();

        let answers = [];
        let answerElements = document.querySelectorAll('.student-answer');
        
        answerElements.forEach((answerElement) => {
            answers.push(answerElement.value);  // Get all student answers
        });

        // Send student answers to the backend
        fetch('/student', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                answers: answers
            })
        })
        .then(response => response.json())
        .then(data => {
            // Display the result after receiving the evaluation
            document.getElementById('result').innerHTML = `Your score: ${data.marks}%`;
        })
        .catch(error => console.error('Error:', error));
    });
});
