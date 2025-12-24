# 🕉️ PARTHASARATHI: The Living AI Partner
**"Not just a bot. A Sarthi."**

Created by **Dipesh Patel** (@starkdipesh).

## 🚀 Features
- **Dual-Brain Architecture**: Uses `llava-phi3` for Vision and `phi4` for High-IQ Reasoning.
- **Hinglish Identity**: Speaks like a true Indian gaming buddy.
- **Memory System**: Remembers you across sessions.
- **Auto-Training**: "Professor Mode" converts your gameplay into training data while you sleep.
- **Hardware Ready**: Built-in hooks for Arduino/ESP32 control.

## 📦 How to Move to a New PC (Portability Guide)

This project is designed to be **Cloned & Run** anywhere.

### Step 1: Clone the Repo
On your new PC:
```bash
git clone <your-repo-url>
cd live-Commentry
```

### Step 2: Run the One-Click Setup
This script will install System Dependencies, download the heavy AI Models (15GB+), and set up the Python environment.
```bash
chmod +x setup.sh
./setup.sh
```

### Step 3: Wake Him Up
```bash
source venv/bin/activate
python3 run.py interactive
```

## 📂 Project Structure
- `src/core/`: The Brain (`interactive_gaming_partner.py`)
- `src/learning/`: The Professor (`auto_trainer.py`)
- `training_data/gold_dataset/`: The "Learned Experience" (Synced via Git)
- `config/personal_memory.json`: The "Long-term Memory" (Synced via Git)

## 🛠️ Hardware Integration
To connect Arduinos, edit `src/core/interactive_gaming_partner.py` and uncomment the `HardwareController` section.
