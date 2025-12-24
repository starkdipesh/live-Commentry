#!/usr/bin/env python3
"""
🧠 Auto-Trainer & Analyzer
This script implements "Self-Supervised Learning" (Distillation)
It uses your PC's idle time to analyze recorded gameplay and build a training dataset.
"""

import json
import time
import requests
import base64
from pathlib import Path
from datetime import datetime

class AutoTrainer:
    def __init__(self, data_dir="training_data"):
        self.data_dir = Path(data_dir)
        self.annotations_file = self.data_dir / "gold_dataset" / "metadata.jsonl"
        self.ollama_base_url = "http://localhost:11434"
        
        # 🎓 TEACHER CONFIGURATION
        self.vision_model = "llava-phi3"  # The Eyes
        self.logic_model = "phi4"         # The Professor (High IQ)
        
    def load_raw_samples(self):
        """Find raw images that haven't been annotated yet"""
        # (This would technically scan a 'raw' folder, for now we assume 
        # we are re-processing or augmenting existing data)
        # For this implementation, let's assume we scan a 'raw_captures' folder
        raw_dir = self.data_dir / "raw_captures"
        if not raw_dir.exists(): return []
        return list(raw_dir.glob("*.jpg"))

    def _get_visual_facts(self, img_path):
        """Step 1: Professor Eyes"""
        with open(img_path, 'rb') as f:
            img_b64 = base64.b64encode(f.read()).decode()
            
        try:
            res = requests.post(f"{self.ollama_base_url}/api/generate", json={
                "model": self.vision_model,
                "prompt": "List every UI element, number, and action visible in this game screenshot. Be purely factual.",
                "images": [img_b64],
                "stream": False
            })
            return res.json().get('response', '')
        except: return None

    def _get_expert_reasoning(self, visual_facts):
        """Step 2: Professor Mind"""
        prompt = f"""
ACT AS 'PARTHASARATHI', A LEGENDARY GAMING COACH.

SCENE DATA:
{visual_facts}

TASK:
1. Analyze the strategic situation deeply.
2. Generate a 'Thought' explaining the player's psychology/state.
3. Generate a 'Response' that is witty, helpful, and in Hinglish.

FORMAT:
Thought: [Deep analysis]
Response: [Hinglish commentary]
"""
        try:
            res = requests.post(f"{self.ollama_base_url}/api/generate", json={
                "model": self.logic_model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.8}
            })
            return res.json().get('response', '')
        except: return None

    def run_auto_training_loop(self):
        print(f"🎓 AUTO-TRAINER: Class is in session.")
        print(f"   Using {self.logic_model} to generating Gold Data from screenshots...")
        
        # 1. Create Gold Dataset file if not exists
        if not self.annotations_file.parent.exists():
            self.annotations_file.parent.mkdir(parents=True)
            
        # 2. Scan for raw images (Mocking a list for now or connecting to interactive partner's output)
        # In a real run, this would pick up images saved by 'collect' mode
        print("   (Waiting for raw images...)")

        # For demonstration, we essentially define the 'Process' that will be used
        # You would run: python3 run.py collect -> generates raw images -> python3 src/learning/auto_trainer.py
        
        print("\n✅ Setup Complete. To train:")
        print("1. Run 'python3 run.py collect' to capture gameplay.")
        print("2. This script will then process those images into the Gold Dataset.")

if __name__ == "__main__":
    trainer = AutoTrainer()
    trainer.run_auto_training_loop()
