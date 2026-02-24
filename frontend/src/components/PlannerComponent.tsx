import { useState } from "react";
import "./PlannerComponent.css";

interface PlanResult {
  goal: string;
  planner_type: string;
  plan?: {
    goal: string;
    steps: Array<{
      function: string;
      plugin: string;
      parameters: Record<string, unknown>;
      description: string;
    }>;
    status: string;
  };
  results?: Array<{
    step: number;
    function: string;
    result?: string;
    error?: string;
    success?: boolean;
  }>;
  status: string;
  final_result?: string;
}

export default function PlannerComponent() {
  const [goal, setGoal] = useState("");
  const [plannerType, setPlannerType] = useState<"stepwise" | "sequential">(
    "stepwise",
  );
  const [isExecuting, setIsExecuting] = useState(false);
  const [result, setResult] = useState<PlanResult | null>(null);

  const handleExecute = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!goal.trim() || isExecuting) return;

    setIsExecuting(true);
    setResult(null);

    try {
      const response = await fetch("/api/planner/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          goal,
          planner_type: plannerType,
          execute: true,
          max_steps: 10,
        }),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const data: PlanResult = await response.json();
      setResult(data);
    } catch (error) {
      setResult({
        goal,
        planner_type: plannerType,
        status: "failed",
        final_result: error instanceof Error ? error.message : "Unknown error",
      });
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <div className="planner-container">
      <form onSubmit={handleExecute} className="planner-form">
        <div className="form-group">
          <label htmlFor="goal">Goal</label>
          <textarea
            id="goal"
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            placeholder="Describe what you want to achieve..."
            rows={3}
            disabled={isExecuting}
          />
        </div>

        <div className="form-group">
          <label htmlFor="planner-type">Planner Type</label>
          <select
            id="planner-type"
            value={plannerType}
            onChange={(e) =>
              setPlannerType(e.target.value as "stepwise" | "sequential")
            }
            disabled={isExecuting}
          >
            <option value="stepwise">Stepwise - Plan one step at a time</option>
            <option value="sequential">
              Sequential - Plan all steps upfront
            </option>
          </select>
        </div>

        <button
          type="submit"
          disabled={isExecuting || !goal.trim()}
          className="btn btn-primary"
        >
          {isExecuting ? "Planning and Executing..." : "Plan and Execute"}
        </button>
      </form>

      {result && (
        <div className="plan-results">
          <div className="result-header">
            <h2>Results</h2>
            <span className={`status-badge status-${result.status}`}>
              {result.status}
            </span>
          </div>

          {result.plan && result.plan.steps.length > 0 && (
            <div className="plan-steps">
              <h3>Plan Steps</h3>
              <div className="steps-list">
                {result.plan.steps.map((step, i) => (
                  <div key={i} className="step-item">
                    <div className="step-number">{i + 1}</div>
                    <div className="step-content">
                      <div className="step-function">
                        <code>
                          {step.plugin}.{step.function}
                        </code>
                      </div>
                      <div className="step-description">{step.description}</div>
                      {Object.keys(step.parameters).length > 0 && (
                        <div className="step-parameters">
                          <strong>Parameters:</strong>{" "}
                          {JSON.stringify(step.parameters)}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {result.results && result.results.length > 0 && (
            <div className="execution-results">
              <h3>Execution Results</h3>
              <div className="results-list">
                {result.results.map((stepResult, i) => (
                  <div
                    key={i}
                    className={`result-item ${stepResult.success === false ? "result-error" : ""}`}
                  >
                    <div className="result-step">Step {stepResult.step}</div>
                    <div className="result-function">{stepResult.function}</div>
                    {stepResult.result && (
                      <div className="result-value">{stepResult.result}</div>
                    )}
                    {stepResult.error && (
                      <div className="result-error-message">
                        {stepResult.error}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {result.final_result && (
            <div className="final-result">
              <h3>Final Result</h3>
              <p>{result.final_result}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
