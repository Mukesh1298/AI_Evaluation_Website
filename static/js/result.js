async function loadResult() {
    const res = await fetch("/api/result");
    const data = await res.json();
    document.getElementById("score").innerText =
        `You scored ${data.correct} out of ${data.total}`;
}

loadResult();
