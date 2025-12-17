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
        self.annotations_file = self.data_dir / "annotations.json"
        
        # We use a more "Analytical" prompt for training data generation
        # This acts as the "Teacher"
        self.teacher_model = "llava:latest" 
        
    def load_unlabeled_samples(self):
        """Find samples that don't have commentary yet"""
        if not self.annotations_file.exists():
            return []
            
        with open(self.annotations_file) as f:
            data = json.load(f)
            
        return [s for s in data.get('samples', []) if s['commentary'] == '[TO BE ADDED]']

    def analyze_and_annotate(self, sample):
        """
        The 'Teacher' analyzes the image deeply to generate perfect training data.
        This is slower than real-time but creates high-quality data.
        """
        img_path = self.data_dir / sample['image']
        if not img_path.exists():
            return None
            
        # heavy analysis prompt
        prompt = """
        ACT AS A PROFESSIONAL GAMING COACH.
        Analyze this gameplay screenshot in 3 steps:
        1. Identify the game state (Menu, Action, Stealth, Victory).
        2. Read any visible text/numbers (HP, Ammo, Objectives).
        3. Describe the key visual action.
        
        Based on this analysis, generate ONE energetic, short Hindi commentary line (10-15 words) that acts as the perfect reaction to this moment.
        
        OUTPUT FORMAT:
        Analysis: [Your analysis]
        Commentary: [The Hindi commentary]
        """
        
        with open(img_path, 'rb') as f:
            img_b64 = base64.b64encode(f.read()).decode()

        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.teacher_model,
                    "prompt": prompt,
                    "images": [img_b64],
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 200, # Allow length for analysis
                    }
                },
                timeout=60
            )
            
            result = response.json()['response']
            
            # Parse the Commentary part
            if "Commentary:" in result:
                final_comment = result.split("Commentary:")[1].strip()
            else:
                final_comment = result.strip()
                
            return final_comment, result # Return simple comment + full analysis
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return None, None

    def run_auto_training_loop(self):
        print(f"🧠 STARTING AUTO-TRAINER using {self.teacher_model}")
        print("   This converts your collected screenshots into a training dataset automatically.")
        
        samples = self.load_unlabeled_samples()
        print(f"   Found {len(samples)} samples to analyze.")
        
        if not samples:
            print("   ✅ No new samples to train on. Run './start.sh collect' first!")
            return

        with open(self.annotations_file) as f:
            full_data = json.load(f)

        count = 0
        for sample in full_data['samples']:
            if sample['commentary'] == '[TO BE ADDED]':
                print(f"\n⚡ Analyzing Sample {sample['id']}...")
                
                commentary, analysis = self.analyze_and_annotate(sample)
                
                if commentary:
                    print(f"   🔎 Analysis: {analysis[:50]}...")
                    print(f"   ✨ Generated: {commentary}")
                    
                    sample['commentary'] = commentary
                    sample['auto_generated'] = True
                    sample['teacher_analysis'] = analysis # Save the deep thought for future
                    count += 1
                    
                    # Save every step
                    with open(self.annotations_file, 'w', encoding='utf-8') as f:
                        json.dump(full_data, f, indent=2, ensure_ascii=False)
                
                time.sleep(1) # Cool down

        print(f"\n✅ Auto-Training Session Complete.")
        print(f"   Processed {count} samples.")
        print("   Your dataset is now ready for fine-tuning!")

if __name__ == "__main__":
    trainer = AutoTrainer()
    trainer.run_auto_training_loop()
