const API_URL = "http://127.0.0.1:8000/api";

// Strategy descriptions
const strategyDescriptions = {
  smart:
    "Balances urgency (35%), importance (30%), effort (20%), and dependencies (15%)",
  fastest: "Prioritizes tasks with lowest estimated hours for quick wins",
  impact: "Prioritizes tasks with highest importance ratings",
  deadline: "Prioritizes tasks by closest due date, with overdue tasks first",
};

// Tab switching
document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    const tabName = btn.dataset.tab;

    // Update buttons
    document
      .querySelectorAll(".tab-btn")
      .forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");

    // Update content
    document.querySelectorAll(".tab-content").forEach((content) => {
      content.classList.remove("active");
    });
    document.getElementById(`${tabName}TaskTab`).classList.add("active");
  });
});

// Strategy selector change
document.getElementById("sortStrategy").addEventListener("change", (e) => {
  const info = document.getElementById("strategyInfo");
  const strategy = e.target.value;
  const strategyNames = {
    smart: "Smart Balance",
    fastest: "Fastest Wins",
    impact: "High Impact",
    deadline: "Deadline Driven",
  };

  info.innerHTML = `<strong>${strategyNames[strategy]}:</strong> ${strategyDescriptions[strategy]}`;
});

// Form validation helper
function validateTaskData(data) {
  const errors = [];

  if (!data.title || data.title.trim().length === 0) {
    errors.push("Title is required");
  }

  if (!data.due_date) {
    errors.push("Due date is required");
  }

  if (!data.estimated_hours || data.estimated_hours < 0.1) {
    errors.push("Estimated hours must be at least 0.1");
  }

  if (!data.importance || data.importance < 1 || data.importance > 10) {
    errors.push("Importance must be between 1 and 10");
  }

  return errors;
}

// Show error message
function showError(message) {
  const errorDiv = document.getElementById("errorMessage");
  errorDiv.textContent = message;
  errorDiv.classList.remove("hidden");

  setTimeout(() => {
    errorDiv.classList.add("hidden");
  }, 5000);
}

// Show success message
function showSuccess(message) {
  const successDiv = document.createElement("div");
  successDiv.className = "success-message";
  successDiv.textContent = message;

  const container = document.querySelector(".input-section");
  container.insertBefore(successDiv, container.firstChild);

  setTimeout(() => {
    successDiv.remove();
  }, 3000);
}

// Show/hide loading
function setLoading(isLoading) {
  const loader = document.getElementById("loadingIndicator");
  if (isLoading) {
    loader.classList.remove("hidden");
  } else {
    loader.classList.add("hidden");
  }
}

// Add single task
document.getElementById("taskForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const taskData = {
    title: document.getElementById("title").value.trim(),
    due_date: document.getElementById("dueDate").value,
    estimated_hours: parseFloat(
      document.getElementById("estimatedHours").value
    ),
    importance: parseInt(document.getElementById("importance").value),
    dependencies: [],
  };

  // Validate
  const errors = validateTaskData(taskData);
  if (errors.length > 0) {
    showError(errors.join(", "));
    return;
  }

  try {
    const response = await fetch(`${API_URL}/tasks/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(taskData),
    });

    if (!response.ok) {
      throw new Error("Failed to add task");
    }

    showSuccess("✅ Task added successfully!");
    document.getElementById("taskForm").reset();
    loadTasks();
  } catch (error) {
    console.error("Error:", error);
    showError("❌ Failed to add task. Please try again.");
  }
});

// Bulk import tasks
document.getElementById("bulkSubmit").addEventListener("click", async () => {
  const jsonInput = document.getElementById("bulkJson").value.trim();

  if (!jsonInput) {
    showError("Please paste JSON data");
    return;
  }

  try {
    const tasks = JSON.parse(jsonInput);

    if (!Array.isArray(tasks)) {
      throw new Error("JSON must be an array of tasks");
    }

    // Validate all tasks
    for (let i = 0; i < tasks.length; i++) {
      const errors = validateTaskData(tasks[i]);
      if (errors.length > 0) {
        throw new Error(`Task ${i + 1}: ${errors.join(", ")}`);
      }
    }

    // Import all tasks
    let successCount = 0;
    for (const task of tasks) {
      const response = await fetch(`${API_URL}/tasks/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(task),
      });

      if (response.ok) {
        successCount++;
      }
    }

    showSuccess(`✅ Successfully imported ${successCount} task(s)!`);
    document.getElementById("bulkJson").value = "";
    loadTasks();
  } catch (error) {
    console.error("Error:", error);
    showError(`❌ Invalid JSON: ${error.message}`);
  }
});

// Get priority class
function getPriorityClass(score) {
  if (score >= 70) return "high";
  if (score >= 40) return "medium";
  return "low";
}

// Get priority label
function getPriorityLabel(score) {
  if (score >= 70) return "High Priority";
  if (score >= 40) return "Medium Priority";
  return "Low Priority";
}

// Format date for display
function formatDate(dateString) {
  const date = new Date(dateString);
  const today = new Date();
  const diffTime = date - today;
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays < 0) {
    return `⚠️ ${Math.abs(diffDays)} days overdue`;
  } else if (diffDays === 0) {
    return "🔥 Due today";
  } else if (diffDays === 1) {
    return "⏰ Due tomorrow";
  } else if (diffDays <= 7) {
    return `📅 Due in ${diffDays} days`;
  } else {
    return `📅 ${dateString}`;
  }
}

// Generate task explanation
function generateExplanation(task, strategy) {
  const parts = [];

  if (strategy === "smart" || strategy === "deadline") {
    const dueDate = new Date(task.due_date);
    const today = new Date();
    const daysUntil = Math.ceil((dueDate - today) / (1000 * 60 * 60 * 24));

    if (daysUntil < 0) {
      parts.push("overdue by " + Math.abs(daysUntil) + " days");
    } else if (daysUntil <= 1) {
      parts.push("due very soon");
    } else if (daysUntil <= 7) {
      parts.push("due this week");
    }
  }

  if (strategy === "smart" || strategy === "impact") {
    if (task.importance >= 8) {
      parts.push("high importance (" + task.importance + "/10)");
    } else if (task.importance >= 6) {
      parts.push("moderate importance (" + task.importance + "/10)");
    }
  }

  if (strategy === "smart" || strategy === "fastest") {
    if (task.estimated_hours <= 1) {
      parts.push("quick win (" + task.estimated_hours + "h)");
    } else if (task.estimated_hours <= 3) {
      parts.push("moderate effort (" + task.estimated_hours + "h)");
    }
  }

  if (parts.length === 0) {
    return "Selected based on " + strategy + " strategy";
  }

  return "<strong>Why prioritized:</strong> " + parts.join(", ");
}

// Render task card
function renderTaskCard(task, strategy = "smart") {
  const priorityClass = getPriorityClass(task.priority_score || 50);
  const priorityLabel = getPriorityLabel(task.priority_score || 50);
  const explanation = generateExplanation(task, strategy);

  return `
        <div class="task-card priority-${priorityClass}">
            ${
              task.priority_score
                ? `<div class="score-display">${task.priority_score}</div>`
                : ""
            }
            <h3>${task.title}</h3>
            <div class="task-details">
                <span>📅 ${formatDate(task.due_date)}</span>
                <span>⏱️ ${task.estimated_hours}h</span>
                <span>⭐ ${task.importance}/10</span>
            </div>
            ${
              task.priority_score
                ? `
                <div style="margin-top: 10px;">
                    <span class="priority-badge ${priorityClass}">${priorityLabel}</span>
                </div>
            `
                : ""
            }
            <div class="task-explanation">${explanation}</div>
        </div>
    `;
}

// Load all tasks
async function loadTasks() {
  try {
    const response = await fetch(`${API_URL}/tasks/`);

    if (!response.ok) {
      throw new Error("Failed to load tasks");
    }

    const tasks = await response.json();

    const tasksList = document.getElementById("tasksList");
    const emptyState = document.getElementById("emptyState");

    if (tasks.length === 0) {
      tasksList.innerHTML = "";
      emptyState.classList.remove("hidden");
    } else {
      emptyState.classList.add("hidden");
      tasksList.innerHTML = tasks.map((task) => renderTaskCard(task)).join("");
    }
  } catch (error) {
    console.error("Error:", error);
    showError("Failed to load tasks");
  }
}

// Analyze tasks with selected strategy
document.getElementById("analyzeTasks").addEventListener("click", async () => {
  const strategy = document.getElementById("sortStrategy").value;

  setLoading(true);

  try {
    // First, get all tasks
    const tasksResponse = await fetch(`${API_URL}/tasks/`);
    if (!tasksResponse.ok) throw new Error("Failed to fetch tasks");

    const tasks = await tasksResponse.json();

    if (tasks.length === 0) {
      showError("No tasks to analyze. Add some tasks first!");
      setLoading(false);
      return;
    }

    // Apply strategy
    let sortedTasks;

    switch (strategy) {
      case "fastest":
        sortedTasks = tasks.sort(
          (a, b) => a.estimated_hours - b.estimated_hours
        );
        // Assign scores based on effort (inverse)
        sortedTasks.forEach((task, index) => {
          task.priority_score = 100 - index * 5;
        });
        break;

      case "impact":
        sortedTasks = tasks.sort((a, b) => b.importance - a.importance);
        // Assign scores based on importance
        sortedTasks.forEach((task, index) => {
          task.priority_score = task.importance * 10;
        });
        break;

      case "deadline":
        sortedTasks = tasks.sort((a, b) => {
          return new Date(a.due_date) - new Date(b.due_date);
        });
        // Assign scores based on urgency
        sortedTasks.forEach((task, index) => {
          const daysUntil = Math.ceil(
            (new Date(task.due_date) - new Date()) / (1000 * 60 * 60 * 24)
          );
          if (daysUntil < 0) {
            task.priority_score = 100;
          } else if (daysUntil === 0) {
            task.priority_score = 95;
          } else {
            task.priority_score = Math.max(0, 90 - daysUntil * 3);
          }
        });
        break;

      case "smart":
      default:
        // Use backend analysis
        const response = await fetch(`${API_URL}/tasks/analyze/`, {
          method: "POST",
        });

        if (!response.ok) throw new Error("Analysis failed");

        sortedTasks = await response.json();
        break;
    }

    // Display sorted tasks
    const tasksList = document.getElementById("tasksList");
    tasksList.innerHTML = sortedTasks
      .map((task) => renderTaskCard(task, strategy))
      .join("");

    showSuccess(`✅ Tasks analyzed using ${strategy} strategy!`);
  } catch (error) {
    console.error("Error:", error);
    showError("❌ Failed to analyze tasks");
  } finally {
    setLoading(false);
  }
});

// Get suggestions
document
  .getElementById("getSuggestions")
  .addEventListener("click", async () => {
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/tasks/suggest/`);

      if (!response.ok) {
        throw new Error("Failed to get suggestions");
      }

      const data = await response.json();
      const suggestionsList = document.getElementById("suggestionsList");

      if (!data.suggestions || data.suggestions.length === 0) {
        suggestionsList.innerHTML =
          '<p style="text-align: center; color: #999;">No tasks available for suggestions. Add some tasks first!</p>';
        setLoading(false);
        return;
      }

      suggestionsList.innerHTML = data.suggestions
        .map(
          (item, index) => `
            <div class="suggestion-card">
                <div class="suggestion-rank">#${index + 1}</div>
                <h3 style="margin-top: 10px;">${item.task.title}</h3>
                <div class="task-details">
                    <span>📅 ${formatDate(item.task.due_date)}</span>
                    <span>⏱️ ${item.task.estimated_hours}h</span>
                    <span>⭐ ${item.task.importance}/10</span>
                </div>
                <div style="margin-top: 10px;">
                    <span class="priority-badge ${getPriorityClass(
                      item.score
                    )}">
                        Score: ${item.score}
                    </span>
                </div>
                <div class="task-explanation">
                    <strong>Recommended because:</strong> ${item.reason}
                </div>
            </div>
        `
        )
        .join("");

      showSuccess("✅ Top 3 suggestions generated!");
    } catch (error) {
      console.error("Error:", error);
      showError("❌ Failed to get suggestions");
    } finally {
      setLoading(false);
    }
  });

// Set minimum date to today
document.getElementById("dueDate").min = new Date().toISOString().split("T")[0];

// Eisenhower Matrix
document
  .getElementById("showEisenhower")
  .addEventListener("click", async () => {
    const container = document.getElementById("eisenhowerMatrix");
    const btn = document.getElementById("showEisenhower");

    // Toggle visibility
    if (!container.classList.contains("hidden")) {
      container.classList.add("hidden");
      btn.innerHTML = '<span class="btn-icon">🎯</span> Show Matrix View';
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/tasks/eisenhower_matrix/`);

      if (!response.ok) {
        throw new Error("Failed to load matrix");
      }

      const matrix = await response.json();

      // Build matrix HTML
      container.innerHTML = `
            <div class="eisenhower-grid">
                <div class="eisenhower-quadrant quadrant-do-first">
                    <h3>🔥 Do First (Urgent & Important)</h3>
                    ${
                      matrix.DO_FIRST.length > 0
                        ? matrix.DO_FIRST.map(
                            (task) => `
                            <div class="eisenhower-task">
                                <strong>${task.title}</strong>
                                <small>Due: ${task.due_date} | Importance: ${task.importance}/10</small>
                            </div>
                        `
                          ).join("")
                        : '<div class="eisenhower-empty">No tasks in this quadrant</div>'
                    }
                </div>
                
                <div class="eisenhower-quadrant quadrant-schedule">
                    <h3>📅 Schedule (Not Urgent but Important)</h3>
                    ${
                      matrix.SCHEDULE.length > 0
                        ? matrix.SCHEDULE.map(
                            (task) => `
                            <div class="eisenhower-task">
                                <strong>${task.title}</strong>
                                <small>Due: ${task.due_date} | Importance: ${task.importance}/10</small>
                            </div>
                        `
                          ).join("")
                        : '<div class="eisenhower-empty">No tasks in this quadrant</div>'
                    }
                </div>
                
                <div class="eisenhower-quadrant quadrant-delegate">
                    <h3>⚡ Delegate (Urgent but Not Important)</h3>
                    ${
                      matrix.DELEGATE.length > 0
                        ? matrix.DELEGATE.map(
                            (task) => `
                            <div class="eisenhower-task">
                                <strong>${task.title}</strong>
                                <small>Due: ${task.due_date} | Importance: ${task.importance}/10</small>
                            </div>
                        `
                          ).join("")
                        : '<div class="eisenhower-empty">No tasks in this quadrant</div>'
                    }
                </div>
                
                <div class="eisenhower-quadrant quadrant-eliminate">
                    <h3>🗑️ Eliminate (Not Urgent & Not Important)</h3>
                    ${
                      matrix.ELIMINATE.length > 0
                        ? matrix.ELIMINATE.map(
                            (task) => `
                            <div class="eisenhower-task">
                                <strong>${task.title}</strong>
                                <small>Due: ${task.due_date} | Importance: ${task.importance}/10</small>
                            </div>
                        `
                          ).join("")
                        : '<div class="eisenhower-empty">No tasks in this quadrant</div>'
                    }
                </div>
            </div>
        `;

      container.classList.remove("hidden");
      btn.innerHTML = '<span class="btn-icon">🎯</span> Hide Matrix View';
    } catch (error) {
      console.error("Error:", error);
      showError("❌ Failed to load Eisenhower Matrix");
    } finally {
      setLoading(false);
    }
  });

// Dependency Graph
document
  .getElementById("showDependencies")
  .addEventListener("click", async () => {
    const container = document.getElementById("dependencyGraph");
    const btn = document.getElementById("showDependencies");
    const alert = document.getElementById("dependencyAlert");

    // Toggle visibility
    if (!container.classList.contains("hidden")) {
      container.classList.add("hidden");
      alert.classList.add("hidden");
      btn.innerHTML = '<span class="btn-icon">🕸️</span> Show Dependencies';
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/tasks/dependency_graph/`);

      if (!response.ok) {
        throw new Error("Failed to load dependency graph");
      }

      const data = await response.json();

      // Show alert if cycles detected
      if (data.has_cycles) {
        alert.classList.remove("hidden");
      } else {
        alert.classList.add("hidden");
      }

      if (data.nodes.length === 0) {
        container.innerHTML =
          '<div class="eisenhower-empty">No tasks with dependencies yet</div>';
        container.classList.remove("hidden");
        btn.innerHTML = '<span class="btn-icon">🕸️</span> Hide Dependencies';
        setLoading(false);
        return;
      }

      // Build graph HTML
      let graphHTML = `
            <div class="dependency-legend">
                <div class="legend-item">
                    <div class="legend-box normal"></div>
                    <span>Normal Task</span>
                </div>
                <div class="legend-item">
                    <div class="legend-box cycle"></div>
                    <span>Circular Dependency</span>
                </div>
            </div>
            <div class="dependency-graph">
        `;

      // Group edges by task
      const taskDependencies = {};
      data.edges.forEach((edge) => {
        if (!taskDependencies[edge.to]) {
          taskDependencies[edge.to] = [];
        }
        taskDependencies[edge.to].push(edge);
      });

      // Render nodes with their dependencies
      data.nodes.forEach((node) => {
        const dependencies = taskDependencies[node.id] || [];

        graphHTML += `
                <div class="dependency-node ${
                  node.has_cycle ? "has-cycle" : ""
                }">
                    <div class="dependency-node-title">
                        ${node.title}
                        ${
                          node.has_cycle
                            ? '<span class="cycle-badge">⚠️ CYCLE</span>'
                            : ""
                        }
                    </div>
                    <div class="dependency-node-id">Task ID: ${node.id}</div>
                    ${
                      dependencies.length > 0
                        ? `
                        <div class="dependency-connections">
                            <strong style="font-size: 12px; color: #666;">Depends on:</strong>
                            ${dependencies
                              .map((edge) => {
                                const depNode = data.nodes.find(
                                  (n) => n.id === edge.from
                                );
                                return `
                                    <div class="dependency-arrow ${
                                      edge.has_cycle ? "cycle-arrow" : ""
                                    }">
                                        ⬅️ ${
                                          depNode
                                            ? depNode.title
                                            : "Task #" + edge.from
                                        }
                                        ${edge.has_cycle ? "(⚠️ circular)" : ""}
                                    </div>
                                `;
                              })
                              .join("")}
                        </div>
                    `
                        : '<div style="margin-top: 10px; font-size: 13px; color: #999;">No dependencies</div>'
                    }
                </div>
            `;
      });

      graphHTML += "</div>";

      container.innerHTML = graphHTML;
      container.classList.remove("hidden");
      btn.innerHTML = '<span class="btn-icon">🕸️</span> Hide Dependencies';
    } catch (error) {
      console.error("Error:", error);
      showError("❌ Failed to load dependency graph");
    } finally {
      setLoading(false);
    }
  });

// Load tasks on page load
loadTasks();
