import { useState } from "react";
import { PenTool, BookOpen, Target } from "lucide-react";
import FormGroup from "./FormGroup";
import Spinner from "./Spinner";
import ResponseBox from "./ResponseBox";
import { generateExercises, saveExercise } from "../api";

export default function ExerciseGeneration({ hasBook, userId }) {
  const [topic, setTopic] = useState("");
  const [exerciseType, setExerciseType] = useState("Multiple Choice");
  const [numQuestions, setNumQuestions] = useState(5);
  const [isLoading, setIsLoading] = useState(false);
  const [exercises, setExercises] = useState(null);
  const [response, setResponse] = useState(null);
  const [saveStatus, setSaveStatus] = useState(null);
  const [grade, setGrade] = useState("");
  const [subject, setSubject] = useState("");
  const [subTopic, setSubTopic] = useState("");

  const exerciseTypes = [
    "Multiple Choice",
    "True/False",
    "Short Answer",
    "Long Questions",
    "Fill in the Blanks",
  ];

  const questionCounts = [3, 5, 10, 15];

  const handleGenerate = async (useBookContext = false) => {
    if (!topic.trim()) {
      setResponse({ type: "error", message: "Please enter a topic." });
      return;
    }

    if (useBookContext && !hasBook) {
      setResponse({
        type: "error",
        message: "Please upload a book first to use book context.",
      });
      return;
    }

    setIsLoading(true);
    setResponse(null);
    setExercises(null);

    try {
      const result = await generateExercises(
        topic,
        exerciseType,
        numQuestions,
        useBookContext,
        userId // Pass userId to API
      );
      // Accept both array and string (backend may return exercises as string)
      let exercisesData = result.exercises;
      if (typeof exercisesData === 'string') {
        // If backend returns a string, show it as a single exercise
        exercisesData = [{ id: 1, type: 'Text', question: exercisesData }];
      }
      setExercises(exercisesData);
      setResponse({
        type: "success",
        message: `Generated ${
          Array.isArray(exercisesData) ? exercisesData.length : 1
        } ${exerciseType.toLowerCase()} exercise(s) successfully!`,
      });
    } catch (error) {
      setResponse({ type: "error", message: error.message });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    setSaveStatus(null);
    try {
      await saveExercise(exerciseType, exercises, grade, subject, topic, subTopic);
      setSaveStatus({ type: "success", message: "Exercises saved successfully!" });
    } catch (error) {
      setSaveStatus({ type: "error", message: error.message });
    }
  };

  const renderExercise = (exercise) => {
    if (exercise.type === 'Text') {
      // For plain text responses (e.g., backend returns a string)
      return (
        <div key={exercise.id} className="bg-gradient-to-br from-purple-50 to-blue-50 p-6 rounded-xl border border-purple-100 shadow">
          <pre className="whitespace-pre-wrap text-dark-purple text-base font-mono leading-relaxed">{exercise.question}</pre>
        </div>
      );
    }
    switch (exercise.type) {
      case "Multiple Choice":
        return (
          <div key={exercise.id} className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-medium text-dark-purple mb-3">
              {exercise.question}
            </h4>
            <div className="space-y-2">
              {exercise.options.map((option, index) => (
                <div key={index} className="flex items-center gap-2">
                  <div className="w-4 h-4 border border-gray-300 rounded-full"></div>
                  <span className="text-sm">{option}</span>
                </div>
              ))}
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Correct answer: {exercise.correct}
            </p>
          </div>
        );

      case "True/False":
        return (
          <div key={exercise.id} className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-medium text-dark-purple mb-3">
              {exercise.question}
            </h4>
            <div className="flex gap-4">
              <label className="flex items-center gap-2">
                <input type="radio" name={`tf-${exercise.id}`} disabled />
                <span>True</span>
              </label>
              <label className="flex items-center gap-2">
                <input type="radio" name={`tf-${exercise.id}`} disabled />
                <span>False</span>
              </label>
            </div>
            {exercise.answer && (
              <p className="text-xs text-gray-500 mt-2">
                Correct answer: <span className="font-semibold">{exercise.answer}</span>
              </p>
            )}
          </div>
        );

      case "Fill in the Blanks":
        return (
          <div key={exercise.id} className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-medium text-dark-purple mb-3">
              {exercise.question}
            </h4>
            {exercise.answer && (
              <p className="text-xs text-gray-500 mt-2">
                Answer: <span className="font-semibold">{exercise.answer}</span>
              </p>
            )}
            <div className="space-y-2">
              {exercise.blanks?.map((blank, index) => (
                <input
                  key={index}
                  type="text"
                  placeholder={blank}
                  className="w-full px-3 py-2 border border-gray-200 rounded text-sm"
                />
              ))}
            </div>
          </div>
        );
      case "Short Answer":
        return (
          <div key={exercise.id} className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-medium text-dark-purple mb-3">
              {exercise.question}
            </h4>
          </div>
        );
      case "Long Questions":
        return (
          <div key={exercise.id} className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-medium text-dark-purple mb-3">
              {exercise.question}
            </h4>
          </div>
        );
      default:
        return (
          <div key={exercise.id} className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-medium text-dark-purple mb-3">
              {exercise.question}
            </h4>
            <textarea
              className="w-full p-3 border border-gray-200 rounded-lg text-sm"
              rows="4"
              placeholder="Type your answer here..."
            />
          </div>
        );
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-md p-6 border border-gray-100">
      <div className="flex items-center gap-3 mb-6">
        <PenTool className="w-6 h-6 text-primary-purple" />
        <h2 className="text-xl font-semibold text-dark-purple">
          Generate an Exercise
        </h2>
      </div>

      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <FormGroup label="Topic" required>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-light-purple focus:border-transparent transition-all duration-200"
              placeholder="Enter topic"
              disabled={isLoading}
            />
          </FormGroup>

          <FormGroup label="Exercise Type">
            <select
              value={exerciseType}
              onChange={(e) => setExerciseType(e.target.value)}
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-light-purple focus:border-transparent transition-all duration-200"
              disabled={isLoading}
            >
              {exerciseTypes.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </FormGroup>

          <FormGroup label="Number of Questions">
            <select
              value={numQuestions}
              onChange={(e) => setNumQuestions(Number(e.target.value))}
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-light-purple focus:border-transparent transition-all duration-200"
              disabled={isLoading}
            >
              {questionCounts.map((count) => (
                <option key={count} value={count}>
                  {count}
                </option>
              ))}
            </select>
          </FormGroup>
          <FormGroup label="Grade" required>
            <input
              type="text"
              value={grade}
              onChange={(e) => setGrade(e.target.value)}
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-light-purple focus:border-transparent transition-all duration-200"
              placeholder="Enter grade"
              disabled={isLoading}
            />
          </FormGroup>
          <FormGroup label="Subject" required>
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-light-purple focus:border-transparent transition-all duration-200"
              placeholder="Enter subject"
              disabled={isLoading}
            />
          </FormGroup>
          <FormGroup label="Sub Topic">
            <input
              type="text"
              value={subTopic}
              onChange={(e) => setSubTopic(e.target.value)}
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-light-purple focus:border-transparent transition-all duration-200"
              placeholder="Enter sub topic (optional)"
              disabled={isLoading}
            />
          </FormGroup>
        </div>

        <div className="flex flex-col sm:flex-row gap-4">
          <button
            onClick={() => handleGenerate(true)}
            disabled={isLoading || !topic.trim()}
            className="flex-1 bg-primary-purple text-white py-3 px-6 rounded-lg font-medium hover:bg-light-purple focus:outline-none focus:ring-2 focus:ring-light-purple focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            <BookOpen className="w-5 h-5" />
            Generate with Book Context
            {!hasBook && <span className="text-xs">(Upload book first)</span>}
          </button>

          <button
            onClick={() => handleGenerate(false)}
            disabled={isLoading || !topic.trim()}
            className="flex-1 bg-gray-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            <Target className="w-5 h-5" />
            Generate without Book
          </button>
        </div>

        {isLoading && (
          <div className="flex justify-center py-8">
            <Spinner size="lg" text="Generating exercises..." />
          </div>
        )}

        {response && (
          <ResponseBox
            type={response.type}
            message={response.message}
            onClose={() => setResponse(null)}
          />
        )}

        {exercises && !isLoading && (
          <div className="mt-6">
            <h3 className="text-lg font-semibold text-dark-purple mb-4">
              Generated Exercises
            </h3>
            <div className="max-h-96 overflow-y-auto custom-scrollbar space-y-4 pr-2">
              {exercises.map(renderExercise)}
            </div>
            <button
              onClick={handleSave}
              className="mt-4 w-full bg-green-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-400 focus:ring-offset-2 transition-all duration-200"
            >
              Save Exercises
            </button>
            {saveStatus && (
              <ResponseBox
                type={saveStatus.type}
                message={saveStatus.message}
                onClose={() => setSaveStatus(null)}
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
}
