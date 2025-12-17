#!/usr/bin/env python3
"""
🎮 Demo Mode - AI Commentary Without Screen Capture
Shows how the AI generates humorous commentary using sample scenarios
"""

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv()

class CommentaryDemo:
    """Demonstrate AI commentary generation without screen capture"""
    
    def __init__(self):
        self.api_key = os.getenv("EMERGENT_LLM_KEY", "sk-emergent-35fA75602D104F9F64")
        
        self.chat = LlmChat(
            api_key=self.api_key,
            session_id=f"demo-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            system_message=self._get_system_prompt()
        ).with_model("openai", "gpt-4o")
        
        print("🎮 AI Commentary Demo Initialized!")
    
    def _get_system_prompt(self) -> str:
        """System prompt for humorous commentary"""
        return """You are an AI-powered gameplay commentator creating LIVE COMMENTARY for YouTube streams.

🎯 YOUR MISSION:
Generate SHORT, PUNCHY, HILARIOUS commentary (1-2 sentences max) that:
- HOOKS viewers instantly with humor
- Uses YouTube algorithm-friendly techniques (excitement, variety, engagement)
- Mixes humor styles: sarcastic, encouraging, roasting, unexpected twists
- Keeps viewers watching with unpredictable energy

🎨 HUMOR STYLE MIX (rotate naturally):
1. Sarcastic: "Oh wow, walking simulator 2025, riveting content"
2. Encouraging: "OKAY OKAY, I see you! That's actually pretty clean!"
3. Roasting: "My grandma plays faster and she uses a trackpad"
4. Unexpected: "This gameplay is smoother than a buttered slip n slide"

RESPOND WITH ONLY THE COMMENTARY - no explanations!"""
    
    async def generate_commentary(self, scenario: str) -> str:
        """Generate commentary for a given scenario"""
        try:
            prompt = f"""Generate ONE SHORT, HILARIOUS commentary line (1-2 sentences max) for this gameplay scenario:

🎮 SCENARIO: {scenario}

What's your commentary?"""
            
            user_message = UserMessage(text=prompt)
            commentary = await self.chat.send_message(user_message)
            
            return commentary.strip().strip('"').strip("'")
            
        except Exception as e:
            return f"Error: {e}"
    
    async def run_demo(self):
        """Run demo with sample scenarios"""
        print("\n" + "="*70)
        print("🎬 AI COMMENTARY DEMO - Sample Scenarios")
        print("="*70)
        print("Watch how the AI generates unique, hilarious commentary!\n")
        
        scenarios = [
            {
                "game": "First-Person Shooter",
                "scene": "Player misses 10 shots in a row, then gets one-shot by enemy"
            },
            {
                "game": "Racing Game",
                "scene": "Player crashes into a wall at 200mph on the first turn"
            },
            {
                "game": "RPG",
                "scene": "Player stuck in menu screen for 3 minutes deciding on character outfit"
            },
            {
                "game": "Battle Royale",
                "scene": "Player lands, finds no weapons, gets eliminated immediately"
            },
            {
                "game": "Platform Game",
                "scene": "Player fails the same jump 8 times in a row"
            },
            {
                "game": "Sports Game",
                "scene": "Player scores an incredible goal with perfect technique"
            }
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n{'─'*70}")
            print(f"🎮 Scenario #{i}: {scenario['game']}")
            print(f"📝 Scene: {scenario['scene']}")
            print("─"*70)
            print("🤖 Generating AI commentary...")
            
            commentary = await self.generate_commentary(scenario['scene'])
            
            print(f"\n💬 COMMENTARY:")
            print(f'   "{commentary}"\n')
            
            await asyncio.sleep(1)  # Brief pause between scenarios
        
        print("\n" + "="*70)
        print("✅ DEMO COMPLETE!")
        print("="*70)
        print("\n💡 This demonstrates the AI's ability to:")
        print("   • Generate unique commentary for different situations")
        print("   • Mix humor styles (sarcastic, encouraging, roasting)")
        print("   • Create YouTube-worthy, shareable content")
        print("   • Adapt to any game or scenario")
        print("\n📌 The full script (gameplay_commentator.py) adds:")
        print("   • Real-time screen capture of YOUR gameplay")
        print("   • Visual analysis with GPT-4 Vision")
        print("   • Text-to-speech voice output")
        print("   • Continuous commentary loop")

async def main():
    """Entry point"""
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║         🎮 AI COMMENTARY DEMO MODE 🎙️                        ║
    ║                                                               ║
    ║         See the AI generate hilarious commentary!             ║
    ║         (No screen capture needed for demo)                   ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    demo = CommentaryDemo()
    await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main())
