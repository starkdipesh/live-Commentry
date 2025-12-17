# 🚀 Model Improvement & Training Guide

## 📋 Overview

This guide covers three improvement paths:
1. **Short-term**: Optimize existing LLaVA model performance (1-2 days)
2. **Medium-term**: Fine-tune LLaVA for gameplay (1-2 weeks)
3. **Long-term**: Train custom vision-language model (1-3 months)

---

## 🎯 PART 1: Optimize Existing LLaVA Model (Immediate)

### 1.1 Use Better LLaVA Variants

```bash
# Current: llava:latest (7B parameters)
ollama pull llava:latest

# Better options:

# Option 1: LLaVA 13B (Better understanding, needs 16GB RAM)
ollama pull llava:13b

# Option 2: LLaVA 34B (Best quality, needs 32GB RAM + GPU)
ollama pull llava:34b

# Option 3: LLaVA v1.6 (Latest, improved vision)
ollama pull llava:7b-v1.6
ollama pull llava:13b-v1.6
ollama pull llava:34b-v1.6
```

**Recommendation**: Start with `llava:13b-v1.6` for best balance.

---

### 1.2 Optimize Ollama Configuration

#### A. Model Parameters Tuning

```python
# In gameplay_commentator_free.py, update generate_commentary_ollama():

response = requests.post(
    f"{self.ollama_base_url}/api/generate",
    json={
        "model": self.model_name,
        "prompt": prompt,
        "images": [img_base64],
        "stream": False,
        "options": {
            # VISION-SPECIFIC OPTIMIZATIONS
            "temperature": 0.7,        # Lower for more focused analysis (was 0.9)
            "top_k": 40,              # More focused (was 50)
            "top_p": 0.9,             # Slightly lower (was 0.95)
            "repeat_penalty": 1.3,    # Prevent repetition
            "num_predict": 80,        # Allow longer, detailed responses
            
            # PERFORMANCE OPTIMIZATIONS
            "num_ctx": 4096,          # Larger context window for vision
            "num_gpu": 1,             # Use GPU if available
            "num_thread": 8,          # CPU threads for inference
            
            # QUALITY OPTIMIZATIONS
            "mirostat": 2,            # Better coherence
            "mirostat_tau": 5.0,      # Diversity control
            "mirostat_eta": 0.1,      # Learning rate
        }
    },
    timeout=30
)
```

---

### 1.3 Multi-Model Ensemble (Advanced)

Use multiple models and combine their outputs:

```python
class MultiModelCommentator:
    """Use multiple vision models for better accuracy"""
    
    def __init__(self):
        self.models = [
            "llava:13b-v1.6",     # Best for detailed analysis
            "llava:7b-v1.6",      # Fast, general understanding
            "bakllava:latest",    # Alternative LLaVA variant
        ]
    
    def generate_commentary_ensemble(self, screenshot):
        """Get commentary from multiple models and combine"""
        responses = []
        
        for model in self.models:
            try:
                response = self._query_model(model, screenshot)
                responses.append(response)
            except:
                continue
        
        # Combine responses (use voting or best response)
        return self._combine_responses(responses)
    
    def _combine_responses(self, responses):
        """Combine multiple model responses"""
        # Strategy 1: Use longest response
        # Strategy 2: Use response with most specific details
        # Strategy 3: Combine best parts of each
        
        # Simple implementation: use most detailed
        return max(responses, key=len)
```

---

## 🎯 PART 2: Fine-Tune LLaVA for Gameplay (Advanced)

### 2.1 Prepare Training Dataset

#### A. Collect Gameplay Images + Commentary Pairs

```python
# dataset_collector.py
"""
Collect training data for gameplay commentary fine-tuning
"""

import json
from pathlib import Path
from PIL import Image

class GameplayDatasetCollector:
    def __init__(self, output_dir="training_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.annotations = []
    
    def collect_sample(self, screenshot: Image.Image, 
                      commentary: str,
                      game_name: str,
                      scene_type: str):
        """
        Save a single training sample
        
        Args:
            screenshot: Game screenshot
            commentary: Good quality commentary for this screenshot
            game_name: Name of the game
            scene_type: 'action', 'menu', 'cutscene', etc.
        """
        sample_id = len(self.annotations)
        img_path = self.output_dir / f"sample_{sample_id:06d}.jpg"
        
        # Save image
        screenshot.save(img_path, quality=95)
        
        # Save annotation
        self.annotations.append({
            "image": str(img_path),
            "commentary": commentary,
            "game": game_name,
            "scene_type": scene_type,
        })
    
    def save_dataset(self):
        """Save all annotations to JSON"""
        with open(self.output_dir / "annotations.json", 'w') as f:
            json.dump(self.annotations, f, indent=2)
        
        print(f"✅ Saved {len(self.annotations)} samples to {self.output_dir}")

# Usage:
collector = GameplayDatasetCollector()

# Collect good examples manually or from existing commentary
collector.collect_sample(
    screenshot=Image.open("gameplay1.png"),
    commentary="यो! ये तो धांसू headshot था!",
    game_name="Valorant",
    scene_type="action"
)

collector.save_dataset()
```

**Goal**: Collect **500-1000 samples** minimum for decent fine-tuning.

---

#### B. Dataset Structure

```
training_data/
├── sample_000000.jpg  # Screenshot 1
├── sample_000001.jpg  # Screenshot 2
├── sample_000002.jpg  # Screenshot 3
├── ...
└── annotations.json   # Commentary for each screenshot
```

**annotations.json format:**
```json
[
  {
    "image": "sample_000000.jpg",
    "commentary": "अरे वाह! perfect timing पर shot मारा!",
    "game": "CS:GO",
    "scene_type": "action",
    "specific_elements": ["headshot", "enemy down", "kill feed"]
  },
  ...
]
```

---

### 2.2 Fine-Tuning Methods

#### Option 1: LoRA Fine-Tuning (Recommended)

**LoRA** (Low-Rank Adaptation) is efficient and requires less compute.

```bash
# Install fine-tuning tools
pip install transformers peft accelerate bitsandbytes datasets

# Use llama.cpp for LoRA training
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make

# Convert your dataset to training format
python convert_dataset.py --input training_data/ --output train.bin
```

**Fine-tuning script** (simplified):

```python
# finetune_llava.py
from transformers import LlavaForConditionalGeneration, AutoProcessor
from peft import get_peft_model, LoraConfig, TaskType
from datasets import load_dataset
import torch

# Load base model
model_name = "llava-hf/llava-1.5-7b-hf"
model = LlavaForConditionalGeneration.from_pretrained(model_name)
processor = AutoProcessor.from_pretrained(model_name)

# Configure LoRA
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=16,  # LoRA rank
    lora_alpha=32,
    lora_dropout=0.1,
    target_modules=["q_proj", "v_proj"]  # Which layers to fine-tune
)

# Apply LoRA
model = get_peft_model(model, lora_config)

# Load your dataset
dataset = load_dataset("json", data_files="training_data/annotations.json")

# Training loop
from transformers import Trainer, TrainingArguments

training_args = TrainingArguments(
    output_dir="./llava_gameplay_lora",
    num_train_epochs=3,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    logging_steps=10,
    save_steps=100,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
)

trainer.train()
trainer.save_model("./llava_gameplay_final")
```

**Time**: 2-3 days on GPU (NVIDIA RTX 3090 or better)  
**Cost**: $50-100 on cloud GPU (RunPod, Vast.ai)

---

#### Option 2: Use Ollama ModelFile (Simpler)

Create a custom model based on LLaVA with better prompts:

```bash
# Create Modelfile
cat > Modelfile << EOF
FROM llava:13b

# Custom system prompt for gameplay
SYSTEM """
You are an expert gameplay commentator specialized in:
- Identifying game UI elements (health bars, ammo, scores)
- Recognizing player actions (shooting, jumping, driving)
- Understanding game states (winning, losing, danger)
- Detecting game genres (FPS, RPG, Racing, etc.)

Analyze screenshots with EXTREME detail. Notice:
1. Colors and their meanings
2. Text and numbers on screen
3. Character positions and actions
4. Environmental context
5. Important UI indicators

Generate SHORT (1-2 sentences) Hindi commentary that is:
- Specific (mention exact details you see)
- Energetic and entertaining
- Uses gaming slang (धांसू, GG, pro, clutch)
"""

# Model parameters
PARAMETER temperature 0.7
PARAMETER top_k 40
PARAMETER top_p 0.9
PARAMETER num_ctx 4096
EOF

# Create custom model
ollama create gameplay-llava -f Modelfile
```

**Usage:**
```python
# Use your custom model
self.model_name = "gameplay-llava"
```

---

## 🎯 PART 3: Train Your Own Vision-Language Model (Expert)

### 3.1 Architecture Options

#### Option A: Train from Scratch (3-6 months)

**Not recommended** - requires massive compute (100K+ GPU hours)

#### Option B: Fine-tune Open-Source Models (Recommended)

Best base models:
1. **LLaVA** - Most accessible
2. **BLIP-2** - Good vision understanding
3. **InstructBLIP** - Instruction-following
4. **Qwen-VL** - Multilingual support (good for Hindi!)

---

### 3.2 Train Custom Vision-Language Model with Qwen-VL

**Qwen-VL** supports Hindi and is more customizable.

```bash
# Install Qwen-VL
git clone https://github.com/QwenLM/Qwen-VL.git
cd Qwen-VL
pip install -r requirements.txt

# Download base model
huggingface-cli download Qwen/Qwen-VL-Chat --local-dir ./Qwen-VL-Chat
```

**Fine-tuning script:**

```python
# train_qwen_gameplay.py
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load model
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen-VL-Chat",
    device_map="auto",
    trust_remote_code=True
)

tokenizer = AutoTokenizer.from_pretrained(
    "Qwen/Qwen-VL-Chat",
    trust_remote_code=True
)

# Prepare training data
train_data = [
    {
        "image": "gameplay1.jpg",
        "query": "Describe this gameplay moment in Hindi as a humorous commentator",
        "response": "यो! ये तो धांसू headshot था! Enemy का game over! 🔥"
    },
    # ... more samples
]

# Training configuration
from transformers import TrainingArguments, Trainer

training_args = TrainingArguments(
    output_dir="./qwen-gameplay",
    num_train_epochs=5,
    per_device_train_batch_size=1,
    learning_rate=1e-5,
    logging_steps=10,
    save_strategy="epoch",
)

# Train
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_data,
)

trainer.train()
```

**Hardware Requirements:**
- GPU: NVIDIA A100 (40GB+) or multiple RTX 4090s
- RAM: 64GB+
- Storage: 500GB+

**Cost**:
- Cloud GPU: $200-500 for full training
- Time: 1-2 weeks

---

### 3.3 Lightweight Alternative: TinyLLaVA

For limited hardware, use **TinyLLaVA** (smaller, faster):

```bash
# Install TinyLLaVA
git clone https://github.com/DLCV-Fall-2024/TinyLLaVA_Factory.git
cd TinyLLaVA_Factory

# Use TinyLLaVA-3.1B (much smaller)
python finetune.py \
    --model_name tinyllava-3.1b \
    --data_path ./training_data \
    --output_dir ./gameplay_tiny_llava
```

**Benefits:**
- Runs on consumer GPU (RTX 3060 12GB)
- Training time: 1-2 days
- Still good performance

---

## 🎯 PART 4: Improve Visual Processing Pipeline

### 4.1 Pre-Processing Techniques

#### A. Multi-Scale Analysis

```python
def multi_scale_inference(screenshot):
    """Analyze image at multiple scales for better detail detection"""
    scales = [1.0, 0.75, 0.5]
    results = []
    
    for scale in scales:
        # Resize
        w, h = screenshot.size
        scaled = screenshot.resize((int(w*scale), int(h*scale)))
        
        # Analyze
        result = analyze_with_model(scaled)
        results.append(result)
    
    # Combine insights from all scales
    return combine_multi_scale_results(results)
```

---

#### B. Object Detection Pre-Processing

Use **YOLOv8** to detect important game objects first:

```python
from ultralytics import YOLO

class GameObjectDetector:
    def __init__(self):
        self.yolo = YOLO('yolov8n.pt')  # Nano model (fast)
    
    def detect_important_objects(self, screenshot):
        """Detect people, vehicles, weapons, etc."""
        results = self.yolo(screenshot)
        
        # Extract detected objects
        detected = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                detected.append({
                    'class': r.names[int(box.cls)],
                    'confidence': float(box.conf),
                    'bbox': box.xyxy[0].tolist()
                })
        
        return detected
    
    def create_annotated_image(self, screenshot, detections):
        """Add bounding boxes to help vision model focus"""
        img = screenshot.copy()
        draw = ImageDraw.Draw(img)
        
        for det in detections:
            bbox = det['bbox']
            label = f"{det['class']} {det['confidence']:.2f}"
            draw.rectangle(bbox, outline='red', width=3)
            draw.text((bbox[0], bbox[1]-10), label, fill='red')
        
        return img
```

---

#### C. OCR for Text Recognition

Extract text from UI using **EasyOCR**:

```python
import easyocr

class GameUITextExtractor:
    def __init__(self):
        self.reader = easyocr.Reader(['en', 'hi'])  # English + Hindi
    
    def extract_ui_text(self, screenshot):
        """Extract all text from game UI"""
        results = self.reader.readtext(np.array(screenshot))
        
        extracted = []
        for (bbox, text, conf) in results:
            if conf > 0.5:  # Confidence threshold
                extracted.append({
                    'text': text,
                    'confidence': conf,
                    'position': bbox
                })
        
        return extracted
    
    def create_text_context(self, extracted_text):
        """Create context for vision model"""
        context = "Visible text on screen:\n"
        for item in extracted_text:
            context += f"- {item['text']}\n"
        return context
```

---

### 4.2 Context-Aware Processing

```python
class ContextAwareProcessor:
    """Add game context to improve model understanding"""
    
    def __init__(self):
        self.game_templates = {
            'fps': {
                'ui_elements': ['health bar', 'ammo count', 'minimap', 'kill feed'],
                'actions': ['shooting', 'reloading', 'taking damage', 'eliminating enemy'],
                'keywords': ['headshot', 'kill', 'death', 'revive']
            },
            'racing': {
                'ui_elements': ['speedometer', 'position', 'lap count', 'timer'],
                'actions': ['accelerating', 'drifting', 'overtaking', 'crashing'],
                'keywords': ['speed', 'lap', 'position', 'checkpoint']
            },
            # Add more game types
        }
    
    def detect_game_type(self, screenshot):
        """Auto-detect game genre from screenshot"""
        # Use simple heuristics or a classifier
        # Check for typical UI patterns
        
        # Simplified example
        text = self.extract_ui_text(screenshot)
        
        if any(word in text for word in ['HP', 'AMMO', 'HEALTH']):
            return 'fps'
        elif any(word in text for word in ['KM/H', 'MPH', 'LAP']):
            return 'racing'
        else:
            return 'unknown'
    
    def create_enhanced_prompt(self, screenshot, game_type):
        """Create game-specific prompt"""
        template = self.game_templates.get(game_type, {})
        
        prompt = f"""
        This is a {game_type} game screenshot.
        
        Look for these UI elements: {', '.join(template.get('ui_elements', []))}
        Possible actions: {', '.join(template.get('actions', []))}
        
        Analyze and create humorous commentary focusing on these specific elements.
        """
        
        return prompt
```

---

## 🎯 PART 5: Complete Enhanced System

### 5.1 Integrated Solution

```python
# enhanced_commentator.py
"""
Complete enhanced commentary system with advanced image processing
"""

from advanced_image_processor import AdvancedImageProcessor, GameplaySceneAnalyzer
import requests
from PIL import Image

class EnhancedGameplayCommentator:
    def __init__(self):
        # Image processor
        self.image_processor = AdvancedImageProcessor(
            target_size=1280,
            enhance_mode='quality'  # or 'balanced' or 'speed'
        )
        
        # Scene analyzer
        self.scene_analyzer = GameplaySceneAnalyzer()
        
        # Model configuration
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "llava:13b-v1.6"  # Upgraded model
    
    def generate_commentary(self, screenshot: Image.Image) -> str:
        """Generate commentary with enhanced processing"""
        
        # Step 1: Analyze scene
        scene_info = self.scene_analyzer.analyze_scene_type(screenshot)
        
        # Step 2: Process image with advanced pipeline
        processed_img = self.image_processor.preprocess_for_vision_model(
            screenshot,
            detect_motion=True
        )
        
        # Step 3: Get image statistics for context
        stats = self.image_processor.get_image_statistics(processed_img)
        
        # Step 4: Create enhanced prompt with context
        prompt = self._create_contextual_prompt(scene_info, stats)
        
        # Step 5: Send to model
        img_base64 = self.image_processor.to_base64(processed_img)
        
        response = requests.post(
            self.ollama_url,
            json={
                "model": self.model_name,
                "prompt": prompt,
                "images": [img_base64],
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_k": 40,
                    "top_p": 0.9,
                    "num_ctx": 4096,
                    "num_predict": 100,
                }
            },
            timeout=30
        )
        
        return response.json()['response']
    
    def _create_contextual_prompt(self, scene_info, stats):
        """Create prompt with scene and image context"""
        prompt = f"""
        Scene Analysis:
        - Type: {scene_info['scene_type']}
        - Motion Level: {scene_info['motion_level']:.2f}
        - Brightness: {'dark' if stats['is_dark_scene'] else 'bright' if stats['is_bright_scene'] else 'normal'}
        - Dominant Color: {stats['dominant_color']}
        
        Generate SHORT (1-2 sentences) Hindi gaming commentary that:
        1. Mentions SPECIFIC visual details you see
        2. Reflects the scene intensity
        3. Uses gaming slang appropriately
        4. Creates an engaging, clip-worthy moment
        
        Be natural and entertaining!
        """
        
        return prompt
```

---

## 🎯 PART 6: Performance Benchmarking

### 6.1 Create Benchmark Suite

```python
# benchmark.py
"""
Benchmark different configurations
"""

import time
from PIL import Image

def benchmark_configuration(config_name, processor, model, test_images):
    """Benchmark a specific configuration"""
    
    results = {
        'config': config_name,
        'total_time': 0,
        'avg_time_per_image': 0,
        'quality_scores': [],
    }
    
    start = time.time()
    
    for img in test_images:
        img_start = time.time()
        
        # Process and generate
        processed = processor.preprocess_for_vision_model(img)
        commentary = model.generate_commentary(processed)
        
        img_time = time.time() - img_start
        
        # Evaluate quality (manual or automated)
        quality = evaluate_commentary_quality(commentary, img)
        results['quality_scores'].append(quality)
    
    results['total_time'] = time.time() - start
    results['avg_time_per_image'] = results['total_time'] / len(test_images)
    results['avg_quality'] = sum(results['quality_scores']) / len(results['quality_scores'])
    
    return results

# Run benchmarks
configs = [
    {'mode': 'speed', 'model': 'llava:7b'},
    {'mode': 'balanced', 'model': 'llava:13b'},
    {'mode': 'quality', 'model': 'llava:13b-v1.6'},
]

for config in configs:
    results = benchmark_configuration(
        config['mode'],
        AdvancedImageProcessor(enhance_mode=config['mode']),
        config['model'],
        test_images
    )
    print(f"{config}: {results}")
```

---

## 🎯 PART 7: Deployment Strategy

### 7.1 Recommended Setup for Production

```python
# production_config.py
PRODUCTION_CONFIG = {
    'model': 'llava:13b-v1.6',  # Best balance
    'image_processing': 'balanced',  # Good quality, reasonable speed
    'enable_motion_detection': True,
    'enable_ui_enhancement': True,
    'screenshot_interval': 8,  # seconds
    'cache_responses': True,  # Cache similar scenes
}
```

---

## 📊 Summary & Recommendations

### Immediate Actions (This Week):
1. ✅ Integrate `advanced_image_processor.py` into `gameplay_commentator_free.py`
2. ✅ Upgrade to `llava:13b-v1.6` model
3. ✅ Implement adaptive preprocessing
4. ✅ Test with different game types

### Short-term (This Month):
1. 📝 Collect 100+ training samples (good commentary examples)
2. 🔧 Create custom Ollama Modelfile with gameplay-specific prompts
3. 📊 Benchmark different configurations
4. 🎯 Fine-tune for your most-played games

### Long-term (3-6 Months):
1. 🧠 Collect 1000+ training samples
2. 🚀 Fine-tune LLaVA with LoRA on your dataset
3. 🎮 Train game-specific detectors (health bars, UI elements)
4. 🌐 Consider Qwen-VL for multilingual support

---

## 🔗 Resources

**Tools & Frameworks:**
- LLaVA: https://github.com/haotian-liu/LLaVA
- Ollama: https://ollama.ai
- Qwen-VL: https://github.com/QwenLM/Qwen-VL
- PEFT (LoRA): https://github.com/huggingface/peft

**Cloud GPU Providers:**
- RunPod: https://runpod.io (Cheapest)
- Vast.ai: https://vast.ai (Flexible)
- Lambda Labs: https://lambdalabs.com

**Datasets:**
- Gameplay screenshots: Collect from your own games
- Gaming commentary: YouTube gaming channels (Fair Use for research)

---

**Next Steps**: Start with integrating advanced image processing, then move to fine-tuning! 🚀
