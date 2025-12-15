# 🚀 Quick Start Guide - FREE AI Commentary

## ⚡ 3-Minute Setup

### Step 1: Install Ollama (2 minutes)

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
- Download from: https://ollama.ai/download

### Step 2: Run Setup Script (1 minute)

**Linux/macOS:**
```bash
chmod +x setup_free_commentary.sh
./setup_free_commentary.sh
```

**Windows:**
```cmd
setup_free_commentary.bat
```

### Step 3: Start Commentary! (30 seconds)

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Run commentator
python3 gameplay_commentator_free.py
```

**That's it!** 🎉

---

## 💡 Even Faster Setup

If you already have Python and want minimal setup:

```bash
# Install deps
pip install mss Pillow pyttsx3 requests

# Install Ollama (one command - Linux/macOS)
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve &

# Download model
ollama pull llava:latest

# Run!
python3 gameplay_commentator_free.py
```

---

## 🎮 Usage

1. **Start Ollama**: `ollama serve` (keep running)
2. **Run script**: `python3 gameplay_commentator_free.py`
3. **Play game**: AI will commentate automatically!
4. **Stop**: Press `Ctrl+C`

---

## ⚙️ What's Happening?

```
Your Screen → LLaVA (Local AI) → Hindi Commentary → Voice Output
     ↑                                                    ↓
     └─────────── Every 8 seconds ──────────────────────┘
```

**Cost**: $0.00 forever ✅
**Internet**: Not needed after setup ✅
**Limits**: None ✅

---

## 🆘 Troubleshooting

### Ollama won't start?
```bash
# Check if already running:
curl http://localhost:11434/api/tags

# If not, start it:
ollama serve
```

### Model not found?
```bash
ollama pull llava:latest
```

### No voice?
```bash
# Linux only:
sudo apt-get install espeak
```

### Everything else?
```bash
# Run test script:
python3 test_free_setup.py
```

---

## 📊 Comparison

| | Paid Version | FREE Version |
|---|---|---|
| Cost/hour | $1.50 | $0.00 |
| Setup | 2 min | 10 min |
| Speed | 2-3s | 5-10s |
| Internet | Required | No |
| Quality | Excellent | Very Good |

---

## 🎯 Pro Tips

### Make it faster:
```python
# Edit gameplay_commentator_free.py:
self.screenshot_interval = 5  # More frequent
```

### Use smaller model:
```bash
ollama pull llava:7b  # Faster, less RAM
```

### Better voice quality:
```bash
pip install TTS  # Coqui TTS (optional upgrade)
```

---

## ✅ Checklist

- [ ] Python 3.8+ installed
- [ ] Ollama installed
- [ ] LLaVA model downloaded
- [ ] `ollama serve` running
- [ ] Dependencies installed
- [ ] Test passed (`python3 test_free_setup.py`)

**All checked?** You're ready! 🚀

```bash
python3 gameplay_commentator_free.py
```

---

**Need more help?** Check `FREE_COMMENTARY_README.md` for detailed guide.

**Happy Gaming!** 🎮🎙️
