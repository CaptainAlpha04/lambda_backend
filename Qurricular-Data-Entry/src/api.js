// API functions

const API_BASE = 'http://localhost:8000/api'; // Adjust if needed

export const uploadBook = async (userId, file) => {
  const formData = new FormData();
  formData.append('userId', userId);
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/exercise/upload-book`, {
    method: 'POST',
    body: formData,
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to upload book');
  }
  return data;
};

export const generateExercises = async (
  topic,
  exerciseType,
  numQuestions,
  useBookContext = false,
  userId = null // Add userId for backend
) => {
  const endpoint = useBookContext
    ? `${API_BASE}/exercise/generate`
    : `${API_BASE}/exercise/generate-simple`;
  const payload = {
    userId,
    topic,
    exercise_type: exerciseType,
    num_questions: numQuestions,
  };
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to generate exercises');
  }
  return data;
};

export const askQuestion = async (userId, question) => {
  const payload = { userId, question };
  const response = await fetch(`${API_BASE}/exercise/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to get answer');
  }
  return data;
};

export const saveExercise = async (exerciseType, exerciseData, grade, subject, topic, subTopic) => {
  const response = await fetch(`${API_BASE}/exercise/save`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ exerciseType, exerciseData, grade, subject, topic, sub_topic: subTopic }),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to save exercise');
  }
  return data;
};

// Helper function to generate mock exercises
const generateMockExercises = (topic, type, count, useBook) => {
  const exercises = [];

  for (let i = 1; i <= count; i++) {
    switch (type) {
      case "Multiple Choice":
        exercises.push({
          id: i,
          type: "Multiple Choice",
          question: `${
            useBook ? "[From Book Context] " : ""
          }Question ${i} about ${topic}: What is the most important concept related to this topic?`,
          options: [
            "Option A: First concept",
            "Option B: Second concept",
            "Option C: Third concept",
            "Option D: Fourth concept",
          ],
          correct: "B",
        });
        break;

      case "True/False":
        exercises.push({
          id: i,
          type: "True/False",
          question: `${
            useBook ? "[From Book Context] " : ""
          }Statement ${i}: ${topic} is a fundamental concept in this field.`,
          correct: true,
        });
        break;

      case "Short Answer":
        exercises.push({
          id: i,
          type: "Short Answer",
          question: `${
            useBook ? "[From Book Context] " : ""
          }Question ${i}: Explain the key aspects of ${topic} in 2-3 sentences.`,
        });
        break;

      case "Essay":
        exercises.push({
          id: i,
          type: "Essay",
          question: `${
            useBook ? "[From Book Context] " : ""
          }Essay Question ${i}: Discuss the importance and applications of ${topic}. Provide examples and analyze its impact.`,
        });
        break;

      case "Fill in the Blanks":
        exercises.push({
          id: i,
          type: "Fill in the Blanks",
          question: `${
            useBook ? "[From Book Context] " : ""
          }Complete this sentence about ${topic}: The main characteristic of _____ is that it _____ and provides _____.`,
          blanks: ["[concept]", "[action/property]", "[benefit/result]"],
        });
        break;

      default:
        exercises.push({
          id: i,
          type: "Short Answer",
          question: `${
            useBook ? "[From Book Context] " : ""
          }Question ${i} about ${topic}`,
        });
    }
  }

  return exercises;
};
