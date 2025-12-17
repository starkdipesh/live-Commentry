#!/usr/bin/env python3
"""
🎮 AI Gameplay Commentary System - Main Launcher
"""

import sys
import os
import argparse
import asyncio

# Ensure src is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    parser = argparse.ArgumentParser(description="AI Gameplay Commentary System")
    parser.add_argument('mode', choices=['enhanced', 'lightweight', 'free', 'collect', 'train'], 
                        default='lightweight', nargs='?',
                        help='Mode to run: enhanced (GPU), lightweight (CPU), free (Legacy), collect (Dataset)')
    
    args = parser.parse_args()
    
    print(f"🚀 Launching in {args.mode} mode...")
    
    try:
        if args.mode == 'enhanced':
            from src.core.gameplay_commentator_enhanced import main as run_enhanced
            asyncio.run(run_enhanced())
            
        elif args.mode == 'lightweight':
            from src.core.gameplay_commentator_lightweight import main as run_lightweight
            asyncio.run(run_lightweight())
            
        elif args.mode == 'free':
            from src.core.gameplay_commentator_free import GameplayCommentatorFree
            commentator = GameplayCommentatorFree()
            asyncio.run(commentator.run())
            
        elif args.mode == 'collect':
            from src.collectors.dataset_collector_simple import SimpleDatasetCollector
            # Simple interactive launcher for collector
            collector = SimpleDatasetCollector(output_dir="training_data")
            collector.collect_session()

        elif args.mode == 'train':
            from src.learning.auto_trainer import AutoTrainer
            trainer = AutoTrainer()
            trainer.run_auto_training_loop()
            
    except KeyboardInterrupt:
        print("\n👋 Exiting...")
    except ImportError as e:
        print(f"\n❌ Error: {e}")
        print("Please check if all dependencies are installed:")
        print("pip install -r requirements/requirements_lightweight.txt")
        print("Or for enhanced:")
        print("pip install -r requirements/requirements_enhanced.txt")
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")

if __name__ == "__main__":
    main()
