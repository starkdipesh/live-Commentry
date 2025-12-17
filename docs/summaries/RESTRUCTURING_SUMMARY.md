# 🏗️ Project Restructuring Summary

The project has been reorganized into a professional "Best Practice" structure.

## 📂 New Directory Structure

```
live-Commentry/
├── run.py                          # 🚀 Main entry point
├── start.sh                        # 🚀 Start script (auto-activates venv)
├── venv/                           # 🐍 Virtual Environment (isolated python)
├── src/                            # 🧠 Source Code
│   ├── core/                       #    - Main commentator scripts
│   ├── processors/                 #    - Image processing modules
│   ├── collectors/                 #    - Dataset collectors
│   └── utils/                      #    - Utility scripts
├── config/                         # ⚙️ Configuration
│   ├── prompts/                    #    - Text prompts
│   ├── models/                     #    - Ollama Modelfiles
│   └── .env                        #    - Environment variables
├── scripts/                        # 📜 Setup and maintenance scripts
│   ├── setup_lightweight.sh        #    - Primary setup script
│   └── ...
├── docs/                           # 📚 Documentation
│   ├── guides/                     #    - Tutorials and guides
│   ├── summaries/                  #    - Improvement summaries
│   └── ...                         #    - Other docs
├── requirements/                   # 📦 Dependency definitions
│   ├── requirements_lightweight.txt
│   └── ...
└── tests/                          # 🧪 Test scripts
```

## 🚀 How to Run

### Option 1: Quick Start (Recommended)
```bash
./start.sh
```
This automatically activates the virtual environment and runs the lightweight commentator.

### Option 2: Run Specific Modes
```bash
source venv/bin/activate

# Run Lightweight (Default)
python3 run.py lightweight

# Run Enhanced (GPU required)
python3 run.py enhanced

# Run Data Collector
python3 run.py collect
```

## 🛠️ Setup Changes
- **Virtual Environment**: All dependencies are now installed in `venv/`. This fixes the "externally-managed-environment" error.
- **Imports**: Code imports have been updated to support the directory structure.

## 📚 Documentation Locations
- **Training Guide**: `docs/guides/FREE_TRAINING_LOW_SPEC.md`
- **Quick Reference**: `docs/summaries/QUICK_REFERENCE.md`
- **Low Spec Guide**: `docs/guides/LOW_SPEC_GUIDE.md`

