// Example JavaScript code to call your API
async function generateQuestionBank(topic, difficulty, count) {
    const response = await fetch('http://127.0.0.1:5000/generate_question_bank', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            topic: topic,
            difficulty: difficulty,
            count: count
        })
    });
    
    const data = await response.json();
    return data;
}

// Usage
const questionBank = await generateQuestionBank('Physics', 'Hard', 50);
console.log(`Generated ${questionBank.total_questions} questions!`);