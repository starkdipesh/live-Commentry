#!/usr/bin/env python3
"""
🕉️ SAARTHIKA: THE STRATEGIC SHADOW
Usage: ./venv/bin/python3 main.py
"""

import os
import sys
import time
import asyncio
import signal
import platform
import logging

# Ensure src is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.interactive_gaming_partner import InteractiveGamingPartner

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

async def main_loop():
    clear_screen()
    print("\n" + "="*60)
    print(" 🕉️  SAARTHIKA: CONNECTED")
    print("    Vision | Voice | Strategy | RL Data")
    print("="*60 + "\n")

    # Initialize Partner
    try:
        partner = InteractiveGamingPartner()
        partner.start_listening()
        print("✅ Core Systems Initialized")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return

    # Check for Xorg/Wayland issue on Linux
    if platform.system() == "Linux":
        session = os.environ.get('XDG_SESSION_TYPE', 'unknown')
        if session == 'wayland':
            print("⚠️  WARNING: WAYLAND DETECTED")
            print("   - Mode: FALLBACK (gnome-screenshot)")
            print("   - Side Effect: Screen might flash/click on capture.")
            print("   - FIX: Switch to 'Ubuntu on Xorg' for SILENT & FAST capture.")
            time.sleep(2)
        else:
            print("✅ Xorg Detected: Silent High-Speed Capture Active.")

    print("\n🎧 Listening for your voice (Say something)...")
    print("📺 Watching your screen...")
    print("   (Press Ctrl+C to Stop)")

    # Main Interaction Loop
    last_proactive_time = time.time()
    PROACTIVE_INTERVAL = 20 # Seconds between proactive checks (Screenshots)
    proactive_interval = PROACTIVE_INTERVAL
    MIN_PROACTIVE_INTERVAL = 10
    MAX_PROACTIVE_INTERVAL = 90
    ENGAGEMENT_WINDOW = 25
    IGNORE_WINDOW = 60
    last_user_speech_time = time.time()
    last_proactive_spoken_time = None
    awaiting_engagement = False
    
    try:
        while True:
            # 1. Listen for user voice (Short timeout for responsiveness)
            user_speech = partner.listen_to_user(timeout=0.3)
            
            should_respond = False
            is_proactive = False
            
            # Logic A: User Spoke -> React Immediately
            if user_speech:
                print(f"\n👤 You said: {user_speech}")
                should_respond = True
                last_user_speech_time = time.time()

                if awaiting_engagement and last_proactive_spoken_time:
                    if (last_user_speech_time - last_proactive_spoken_time) <= ENGAGEMENT_WINDOW:
                        proactive_interval = max(MIN_PROACTIVE_INTERVAL, proactive_interval - 5)
                        print(f"📉 Engagement detected → proactive interval: {proactive_interval}s")
                    awaiting_engagement = False
            
            # Logic B: Silent -> Check periodically (Proactive)
            elif (time.time() - last_proactive_time) > proactive_interval:
                print("\n⏰ Proactive visual check...")
                should_respond = True # Or make this conditional on scene verification
                is_proactive = True
                last_proactive_time = time.time()

            if awaiting_engagement and last_proactive_spoken_time:
                if (time.time() - last_proactive_spoken_time) > IGNORE_WINDOW:
                    proactive_interval = min(MAX_PROACTIVE_INTERVAL, proactive_interval + 10)
                    print(f"📈 No engagement → proactive interval: {proactive_interval}s")
                    awaiting_engagement = False
            
            if should_respond:
                # 2. Capture & Think & Speak
                # Note: generate_response handles capture internally now
                print("🧠 Thinking...")
                reply = await partner.generate_response(
                    user_speech=user_speech, 
                    proactive=is_proactive
                )
                
                if reply:
                    print(f"🤖 Saarthika: {reply}")
                    asyncio.create_task(partner.speak(reply))

                    if is_proactive:
                        last_proactive_spoken_time = time.time()
                        awaiting_engagement = True
            
            # Small breather
            await asyncio.sleep(0.05)

    except KeyboardInterrupt:
        print("\n\n🛑 Saarthika Disconnected.")
        print("   RL Dataset saved in: training_data/gold_dataset/")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        pass
