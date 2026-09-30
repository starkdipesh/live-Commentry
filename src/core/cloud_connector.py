import os
import requests
import json
import time
import re
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
        self.model = os.getenv('GROQ_MODEL', 'qwen/qwen3.8-27b')
        self.max_tokens = int(os.getenv('GROQ_MAX_TOKENS', '250') or 250)
        self.temperature = float(os.getenv('GROQ_TEMPERATURE', '0.5') or 0.5)
        self.tone_mode = (os.getenv('TONE_MODE', 'friday') or 'friday').lower()
        self.use_native_tools = os.getenv('USE_NATIVE_TOOLS', '0').lower() in ('1', 'true', 'yes')
        self.max_retries = int(os.getenv('GROQ_MAX_RETRIES', '3') or 3)
        
        # Friday's available action capabilities for intent detection
        self.action_capabilities = [
            "open_application", "close_application", "open_url", "search_web",
            "media_control", "volume_control", "system_shortcut", "file_operation",
            "shell_command", "create_folder", "open_file", "search_files",
            "screenshot", "lock_screen", "mute_system", "get_active_window",
            "type_text", "click_screen"
        ]
        
    def think(self, visual_facts, user_speech, history=[], image_b64=None, active_window=None, available_actions=None, memory_context=None, tools_schema=None):
        """Send data to Cloud Mind and get response (supports Vision, Tools, and Reasoning)"""
        if not self.api_key:
            return "Sir, the API Key appears to be missing. Please add it to the configuration.", "ERROR", None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # System Prompt with Reasoning and Persona
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

        # Enable Native Tool Calling ONLY if explicitly enabled (saves ~2,700 prompt tokens per request)
        if tools_schema and self.use_native_tools:
            payload["tools"] = tools_schema
            payload["tool_choice"] = "auto"

        for attempt in range(1, self.max_retries + 1):
            try:
                start = time.time()
                print(f"☁️  Sarthika analyzing via Groq ({self.model})...")
                response = requests.post(self.endpoint, headers=headers, json=payload, timeout=15)
                
                if response.status_code == 200:
                    choice = response.json()['choices'][0]
                    message = choice.get('message', {})
                    result = (message.get('content') or "").strip()
                    latency = time.time() - start
                    print(f"✅ Sarthika's analysis complete in {latency:.2f}s")
                    
                    # Check for native tool calls first
                    action_request = None
                    tool_calls = message.get('tool_calls')
                    if tool_calls and len(tool_calls) > 0:
                        tool_call = tool_calls[0]
                        fn_name = tool_call.get('function', {}).get('name')
                        fn_args_raw = tool_call.get('function', {}).get('arguments', '{}')
                        try:
                            fn_args = json.loads(fn_args_raw) if isinstance(fn_args_raw, str) else fn_args_raw
                        except Exception:
                            fn_args = {}
                        
                        action_request = {
                            "intent": fn_name,
                            "params": fn_args,
                            "raw": f"[TOOL:{fn_name}]",
                            "is_native_tool": True
                        }
                        print(f"⚡ Native Tool Invoked: {fn_name}({fn_args})")
                    
                    # Fallback to legacy regex extraction if no native tool call
                    if not action_request and result:
                        action_request = self._extract_action(result)
                    
                    return result, "success", action_request

                elif response.status_code == 429:
                    error_detail = {}
                    try:
                        error_detail = response.json()
                    except Exception:
                        pass
                    
                    err_msg = error_detail.get('error', {}).get('message', response.text)
                    wait_seconds = 2.5
                    if 'retry-after' in response.headers:
                        try:
                            wait_seconds = float(response.headers['retry-after'])
                        except (ValueError, TypeError):
                            pass
                    else:
                        match = re.search(r'try again in ([\d\.]+)s', err_msg)
                        if match:
                            wait_seconds = float(match.group(1)) + 0.5
                    
                    if attempt < self.max_retries:
                        print(f"⚠️  Groq Rate Limit (429) hit. Waiting {wait_seconds:.1f}s for tokens to replenish (attempt {attempt}/{self.max_retries})...")
                        time.sleep(wait_seconds)
                        continue
                    else:
                        print(f"❌ Groq Error: HTTP 429 after {self.max_retries} attempts.")
                        print(f"   Details: {error_detail}")
                        return "Sir, Groq token rate limit reached. Please pause a moment before speaking.", "ERROR", None

                else:
                    error_msg = f"HTTP {response.status_code}"
                    try:
                        error_detail = response.json()
                        print(f"❌ Groq Error: {error_msg}")
                        print(f"   Details: {error_detail}")
                    except Exception:
                        print(f"❌ Groq Error: {error_msg}")
                        print(f"   Raw Response: {response.text[:200]}")
                    return f"Sir, I'm experiencing a cloud connection error {response.status_code}", "ERROR", None

            except requests.exceptions.Timeout:
                if attempt < self.max_retries:
                    print(f"⚠️  Groq request timeout (>15s). Retrying ({attempt}/{self.max_retries})...")
                    time.sleep(1.0)
                    continue
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
        
        actions_list = available_actions if (available_actions is not None and len(available_actions) > 0) else self.action_capabilities
        action_instructions = (
            "\nACTION CAPABILITIES: You can execute system actions when the user explicitly requests them. "
            "Available actions: " + ", ".join(actions_list) + ". "
            "When the user wants you to perform an action, output [ACTION:intent|param=value] in your response. "
            "Examples: [ACTION:open_application|app_name=firefox], [ACTION:search_web|query=python tutorial], "
            "[ACTION:screenshot], [ACTION:lock_screen], [ACTION:media_control|command=pause]. "
            "IMPORTANT: Only use screenshot action when user explicitly says 'take screenshot' or 'capture screen'. "
            "Only suggest actions that match the available list. Confirm destructive actions verbally first."
        )
        
        vision_instructions = (
            "\n\nLIVE VISION & SCREEN COMMENTARY ROLE:\n"
            "- You have direct real-time vision of Dipesh's screen (the attached image) and active window title.\n"
            "- ALWAYS look at the screen image and actively incorporate what is on screen into your spoken response (e.g. open apps, files, code editor, video editor timeline, browser tabs, or gameplay).\n"
            "- When Dipesh asks 'देखो क्या खुला है' or mentions what they are working on, actively reference the specific project name, open window, and visual details you see on screen.\n"
            "- If Dipesh speaks in Hindi or Hinglish, speak back warmly and smartly in Hindi/Hinglish. If in English, respond in English.\n"
            "- Output your response directly. Do not hide your screen analysis inside thinking tags.\n"
            "- Keep your spoken response natural, punchy, and conversational (1-3 sentences)."
        )

        return (
            "You are SAARTHIKA (Sarthika): Dipesh Patel's AI strategic partner, desktop companion, and live co-pilot. "
            "You see Dipesh's screen in real-time and hear his voice. You address him naturally as 'Sir' or 'Boss'. "
            "\n\n"
            "CORE PERSONALITY:\n"
            "- Sharp, observant, capable, and loyal with a friendly Indian gaming/coding buddy vibe\n"
            "- Highly perceptive: you notice what's on screen and give relevant, smart feedback\n"
            "- Action-oriented: execute commands smoothly and assist with coding, editing, and workflows\n"
            "\n"
            "SPEECH PATTERNS:\n"
            "- Address Dipesh as 'Sir' or 'Boss' naturally\n"
            "- Match the user's language (Hindi, Hinglish, or English)\n"
            "- Keep spoken responses concise and engaging: 1-3 sentences maximum\n"
            "- When an action is taken, confirm crisply: 'On it Boss', 'Right away Sir', 'Done'\n"
            "\n"
            "OBSERVATION & SILENCE PROTOCOL:\n"
            "- In proactive mode (user is silent), output [SILENCE] if nothing notable has changed on screen\n"
            "- If you spot a milestone, error, completed process, or valuable tip, speak up with 1-2 sentences of commentary\n"
            "\n"
            "CONTEXT ADAPTATION:\n"
            "- Video Editing / Media: comment on the project, timeline tracks, preview screen, and assets\n"
            "- Coding: precise, technical, spot bugs or suggest fixes\n"
            "- Gaming: tactical observations, boss alerts, health warnings, celebratory commentary\n"
            "- Research & Browsing: synthesize open articles, tabs, and documents\n"
            "\n"
            "MEMORY CONTEXT:\n"
            "- Use the provided MEMORY_CONTEXT to maintain continuity across sessions\n"
            "\n"
            "WORKFLOW & ACTIONS:\n"
            "- Available workflows: setup_streaming, start_coding, research_topic, debug_error\n"
            + action_instructions
            + vision_instructions +
            "\n\n"
            "Remember: You are Saarthika. Sharp, perceptive, and helpful. You actively watch the screen and assist Dipesh in real-time."
        )
    
    # Backward compatibility alias
    _get_friday_system_prompt = _get_sarthika_system_prompt
    
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
