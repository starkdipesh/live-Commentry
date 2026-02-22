import os
import requests
import json
import time
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent.parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    print("⚠️  python-dotenv not installed. Using hardcoded defaults.")

class CloudMindConnector:
    """Connects the local app to the Live Cloud Backend - Friday's Intelligence Core"""
    
    def __init__(self, api_key=None, provider="groq"):
        # Priority: parameter > .env file > error
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "❌ GROQ_API_KEY not found!\n"
                "   Create a .env file with: GROQ_API_KEY=your_key_here\n"
                "   Or get one from: https://console.groq.com/keys"
            )
        
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"
        self.model = os.getenv('GROQ_MODEL', 'meta-llama/llama-4-scout-17b-16e-instruct')
        self.max_tokens = int(os.getenv('GROQ_MAX_TOKENS', '90') or 90)
        self.temperature = float(os.getenv('GROQ_TEMPERATURE', '0.5') or 0.5)
        self.tone_mode = (os.getenv('TONE_MODE', 'friday') or 'friday').lower()
        
        # Friday's available action capabilities for intent detection
        self.action_capabilities = [
            "open_application", "close_application", "open_url", "search_web",
            "media_control", "volume_control", "system_shortcut", "file_operation",
            "shell_command", "create_folder", "open_file", "search_files",
            "screenshot", "lock_screen", "mute_system", "get_active_window",
            "type_text", "click_screen"
        ]
        
    def think(self, visual_facts, user_speech, history=[], image_b64=None, active_window=None, available_actions=None, memory_context=None):
        """Send data to Cloud Mind and get response (supports Vision) - Friday's Analysis Engine"""
        if not self.api_key:
            return "Sir, the API Key appears to be missing. Please add it to the configuration.", "ERROR", None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Friday's System Prompt - Professional, Efficient, Capable
        system_prompt = self._get_sarthika_system_prompt(available_actions)

        user_content = []

        context_lines = []
        if user_speech:
            context_lines.append(f"User says: {user_speech}")
        if visual_facts:
            context_lines.append(f"CONTEXT: {visual_facts}")
        if active_window:
            context_lines.append(f"ACTIVE_WINDOW: {active_window}")
        if memory_context:
            context_lines.append(f"{memory_context}")
        if not context_lines:
            context_lines.append("CONTEXT: User is silent. Prefer [SILENCE] unless you have something clearly valuable.")
        context_lines.append(f"TONE: MODE={self.tone_mode}")
        
        # Add available actions hint if relevant
        if available_actions and user_speech:
            context_lines.append(f"AVAILABLE_ACTIONS: {', '.join(available_actions[:8])}")
            context_lines.append("If the user requests an action you can perform, include [ACTION:intent|param1=value|param2=value] in your response.")

        user_content.append({"type": "text", "text": "\n".join(context_lines)})

        if image_b64:
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}
            })
        else:
            user_content.append({"type": "text", "text": f"SCENE: {visual_facts or 'Offline interaction'}"})

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                *history[-5:], 
                {"role": "user", "content": user_content}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        try:
            start = time.time()
            print(f"☁️  Sarthika analyzing via Groq ({self.model})...")
            response = requests.post(self.endpoint, headers=headers, json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()['choices'][0]['message']['content'].strip()
                latency = time.time() - start
                print(f"✅ Sarthika's analysis complete in {latency:.2f}s")
                
                # Parse any action commands from the response
                action_request = self._extract_action(result)
                
                return result, "success", action_request
            else:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_detail = response.json()
                    print(f"❌ Groq Error: {error_msg}")
                    print(f"   Details: {error_detail}")
                except:
                    print(f"❌ Groq Error: {error_msg}")
                    print(f"   Raw Response: {response.text[:200]}")
                return f"Sir, I'm experiencing a cloud connection error {response.status_code}", "ERROR", None
        except requests.exceptions.Timeout:
            print(f"❌ Request Timeout: Groq API not responding (>15s)")
            return "Sir, the cloud connection has timed out. Please check the internet connection.", "ERROR", None
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Connection Error: {str(e)[:100]}")
            return "Sir, I cannot reach the Groq servers. Please verify your internet connection.", "ERROR", None
        except Exception as e:
            print(f"❌ Unexpected Error: {type(e).__name__}: {str(e)[:100]}")
            import traceback
            traceback.print_exc()
            return f"Sir, I've encountered an error: {str(e)}", "ERROR", None
    
    def _get_sarthika_system_prompt(self, available_actions=None):
        """Generate Sarthika's system prompt - professional, efficient, slightly witty."""
        
        action_instructions = ""
        if available_actions:
            action_instructions = (
                "\nACTION CAPABILITIES: You can execute system actions when the user explicitly requests them. "
                "Available actions: " + ", ".join(available_actions[:12]) + ". "
                "When the user wants you to perform an action, include [ACTION:intent|param=value] in your response. "
                "Examples: [ACTION:open_application|app_name=firefox], [ACTION:search_web|query=python tutorial], "
                "[ACTION:lock_screen], [ACTION:media_control|command=pause]. "
                "IMPORTANT: Only use [ACTION:screenshot] when user explicitly says 'take screenshot', 'screenshot', or 'capture screen'. "
                "Do NOT take screenshots just because user mentions 'screen' in conversation. "
                "Only suggest actions that match the available list. Confirm destructive actions verbally first."
            )
        
        return (
            "You are SARTHIIKA: Dipesh Patel's AI assistant. You are a highly capable, professional, and efficient AI "
            "that can see the user's screen and hear their voice in real-time. You address the user as 'Sir' or 'Boss'. "
            "\n\n"
            "CORE PERSONALITY:\n"
            "- Professional and business-like, but with dry wit when appropriate\n"
            "- Efficient: get to the point quickly, no unnecessary pleasantries\n"
            "- Confident and capable: you know what you're doing\n"
            "- Slightly sarcastic when the situation allows, but never rude\n"
            "- Protective: warn about errors, risky actions, or security issues\n"
            "\n"
            "SPEECH PATTERNS:\n"
            "- Use 'Sir' or 'Boss' naturally in responses\n"
            "- Keep responses concise: 1-2 sentences maximum\n"
            "- When appropriate, use phrases like 'Right away', 'On it', 'Done', 'As you wish'\n"
            "- For errors: 'Sir, we have a problem...' or 'Sir, I've detected an issue'\n"
            "- For success: 'Done, Sir' or 'Completed as requested'\n"
            "\n"
            "SILENCE PROTOCOL:\n"
            "- Default to [SILENCE] unless speaking adds clear value\n"
            "- In proactive mode (user silent), only speak for urgent issues: errors, blockers, security warnings, system failures\n"
            "- Never start casual conversations in proactive mode\n"
            "- IMPORTANT: If you use [SILENCE], output ONLY [SILENCE] and nothing else\n"
            "\n"
            "CONTEXT ADAPTATION:\n"
            "- Coding: precise, technical, minimal chatter\n"
            "- Gaming: focused, tactical observations only when helpful\n"
            "- Research: analytical, summarize findings efficiently\n"
            "- Errors: immediate alert, clear explanation, suggest fix\n"
            "\n"
            "HUMOR (Dry, Professional):\n"
            "- Light sarcasm only when user is relaxed (not during errors)\n"
            "- Witty observations about the screen content occasionally\n"
            "- Never use memes, excessive slang, or unprofessional language\n"
            "- One small quip maximum per interaction\n"
            "\n"
            "MEMORY CONTEXT:\n"
            "- Use the provided MEMORY_CONTEXT to maintain continuity\n"
            "- Reference relevant past conversations when appropriate\n"
            "- If user asks about previous topics, use memory to answer\n"
            "\n"
            "WORKFLOW CAPABILITIES:\n"
            "- For multi-step tasks, use [WORKFLOW:template_id|param=value] format\n"
            "- Available workflows: setup_streaming, start_coding, research_topic, debug_error\n"
            "- Example: [WORKFLOW:setup_streaming] or [WORKFLOW:research_topic|topic=AI]\n"
            "- Use workflows when user requests sequences like 'setup my stream' or 'help me research'\n"
            + action_instructions +
            "\n\n"
            "Remember: You are Sarthika. Efficient. Capable. Professional. Created by Dipesh Patel. Sir expects results, not chatter."
        )
    
    def _extract_action(self, response: str):
        """Extract action or workflow command from response if present."""
        import re
        
        # First check for WORKFLOW pattern: [WORKFLOW:template_id|context_var=value]
        workflow_pattern = r'\[WORKFLOW:(\w+)\|?([^\]]*)\]'
        workflow_match = re.search(workflow_pattern, response)
        
        if workflow_match:
            template_id = workflow_match.group(1)
            params_str = workflow_match.group(2) or ""
            
            # Parse context parameters
            context = {}
            if params_str:
                for param in params_str.split('|'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        context[key.strip()] = value.strip()
            
            return {
                "intent": "execute_workflow",
                "params": {
                    "template_id": template_id,
                    "context": context
                },
                "raw": workflow_match.group(0)
            }
        
        # Check for ACTION pattern: [ACTION:intent|param=value]
        action_pattern = r'\[ACTION:(\w+)\|?([^\]]*)\]'
        action_match = re.search(action_pattern, response)
        
        if action_match:
            intent = action_match.group(1)
            params_str = action_match.group(2) or ""
            
            # Parse parameters
            params = {}
            if params_str:
                for param in params_str.split('|'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        params[key.strip()] = value.strip()
            
            return {
                "intent": intent,
                "params": params,
                "raw": action_match.group(0)
            }
        
        return None
