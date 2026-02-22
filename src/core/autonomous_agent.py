"""
Friday's Autonomous Task Agent
Planning and execution capabilities for autonomous task completion.
"""

import asyncio
import json
import re
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import time


class TaskStatus(Enum):
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    WAITING_INPUT = "waiting_input"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskPlan:
    """A planned task with steps."""
    goal: str
    steps: List[Dict[str, Any]]
    estimated_duration: int  # seconds
    requires_confirmation: bool = False
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AutonomousTask:
    """An autonomous task being executed."""
    id: str
    goal: str
    plan: TaskPlan
    status: TaskStatus = TaskStatus.PENDING
    current_step: int = 0
    results: List[Dict] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    user_confirmations: Dict[int, bool] = field(default_factory=dict)


class TaskPlanner:
    """
    Plans complex tasks by breaking them into actionable steps.
    Uses LLM or rule-based planning depending on complexity.
    """
    
    def __init__(self, action_executor):
        """Initialize TaskPlanner."""
        self.action_executor = action_executor
        self.planning_patterns = self._load_planning_patterns()
    
    def _load_planning_patterns(self) -> Dict:
        """Load predefined planning patterns for common tasks."""
        return {
            "research": {
                "steps": [
                    {"action": "open_application", "params": {"app_name": "chrome"}, "desc": "Open browser"},
                    {"action": "search_web", "params": {"query": "{topic}", "engine": "google"}, "desc": "Search for {topic}"},
                    {"action": "screenshot", "params": {}, "desc": "Capture search results"},
                    {"action": "create_folder", "params": {"path": "~/Research/{topic}"}, "desc": "Create research folder"},
                ]
            },
            "debug_error": {
                "steps": [
                    {"action": "screenshot", "params": {}, "desc": "Capture error screenshot"},
                    {"action": "search_web", "params": {"query": "{error_message}", "engine": "stackoverflow"}, "desc": "Search StackOverflow"},
                    {"action": "open_application", "params": {"app_name": "code"}, "desc": "Open IDE"},
                ]
            },
            "create_project": {
                "steps": [
                    {"action": "create_folder", "params": {"path": "{project_path}"}, "desc": "Create project folder"},
                    {"action": "open_application", "params": {"app_name": "code"}, "desc": "Open VS Code"},
                    {"action": "file_operation", "params": {"operation": "create", "source": "{project_path}/README.md"}, "desc": "Create README"},
                ]
            },
            "daily_standup_prep": {
                "steps": [
                    {"action": "shell_command", "params": {"command": "git log --oneline --since=yesterday"}, "desc": "Get yesterday's commits"},
                    {"action": "screenshot", "params": {}, "desc": "Capture current work"},
                    {"action": "file_operation", "params": {"operation": "create", "source": "~/standup_notes.md"}, "desc": "Create standup notes"},
                ]
            }
        }
    
    def plan_task(self, goal: str, context: Dict[str, Any] = None) -> Optional[TaskPlan]:
        """
        Create a plan for achieving a goal.
        
        Args:
            goal: Natural language goal description
            context: Additional context variables
            
        Returns:
            TaskPlan or None if planning failed
        """
        context = context or {}
        
        # Try pattern matching first
        matched_pattern = self._match_pattern(goal)
        if matched_pattern:
            return self._build_plan_from_pattern(matched_pattern, goal, context)
        
        # Fallback to generic planning
        return self._generic_plan(goal, context)
    
    def _match_pattern(self, goal: str) -> Optional[str]:
        """Match goal to known planning patterns."""
        goal_lower = goal.lower()
        
        # Research patterns
        if any(word in goal_lower for word in ["research", "find info", "look up", "search for"]):
            return "research"
        
        # Debug patterns
        if any(word in goal_lower for word in ["debug", "fix error", "solve this error", "help with error"]):
            return "debug_error"
        
        # Project creation
        if any(word in goal_lower for word in ["create project", "new project", "setup project", "initialize project"]):
            return "create_project"
        
        # Standup prep
        if any(word in goal_lower for word in ["standup", "daily update", "meeting prep"]):
            return "daily_standup_prep"
        
        return None
    
    def _build_plan_from_pattern(self, pattern_id: str, goal: str, context: Dict) -> TaskPlan:
        """Build a plan from a matched pattern."""
        pattern = self.planning_patterns.get(pattern_id, {})
        steps = pattern.get("steps", [])
        
        # Extract variables from goal
        variables = self._extract_variables(goal, pattern_id)
        variables.update(context)
        
        # Substitute variables in steps
        processed_steps = []
        for step in steps:
            processed_step = {
                "action": step["action"],
                "params": {},
                "desc": step["desc"]
            }
            
            for key, value in step["params"].items():
                if isinstance(value, str) and "{" in value:
                    # Substitute variables
                    for var_name, var_value in variables.items():
                        placeholder = f"{{{var_name}}}"
                        if placeholder in value:
                            value = value.replace(placeholder, str(var_value))
                processed_step["params"][key] = value
            
            # Also substitute in description
            desc = step["desc"]
            for var_name, var_value in variables.items():
                placeholder = f"{{{var_name}}}"
                if placeholder in desc:
                    desc = desc.replace(placeholder, str(var_value))
            processed_step["desc"] = desc
            
            processed_steps.append(processed_step)
        
        # Estimate duration (rough estimate: 10s per step)
        estimated_duration = len(processed_steps) * 10
        
        return TaskPlan(
            goal=goal,
            steps=processed_steps,
            estimated_duration=estimated_duration,
            requires_confirmation=pattern_id in ["create_project", "debug_error"],
            context=variables
        )
    
    def _extract_variables(self, goal: str, pattern_id: str) -> Dict[str, str]:
        """Extract relevant variables from the goal."""
        variables = {}
        goal_lower = goal.lower()
        
        if pattern_id == "research":
            # Extract topic
            prefixes = ["research", "find info about", "look up", "search for"]
            for prefix in prefixes:
                if prefix in goal_lower:
                    topic = goal_lower.split(prefix, 1)[-1].strip()
                    # Clean up topic
                    topic = re.sub(r'[?.!,]$', '', topic)
                    variables["topic"] = topic[:50]  # Limit length
                    break
        
        elif pattern_id == "debug_error":
            # Try to extract error message
            if "error" in goal_lower:
                # Simple extraction - could be improved
                variables["error_message"] = goal[:100]  # First 100 chars
        
        elif pattern_id == "create_project":
            # Extract project name
            words = goal.split()
            for i, word in enumerate(words):
                if word.lower() in ["project", "app", "application"] and i + 1 < len(words):
                    project_name = words[i + 1]
                    project_name = re.sub(r'[^\w\-]', '', project_name)
                    variables["project_name"] = project_name
                    variables["project_path"] = f"~/Projects/{project_name}"
                    break
        
        return variables
    
    def _generic_plan(self, goal: str, context: Dict) -> TaskPlan:
        """Create a generic plan when no pattern matches."""
        # Simple heuristic: analyze what tools might be needed
        steps = []
        
        goal_lower = goal.lower()
        
        # Check if browser needed
        if any(word in goal_lower for word in ["search", "find", "lookup", "browser", "website", "online"]):
            steps.append({
                "action": "open_application",
                "params": {"app_name": "chrome"},
                "desc": "Open browser"
            })
        
        # Check if code/IDE needed
        if any(word in goal_lower for word in ["code", "program", "develop", "write", "edit file"]):
            steps.append({
                "action": "open_application",
                "params": {"app_name": "code"},
                "desc": "Open code editor"
            })
        
        # Check if terminal needed
        if any(word in goal_lower for word in ["run", "execute", "command", "terminal", "shell"]):
            steps.append({
                "action": "open_application",
                "params": {"app_name": "terminal"},
                "desc": "Open terminal"
            })
        
        # Always capture context
        steps.append({
            "action": "screenshot",
            "params": {},
            "desc": "Capture current state"
        })
        
        return TaskPlan(
            goal=goal,
            steps=steps,
            estimated_duration=len(steps) * 10,
            requires_confirmation=True,
            context=context
        )


class AutonomousAgent:
    """
    Friday's Autonomous Task Agent.
    Executes planned tasks with minimal supervision.
    """
    
    def __init__(self, action_executor, workflow_engine):
        """Initialize AutonomousAgent."""
        self.action_executor = action_executor
        self.workflow_engine = workflow_engine
        self.planner = TaskPlanner(action_executor)
        self.active_tasks: Dict[str, AutonomousTask] = {}
        self.completed_tasks: List[AutonomousTask] = []
        self.on_progress: Optional[Callable[[str, int, str], None]] = None
        self.on_request_confirmation: Optional[Callable[[str, str], bool]] = None
    
    def register_progress_callback(self, callback: Callable[[str, int, str], None]):
        """Register callback for progress updates."""
        self.on_progress = callback
    
    def register_confirmation_callback(self, callback: Callable[[str, str], bool]):
        """Register callback for user confirmation requests."""
        self.on_request_confirmation = callback
    
    async def create_and_execute(self, goal: str, context: Dict = None, 
                                  auto_confirm: bool = False) -> AutonomousTask:
        """
        Plan and execute a task autonomously.
        
        Args:
            goal: Task goal in natural language
            context: Additional context
            auto_confirm: Whether to auto-confirm all steps
            
        Returns:
            Completed task object
        """
        # Plan the task
        plan = self.planner.plan_task(goal, context)
        
        if not plan:
            task = AutonomousTask(
                id=f"task_{int(time.time())}",
                goal=goal,
                plan=TaskPlan(goal=goal, steps=[], estimated_duration=0),
                status=TaskStatus.FAILED
            )
            return task
        
        # Create task object
        task = AutonomousTask(
            id=f"task_{int(time.time())}",
            goal=goal,
            plan=plan,
            status=TaskStatus.PENDING
        )
        
        self.active_tasks[task.id] = task
        
        # Execute
        await self._execute_task(task, auto_confirm)
        
        return task
    
    async def _execute_task(self, task: AutonomousTask, auto_confirm: bool):
        """Execute a planned task."""
        task.status = TaskStatus.EXECUTING
        task.started_at = time.time()
        
        print(f"\n🤖 AUTONOMOUS TASK: {task.goal}")
        print(f"   Steps: {len(task.plan.steps)}")
        print(f"   Estimated: {task.plan.estimated_duration}s")
        print(f"   Confirmation needed: {task.plan.requires_confirmation and not auto_confirm}\n")
        
        for i, step in enumerate(task.plan.steps):
            task.current_step = i
            
            # Check for confirmation
            if task.plan.requires_confirmation and not auto_confirm:
                if self.on_request_confirmation:
                    confirmed = self.on_request_confirmation(task.id, step.get("desc", "Continue?"))
                    if not confirmed:
                        task.status = TaskStatus.CANCELLED
                        break
                else:
                    # Default to auto-confirm if no callback
                    pass
            
            # Execute step
            print(f"   [{i+1}/{len(task.plan.steps)}] {step.get('desc', step['action'])}")
            
            result = self.action_executor.execute(
                step["action"],
                step.get("params", {})
            )
            
            step_result = {
                "step_index": i,
                "action": step["action"],
                "result": result,
                "timestamp": time.time()
            }
            task.results.append(step_result)
            
            # Update progress
            progress = int(((i + 1) / len(task.plan.steps)) * 100)
            if self.on_progress:
                self.on_progress(task.id, progress, step.get("desc", ""))
            
            # Check for failure
            if result.get("status") == "error":
                print(f"   ⚠️  Step failed: {result.get('message')}")
                # Continue with next step
            else:
                print(f"   ✓ Done")
            
            # Small delay between steps
            await asyncio.sleep(0.5)
        
        # Complete task
        task.status = TaskStatus.COMPLETED if task.status != TaskStatus.CANCELLED else TaskStatus.CANCELLED
        task.completed_at = time.time()
        
        # Move to completed
        if task.id in self.active_tasks:
            del self.active_tasks[task.id]
        self.completed_tasks.append(task)
        
        print(f"\n✅ Task completed: {task.goal}")
        print(f"   Duration: {task.completed_at - task.started_at:.1f}s")
    
    def get_task_summary(self, task_id: str) -> Optional[Dict]:
        """Get summary of a task."""
        # Check active
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
        else:
            # Check completed
            task = next((t for t in self.completed_tasks if t.id == task_id), None)
        
        if not task:
            return None
        
        return {
            "id": task.id,
            "goal": task.goal,
            "status": task.status.value,
            "progress": task.current_step / len(task.plan.steps) if task.plan.steps else 0,
            "steps_total": len(task.plan.steps),
            "steps_completed": len([r for r in task.results if r["result"].get("status") == "success"]),
            "duration": (task.completed_at or time.time()) - (task.started_at or task.created_at)
        }
    
    def get_recent_tasks(self, n: int = 5) -> List[Dict]:
        """Get recent task summaries."""
        all_tasks = list(self.completed_tasks) + list(self.active_tasks.values())
        all_tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        return [self.get_task_summary(t.id) for t in all_tasks[:n]]


# Helper function
def quick_autonomous_task(goal: str, agent: AutonomousAgent, context: Dict = None) -> AutonomousTask:
    """Quick helper to execute an autonomous task."""
    return asyncio.run(agent.create_and_execute(goal, context))
