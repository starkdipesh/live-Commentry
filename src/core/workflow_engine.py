"""
Friday's Workflow Engine
Multi-step task orchestration for complex workflows.
Enables Friday to execute sequences of actions like "Setup streaming environment".
"""

import asyncio
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum


class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """A single step in a workflow."""
    id: str
    name: str
    action: str
    params: Dict[str, Any] = field(default_factory=dict)
    requires_confirmation: bool = False
    confirmation_prompt: Optional[str] = None
    retry_on_failure: bool = False
    max_retries: int = 1
    depends_on: List[str] = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    result: Optional[Dict] = None
    error_message: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None


@dataclass
class Workflow:
    """A multi-step workflow definition."""
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    context: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    current_step_idx: int = 0
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    def get_progress(self) -> float:
        """Get workflow progress as percentage."""
        if not self.steps:
            return 100.0
        completed = sum(1 for s in self.steps if s.status == StepStatus.COMPLETED)
        return (completed / len(self.steps)) * 100


class WorkflowEngine:
    """
    Friday's Workflow Execution Engine.
    Orchestrates multi-step tasks with dependencies, retries, and progress tracking.
    """
    
    def __init__(self, action_executor):
        """
        Initialize WorkflowEngine.
        
        Args:
            action_executor: ActionExecutor instance for executing actions
        """
        self.action_executor = action_executor
        self.active_workflows: Dict[str, Workflow] = {}
        self.workflow_history: List[Workflow] = []
        self.on_progress_callback: Optional[Callable[[str, float, str], None]] = None
        self.on_step_complete: Optional[Callable[[str, str, Dict], None]] = None
    
    def register_progress_callback(self, callback: Callable[[str, float, str], None]):
        """Register callback for progress updates: (workflow_id, progress_pct, status_message)"""
        self.on_progress_callback = callback
    
    def register_step_callback(self, callback: Callable[[str, str, Dict], None]):
        """Register callback for step completion: (workflow_id, step_id, result)"""
        self.on_step_complete = callback
    
    def create_workflow(self, name: str, description: str, steps: List[WorkflowStep]) -> Workflow:
        """Create a new workflow definition."""
        workflow_id = f"wf_{int(time.time())}_{name.lower().replace(' ', '_')}"
        workflow = Workflow(
            id=workflow_id,
            name=name,
            description=description,
            steps=steps
        )
        return workflow
    
    async def execute_workflow(self, workflow: Workflow, skip_confirmation: bool = False) -> Workflow:
        """
        Execute a workflow with all its steps.
        
        Args:
            workflow: The workflow to execute
            skip_confirmation: If True, skip all confirmation prompts
            
        Returns:
            Completed workflow with results
        """
        workflow.start_time = time.time()
        workflow.status = "running"
        self.active_workflows[workflow.id] = workflow
        
        print(f"\n🔧 Starting Workflow: {workflow.name}")
        print(f"   Description: {workflow.description}")
        print(f"   Steps: {len(workflow.steps)}")
        print(f"   ID: {workflow.id}\n")
        
        try:
            for idx, step in enumerate(workflow.steps):
                workflow.current_step_idx = idx
                
                # Check dependencies
                if step.depends_on:
                    deps_satisfied = all(
                        self._get_step_by_id(workflow, dep_id).status == StepStatus.COMPLETED
                        for dep_id in step.depends_on
                    )
                    if not deps_satisfied:
                        print(f"   ⏭️  Skipping {step.name} - dependencies not satisfied")
                        step.status = StepStatus.SKIPPED
                        continue
                
                # Check for confirmation
                if step.requires_confirmation and not skip_confirmation:
                    if step.confirmation_prompt:
                        print(f"   ⚠️  {step.confirmation_prompt}")
                    # In real implementation, this would wait for user input
                    # For now, we auto-confirm for testing
                    print(f"   ✓ Auto-confirmed (would prompt user in interactive mode)")
                
                # Execute step
                await self._execute_step(workflow, step)
                
                # Update progress
                progress = workflow.get_progress()
                if self.on_progress_callback:
                    self.on_progress_callback(workflow.id, progress, f"Completed: {step.name}")
                
                # Check if step failed and we should abort
                if step.status == StepStatus.FAILED and not step.retry_on_failure:
                    print(f"   ❌ Workflow failed at step: {step.name}")
                    workflow.status = "failed"
                    break
            
            if workflow.status != "failed":
                workflow.status = "completed"
                print(f"\n✅ Workflow completed: {workflow.name}")
            
        except Exception as e:
            workflow.status = "error"
            print(f"\n❌ Workflow error: {e}")
        
        workflow.end_time = time.time()
        self.workflow_history.append(workflow)
        
        if workflow.id in self.active_workflows:
            del self.active_workflows[workflow.id]
        
        return workflow
    
    async def _execute_step(self, workflow: Workflow, step: WorkflowStep):
        """Execute a single workflow step."""
        step.start_time = time.time()
        step.status = StepStatus.RUNNING
        
        print(f"   ▶️  Executing: {step.name}")
        
        attempt = 0
        max_attempts = 1 + (step.max_retries if step.retry_on_failure else 0)
        
        while attempt < max_attempts:
            attempt += 1
            
            try:
                # Execute the action
                result = self.action_executor.execute(step.action, step.params)
                
                if result.get("status") in ["success", "pending_confirmation"]:
                    step.status = StepStatus.COMPLETED
                    step.result = result
                    print(f"   ✓ {step.name} completed")
                    
                    if self.on_step_complete:
                        self.on_step_complete(workflow.id, step.id, result)
                    
                    break
                else:
                    step.error_message = result.get("message", "Unknown error")
                    if attempt < max_attempts:
                        print(f"   ⚠️  {step.name} failed, retrying... ({attempt}/{max_attempts})")
                        await asyncio.sleep(1)
                    else:
                        step.status = StepStatus.FAILED
                        print(f"   ✗ {step.name} failed: {step.error_message}")
                
            except Exception as e:
                step.error_message = str(e)
                if attempt < max_attempts:
                    print(f"   ⚠️  {step.name} error, retrying... ({attempt}/{max_attempts})")
                    await asyncio.sleep(1)
                else:
                    step.status = StepStatus.FAILED
                    print(f"   ✗ {step.name} error: {e}")
        
        step.end_time = time.time()
    
    def _get_step_by_id(self, workflow: Workflow, step_id: str) -> Optional[WorkflowStep]:
        """Get a step by its ID."""
        for step in workflow.steps:
            if step.id == step_id:
                return step
        return None
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict]:
        """Get current status of a workflow."""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            # Check history
            for wf in self.workflow_history:
                if wf.id == workflow_id:
                    workflow = wf
                    break
        
        if not workflow:
            return None
        
        return {
            "id": workflow.id,
            "name": workflow.name,
            "status": workflow.status,
            "progress": workflow.get_progress(),
            "current_step": workflow.current_step_idx,
            "total_steps": len(workflow.steps),
            "start_time": workflow.start_time,
            "end_time": workflow.end_time,
            "steps": [
                {
                    "id": s.id,
                    "name": s.name,
                    "status": s.status.value,
                    "result": s.result,
                    "error": s.error_message
                }
                for s in workflow.steps
            ]
        }
    
    def get_workflow_templates(self) -> Dict[str, Dict]:
        """Get available workflow templates."""
        return {
            "setup_streaming": {
                "name": "Setup Streaming Environment",
                "description": "Prepare OBS, open streaming tools, and check audio",
                "steps": [
                    WorkflowStep("1", "Open OBS", "open_application", {"app_name": "obs"}),
                    WorkflowStep("2", "Open Browser", "open_application", {"app_name": "chrome"}),
                    WorkflowStep("3", "Open Chat", "open_url", {"url": "https://studio.youtube.com"}),
                    WorkflowStep("4", "Check Audio", "media_control", {"command": "play-pause"}),
                ]
            },
            "start_coding": {
                "name": "Start Coding Session",
                "description": "Open IDE, terminal, and project folder",
                "steps": [
                    WorkflowStep("1", "Open VS Code", "open_application", {"app_name": "code"}),
                    WorkflowStep("2", "Open Terminal", "open_application", {"app_name": "terminal"}),
                    WorkflowStep("3", "Screenshot for context", "screenshot", {}),
                ]
            },
            "research_topic": {
                "name": "Research Topic",
                "description": "Open browser, search, and capture notes",
                "steps": [
                    WorkflowStep("1", "Open Browser", "open_application", {"app_name": "chrome"}),
                    WorkflowStep("2", "Search", "search_web", {"query": "{topic}", "engine": "google"}),
                    WorkflowStep("3", "Create Notes Folder", "create_folder", {"path": "~/Research/{topic}"}),
                    WorkflowStep("4", "Screenshot", "screenshot", {}),
                ]
            },
            "debug_error": {
                "name": "Debug Error",
                "description": "Capture error, search solution, open documentation",
                "steps": [
                    WorkflowStep("1", "Screenshot Error", "screenshot", {}),
                    WorkflowStep("2", "Search Error", "search_web", {"query": "{error_message}", "engine": "stackoverflow"}),
                    WorkflowStep("3", "Open Documentation", "open_url", {"url": "https://docs.python.org"}),
                ]
            },
        }
    
    def create_from_template(self, template_id: str, context: Dict[str, Any] = None) -> Optional[Workflow]:
        """Create a workflow from a template."""
        templates = self.get_workflow_templates()
        
        if template_id not in templates:
            return None
        
        template = templates[template_id]
        context = context or {}
        
        # Replace template variables in steps
        steps = []
        for step_template in template["steps"]:
            params = {}
            for key, value in step_template.params.items():
                if isinstance(value, str) and "{" in value:
                    # Replace template variables
                    for var_name, var_value in context.items():
                        value = value.replace(f"{{{var_name}}}", str(var_value))
                params[key] = value
            
            step = WorkflowStep(
                id=step_template.id,
                name=step_template.name,
                action=step_template.action,
                params=params,
                requires_confirmation=step_template.requires_confirmation,
                confirmation_prompt=step_template.confirmation_prompt,
                retry_on_failure=step_template.retry_on_failure,
                max_retries=step_template.max_retries,
                depends_on=step_template.depends_on
            )
            steps.append(step)
        
        return self.create_workflow(
            name=template["name"],
            description=template["description"],
            steps=steps
        )
    
    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow."""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            workflow.status = "cancelled"
            del self.active_workflows[workflow_id]
            return True
        return False
    
    def get_history(self) -> List[Dict]:
        """Get workflow execution history."""
        return [
            {
                "id": wf.id,
                "name": wf.name,
                "status": wf.status,
                "progress": wf.get_progress(),
                "duration": (wf.end_time - wf.start_time) if wf.end_time and wf.start_time else None,
                "completed_at": wf.end_time
            }
            for wf in sorted(self.workflow_history, key=lambda x: x.start_time or 0, reverse=True)
        ]


# Predefined workflow templates for common tasks
WORKFLOW_TEMPLATES = {
    "morning_routine": {
        "name": "Morning Routine",
        "description": "Start the day: check calendar, open email, news",
        "steps": [
            ("1", "Screenshot", "screenshot", {}),
            ("2", "Open Calendar", "open_application", {"app_name": "calendar"}),
            ("3", "Open Browser", "open_application", {"app_name": "chrome"}),
            ("4", "Check Volume", "volume_control", {"action": "set", "level": 50}),
        ]
    },
    "focus_mode": {
        "name": "Focus Mode",
        "description": "Minimize distractions for deep work",
        "steps": [
            ("1", "Mute System", "mute_system", {"mute": True}),
            ("2", "Open Code Editor", "open_application", {"app_name": "code"}),
            ("3", "Screenshot", "screenshot", {}),
        ]
    },
    "end_session": {
        "name": "End Session",
        "description": "Wrap up work: save, commit, close apps",
        "steps": [
            ("1", "Screenshot", "screenshot", {}),
            ("2", "Open Terminal", "open_application", {"app_name": "terminal"}),
            ("3", "Git Status", "shell_command", {"command": "git status", "requires_confirmation": False}),
        ]
    }
}
