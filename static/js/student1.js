let questions = [];
let currentIndex = 0;

window.onload = async function () {
  const res = await fetch('/get_questions');
  questions = await res.json();
  showQuestion();
};

function showQuestion() {
  if (currentIndex < questions.length) {
    document.getElementById("questionText").innerText = questions[currentIndex].question;
    document.getElementById("studentAnswer").value = "";
  } else {
    document.getElementById("quizSection").style.display = "none";
    document.getElementById("thankYou").style.display = "block";
  }
}

async function submitAnswer() {
  const answer = document.getElementById("studentAnswer").value.trim();
  if (!answer) {
    alert("Please enter your answer.");
    return;
  }

  const questionId = questions[currentIndex].id;

  await fetch('/submit_answer', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ question_id: questionId, answer: answer })
  });

  currentIndex++;
  showQuestion();
}
