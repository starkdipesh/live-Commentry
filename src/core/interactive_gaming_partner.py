#!/usr/bin/env python3
"""
🕉️ Saarthika - Your Strategic AI Partner
A strategic AI companion for Gaming, Coding, and Personal Growth.
"""

import json
import os
import asyncio
import base64
import io
import time
import threading
import random
import queue
import re
from pathlib import Path
from datetime import datetime

import cv2
import mss
import numpy as np
from PIL import Image
import requests
import edge_tts
import speech_recognition as sr

# Import local processors
# Import local processors
try:
    from src.core.cloud_connector import CloudMindConnector
    from src.core.action_executor import ActionExecutor
    from src.core.workflow_engine import WorkflowEngine, WorkflowStep
    from src.core.proactivity_engine import ProactivityEngine, get_proactivity_engine
    from src.core.autonomous_agent import AutonomousAgent, TaskPlanner
    from src.core.emotional_intelligence import EmotionalIntelligence, Mood, PersonalityMode
    from src.integrations.tool_integrations import ToolIntegrations
except ImportError:
    class CloudMindConnector:
        def __init__(self, **kwargs): pass
    class ActionExecutor:
        def __init__(self): pass
        def execute(self, intent, params): return {"status": "error", "message": "ActionExecutor not available"}
    class WorkflowEngine:
        def __init__(self, *args, **kwargs): pass
        def create_from_template(self, *args, **kwargs): return None
        def execute_workflow(self, *args, **kwargs): return None
    class WorkflowStep:
        pass
    class ProactivityEngine:
        def __init__(self): pass
        def analyze_context(self, *args, **kwargs): return []
    class AutonomousAgent:
        def __init__(self, *args, **kwargs): pass
    class TaskPlanner:
        pass
    class EmotionalIntelligence:
        def __init__(self): pass
        def analyze_interaction(self, *args, **kwargs): pass
    class ToolIntegrations:
        def __init__(self): pass

# Image Processor Stub (Use this since we are lightweight now)
class AdvancedImageProcessor:
    def __init__(self, **kwargs):
        self.enhance_mode = kwargs.get('enhance_mode')
        self.target_size = int(kwargs.get('target_size', 336) or 336)
        self.max_width = int(os.getenv('CAPTURE_WIDTH', str(self.target_size)) or self.target_size)
        self.max_height = int(os.getenv('CAPTURE_HEIGHT', str(self.target_size)) or self.target_size)
        self.jpeg_quality = int(os.getenv('CAPTURE_QUALITY', '70') or 70)

    def preprocess_for_vision_model(self, img, **kwargs):
        if img is None:
            return img
        try:
            if hasattr(img, 'mode') and img.mode == 'RGBA':
                img = img.convert('RGB')

            max_w = max(1, self.max_width)
            max_h = max(1, self.max_height)

            scale = min(max_w / img.width, max_h / img.height, 1.0)
            new_w = max(1, int(img.width * scale))
            new_h = max(1, int(img.height * scale))

            if new_w != img.width or new_h != img.height:
                img = img.resize((new_w, new_h), Image.Resampling.BILINEAR)

            return img
        except Exception:
            return img
    def to_base64(self, img):
        if hasattr(img, 'mode') and img.mode == 'RGBA':
            img = img.convert('RGB')
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=self.jpeg_quality, optimize=True)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

class GameplaySceneAnalyzer:
    def analyze_scene_type(self, img): return {}

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

class InteractiveGamingPartner:
    """The World's Best Life-Long Partner Backbone"""
    
    def __init__(self):
        self.ollama_base_url = "http://localhost:11434"
        
        # 🧠 DUAL BRAIN CONFIGURATION
        self.use_cloud_mind = True  # Enabled for Groq processing
        
        # Cloud Mind Config (The Genius Brain - Zero CPU Load)
        # API key loaded from .env file automatically
        self.cloud_base_url = "https://api.groq.com/openai/v1" 
        self.thinking_model = "meta-llama/llama-4-scout-17b-16e-instruct"
        
        # Initialize Connector (reads from .env automatically)
        self.cloud_mind = CloudMindConnector()
        
        # 🎯 SARTHAKA'S ACTION EXECUTOR
        self.action_executor = ActionExecutor()
        
        # 🔄 SARTHAKA'S WORKFLOW ENGINE
        self.workflow_engine = WorkflowEngine(self.action_executor)
        print("✅ WorkflowEngine initialized for multi-step tasks")
        
        # 🎯 SARTHAKA'S PROACTIVITY ENGINE
        self.proactivity_engine = ProactivityEngine()
        self.proactivity_engine.register_trigger_callback(self._on_proactive_trigger)
        print("✅ ProactivityEngine initialized with event-driven triggers")
        
        # 🤖 SARTHAKA'S AUTONOMOUS AGENT
        self.autonomous_agent = AutonomousAgent(self.action_executor, self.workflow_engine)
        print("✅ AutonomousAgent initialized for planning and execution")
        
        # 💝 SARTHAKA'S EMOTIONAL INTELLIGENCE
        self.emotional_intel = EmotionalIntelligence()
        print("✅ EmotionalIntelligence initialized for mood detection")
        
        # 🔧 PROFESSIONAL TOOL INTEGRATIONS
        self.tool_integrations = ToolIntegrations()
        print("✅ ToolIntegrations ready (Git, IDE, Notes, Calendar")
        
        # Identity
        self.name = os.getenv('AI_NAME', 'Friday')
        self.creator = "Dipesh Patel"
        
        # Hardware
        # Hardware (Disabled)
        self.hardware = None
        
        # Vision Tools (Turbo Optimized: 336px is native for llava-phi3)
        self.image_processor = AdvancedImageProcessor(enhance_mode='speed', target_size=336)
        self.scene_analyzer = GameplaySceneAnalyzer()
        self.cap = None 
        use_camera_env = os.getenv('USE_CAMERA', '0')
        self.use_camera = str(use_camera_env).lower() in ('1', 'true', 'yes', 'on')
        
        # Audio Configuration (Professional Voice - Friday's Tone)
        # Default to a professional English voice for Friday
        self.tts_voice = os.getenv('TTS_VOICE', 'en-IN-NeerjaNeural')  # Professional Indian English
        self.tts_rate = os.getenv('TTS_RATE', '+8%')               # Slightly faster but clear
        self.tts_pitch = os.getenv('TTS_PITCH', '+0Hz')              # Natural pitch
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = float(os.getenv('STT_PAUSE_THRESHOLD', '0.5') or 0.5)
        self.recognizer.non_speaking_duration = float(os.getenv('STT_NON_SPEAKING_DURATION', '0.25') or 0.25)
        self.phrase_time_limit = float(os.getenv('STT_PHRASE_TIME_LIMIT', '2.5') or 2.5)
        
        # Hardware Check: Mic
        try:
            self.mic = sr.Microphone()
            self.mic_available = True
            print("✅ Microphone detected")
        except Exception as e:
            print(f"⚠️ Microphone issue: {e}")
            self.mic_available = False
            self.mic = None
        
        # Memory & State
        self.conversation_history = []
        self.speech_queue = queue.Queue()
        self.is_running = False
        self.is_speaking = False
        self.last_observation_time = time.time()
        self.observation_interval = 45  # Increased for CPU efficiency
        self.last_visual_context = ""
        # Capture cache for CPU optimization
        self._last_img_b64 = None
        self._last_img_time = 0
        self._last_processed_image = None
        self.capture_min_interval = float(os.getenv('CAPTURE_MIN_INTERVAL', '1.5') or 1.5)
        # Proactive change detection (skip cloud if little has changed)
        self._last_thumb = None
        self.thumb_size = int(os.getenv('THUMB_SIZE', '64') or 64)
        self.proactive_change_threshold = float(os.getenv('PROACTIVE_CHANGE_THRESHOLD', '0.12') or 0.12)
        
        # Storage Paths
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.logger_dir = self.base_dir / "training_data" / "gold_dataset"
        self.master_log_file = self.logger_dir / "partha_rl_dataset.json" # One file to rule them all
        self.memory_file = self.base_dir / "config" / "personal_memory.json"
        
        self.logger_dir.mkdir(parents=True, exist_ok=True)
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        self.personal_memory = self._load_memory()
        
        # 🧠 SARTHAKA'S SMART MEMORY (RAG-enabled)
        try:
            from src.memory.smart_memory import SmartMemory
            self.smart_memory = SmartMemory()
            print("✅ SmartMemory initialized with RAG")
        except Exception as e:
            print(f"⚠️ SmartMemory init failed: {e}")
            self.smart_memory = None
        
        # Initialize Audio Output
        if PYGAME_AVAILABLE:
            try: 
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                print("✅ Audio output initialized")
            except Exception as e:
                print(f"⚠️ Audio init warning: {e}")
        print(f"✨ {self.name} is online...")
        print(f"🧠 Universal Brain: {self.thinking_model} (Groq)")
        print(f"👨‍💻 Creator: {self.creator}")
        print(f"⚡ Action Layer: Enabled ({len(self.action_executor.get_available_intents())} capabilities)")
        print(f"🔄 Workflow Engine: Ready for multi-step tasks")
        print(f"🎯 Proactivity: Event-driven triggers active")
        print(f"🤖 Autonomous Agent: Planning & execution ready")
        print(f"💝 Emotional Intelligence: Mood detection active")
        print(f"🔧 Tool Integrations: Git, IDE, Notes, Calendar")
        if self.smart_memory:
            stats = self.smart_memory.get_stats()
            if stats:
                print(f"🧠 SmartMemory: {stats.get('total_chunks', 0)} memories, {stats.get('total_projects', 0)} projects")
        
        # Check for Wayland (Ubuntu)
        if os.environ.get('XDG_SESSION_TYPE') == 'wayland':
            print("\n⚠️  WARNING: You are running Ubuntu on Wayland.")
            print("   Screen capture might return a black screen.")
            print("   If it fails, switch to 'Ubuntu on Xorg' at the login screen.\n")
            
        print(f"{'='*60}\n")
        
        if self.use_camera:
            self._init_camera()
        # self._verify_models() # Disabled for pure cloud mode

    def _should_speak_proactively(self, text):
        if not text:
            return False
        if text == "[SILENCE]":
            return False

        lowered = text.lower()
        urgent_markers = [
            "error",
            "failed",
            "failure",
            "exception",
            "traceback",
            "warning",
            "critical",
            "crash",
            "blocked",
            "permission",
            "denied",
            "disconnect",
            "timeout",
            "risk",
            "danger",
            "urgent",
        ]

        if any(marker in lowered for marker in urgent_markers):
            return True

        if "?" in text:
            return False

    def _get_active_window_title(self):
        """Get the currently active window title for context."""
        result = self.action_executor.execute("get_active_window", {})
        if result.get("status") == "success":
            return result.get("message")
        return None

    def _handle_workflow_request(self, params):
        """Handle workflow execution request."""
        from typing import Dict, Any, Optional
        
        workflow_name = params.get('workflow_name')
        template_id = params.get('template_id')
        
        if template_id:
            context = params.get('context', {})
            return self.workflow_engine.create_from_template(template_id, context)
        elif workflow_name:
            # Create custom workflow from provided steps
            steps_data = params.get('steps', [])
            steps = []
            for i, step_data in enumerate(steps_data, 1):
                step = WorkflowStep(
                    id=str(i),
                    name=step_data.get('name', f'Step {i}'),
                    action=step_data.get('action'),
                    params=step_data.get('params', {}),
                    requires_confirmation=step_data.get('requires_confirmation', False)
                )
                steps.append(step)
            
            return self.workflow_engine.create_workflow(workflow_name, "Custom workflow", steps)
        
        return None

    def _on_proactive_trigger(self, trigger_id: str, message: str, priority: int):
        """Handle proactive trigger events."""
        # Only speak for medium and high priority triggers
        if priority >= 2:
            print(f"\n🎯 PROACTIVE TRIGGER: {trigger_id} (priority {priority})")
            # In full implementation, this would queue the message for speaking
            # For now, we just log it
            pass

    def _analyze_for_triggers(self, screen_text: str, active_window: str):
        """Analyze context and trigger proactive events."""
        if not hasattr(self, 'proactivity_engine') or not self.proactivity_engine:
            return
        
        # Determine if user is active
        user_active = (time.time() - self.last_observation_time) < 60
        
        # Analyze context
        triggered = self.proactivity_engine.analyze_context(
            screen_text=screen_text,
            active_window=active_window,
            user_active=user_active
        )
        
        # Handle high-priority triggers
        for event in triggered:
            if event["priority"] >= 3:
                # High priority - speak immediately
                print(f"\n🔔 High priority alert: {event['message']}")
                # In full implementation: asyncio.create_task(self.speak(event['message']))

    def listen_to_user(self, timeout=None):
        """Blocking listen for user speech (safe for main loop)"""
        try:
            return self.speech_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def start_listening(self):
        """Start the background listening thread"""
        if self.mic_available and self.mic:
            try:
                print("🎤 Calibrating microphone...")
                with self.mic as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                self.recognizer.listen_in_background(
                    self.mic, 
                    self._listen_callback,
                    phrase_time_limit=self.phrase_time_limit
                )
                print("✅ Voice recognition active")
            except Exception as e:
                print(f"❌ Mic error: {e}")

    async def capture_vision_safe(self):
        """Safely capture vision data"""
        try:
            vision_data = self.capture_vision()
            return vision_data
        except Exception as e:
            print(f"Error capturing vision: {e}")
            return {'screen': None, 'camera': None}

    def _verify_models(self):
        """Deprecated: We are cloud-native now"""
        pass
        
    def _init_camera(self):
        """Initialize webcam if available"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("⚠️ Camera not found. Screen Only mode.")
                self.use_camera = False
            else:
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.cap.set(cv2.CAP_PROP_FPS, 30)
                print("✅ Camera initialized (640x480)")
        except Exception as e:
            print(f"⚠️ Camera initialization failed: {e}")
            self.use_camera = False

    def _load_memory(self):
        """Load persistent memory from disk"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f: 
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Memory load error: {e}")
        return {
            "user_name": "Dipesh", 
            "interests": [], 
            "interactions_count": 0,
            "favorite_games": [],
            "last_session": None
        }

    def _save_memory(self):
        """Save persistent memory to disk"""
        try:
            self.personal_memory['last_session'] = datetime.now().isoformat()
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.personal_memory, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Memory save error: {e}")

    def _compute_thumb(self, pil_img):
        try:
            if hasattr(pil_img, 'mode') and pil_img.mode != 'L':
                gray = pil_img.convert('L')
            else:
                gray = pil_img
            ts = max(8, int(self.thumb_size))
            thumb = gray.resize((ts, ts), Image.Resampling.BILINEAR)
            return np.asarray(thumb, dtype=np.uint8)
        except Exception:
            return None

    def _should_skip_proactive(self, pil_img):
        thumb = self._compute_thumb(pil_img)
        if thumb is None:
            return False
        if self._last_thumb is None:
            self._last_thumb = thumb
            return False
        try:
            diff = np.mean(np.abs(thumb.astype(np.int16) - self._last_thumb.astype(np.int16))) / 255.0
            self._last_thumb = thumb
            if diff < self.proactive_change_threshold:
                print(f"      - Screen change small (diff={diff:.3f}) → skipping cloud call")
                return True
            return False
        except Exception:
            return False

    def _log_interaction(self, final_image, user_input, ai_response, visual_facts):
        """Log interaction into a unified JSON dataset for Reinforcement Learning"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            img_filename = f"frame_{timestamp}.jpg"
            
            # 1. State-Action Transition Structure
            entry = {
                "id": timestamp,
                "timestamp": datetime.now().isoformat(),
                "state": {
                    "visual": img_filename,
                    "audio_transcript": user_input or "[SILENT_OBSERVATION]"
                },
                "action": {
                    "response": ai_response,
                    "reasoning": visual_facts
                },
                "reward": 0.0,
                "training_format": {
                    "image": img_filename,
                    "conversations": [
                        { "from": "human", "value": f"<image>\n{user_input or 'Analyze screen.'}" },
                        { "from": "gpt", "value": ai_response }
                    ]
                }
            }
            
            # 2. Save Image (with RGBA fix)
            img_path = self.logger_dir / img_filename
            if final_image.mode == 'RGBA':
                final_image = final_image.convert('RGB')
            final_image.save(img_path, quality=85)
            
            # 3. Append to Master JSON File
            dataset = []
            if self.master_log_file.exists():
                try:
                    with open(self.master_log_file, 'r', encoding='utf-8') as f:
                        dataset = json.load(f)
                        if not isinstance(dataset, list): dataset = []
                except:
                    dataset = []
            
            dataset.append(entry)
            
            with open(self.master_log_file, 'w', encoding='utf-8') as f:
                json.dump(dataset, f, indent=4, ensure_ascii=False)
            
            # 3. Save the actual State Image
            img_path = self.logger_dir / img_filename
            final_image.save(img_path, quality=85)
                
            print(f"💾 Step logged to master dataset: {self.master_log_file.name}")
                
        except Exception as e:
            print(f"⚠️ Master Log Error: {e}")

    async def capture_vision_safe(self):
        """Get visibility from display and optionally camera"""
        print("   [1] Capturing vision...")
        vision_data = {}
        
        # 1. Capture Screen
        try:
            print("      - Grabbing screen...")
            # CHECK FOR WAYLAND
            if os.environ.get('XDG_SESSION_TYPE') == 'wayland':
                # Wayland Fallback: gnome-screenshot
                try:
                    import subprocess
                    temp_shot = "/tmp/saarthika_vision.png"
                    # Quietly take screenshot
                    subprocess.run(["gnome-screenshot", "-f", temp_shot], check=True, timeout=2, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    vision_data['screen'] = Image.open(temp_shot)
                    print("      ✓ Screen captured (Wayland/Gnome)")
                except Exception as w_err:
                    print(f"      ✗ Wayland Capture Failed: {w_err}")
                    print("        (Try: sudo apt install gnome-screenshot)")
                    vision_data['screen_blocked'] = True
            else:
                # Xorg (Standard)
                with mss.mss() as sct:
                    monitor = sct.monitors[1]
                    sct_img = sct.grab(monitor)
                    screen_img = Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')
                    vision_data['screen'] = screen_img
                    print("      ✓ Screen captured (Xorg)")
        except Exception as e:
            print(f"      ✗ Screen capture failed: {e}")
            vision_data['screen_blocked'] = True
            
        # 2. Capture Camera (if enabled)
        if self.use_camera and self.cap:
            try:
                print("      - Grabbing camera...")
                ret, frame = self.cap.read()
                if ret:
                    cam_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    vision_data['camera'] = Image.fromarray(cam_img)
                    print("      ✓ Camera captured")
            except Exception as e:
                print(f"      ✗ Camera capture failed: {e}")
                vision_data['camera_error'] = True
                
        return vision_data

    def prepare_multimodal_input(self, vision_data):
        """Combine available vision sources"""
        print("   [2] Preparing image...")
        if 'screen' in vision_data:
            screen = vision_data['screen']
            
            if vision_data.get('camera'):
                cam = vision_data['camera']
                h = screen.height // 3
                w = int(cam.width * (h / cam.height))
                cam_resized = cam.resize((w, h), Image.Resampling.LANCZOS)
                
                combined = screen.copy()
                combined.paste(cam_resized, (screen.width - w - 20, screen.height - h - 20))
                print("      ✓ Combined screen + camera")
                return combined
            print("      ✓ Using screen only")
            return screen
            
        elif 'camera' in vision_data:
            print("      ✓ Using camera only")
            return vision_data['camera']
        
        print("      ✓ Using black fallback")
        return Image.new('RGB', (1024, 768), color=(30, 30, 30))

    async def _get_visual_description(self, img_b64):
        """Step 1: Vision Model Analysis"""
        print("   [3] Calling VISION model...")
        
        prompt = "Describe what you see in 1-2 sentences. Mention any UI, actions, or environment."
        
        try:
            start_time = time.time()
            print(f"      - Sending request to {self.vision_model}...")
            
            response = requests.post(
                f"{self.ollama_base_url}/api/generate", 
                json={
                    "model": self.vision_model,
                    "prompt": prompt,
                    "images": [img_b64],
                    "stream": False,
                    "options": {
                        "num_predict": 30,  # Ultra-fast punchy description
                        "temperature": 0.1,
                        "num_thread": 8     # Assuming 8 threads, Ollama will optimize
                    },
                    "keep_alive": "10m" 
                }, 
                timeout=60
            )
            
            elapsed = time.time() - start_time
            print(f"      - Response received in {elapsed:.1f}s")
            
            if response.status_code == 200:
                result = response.json().get('response', '').strip()
                if result:
                    print(f"      ✓ Vision: {result[:60]}...")
                    return result
                else:
                    return "Visual clear but no detail"
            else:
                return "Visual analysis failed"
                
        except Exception as e:
            print(f"      ✗ Vision Error: {e}")
            return "Visual error"

    async def _get_strategic_response(self, visual_context, user_speech):
        """Step 2: Thinking Model Response"""
        if self.use_cloud_mind:
            return await self._get_cloud_strategic_response(visual_context, user_speech)
        
        print(f"   [4] Calling LOCAL MIND ({self.thinking_model})...")
        user_name = self.personal_memory.get('user_name', 'Dipesh')
        
        # Simplified prompt for faster response
        if user_speech:
            prompt = f"User says: {user_speech}\nGame scene: {visual_context}\nStrategy: Be a Hinglish friend. {user_name} is playing. Short reaction."
        else:
            prompt = f"Game scene: {visual_context}\nStrategy: 1 short Hinglish comment for {user_name}."

        try:
            start_time = time.time()
            response = requests.post(
                f"{self.ollama_base_url}/api/generate", 
                json={
                    "model": self.thinking_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,
                        "num_predict": 25,
                        "num_ctx": 1024,
                        "num_thread": 8
                    },
                    "keep_alive": "10m"
                }, 
                timeout=60
            )
            if response.status_code == 200:
                result = response.json().get('response', '').strip()
                
                # Clean up
                result = result.strip('"').strip("'").strip()
                if "Reply:" in result:
                    result = result.split("Reply:")[-1].strip()
                
                if result:
                    print(f"      ✓ Response: {result[:60]}...")
                    return result, "success"
                else:
                    print("      ✗ Empty response from thinking model")
                    return None, None
            else:
                print(f"      ✗ Thinking API Error: {response.status_code}")
                print(f"         {response.text[:200]}")
                return None, None
                
        except requests.exceptions.Timeout:
            print("      ✗ TIMEOUT: Thinking model took too long!")
            return None, None
        except Exception as e:
            print(f"      ✗ Thinking Error: {e}")
            return None, None

    async def _get_cloud_strategic_response(self, visual_facts, user_speech, image_b64=None):
        """Step 2: Cloud Mind Response with Action Support"""
        print(f"   [4] Sarthika analyzing via CLOUD MIND ({self.thinking_model})...")
        
        # Get active window for context
        active_window = self._get_active_window_title()
        if active_window:
            print(f"      - Active window: {active_window[:50]}...")
        
        # Get available actions
        available_actions = self.action_executor.get_available_intents()
        
        # Get SmartMemory context
        memory_context = ""
        if self.smart_memory:
            context_parts = []
            
            # Get current project
            current_project = self.smart_memory.get_current_project()
            if current_project:
                context_parts.append(f"PROJECT: {current_project}")
            
            # Get relevant context from user speech
            if user_speech:
                memory_context = self.smart_memory.format_context_for_prompt(
                    user_speech, recent_n=3, relevant_k=2
                )
                if memory_context:
                    context_parts.append(f"MEMORY_CONTEXT:\n{memory_context}")
            
        # Update memory with workflow capability info
        workflow_templates = self.workflow_engine.get_workflow_templates()
        context_parts.append(f"WORKFLOW_TEMPLATES: {', '.join(workflow_templates.keys())}")
        context_parts.append("For multi-step tasks, include [WORKFLOW:template_id|context_var=value]")
        
        # Use our new dedicated connector with image support and action extraction
        reply, status, action_request = self.cloud_mind.think(
            visual_facts=visual_facts, 
            user_speech=user_speech,
            history=self.conversation_history,
            image_b64=image_b64,
            active_window=active_window,
            available_actions=available_actions,
            memory_context=memory_context
        )
        
        # Execute action if requested
        if action_request and action_request.get("intent"):
            intent = action_request.get("intent")
            params = action_request.get("params", {})
            
            # Check if it's a workflow request
            if intent == "execute_workflow":
                print(f"      ⚡ Starting workflow: {params.get('workflow_name', 'custom')}")
                workflow = self._handle_workflow_request(params)
                if workflow:
                    await self.workflow_engine.execute_workflow(workflow)
                    reply = f"{reply}\n[Workflow completed: {workflow.name}]"
                else:
                    reply = f"{reply}\n[Workflow creation failed]"
            else:
                print(f"      ⚡ Executing action: {intent}")
                action_result = self.action_executor.execute(intent, params)
                
                # Guard against None result
                if action_result is None:
                    action_result = {"status": "error", "message": "Action returned no result"}
                
                print(f"      ✓ Action result: {action_result.get('message', 'Done')}")
                
                # Don't append action results to the spoken reply - only log them
                # The AI's response should stand on its own without technical error messages
                if action_result.get("status") != "success":
                    print(f"      ⚠️ Action failed (logged but not spoken): {action_result.get('message')}")
        
        if status == "success":
            return reply, "Sarthika's analysis complete."
        else:
            print(f"      ✗ Cloud Mind Error: {reply}")
            return "Sir, I'm experiencing a connection issue. Please check the network.", "Error"

    async def generate_response(self, user_speech=None, proactive=False):
        """Execute the Dual-Brain Pipeline with extensive logging"""
        try:
            print(f"\n{'='*60}")
            print(f"🎯 STARTING RESPONSE GENERATION")
            if user_speech:
                print(f"   Mode: User spoke '{user_speech}'")
            else:
                print(f"   Mode: Proactive observation")
            print(f"{'='*60}")
            
            # 1. Capture or reuse recent image (CPU-optimized)
            now_ts = time.time()
            if (self._last_img_b64 is not None 
                and self._last_processed_image is not None 
                and (now_ts - self._last_img_time) < self.capture_min_interval):
                processed_img = self._last_processed_image
                img_b64 = self._last_img_b64
                print("      - Using cached image")
                print(f"      ✓ Image ready ({len(img_b64)} bytes)")
            else:
                vision_data = await self.capture_vision_safe()
                combined_img = self.prepare_multimodal_input(vision_data)
                
                print("      - Processing image...")
                processed_img = self.image_processor.preprocess_for_vision_model(combined_img)
                img_b64 = self.image_processor.to_base64(processed_img)
                self._last_processed_image = processed_img
                self._last_img_b64 = img_b64
                self._last_img_time = now_ts
                print(f"      ✓ Image ready ({len(img_b64)} bytes)")
            
            # 2. Get Response (Directly via Groq Vision if enabled)
            reply, thought = None, None
            visual_facts = "[Full Multimodal Analysis]"

            # Proactive skip if no meaningful screen change
            if (self.use_cloud_mind and not user_speech):
                if self._should_skip_proactive(processed_img):
                    reply, thought = "[SILENCE]", "Skipped due to low change"

            if reply is None:
                if self.use_cloud_mind:
                    if user_speech:
                        mode_context = "MODE: USER_SPOKE"
                    else:
                        mode_context = (
                            "MODE: PROACTIVE\n"
                            "USER_STATE: silent\n"
                            "RULE: Output [SILENCE] unless there is something clearly valuable or urgent."
                        )
                    reply, thought = await self._get_cloud_strategic_response(mode_context, user_speech, img_b64)
                    visual_facts = "[Full Multimodal Analysis]"
                else:
                    # Fallback to local vision + local mind (if configured)
                    visual_facts = await self._get_visual_description(img_b64)
                    reply, thought = await self._get_strategic_response(visual_facts, user_speech)

            normalized_reply = reply.strip() if isinstance(reply, str) else reply

            if isinstance(normalized_reply, str) and "[SILENCE]" in normalized_reply and normalized_reply != "[SILENCE]":
                normalized_reply = normalized_reply.replace("[SILENCE]", "").strip()

            if proactive and not user_speech and isinstance(normalized_reply, str):
                if not self._should_speak_proactively(normalized_reply):
                    normalized_reply = "[SILENCE]"

            if normalized_reply:
                # Clean up action markers from speech output
                cleaned_reply = re.sub(r'\[ACTION:[^\]]+\]', '', normalized_reply).strip()
                cleaned_reply = re.sub(r'\[Action [^\]]+\]', '', cleaned_reply).strip()
                
                if cleaned_reply == "[SILENCE]":
                    print(f"\n🤐 SILENCE: No response needed")
                else:
                    print(f"\n✅ SUCCESS: Response generated!")

                print(f"{'='*60}\n")

                self.personal_memory['interactions_count'] = self.personal_memory.get('interactions_count', 0) + 1
                self._save_memory()

                self._log_interaction(processed_img, user_speech or "[PROACTIVE]", normalized_reply, visual_facts)

                if user_speech:
                    self.conversation_history.append({"role": "user", "content": user_speech})
                self.conversation_history.append({"role": "assistant", "content": normalized_reply})

                if len(self.conversation_history) > 10:
                    self.conversation_history = self.conversation_history[-10:]

                if cleaned_reply == "[SILENCE]" or cleaned_reply == "":
                    return ""

                # Store in SmartMemory before returning
                if self.smart_memory and user_speech and cleaned_reply:
                    # Get active window for memory context
                    active_window = self._get_active_window_title()
                    self.smart_memory.store_interaction(
                        user_input=user_speech,
                        ai_response=cleaned_reply,
                        visual_context=active_window or "",
                        session_id="default"
                    )
                
                return cleaned_reply
            else:
                print(f"\n❌ FAILED: No response generated")
                print(f"{'='*60}\n")
                return None
                
        except Exception as e:
            print(f"\n❌ PIPELINE ERROR: {e}")
            import traceback
            traceback.print_exc()
            print(f"{'='*60}\n")
            return None

    async def speak(self, text):
        """Convert text to speech and play"""
        if not text: 
            return
            
        print(f"\n💬 SPEAKING: \"{text}\"\n")
        
        self.is_speaking = True
        try:
            temp_dir = self.base_dir / "src" / "core" / "tmp"
            temp_dir.mkdir(parents=True, exist_ok=True)
            temp_file = temp_dir / f"partha_{int(time.time() * 1000)}.mp3"
            
            print("   - Generating speech...")
            print("   - Generating speech...")
            # Sweet Tone Tuning
            communicate = edge_tts.Communicate(
                text, 
                self.tts_voice, 
                rate=self.tts_rate,
                pitch=self.tts_pitch
            )
            await communicate.save(str(temp_file))
            print("   ✓ Speech generated")
            
            # Play audio
            print("   - Playing audio...")
            if PYGAME_AVAILABLE:
                try:
                    pygame.mixer.music.load(str(temp_file))
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        await asyncio.sleep(0.1)
                    print("   ✓ Audio played")
                except Exception as e:
                    print(f"   ✗ Pygame failed: {e}, using system player")
                    os.system(f"mpg123 -q '{temp_file}' 2>/dev/null &")
                    await asyncio.sleep(3)
            else:
                os.system(f"mpg123 -q '{temp_file}' 2>/dev/null &")
                await asyncio.sleep(3)
                
            # Cleanup
            await asyncio.sleep(0.5)
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ TTS Error: {e}")
        finally:
            self.is_speaking = False

    def _listen_callback(self, recognizer, audio):
        """Callback for background listener"""
        try:
            if getattr(self, 'is_speaking', False):
                return
            print("\n👂 Heard audio, recognizing...")
            speech_text = recognizer.recognize_google(audio, language="hi-IN")
            print(f"🗣️  USER: {speech_text}")
            self.speech_queue.put(speech_text)
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(f"⚠️  Speech service error: {e}")
        except Exception as e:
            print(f"⚠️  STT Error: {e}")

    async def run(self):
        """Main loop with debug output"""
        print("\n" + "="*60)
        print("🚀 DEBUG MODE - INTERACTIVE GAMING PARTNER")
        print("="*60)
        if self.mic_available:
            print("🎙️  Microphone ready")
        else:
            print("⚠️  No microphone")
        print("🛑 Press Ctrl+C to stop")
        print("="*60 + "\n")
        
        self.is_running = True
        stop_listening = None
        
        # Start voice listener
        if self.mic_available and self.mic:
            try:
                print("🎤 Calibrating microphone...")
                with self.mic as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                stop_listening = self.recognizer.listen_in_background(
                    self.mic, 
                    self._listen_callback,
                    phrase_time_limit=10
                )
                print("✅ Voice recognition active\n")
            except Exception as e:
                print(f"❌ Mic error: {e}\n")
                stop_listening = lambda wait_for_stop=False: None
        else:
            stop_listening = lambda wait_for_stop=False: None

        try:
            # TEST: Generate one response immediately
            print("🧪 TESTING: Generating initial greeting...\n")
            greeting = await self.generate_response(proactive=True)
            if greeting:
                await self.speak(greeting)
            else:
                print("⚠️ Initial greeting failed - check logs above!\n")
            
            iteration = 0
            while self.is_running:
                iteration += 1
                
                # Debug: Show we're alive
                if iteration % 50 == 0:
                    print(f"💓 Heartbeat {iteration} - waiting for speech or proactive trigger...")
                
                # 1. Check for user speech
                try:
                    user_speech = self.speech_queue.get(timeout=0.5)
                    print(f"\n🎤 Got speech from queue: '{user_speech}'")
                    
                    response_text = await self.generate_response(user_speech=user_speech)
                    
                    if response_text:
                        await self.speak(response_text)
                    else:
                        print("⚠️ No response generated for user speech")
                    
                    self.last_observation_time = time.time()
                    
                except queue.Empty:
                    pass
                
                # 2. Proactive observation
                current_time = time.time()
                if current_time - self.last_observation_time > self.observation_interval:
                    print(f"\n⏰ Proactive trigger ({self.observation_interval}s elapsed)")
                    proactive_text = await self.generate_response(proactive=True)
                    
                    if proactive_text:
                        await self.speak(proactive_text)
                    
                    self.last_observation_time = current_time
                
                await asyncio.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n\n⏸️  Shutdown requested")
        finally:
            self.is_running = False
            
            if stop_listening:
                stop_listening(wait_for_stop=False)
            if self.cap and self.cap.isOpened():
                self.cap.release()
            
            print("\n👋 Debug session ended")
            print(f"📊 Total interactions: {self.personal_memory.get('interactions_count', 0)}")

def main():
    """Entry point"""
    print("\n🔍 DIAGNOSTIC MODE - Running checks...\n")
    
    # Check Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            print("✅ Ollama is running")
        else:
            print("⚠️  Ollama responded with unusual status")
    except:
        print("❌ Ollama is NOT running! Start it with: ollama serve")
        return
    
    print("\nStarting in 3 seconds...\n")
    time.sleep(3)
    
    partner = InteractiveGamingPartner()
    
    try:
        asyncio.run(partner.run())
    except KeyboardInterrupt:
        print("\n✅ Clean exit")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()