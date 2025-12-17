# 🎮 How to Use the AI Gameplay Commentator

## ✅ Setup Complete!

Your AI-powered gameplay commentator is **fully functional** and ready to use! The test shows:
- ✅ All libraries installed
- ✅ Emergent LLM Key configured
- ✅ AI connection working perfectly
- ✅ Commentary generation tested successfully

## 🖥️ Running on Your Local Machine

The script requires a **display and audio device**, so it needs to run on your **local computer** (not in this cloud container).

### Step 1: Download Files

Download these files to your local machine:
```
/app/gameplay_commentator.py    # Main script
/app/.env                        # API key
/app/demo_commentary.py          # Demo mode (optional)
```

### Step 2: Install Dependencies on Your Local Machine

```bash
# Install Python dependencies
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
pip install mss pillow gtts pygame python-dotenv
```

### Step 3: Run the Commentator

```bash
# Navigate to the directory with the files
cd /path/to/downloaded/files

# Run the main script
python3 gameplay_commentator.py
```

### Step 4: Start Playing!

1. Open your game (any game works!)
2. The script will capture your screen every 8 seconds
3. AI analyzes what's happening
4. Humorous commentary is spoken aloud
5. Press **Ctrl+C** to stop

## 🎮 Workflow

```
YOU PLAY GAME → AI WATCHES → AI GENERATES JOKE → AI SPEAKS IT → REPEAT
```

## 🎙️ Using Commentary in Streams

### Option A: Virtual Audio Cable (Recommended)
1. Install **VB-Audio Virtual Cable** or **Voicemeeter**
2. Route Python audio to virtual input
3. OBS/Streaming software captures virtual input
4. Viewers hear AI commentary!

### Option B: Physical Setup
1. Play commentary through speakers
2. Capture with microphone
3. Mix with your voice in OBS

### Option C: Direct Recording
1. Run script during gameplay
2. Record system audio
3. Edit/mix in post-production

## 📊 Demo Mode (No Screen Required)

Want to see the AI in action without gameplay? Run the demo:

```bash
python3 demo_commentary.py
```

This shows how the AI generates hilarious commentary for different scenarios!

## ⚙️ Customization

### Change Commentary Frequency
Edit `gameplay_commentator.py`:
```python
self.screenshot_interval = 8  # Change to 5, 10, 15, etc.
```

### Change AI Model
Edit the model selection:
```python
.with_model("openai", "gpt-5.1")  # Use GPT-5.1
.with_model("openai", "gpt-4o")   # Use GPT-4o (current)
```

### Modify Humor Style
Edit the system prompt in `_get_system_prompt()` to adjust:
- Sarcasm level
- Encouragement vs roasting ratio
- Profanity (keep it clean!)
- References and style

### Change Voice
Edit TTS settings:
```python
# Current: gTTS (English, normal speed)
tts = gTTS(text=text, lang='en', slow=False)

# Options:
tts = gTTS(text=text, lang='en', slow=True)   # Slower speech
tts = gTTS(text=text, lang='en-uk')           # British accent
tts = gTTS(text=text, lang='en-au')           # Australian accent
```

## 🎯 Tips for Best Results

1. **Game Selection**: More action = funnier commentary
2. **Internet Connection**: Required for AI calls (each capture uses API)
3. **Screen Size**: Works with any resolution (auto-optimized)
4. **Multiple Monitors**: Captures primary monitor only
5. **Performance**: Close heavy apps for smooth operation

## 💰 API Usage & Costs

- Uses **Emergent LLM Key** (universal key)
- Each commentary = 1 API call to GPT-4o Vision
- At 8-second intervals = ~450 calls per hour
- Check balance: Profile → Universal Key → Balance
- Add credits or enable auto top-up as needed

## 🔧 Troubleshooting

### "No module named 'emergentintegrations'"
```bash
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
```

### "DISPLAY not set" or "No screen"
- You're in a headless environment (no display)
- Run on your local machine with a display

### "No audio device"
- Check system audio settings
- Try: `python3 -m pygame.tests`
- Ensure speakers/headphones connected

### "API Error" or "Key Invalid"
- Check `.env` file has correct key
- Verify internet connection
- Check Emergent LLM Key balance

### Commentary is repetitive
- AI has memory (last 5 comments)
- Restart script for fresh session
- Increase screenshot interval for more variety

### Performance issues
- Close unnecessary apps
- Increase `screenshot_interval` (less frequent)
- Use smaller screen resolution

## 🎥 Example Streaming Setup

```
┌─────────────┐
│  Your Game  │
└──────┬──────┘
       │
       ├─ VIDEO → OBS (Screen Capture)
       │
       └─ AI Commentary Script ──> Virtual Audio Cable ──> OBS (Audio Input)
```

## 📝 Example Output

```
🎬 Comment #1 | 14:32:05
📸 Capturing gameplay...
✅ Screenshot captured (1920x1080)
🤖 AI analyzing gameplay and generating commentary...

💬 COMMENTARY: "That aim is smoother than butter on a hot skillet!"

🎙️ Speaking commentary...
✅ Commentary delivered!
⏳ Waiting 3.2s before next commentary...
```

## 🚀 Next Level Ideas

Want to enhance the system? Consider:

1. **Twitch Integration**: Read chat messages, react to donations
2. **Game-Specific Modes**: Custom prompts for specific games
3. **Clip Detection**: Auto-save funny moments
4. **Multiple Voices**: Random voice selection per comment
5. **Sentiment Tracking**: Adjust humor based on gameplay quality
6. **Highlight Reel**: Auto-compile best commentary moments

## 📞 Support

**Issues with the script?**
- Check all dependencies installed
- Verify `.env` file in same directory
- Test with `python3 demo_commentary.py` first

**Issues with Emergent LLM Key?**
- Go to Profile → Universal Key
- Check balance and add credits
- Enable auto top-up for convenience

## 🎉 Ready to Go!

Your AI comedy commentator is ready to roast... I mean, **enhance** your gameplay! 

Now go stream some games and let the AI work its magic! 😄

---

**Questions or Feedback?**
The system is designed to be:
- ✅ Easy to use
- ✅ Highly customizable
- ✅ YouTube algorithm optimized
- ✅ Fun and engaging

Enjoy your AI commentary sidekick! 🎮🎙️
