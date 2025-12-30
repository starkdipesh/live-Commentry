#!/usr/bin/env python3
"""
📸 Simple Dataset Collector for Low-Spec PC
Collects screenshots while you play - add commentary later
100% FREE, runs on any PC
"""

import json
import time
from pathlib import Path
from PIL import Image
import mss
from datetime import datetime


class SimpleDatasetCollector:
    """Lightweight dataset collector for training data"""
    
    def __init__(self, output_dir="training_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.samples = []
        self.sample_count = 0
        
        # Load existing annotations if any
        self.annotations_file = self.output_dir / "annotations.json"
        if self.annotations_file.exists():
            with open(self.annotations_file) as f:
                existing = json.load(f)
                self.samples = existing.get('samples', [])
                self.sample_count = len(self.samples)
        
        print(f"""
╔════════════════════════════════════════════════════════════╗
║  📸 Simple Dataset Collector                                ║
╚════════════════════════════════════════════════════════════╝

Output directory: {self.output_dir}
Existing samples: {self.sample_count}
        """)
    
    def collect_session(self, duration_minutes=10, interval_seconds=8):
        """
        Collect screenshots while you play
        
        Args:
            duration_minutes: How long to collect (default 10 minutes)
            interval_seconds: Interval between screenshots (default 8 seconds)
        """
        total_screenshots = int((duration_minutes * 60) / interval_seconds)
        
        print(f"""
🎮 AUTO-COLLECTION MODE

Duration: {duration_minutes} minutes
Interval: {interval_seconds} seconds
Expected screenshots: {total_screenshots}

Starting in 5 seconds... Get ready to play!
        """)
        
        time.sleep(5)
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        with mss.mss() as sct:
            while time.time() < end_time:
                try:
                    # Capture screenshot
                    monitor = sct.monitors[1]
                    screenshot = sct.grab(monitor)
                    img = Image.frombytes('RGB', screenshot.size, 
                                         screenshot.bgra, 'raw', 'BGRX')
                    
                    # Resize to save disk space (512px is enough for training)
                    if img.width > 512:
                        ratio = 512 / img.width
                        new_size = (512, int(img.height * ratio))
                        img = img.resize(new_size, Image.Resampling.BILINEAR)
                    
                    # Save screenshot
                    img_filename = f"sample_{self.sample_count:05d}.jpg"
                    img_path = self.output_dir / img_filename
                    img.save(img_path, quality=85)
                    
                    # Add to samples
                    sample = {
                        'id': self.sample_count,
                        'image': img_filename,
                        'commentary': '[TO BE ADDED]',
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'size': f"{img.width}x{img.height}"
                    }
                    
                    self.samples.append(sample)
                    self.sample_count += 1
                    
                    elapsed = int(time.time() - start_time)
                    remaining = int(end_time - time.time())
                    
                    print(f"📸 Sample {self.sample_count} saved | "
                          f"Elapsed: {elapsed}s | Remaining: {remaining}s")
                    
                    # Wait for next capture
                    time.sleep(interval_seconds)
                    
                except KeyboardInterrupt:
                    print("\n⚠️  Collection interrupted by user")
                    break
                except Exception as e:
                    print(f"⚠️  Error: {e}")
                    time.sleep(1)
        
        # Save annotations
        self.save_annotations()
        
        print(f"""
\n✅ Collection Complete!

Total samples collected: {len(self.samples)}
Saved to: {self.output_dir}

📝 Next steps:
1. Review screenshots in {self.output_dir}/
2. Add commentary using: python3 dataset_collector_simple.py --annotate
3. Once you have 200+ samples, train using Google Colab (FREE)
        """)
    
    async def auto_annotate_with_professor(self, batch_size=50):
        """Use local AI to automatically generate Gold Data"""
        from src.learning.auto_trainer import AutoTrainer
        trainer = AutoTrainer(data_dir=self.output_dir.parent)
        
        unannotated = [s for s in self.samples if s['commentary'] == '[TO BE ADDED]']
        if not unannotated:
            print("✅ All samples already have commentary.")
            return

        print(f"🎓 Professor Parthasarathi is reviewing {len(unannotated[:batch_size])} samples...")
        
        for sample in unannotated[:batch_size]:
            img_path = self.output_dir / sample['image']
            visual_facts = trainer._get_visual_facts(img_path)
            if visual_facts:
                expert_data = trainer._get_expert_reasoning(visual_facts)
                if expert_data:
                    # Extract Response from "Thought: ... Response: ..."
                    if "Response:" in expert_data:
                        commentary = expert_data.split("Response:")[1].strip()
                    else:
                        commentary = expert_data.strip()
                    
                    sample['commentary'] = commentary
                    print(f"✅ AI Annotated: {commentary[:50]}...")
            
            # Small cooldown for CPU thermal safety
            time.sleep(0.5)

        self.save_annotations()

    def save_annotations(self):
        """Save all annotations to JSON"""
        data = {
            'version': '1.0',
            'total_samples': len(self.samples),
            'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'samples': self.samples
        }
        
        with open(self.annotations_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Annotations saved to: {self.annotations_file}")
    
    def annotate_samples(self, batch_size=10):
        """
        Add commentary to collected samples interactively
        """
        # Filter samples that need annotation
        unannotated = [s for s in self.samples if s['commentary'] == '[TO BE ADDED]']
        
        if not unannotated:
            print("✅ All samples already annotated!")
            return
        
        print(f"""
╔════════════════════════════════════════════════════════════╗
║  📝 Add Commentary to Samples                               ║
╚════════════════════════════════════════════════════════════╝

Unannotated samples: {len(unannotated)}
Processing in batches of {batch_size}

Tips for good commentary:
- Keep it SHORT (10-15 words)
- Mention SPECIFIC details (colors, numbers, actions)
- Use gaming slang naturally
- Be energetic and entertaining!

Examples:
✅ "यो! HP लाल - केवल 15% बचा! खतरा!"
✅ "देखो 3 enemies - triple threat! Fight time!"
✅ "Perfect headshot! Enemy eliminated! धांसू!"

Press Ctrl+C to save and exit anytime
        """)
        
        annotated_count = 0
        
        for i, sample in enumerate(unannotated[:batch_size]):
            print(f"\n{'='*60}")
            print(f"Sample {i+1}/{min(batch_size, len(unannotated))}")
            print(f"Image: {sample['image']}")
            print(f"Timestamp: {sample['timestamp']}")
            
            # Try to show image
            try:
                img_path = self.output_dir / sample['image']
                img = Image.open(img_path)
                img.show()  # Opens in default image viewer
                print("🖼️  Image opened in viewer")
            except Exception as e:
                print(f"⚠️  Could not display image: {e}")
            
            # Get commentary
            print("\nEnter commentary (or 'skip' to skip this image):")
            commentary = input("➤ ").strip()
            
            if commentary.lower() == 'skip':
                print("⏭️  Skipped")
                continue
            
            if not commentary:
                print("⚠️  Empty commentary, skipping")
                continue
            
            # Update sample
            sample['commentary'] = commentary
            annotated_count += 1
            
            print(f"✅ Saved: {commentary}")
        
        # Save progress
        self.save_annotations()
        
        remaining = len([s for s in self.samples if s['commentary'] == '[TO BE ADDED]'])
        
        print(f"""
\n✅ Batch Complete!

Annotated this session: {annotated_count}
Total annotated: {len(self.samples) - remaining}/{len(self.samples)}
Remaining: {remaining}

Run again to annotate more samples!
        """)
    
    def show_stats(self):
        """Show dataset statistics"""
        annotated = len([s for s in self.samples if s['commentary'] != '[TO BE ADDED]'])
        unannotated = len(self.samples) - annotated
        
        print(f"""
╔════════════════════════════════════════════════════════════╗
║  📊 Dataset Statistics                                      ║
╚════════════════════════════════════════════════════════════╝

Total samples: {len(self.samples)}
Annotated: {annotated} ({annotated/max(1,len(self.samples))*100:.1f}%)
Unannotated: {unannotated}

Ready for training: {'✅ YES (200+ samples)' if annotated >= 200 else f'❌ NO (need {200-annotated} more)'}

Output directory: {self.output_dir}
Annotations file: {self.annotations_file}
        """)


if __name__ == "__main__":
    import sys
    
    collector = SimpleDatasetCollector()
    
    if '--stats' in sys.argv:
        collector.show_stats()
    
    elif '--auto-annotate' in sys.argv:
        import asyncio
        batch_size = 50
        if '--batch' in sys.argv:
            idx = sys.argv.index('--batch')
            batch_size = int(sys.argv[idx + 1])
        
        asyncio.run(collector.auto_annotate_with_professor(batch_size=batch_size))
    
    else:
        # Collection mode (default)
        duration = 10  # minutes
        interval = 5   # seconds (faster for better data)
        
        if '--duration' in sys.argv:
            idx = sys.argv.index('--duration')
            duration = int(sys.argv[idx+1])
        
        if '--interval' in sys.argv:
            idx = sys.argv.index('--interval')
            interval = int(sys.argv[idx+1])
        
        collector.collect_session(
            duration_minutes=duration,
            interval_seconds=interval
        )
