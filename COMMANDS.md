# 🤖 SARTHAKA - Command & Feature Guide
**Complete reference for enabling and using all 7 phases**

Created by **Dipesh Patel**

---

## 📋 Quick Start Commands

### Launch Sarthika
```bash
# Basic start
python3 main.py

# With custom voice
AI_NAME=Sarthika TTS_VOICE=en-IN-NeerjaNeural python3 main.py

# Debug mode (verbose logging)
python3 main.py --debug
```

### Test Individual Components
```bash
# Test all phases
python3 test_main_system.py

# Test specific phase
python3 test_phase1.py  # Actions
python3 test_phase2.py  # Memory
python3 test_phase3.py  # Workflows
python3 test_phase4.py  # Proactivity
python3 test_phases_5_7.py  # Tools, Agent, EI
```

---

## ⚙️ Configuration Commands (.env file)

### Core Settings
```bash
# Required
GROQ_API_KEY=your_api_key_here

# AI Identity
AI_NAME=Sarthika                    # Assistant name
TONE_MODE=friday                    # friday | casual | professional

# Model Configuration
GROQ_MODEL=meta-llama/llama-4-scout-17b-16e-instruct
GROQ_MAX_TOKENS=90
GROQ_TEMPERATURE=0.5
```

### Phase 1: Action Executor Settings
```bash
# Enable/disable action categories
ACTIONS_SYSTEM=1        # screenshot, lock, mute
ACTIONS_MEDIA=1         # volume, media control
ACTIONS_APPS=1          # open/close applications
ACTIONS_FILES=1         # file operations
ACTIONS_BROWSER=1       # web search, open URLs
ACTIONS_SHELL=0         # shell commands (disabled by default for safety)
```

### Phase 2: Smart Memory Settings
```bash
# Memory database
MEMORY_DB_PATH=./config/sarthika_memory.db
MEMORY_MAX_CHUNKS=10000

# Embeddings (optional but recommended)
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDINGS_ENABLED=1

# Context window
MEMORY_RECENT_N=5       # Recent interactions to include
MEMORY_RELEVANT_K=3     # Relevant memories to retrieve
```

### Phase 3: Workflow Engine Settings
```bash
# Workflow behavior
WORKFLOW_AUTO_CONFIRM=0     # 1 = skip confirmation, 0 = ask
WORKFLOW_MAX_RETRIES=3
WORKFLOW_TIMEOUT=300        # seconds
```

### Phase 4: Proactivity Settings
```bash
# Proactive triggers
PROACTIVITY_ENABLED=1
ERROR_DETECTION=1
SUCCESS_DETECTION=1
BREAK_REMINDERS=1
WORK_HOURS_START=09:00
WORK_HOURS_END=18:00
```

### Phase 5: Tool Integration Settings
```bash
# Git
GIT_AUTO_COMMIT=0       # Auto-generate commit messages
GIT_REPO_SCAN_DEPTH=3

# IDE
IDE_EDITOR=code         # code | pycharm | subl

# Notes
NOTES_DIR=./notes
NOTES_AUTO_TAG=1

# Calendar
CALENDAR_CHECK_INTERVAL=300  # seconds
```

### Phase 6: Autonomous Agent Settings
```bash
# Autonomous mode
AUTONOMOUS_ENABLED=1
AUTO_CONFIRM_TASKS=0    # Require confirmation for autonomous tasks
MAX_AUTO_STEPS=10     # Maximum steps without confirmation
```

### Phase 7: Emotional Intelligence Settings
```bash
# Mood detection
EI_ENABLED=1
MOOD_DETECTION_SENSITIVITY=medium  # low | medium | high
ADAPTIVE_RESPONSES=1
PROACTIVE_ENGAGEMENT=1
```

---

## 🎤 Voice Commands

### Phase 1: Actions - "Sarthika, [command]"

#### System Actions
```
"Sarthika, take a screenshot"
"Sarthika, lock the screen"
"Sarthika, mute the system"
"Sarthika, set volume to 50%"
"Sarthika, what's the time?"
```

#### Application Control
```
"Sarthika, open Chrome"
"Sarthika, open VS Code"
"Sarthika, close Firefox"
"Sarthika, open Terminal"
```

#### Media Control
```
"Sarthika, play music"
"Sarthika, pause"
"Sarthika, next track"
"Sarthika, volume up"
```

#### File Operations
```
"Sarthika, create a file called notes.txt"
"Sarthika, open my downloads folder"
"Sarthika, search for PDF files"
```

#### Browser & Web
```
"Sarthika, search for Python tutorials"
"Sarthika, open github.com"
"Sarthika, look up weather in Delhi"
```

---

### Phase 2: Memory - "Sarthika, [remember/recall]"

```
"Sarthika, remember I prefer dark mode"
"Sarthika, what was I working on yesterday?"
"Sarthika, recall my last conversation about AI"
"Sarthika, save this: my API key is xyz"
"Sarthika, what projects have I been working on?"
"Sarthika, remind me about the meeting with John"
```

---

### Phase 3: Workflows - "Sarthika, [setup/start]"

#### Predefined Workflows
```
"Sarthika, setup my streaming environment"
"Sarthika, start my coding session"
"Sarthika, research machine learning for me"
"Sarthika, help me debug this error"
```

#### Custom Workflows
```
"Sarthika, create a workflow for morning routine"
"Sarthika, run my custom workflow: deploy_app"
```

---

### Phase 4: Proactivity (Automatic)

Sarthika monitors and alerts automatically:

```
# Error detected on screen → "Sir, I see an error. Shall I help debug?"
# Success detected → "Build successful! Well done, Sir."
# Long session → "Sir, you've been working for 2 hours. Time for a break?"
# Work hours start → "Good morning, Sir. Ready to begin?"
```

**Enable/disable:**
```bash
# In code
from src.core.proactivity_engine import get_proactivity_engine
engine = get_proactivity_engine()
engine.disable_trigger("break_reminder")  # Disable specific trigger
engine.pause()  # Pause all proactivity
engine.resume()  # Resume proactivity
```

---

### Phase 5: Professional Tools - "Sarthika, [git/notes/calendar]"

#### Git Helper
```
"Sarthika, what's the git status?"
"Sarthika, commit my changes"
"Sarthika, suggest a commit message"
"Sarthika, show me recent commits"
"Sarthika, create a new branch called feature-x"
```

#### IDE Assistant
```
"Sarthika, open my recent project"
"Sarthika, what IDE am I using?"
"Sarthika, open project: MyApp"
```

#### Notes Manager
```
"Sarthika, create a note about AI ideas"
"Sarthika, search my notes for 'python'"
"Sarthika, show my recent notes"
"Sarthika, save this: remember to refactor the auth module"
```

#### Calendar Helper
```
"Sarthika, what's on my calendar today?"
"Sarthika, do I have any meetings?"
"Sarthika, remind me about my 3pm call"
```

---

### Phase 6: Autonomous Agent - "Sarthika, [do/research]"

```
"Sarthika, research Python async libraries for me"
"Sarthika, find the best practices for REST APIs"
"Sarthika, check my code for errors and fix them"
"Sarthika, update all my packages"
"Sarthika, organize my downloads folder"
```

**Autonomous confirmation modes:**
```bash
# In .env - control how autonomous tasks are confirmed
AUTO_CONFIRM_TASKS=ask       # Always ask before executing
AUTO_CONFIRM_TASKS=safe      # Auto-confirm safe actions only
AUTO_CONFIRM_TASKS=all       # Auto-confirm all (use with caution)
```

---

### Phase 7: Emotional Intelligence (Automatic + Commands)

**Automatic adaptation:**
```
User frustrated → Sarthika responds with supportive tone
User excited → Sarthika matches enthusiasm
User tired → Sarthika suggests break
```

**Manual mood setting:**
```python
# In code
from src.core.emotional_intelligence import EmotionalIntelligence, Mood

ei = EmotionalIntelligence()
ei.state.mood = Mood.FOCUSED  # Manually set mood
ei.state.energy_level = 0.8
```

---

## 💻 Programmatic API

### Initialize Sarthika Components

```python
from src.core.interactive_gaming_partner import InteractiveGamingPartner

# Full system initialization
sarthika = InteractiveGamingPartner()
sarthika.start()  # Start listening
```

### Phase 1: Action Executor (Direct API)

```python
from src.core.action_executor import ActionExecutor, quick_screenshot, quick_search

executor = ActionExecutor()

# Execute actions programmatically
result = executor.execute("screenshot", {})
result = executor.execute("open_application", {"app_name": "firefox"})
result = executor.execute("search_web", {"query": "python tutorial"})
result = executor.execute("media_control", {"command": "pause"})

# Quick helpers
quick_screenshot("/path/to/save.png")
quick_search("django best practices")
quick_note("Remember to refactor auth.py")
```

### Phase 2: Smart Memory (Direct API)

```python
from src.memory.smart_memory import SmartMemory, get_memory

# Initialize
memory = SmartMemory()
# OR use singleton
memory = get_memory()

# Store interaction
memory.store_interaction(
    user_input="User said this",
    ai_response="Sarthika replied this",
    visual_context="VS Code - ProjectX",
    session_id="coding_session_1"
)

# Retrieve relevant context
results = memory.retrieve_relevant_context("python async", top_k=5)

# Get stats
stats = memory.get_stats()
print(f"Total memories: {stats['total_chunks']}")

# Get current project
project = memory.get_current_project()
print(f"Working on: {project}")
```

### Phase 3: Workflow Engine (Direct API)

```python
from src.core.workflow_engine import WorkflowEngine, WorkflowStep
from src.core.action_executor import ActionExecutor

executor = ActionExecutor()
workflow_eng = WorkflowEngine(executor)

# Create workflow from template
wf = workflow_eng.create_from_template("setup_streaming")

# Create custom workflow
from src.core.workflow_engine import WorkflowStep
custom_wf = workflow_eng.create_workflow(
    name="Deploy App",
    description="Deploy application to production",
    steps=[
        WorkflowStep("1", "Run Tests", "shell_command", {"command": "pytest"}),
        WorkflowStep("2", "Build", "shell_command", {"command": "npm run build"}),
        WorkflowStep("3", "Deploy", "shell_command", {"command": "deploy.sh"}),
    ]
)

# Execute workflow
import asyncio
completed_wf = asyncio.run(workflow_eng.execute_workflow(custom_wf))

# Check status
status = workflow_eng.get_workflow_status(custom_wf.id)
print(f"Progress: {status['progress']:.0%}")
```

### Phase 4: Proactivity Engine (Direct API)

```python
from src.core.proactivity_engine import (
    ProactivityEngine, ProactiveTrigger, 
    TriggerType, get_proactivity_engine
)

# Get singleton instance
engine = get_proactivity_engine()

# Register custom trigger
trigger = ProactiveTrigger(
    id="deploy_success",
    trigger_type=TriggerType.SCREEN_PATTERN,
    condition={"patterns": ["Build successful", "Deployment complete"]},
    message_template="Deployment complete! Shall I update the changelog?",
    priority=8
)
engine.register_trigger(trigger)

# Analyze context manually
triggers = engine.analyze_context(
    screen_text="Error: Connection refused",
    active_window="Terminal",
    user_active=True
)

# Register callback
def on_trigger(trigger_info):
    print(f"Triggered: {trigger_info['message']}")

engine.register_callback(on_trigger)

# Pause/Resume
engine.pause()
engine.resume()
```

### Phase 5: Tool Integrations (Direct API)

```python
from src.integrations.tool_integrations import (
    ToolIntegrations, GitHelper, 
    quick_commit, quick_note
)

# Unified tools
tools = ToolIntegrations()
context = tools.get_context_summary()

# Git helper
git = GitHelper()
if git.is_git_repo():
    status = git.get_status()
    suggestion = git.suggest_commit()
    print(f"Suggested: {suggestion['suggestion']}")

# Quick helpers
quick_commit("Fixed the authentication bug")
quick_note("Ideas for new feature: implement caching")
```

### Phase 6: Autonomous Agent (Direct API)

```python
from src.core.autonomous_agent import AutonomousAgent
from src.core.action_executor import ActionExecutor
from src.core.workflow_engine import WorkflowEngine

executor = ActionExecutor()
workflow = WorkflowEngine(executor)
agent = AutonomousAgent(executor, workflow)

# Create and execute task
import asyncio
task = asyncio.run(agent.create_and_execute(
    goal="Research best Python web frameworks",
    context={"focus": "async performance"},
    auto_confirm=False  # Ask before each step
))

# Get task summary
summary = agent.get_task_summary(task.id)
print(f"Task {task.id}: {summary['progress']:.0%} complete")

# List all tasks
all_tasks = agent.list_tasks()
```

### Phase 7: Emotional Intelligence (Direct API)

```python
from src.core.emotional_intelligence import (
    EmotionalIntelligence, Mood, 
    PersonalityMode, get_voice_settings_for_mood
)

ei = EmotionalIntelligence()

# Analyze mood
mood = ei.analyze_interaction(
    user_input="I can't get this to work!",
    screen_context="Error traceback",
    error_detected=True
)
print(f"Detected mood: {mood.value}")  # "frustrated"

# Get personality mode
personality = ei.get_personality_mode()
print(f"Personality: {personality.value}")  # "supportive"

# Adapt response
response = ei.adapt_response_style(
    "Let me help you debug this.",
    mood
)
print(f"Adapted: {response}")

# Get voice settings
settings = get_voice_settings_for_mood(Mood.EXCITED)
print(f"Rate: {settings['rate']}, Volume: {settings['volume']}")

# Should proactively engage?
should_engage, reason = ei.should_proactively_engage()
```

---

## 🎛️ Feature Toggles

### Enable/Disable Features at Runtime

```python
from src.core.interactive_gaming_partner import InteractiveGamingPartner

sarthika = InteractiveGamingPartner()

# Toggle features
sarthika.use_cloud_mind = True      # Use Groq API
sarthika.use_local_fallback = True  # Fallback to local if cloud fails
sarthika.proactive_enabled = True   # Phase 4 proactivity

# Component-specific toggles
sarthika.proactivity_engine.pause()           # Pause all proactivity
sarthika.proactivity_engine.resume()          # Resume proactivity
sarthika.autonomous_agent.enabled = False     # Disable autonomous mode
```

---

## 🔧 Troubleshooting Commands

### Check System Status
```bash
# Run diagnostics
python3 test_main_system.py

# Check specific component
python3 -c "from src.core.action_executor import ActionExecutor; print(ActionExecutor().get_available_intents())"
```

### Reset/Clear Data
```bash
# Clear memory database
rm config/sarthika_memory.db

# Clear workflow cache
rm config/workflows/*.json

# Reset notes
rm -rf notes/*
```

### Debug Mode
```bash
# Enable verbose logging
DEBUG=1 python3 main.py

# Log to file
python3 main.py 2>&1 | tee sarthika.log
```

---

## 📚 Voice Command Reference Table

| Feature | Command Pattern | Example |
|---------|-----------------|---------|
| **Actions** | "Sarthika, [action]" | "Sarthika, take a screenshot" |
| **Memory** | "Sarthika, remember/recall [what]" | "Sarthika, remember my API key" |
| **Workflows** | "Sarthika, [setup/start] [workflow]" | "Sarthika, setup streaming" |
| **Git** | "Sarthika, [git command]" | "Sarthika, commit changes" |
| **Notes** | "Sarthika, note [content]" | "Sarthika, note: refactor auth" |
| **Research** | "Sarthika, research [topic]" | "Sarthika, research async Python" |
| **Help** | "Sarthika, help [with what]" | "Sarthika, help me debug" |

---

**Sarthika awaits your commands, Sir.** 🤖
