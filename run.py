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
    parser = argparse.ArgumentParser(description="Parthasarathi - World's Best All-Rounder Partner")
    parser.add_argument('mode', choices=['interactive', 'collect', 'train'], 
                        default='interactive', nargs='?',
                        help='Mode to run: interactive (Connect to Partner), collect (Build Dataset), train (Professor Mode)')
    
    args = parser.parse_args()
    
    print(f"🚀 Launching in {args.mode} mode...")
    
    try:
        if args.mode == 'interactive':
            from src.core.interactive_gaming_partner import InteractiveGamingPartner
            partner = InteractiveGamingPartner()
            asyncio.run(partner.run())
            
        elif args.mode == 'collect':
            from src.collectors.dataset_collector_simple import SimpleDatasetCollector
            collector = SimpleDatasetCollector(output_dir="training_data")
            collector.collect_session()

        elif args.mode == 'train':
            from src.learning.auto_trainer import AutoTrainer
            trainer = AutoTrainer()
            trainer.run_auto_training_loop()
            
    except KeyboardInterrupt:
        print("\n👋 Exiting...")
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")

if __name__ == "__main__":
    main()
