# 🤖 SARTHAKA: Advanced AI Assistant
**"Not just an AI. A capable partner."**

Created by **Dipesh Patel** (@starkdipesh).

---

## 🚀 What's New - The 7-Phase Evolution

### ✅ Phase 1: Action Layer
Sarthika can now **act** on your commands:
- Open/close applications (Chrome, VS Code, OBS, etc.)
- Control media (play, pause, volume)
- System shortcuts (screenshot, lock screen, mute)
- File operations (create, delete, search)
- Browser automation (open URLs, search)
- Shell commands (with safety checks)

**Example:** *"Sarthika, open Chrome and search for Python tutorials"* → Opens Chrome, searches Google

### ✅ Phase 2: Smart Memory (RAG)
Sarthika remembers everything with **semantic search**:
- Vector-based memory storage (SQLite + embeddings)
- Project context detection from window titles
- Conversation retrieval with relevance scoring
- User profile storage

**Example:** *"Sarthika, what was I working on yesterday?"* → Retrieves from memory

### ✅ Phase 3: Workflow Engine
Sarthika executes **multi-step workflows**:
- Predefined templates: setup_streaming, start_coding, research_topic
- Dependency management between steps
- Progress tracking and retry logic
- Custom workflow creation

**Example:** *"Sarthika, setup my streaming environment"* → Opens OBS, browser, chat, tests audio

### ✅ Phase 4: Enhanced Proactivity
Sarthika is **event-driven**, not timer-based:
- Error detection on screen → Immediate alert
- Success detection → Celebration
- Break reminders after long sessions
- High activity detection
- Work hours notifications

**Example:** Sarthika sees an error on your screen: *"Sir, I've detected an error. Shall I help debug?"*

### ✅ Phase 5: Professional Tool Integrations
Sarthika integrates with your **professional tools**:
- **Git Helper:** Status, diff, auto-commit message generation
- **IDE Assistant:** Detect open editor, open projects
- **Notes Manager:** Create, search, manage knowledge
- **Calendar Helper:** Meeting reminders, daily prep

**Example:** *"Sarthika, commit my changes"* → Suggests message, commits

### ✅ Phase 6: Autonomous Task Agent
Sarthika **plans and executes** autonomously:
- Natural language goal parsing
- Task breakdown into steps
- Pattern-based planning
- Progress tracking
- Self-correction

**Example:** *"Sarthika, research Python AI for me"* → Plans steps, executes, saves notes

### ✅ Phase 7: Emotional Intelligence
Sarthika **adapts to your mood**:
- Mood detection: focused, frustrated, excited, tired
- Personality adaptation: professional, supportive, casual
- Response style modification
- Voice tone adjustment suggestions
- Proactive engagement based on state

**Example:** Detects frustration: *"Don't worry, Sir. We'll get this sorted."*

---

## 📋 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   SARTHAKA AI ASSISTANT                  │
├─────────────────────────────────────────────────────────┤
│  Phase 7: Emotional Intelligence (Mood Detection)       │
│  Phase 6: Autonomous Agent (Planning & Execution)       │
│  Phase 5: Tool Integrations (Git, IDE, Notes, Calendar)   │
│  Phase 4: Proactivity Engine (Event-Driven Triggers)    │
│  Phase 3: Workflow Engine (Multi-Step Tasks)            │
│  Phase 2: Smart Memory (RAG - Vector Search)            │
│  Phase 1: Action Executor (System Control)                │
├─────────────────────────────────────────────────────────┤
│  Core: Vision, Speech, Groq Cloud Brain, TTS            │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Linux (Ubuntu/Debian recommended)
- Groq API Key

### Quick Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd live-Commentry

# Install dependencies
pip install -r requirements.txt

# Optional: Install sentence-transformers for Smart Memory
pip install sentence-transformers

# Set up environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Run Sarthika
python3 main.py
```

### System Dependencies (Linux)
```bash
sudo apt install python3-pyaudio portaudio19-dev mpg123 xdotool
```

---

## 📂 Project Structure

```
live-Commentry/
├── main.py                          # Entry point
├── src/
│   ├── core/
│   │   ├── cloud_connector.py       # Groq API integration
│   │   ├── interactive_gaming_partner.py  # Main orchestrator
│   │   ├── action_executor.py       # Phase 1: System actions
│   │   ├── workflow_engine.py       # Phase 3: Multi-step workflows
│   │   ├── proactivity_engine.py    # Phase 4: Event-driven triggers
│   │   ├── autonomous_agent.py      # Phase 6: Planning & execution
│   │   └── emotional_intelligence.py # Phase 7: Mood detection
│   ├── memory/
│   │   └── smart_memory.py          # Phase 2: RAG memory
│   └── integrations/
│       └── tool_integrations.py     # Phase 5: Git, IDE, Notes
├── test_phase1.py                   # Test action layer
├── test_phase2.py                   # Test smart memory
├── test_phase3.py                   # Test workflows
├── test_phase4.py                   # Test proactivity
├── test_phases_5_7.py               # Test remaining phases
└── .env                             # Environment variables
```

---

## 🎮 Usage Examples

### Basic Commands
```bash
# Start Sarthika
python3 main.py

# Test specific phase
python3 test_phase1.py
python3 test_phase2.py
python3 test_phases_5_7.py
```

### Voice Commands You Can Say
- *"Sarthika, take a screenshot"*
- *"Sarthika, open Chrome"*
- *"Sarthika, search for Python tutorials"*
- *"Sarthika, setup my streaming environment"*
- *"Sarthika, what was I working on?"*
- *"Sarthika, commit my changes"*
- *"Sarthika, create a note about AI ideas"*
- *"Sarthika, research machine learning"*
- *"Sarthika, help me debug this error"*

---

## ⚙️ Configuration

### Environment Variables (.env)
```bash
# Required
GROQ_API_KEY=your_key_here

# AI Identity
AI_NAME=Sarthika
TONE_MODE=friday

# Model Settings
GROQ_MODEL=meta-llama/llama-4-scout-17b-16e-instruct
GROQ_MAX_TOKENS=90

# Voice Settings
TTS_VOICE=en-IN-NeerjaNeural
TTS_RATE=+8%

# Screen Capture
CAPTURE_QUALITY=70
CAPTURE_WIDTH=336
CAPTURE_HEIGHT=336
USE_CAMERA=0
```

---

## 🔧 Extending Sarthika

### Add Custom Actions
Edit `src/core/action_executor.py`:
```python
def _my_custom_action(self, params):
    # Your logic here
    return {"status": "success", "message": "Done"}
```

### Add Custom Workflows
Edit `src/core/workflow_engine.py`:
```python
"my_workflow": {
    "name": "My Custom Workflow",
    "steps": [
        WorkflowStep("1", "Open App", "open_application", {"app_name": "firefox"}),
    ]
}
```

### Add Custom Triggers
Edit `src/core/proactivity_engine.py`:
```python
custom_trigger = ProactiveTrigger(
    id="my_trigger",
    trigger_type=TriggerType.SCREEN_PATTERN,
    condition={"patterns": ["specific_text"]},
    message_template="Your message here"
)
```

---

## 🧪 Testing

Run individual phase tests:
```bash
python3 test_phase1.py  # Action layer
python3 test_phase2.py  # Smart memory
python3 test_phase3.py  # Workflow engine
python3 test_phase4.py  # Proactivity
python3 test_phases_5_7.py  # Tools, Agent, EI
```

---

## 📝 TODO / Future Enhancements

- [ ] Web interface for configuration
- [ ] Mobile app companion
- [ ] Home automation integration (MQTT)
- [ ] Advanced calendar integration (Google/Outlook API)
- [ ] Voice cloning for personalized TTS
- [ ] Multi-language support expansion
- [ ] Docker containerization
- [ ] Cloud sync for memory across devices

---

## 🤝 Credits

- **Created by:** Dipesh Patel (@starkdipesh)
- **Powered by:** Groq Cloud API
- **Voice:** edge-tts
- **Vision:** MSS + PIL

---

## 📜 License

MIT License - See LICENSE file

---

**"Sarthika, at your service, Sir."** 🤖
