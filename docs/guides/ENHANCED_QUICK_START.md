# 🚀 Enhanced Commentary System - Quick Start Guide

## 🎯 What's New in v3.0 (Enhanced Version)

### Major Improvements:
1. **Advanced Image Processing**
   - Multi-scale preprocessing
   - Motion detection between frames
   - UI element enhancement
   - Adaptive scene optimization (dark/bright)
   - Edge detection for better UI recognition

2. **Upgraded Model**
   - Using `llava:13b-v1.6` (better than previous 7b)
   - Optimized parameters for vision understanding
   - Larger context window (4096 tokens)

3. **Scene Analysis**
   - Auto-detects scene type (action, menu, loading)
   - Measures motion intensity
   - Adapts commentary energy to scene

4. **Context-Aware Prompts**
   - Provides scene context to model
   - Image statistics (brightness, dominant color)
   - Better anti-repetition

---

## 📦 Installation

### Step 1: Install Python Dependencies

```bash
# Core dependencies
pip install -r requirements_enhanced.txt

# This installs:
# - opencv-python (for advanced processing)
# - numpy (for image operations)
# - edge-tts (for natural voice)
# - pygame (for audio)
# - All other requirements
```

### Step 2: Install/Upgrade Ollama Model

```bash
# For best results, use the upgraded model:
ollama pull llava:13b-v1.6

# This is MUCH better than the default llava:latest (7b)
# Needs: 16GB RAM recommended

# Alternative (if limited RAM):
ollama pull llava:7b-v1.6

# Edit gameplay_commentator_enhanced.py:
# Change self.model_name = "llava:7b-v1.6"
```

### Step 3: Verify Installation

```bash
# Test advanced image processor
python3 -c "
from advanced_image_processor import AdvancedImageProcessor
from PIL import Image
import numpy as np

processor = AdvancedImageProcessor(enhance_mode='balanced')
test_img = Image.new('RGB', (1920, 1080), color='blue')
processed = processor.preprocess_for_vision_model(test_img)
print('✅ Image processor working!')
print(f'   Processed size: {processed.size}')
"

# Test Ollama connection
python3 -c "
import requests
try:
    r = requests.get('http://localhost:11434/api/tags', timeout=5)
    if r.status_code == 200:
        models = [m['name'] for m in r.json().get('models', [])]
        print('✅ Ollama running!')
        print(f'   Models: {models}')
    else:
        print('❌ Ollama not responding')
except:
    print('❌ Ollama not running. Start with: ollama serve')
"
```

---

## 🎮 Basic Usage

### Running the Enhanced Commentator

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Run enhanced commentator
python3 gameplay_commentator_enhanced.py
```

### What Happens:
1. **Captures screen** every 8 seconds
2. **Analyzes scene** (type, motion, brightness)
3. **Processes image** with multi-scale enhancement
4. **Detects motion** from previous frame
5. **Enhances UI elements** (health bars, text, etc.)
6. **Adapts to scene** (dark/bright optimization)
7. **Generates commentary** with context-aware prompt
8. **Speaks naturally** with Edge-TTS

---

## ⚙️ Configuration & Customization

### Performance Modes

Edit `gameplay_commentator_enhanced.py`:

```python
# Line ~37: Change enhance_mode
self.image_processor = AdvancedImageProcessor(
    target_size=1280,
    enhance_mode='balanced'  # CHANGE THIS
)

# Options:
# 'speed'    - Fast processing, lower quality (768px, minimal enhancements)
# 'balanced' - Good balance (1024px, moderate enhancements) ⭐ RECOMMENDED
# 'quality'  - Best quality, slower (1280px, maximum enhancements)
```

### Model Selection

```python
# Line ~33: Change model
self.model_name = "llava:13b-v1.6"  # CHANGE THIS

# Options (in order of quality):
# "llava:7b"         - Fast, basic
# "llava:7b-v1.6"    - Fast, improved
# "llava:13b-v1.6"   - Best balance ⭐ RECOMMENDED
# "llava:34b-v1.6"   - Highest quality (needs 32GB RAM + GPU)
```

### Screenshot Interval

```python
# Line ~46: Change interval
self.screenshot_interval = 8  # CHANGE THIS (seconds)

# Recommendations:
# 5-6  - Very frequent (intense action games)
# 8    - Standard ⭐ RECOMMENDED
# 10   - Slower pace (strategy games)
# 12+  - Very slow (casual games, lower CPU usage)
```

### Voice Selection

```python
# Line ~49: Change voice
self.tts_voice = "hi-IN-SwaraNeural"  # CHANGE THIS

# Hindi Options:
# "hi-IN-SwaraNeural"  - Female, natural ⭐ RECOMMENDED
# "hi-IN-MadhurNeural" - Male, clear

# To list all available voices:
# edge-tts --list-voices | grep hi-IN
```

---

## 🎨 Image Processing Features

### Feature Comparison

| Feature | Old Version | Enhanced Version |
|---------|-------------|------------------|
| Image Size | 1024px | Adaptive (768-1280px) |
| Enhancements | Basic sharpening | Multi-layer processing |
| Motion Detection | ❌ No | ✅ Yes |
| Scene Analysis | ❌ No | ✅ Yes (type, intensity) |
| UI Enhancement | ❌ No | ✅ Yes (edge detection) |
| Adaptive Processing | ❌ No | ✅ Yes (dark/bright scenes) |
| Context Prompts | Basic | Advanced (scene-aware) |

### What Gets Enhanced:

1. **Contrast & Brightness**
   - Auto-adjusts for dark/bright scenes
   - Boosts visibility without oversaturation

2. **Sharpness**
   - Multi-level sharpening for detail
   - Unsharp mask for critical elements

3. **Color Enhancement**
   - Boosts important colors (red health bars, etc.)
   - Better saturation for color recognition

4. **Motion Highlighting**
   - Detects motion from previous frame
   - Subtle brightness boost in action areas
   - Helps model focus on dynamic elements

5. **UI Element Enhancement**
   - Edge detection emphasizes UI boundaries
   - Better recognition of text, bars, indicators

---

## 📊 Performance Benchmarks

### Expected Processing Times (per commentary):

| Configuration | GPU | Avg Time | Quality |
|---------------|-----|----------|---------|
| llava:7b + speed | RTX 3060 | 3-4s | Good |
| llava:7b-v1.6 + balanced | RTX 3060 | 4-5s | Very Good |
| llava:13b-v1.6 + balanced | RTX 3090 | 5-7s | Excellent ⭐ |
| llava:13b-v1.6 + quality | RTX 4090 | 6-8s | Outstanding |
| llava:34b-v1.6 + quality | A100 40GB | 10-15s | Best Possible |

**CPU Only:**
- llava:7b: 10-20s
- llava:13b: 30-60s
- ❌ Not recommended for llava:34b

---

## 🔧 Troubleshooting

### Issue: "Model not found"

```bash
# Download the upgraded model
ollama pull llava:13b-v1.6

# Verify installation
ollama list
```

### Issue: "OpenCV not working"

```bash
# Reinstall opencv
pip uninstall opencv-python opencv-python-headless
pip install opencv-python==4.8.0
```

### Issue: "Slow processing (>30s per commentary)"

**Solutions:**
1. Use faster model: `llava:7b-v1.6`
2. Change mode to 'speed': `enhance_mode='speed'`
3. Increase interval: `screenshot_interval = 12`
4. Check GPU usage: `nvidia-smi`

### Issue: "Memory error"

**Solutions:**
1. Use smaller model: `llava:7b-v1.6`
2. Reduce target size:
   ```python
   self.image_processor = AdvancedImageProcessor(
       target_size=768,  # Reduced from 1280
       enhance_mode='speed'
   )
   ```
3. Close other applications
4. Reduce memory: Change in settings:
   ```python
   "num_ctx": 2048,  # Reduced from 4096
   ```

---

## 🚀 Advanced Features

### Motion Detection

The system now tracks motion between frames:
- Highlights areas with movement
- Helps model focus on action
- Better for fast-paced games

**Disable if needed:**
```python
# In generate_commentary_enhanced(), line ~220:
processed_img = self.image_processor.preprocess_for_vision_model(
    screenshot,
    detect_motion=False  # Change to False
)
```

### Scene Type Detection

Auto-detects:
- **Menu**: Lower energy commentary
- **Gameplay**: Standard commentary
- **Intense Action**: High energy, excited commentary
- **Loading**: Time-filling remarks

**View scene info:**
```python
# It's printed automatically:
# 📊 Scene: intense_action | Motion: 0.85
```

### Image Statistics

Automatically analyzes:
- Brightness level (dark/bright scene)
- Dominant color (red/green/blue/yellow)
- Contrast level
- Scene type

**View stats:**
```python
# Printed automatically:
# 🎨 Image: red | Dark
```

---

## 🎯 Best Practices

### For Best Commentary Quality:

1. **Use adequate hardware**
   - GPU recommended (RTX 3060 or better)
   - 16GB RAM minimum
   - SSD for faster loading

2. **Choose right settings**
   - Fast action games: `enhance_mode='balanced'`, `interval=6`
   - Strategy games: `enhance_mode='quality'`, `interval=10`
   - Streaming: `enhance_mode='speed'`, `interval=8`

3. **Optimize Ollama**
   - Keep Ollama running in background
   - Use latest version: `brew upgrade ollama`
   - Monitor GPU usage: `nvidia-smi -l 1`

4. **Regular updates**
   - Update models: `ollama pull llava:13b-v1.6`
   - Update deps: `pip install -r requirements_enhanced.txt --upgrade`

---

## 📈 Comparison: Old vs Enhanced

### Commentary Quality Examples:

**Old Version (v1.0):**
- "Gameplay चल रहा है"
- "ठीक ठीक, देखते हैं"
- "अच्छा, समझ आ रहा है"

**Enhanced Version (v3.0):**
- "यो! लाल HP bar - danger zone में है!"
- "देखो screen पे 'Victory' लिखा - जीत गए! 🔥"
- "होली मोली! तीन enemies एक साथ eliminated!"

### Key Improvements:
✅ **Specificity**: Mentions exact details (colors, text, numbers)  
✅ **Context**: Understands scene type and energy level  
✅ **Variety**: Scene analysis prevents repetition  
✅ **Accuracy**: Better image processing = better understanding  
✅ **Natural**: Context-aware prompts = more human-like commentary  

---

## 🎓 Next Steps

### Immediate (Try Now):
1. Run enhanced commentator and compare to old version
2. Test different enhance modes
3. Try different games

### This Week:
1. Collect good commentary examples
2. Fine-tune interval for your games
3. Experiment with voices

### This Month:
1. Follow `MODEL_IMPROVEMENT_GUIDE.md`
2. Create custom Ollama Modelfile
3. Collect training data (500+ samples)

### Long-term:
1. Fine-tune LLaVA with LoRA
2. Train game-specific detector
3. Build custom vision-language model

---

## 📚 Related Files

- `advanced_image_processor.py` - Image processing module
- `MODEL_IMPROVEMENT_GUIDE.md` - Comprehensive training guide
- `gameplay_commentator_free.py` - Original free version
- `gameplay_commentator_enhanced.py` - This enhanced version

---

## 🎉 Enjoy!

You now have a **significantly improved** gameplay commentator with:
- 🧠 Better visual understanding
- 🎨 Advanced image preprocessing
- 📊 Scene awareness
- 💬 Context-aware commentary
- ⚡ Optimized performance

**Start playing and enjoy enhanced AI commentary!** 🎮🎙️

---

**Version**: 3.0 Enhanced  
**Status**: ✅ Production Ready  
**Updated**: December 2024
