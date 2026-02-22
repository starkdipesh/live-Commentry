"""
ActionExecutor - Friday's Action Layer
Handles system commands, application control, media, browser automation, and file operations.
"""

import subprocess
import os
import platform
import webbrowser
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
import time
from urllib.parse import quote


class ActionExecutor:
    """
    Friday's action execution engine.
    Translates natural language intents into system actions.
    """
    
    def __init__(self):
        self.system = platform.system()
        self.command_history = []
        self.dangerous_commands = [
            'rm -rf', 'del /f /s', 'format', 'mkfs', 'dd if',
            '>:', 'shutdown -h now', 'init 0', 'halt',
            'reg delete', 'rd /s /q c:', 'erase /f /s /q c:',
            'sudo rm', 'chmod -R 777 /', 'chown -R root:root /'
        ]
        self.allowed_shell_commands = [
            'ls', 'dir', 'cat', 'type', 'head', 'tail', 'grep', 'find',
            'ps', 'top', 'htop', 'df', 'du', 'pwd', 'cd', 'echo',
            'git status', 'git log', 'git diff', 'git branch',
            'python', 'python3', 'pip', 'pip3', 'node', 'npm',
            'docker ps', 'docker images', 'docker logs',
            'mkdir', 'touch', 'cp', 'copy', 'mv', 'move', 'rm', 'del'
        ]
        
    def execute(self, intent: str, params: Dict) -> Dict:
        """
        Execute an action based on intent and parameters.
        Returns result dict with status and message.
        """
        timestamp = time.time()
        result = {"status": "error", "message": "Unknown intent", "action": intent}
        
        try:
            if intent == "open_application":
                result = self._open_application(params.get("app_name"), params.get("args", []))
            elif intent == "close_application":
                result = self._close_application(params.get("app_name"))
            elif intent == "open_url":
                result = self._open_url(params.get("url"), params.get("browser"))
            elif intent == "search_web":
                result = self._search_web(params.get("query"), params.get("engine", "google"))
            elif intent == "media_control":
                result = self._media_control(params.get("command"), params.get("value"))
            elif intent == "volume_control":
                result = self._volume_control(params.get("action"), params.get("level"))
            elif intent == "system_shortcut":
                result = self._system_shortcut(params.get("action"))
            elif intent == "file_operation":
                result = self._file_operation(
                    params.get("operation"),
                    params.get("source"),
                    params.get("destination"),
                    params.get("content")
                )
            elif intent == "shell_command":
                result = self._execute_shell_command(
                    params.get("command"),
                    params.get("requires_confirmation", True)
                )
            elif intent == "create_folder":
                result = self._create_folder(params.get("path"))
            elif intent == "open_file":
                result = self._open_file(params.get("path"))
            elif intent == "search_files":
                result = self._search_files(params.get("query"), params.get("location"))
            elif intent == "screenshot":
                result = self._take_screenshot(params.get("save_path"))
            elif intent == "click_screen":
                result = self._click_screen(params.get("x"), params.get("y"))
            elif intent == "type_text":
                result = self._type_text(params.get("text"))
            elif intent == "lock_screen":
                result = self._lock_screen()
            elif intent == "mute_system":
                result = self._mute_system(params.get("mute", True))
            elif intent == "get_active_window":
                result = self._get_active_window()
            else:
                result = {"status": "error", "message": f"Intent '{intent}' not implemented"}
                
        except Exception as e:
            result = {"status": "error", "message": f"Execution failed: {str(e)}"}
        
        # Log action
        self.command_history.append({
            "timestamp": timestamp,
            "intent": intent,
            "params": params,
            "result": result
        })
        
        return result
    
    def _open_application(self, app_name: str, args: List[str] = None) -> Dict:
        """Open an application by name."""
        if not app_name:
            return {"status": "error", "message": "No application name provided"}
        
        args = args or []
        
        # Normalize app name - handle Hindi/Unicode
        normalized_name = app_name.lower().strip()
        
        # Application mapping for common apps (OS-specific)
        app_map = self._get_app_map()
        
        # Add aliases for common terms in different languages
        aliases = {
            # Hindi aliases
            "कैलकुलेटर": "calculator",
            "कैल्कुलेटर": "calculator",
            "ब्राउज़र": "browser",
            "फाइल": "files",
            "फाइल मैनेजर": "file manager",
            "टर्मिनल": "terminal",
            "संगीत": "spotify",
            "वीडियो": "vlc",
            # English variations
            "calc": "calculator",
            "math": "calculator",
            "internet": "browser",
            "web": "browser",
            "editor": "code",
            "ide": "code",
            "command prompt": "terminal",
            "cmd": "terminal" if self.system == "Linux" else "cmd",
            "bash": "terminal",
            "shell": "terminal",
        }
        
        # Check aliases first
        if normalized_name in aliases:
            normalized_name = aliases[normalized_name]
        
        # Try exact match first
        command = app_map.get(normalized_name)
        
        if not command:
            # Try partial match
            for key, cmd in app_map.items():
                if normalized_name in key or key in normalized_name:
                    command = cmd
                    break
        
        if not command:
            # For Linux, try common command names
            if self.system == "Linux":
                linux_commands = ["gnome-calculator", "gnome-terminal", "firefox", "google-chrome", 
                                  "nautilus", "gedit", "vlc", "rhythmbox", "gnome-system-monitor",
                                  "gnome-screenshot", "gnome-control-center", "xcalc", "galculator"]
                if normalized_name in linux_commands or any(cmd in normalized_name for cmd in linux_commands):
                    command = normalized_name
            else:
                command = app_name  # Assume it's a valid command
        
        if not command:
            return {"status": "error", "message": f"Don't know how to open '{app_name}' on {self.system}"}
        
        try:
            if self.system == "Windows":
                subprocess.Popen([command] + args, shell=True)
            else:
                # Linux/macOS - use subprocess without shell for security
                subprocess.Popen([command] + args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            return {"status": "success", "message": f"Opened {app_name}"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to open {app_name}: {str(e)}"}
    
    def _close_application(self, app_name: str) -> Dict:
        """Close an application by name."""
        if not app_name:
            return {"status": "error", "message": "No application name provided"}
        
        try:
            if self.system == "Windows":
                subprocess.run(["taskkill", "/F", "/IM", f"{app_name}.exe"], capture_output=True)
            elif self.system == "Linux":
                # Try pkill with various patterns
                subprocess.run(["pkill", "-f", app_name], capture_output=True)
            else:  # macOS
                subprocess.run(["pkill", "-f", app_name], capture_output=True)
            
            return {"status": "success", "message": f"Closed {app_name}"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to close {app_name}: {str(e)}"}
    
    def _open_url(self, url: str, browser: Optional[str] = None) -> Dict:
        """Open a URL in browser."""
        if not url:
            return {"status": "error", "message": "No URL provided"}
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            if browser:
                # Open with specific browser
                self._open_application(browser, [url])
            else:
                webbrowser.open(url)
            
            return {"status": "success", "message": f"Opened {url}"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to open URL: {str(e)}"}
    
    def _search_web(self, query: str, engine: str = "google") -> Dict:
        """Search the web."""
        if not query:
            return {"status": "error", "message": "No search query provided"}
        
        encoded_query = quote(query)
        
        search_urls = {
            "google": f"https://www.google.com/search?q={encoded_query}",
            "youtube": f"https://www.youtube.com/results?search_query={encoded_query}",
            "github": f"https://github.com/search?q={encoded_query}",
            "stackoverflow": f"https://stackoverflow.com/search?q={encoded_query}",
            "duckduckgo": f"https://duckduckgo.com/?q={encoded_query}",
            "bing": f"https://www.bing.com/search?q={encoded_query}"
        }
        
        url = search_urls.get(engine.lower(), search_urls["google"])
        return self._open_url(url)
    
    def _media_control(self, command: str, value: Optional[str] = None) -> Dict:
        """Control media playback with fallbacks for different systems."""
        try:
            if self.system == "Linux":
                # Try playerctl first (most common)
                try:
                    if command in ["play", "pause", "play-pause", "stop", "next", "previous"]:
                        result = subprocess.run(["playerctl", command], capture_output=True, text=True)
                        if result.returncode == 0:
                            return {"status": "success", "message": f"Media {command}"}
                except FileNotFoundError:
                    pass  # playerctl not installed, try alternatives
                
                # Fallback 1: Try dbus-send for MPRIS media control
                try:
                    mpris_commands = {
                        "play": "Play",
                        "pause": "Pause", 
                        "play-pause": "PlayPause",
                        "stop": "Stop",
                        "next": "Next",
                        "previous": "Previous"
                    }
                    if command in mpris_commands:
                        dbus_cmd = [
                            "dbus-send", "--print-reply", "--dest=org.mpris.MediaPlayer2.spotify",
                            "/org/mpris/MediaPlayer2", f"org.mpris.MediaPlayer2.Player.{mpris_commands[command]}"
                        ]
                        result = subprocess.run(dbus_cmd, capture_output=True, text=True)
                        if result.returncode == 0:
                            return {"status": "success", "message": f"Media {command} via D-Bus"}
                except Exception:
                    pass
                
                # Fallback 2: Try xdotool to send media keys
                try:
                    media_keys = {
                        "play": "XF86AudioPlay",
                        "pause": "XF86AudioPause",
                        "play-pause": "XF86AudioPlay",
                        "stop": "XF86AudioStop", 
                        "next": "XF86AudioNext",
                        "previous": "XF86AudioPrev"
                    }
                    if command in media_keys:
                        subprocess.run(["xdotool", "key", media_keys[command]], capture_output=True)
                        return {"status": "success", "message": f"Media {command} via key simulation"}
                except Exception:
                    pass
                
                return {"status": "error", "message": "Media control not available. Install playerctl: sudo apt install playerctl"}
                
            elif self.system == "Windows":
                # Windows media keys using keyboard simulation would go here
                return {"status": "success", "message": f"Media command '{command}' sent"}
            else:  # macOS
                # Use osascript for macOS media control
                cmd_map = {
                    "play": "play",
                    "pause": "pause",
                    "play-pause": "playpause",
                    "stop": "stop",
                    "next": "next track",
                    "previous": "previous track"
                }
                apple_script = f'tell application "System Events" to {cmd_map.get(command, command)}'
                subprocess.run(["osascript", "-e", apple_script], capture_output=True)
                return {"status": "success", "message": f"Media {command}"}
            
        except Exception as e:
            return {"status": "error", "message": f"Media control failed: {str(e)}"}
    
    def _volume_control(self, action: str, level: Optional[int] = None) -> Dict:
        """Control system volume."""
        try:
            if self.system == "Linux":
                if action == "mute":
                    subprocess.run(["amixer", "-D", "pulse", "set", "Master", "mute"], capture_output=True)
                elif action == "unmute":
                    subprocess.run(["amixer", "-D", "pulse", "set", "Master", "unmute"], capture_output=True)
                elif action == "set" and level is not None:
                    subprocess.run(["amixer", "-D", "pulse", "set", "Master", f"{level}%"], capture_output=True)
                elif action == "up":
                    subprocess.run(["amixer", "-D", "pulse", "set", "Master", "10%+"], capture_output=True)
                elif action == "down":
                    subprocess.run(["amixer", "-D", "pulse", "set", "Master", "10%-"], capture_output=True)
                    
            elif self.system == "Windows":
                # Windows volume control using nircmd or similar would go here
                pass
            else:  # macOS
                if action == "mute":
                    subprocess.run(["osascript", "-e", "set volume with output muted"], capture_output=True)
                elif action == "unmute":
                    subprocess.run(["osascript", "-e", "set volume without output muted"], capture_output=True)
                elif action == "set" and level is not None:
                    # macOS volume is 0-100
                    subprocess.run(["osascript", "-e", f"set volume output volume {level}"], capture_output=True)
            
            return {"status": "success", "message": f"Volume {action}"}
        except Exception as e:
            return {"status": "error", "message": f"Volume control failed: {str(e)}"}
    
    def _system_shortcut(self, action: str) -> Dict:
        """Execute system shortcuts."""
        try:
            if action == "screenshot":
                return self._take_screenshot()
            elif action == "lock":
                return self._lock_screen()
            elif action == "screenshot_area":
                # Screenshot of selected area
                if self.system == "Linux":
                    subprocess.Popen(["gnome-screenshot", "-a"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return {"status": "success", "message": "Area screenshot mode activated"}
            elif action == "screenshot_window":
                if self.system == "Linux":
                    subprocess.Popen(["gnome-screenshot", "-w"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return {"status": "success", "message": "Window screenshot captured"}
            elif action == "minimize_all":
                if self.system == "Linux":
                    subprocess.run(["xdotool", "key", "Super+d"], capture_output=True)
                return {"status": "success", "message": "All windows minimized"}
            else:
                return {"status": "error", "message": f"Unknown system action: {action}"}
        except Exception as e:
            return {"status": "error", "message": f"System shortcut failed: {str(e)}"}
    
    def _file_operation(self, operation: str, source: Optional[str], 
                       destination: Optional[str], content: Optional[str]) -> Dict:
        """Perform file operations."""
        try:
            if operation == "create" and source:
                Path(source).touch()
                return {"status": "success", "message": f"Created file {source}"}
            elif operation == "write" and source and content:
                with open(source, 'w') as f:
                    f.write(content)
                return {"status": "success", "message": f"Wrote to {source}"}
            elif operation == "read" and source:
                with open(source, 'r') as f:
                    data = f.read()
                return {"status": "success", "message": f"Read {source}", "data": data}
            elif operation == "copy" and source and destination:
                shutil.copy2(source, destination)
                return {"status": "success", "message": f"Copied {source} to {destination}"}
            elif operation == "move" and source and destination:
                shutil.move(source, destination)
                return {"status": "success", "message": f"Moved {source} to {destination}"}
            elif operation == "delete" and source:
                if os.path.isdir(source):
                    shutil.rmtree(source)
                else:
                    os.remove(source)
                return {"status": "success", "message": f"Deleted {source}"}
            elif operation == "list" and source:
                files = os.listdir(source)
                return {"status": "success", "message": f"Listed {len(files)} items", "data": files}
            else:
                return {"status": "error", "message": "Invalid file operation"}
        except Exception as e:
            return {"status": "error", "message": f"File operation failed: {str(e)}"}
    
    def _create_folder(self, path: str) -> Dict:
        """Create a folder."""
        if not path:
            return {"status": "error", "message": "No path provided"}
        
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return {"status": "success", "message": f"Created folder {path}"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to create folder: {str(e)}"}
    
    def _open_file(self, path: str) -> Dict:
        """Open a file with default application."""
        if not path or not os.path.exists(path):
            return {"status": "error", "message": f"File not found: {path}"}
        
        try:
            if self.system == "Windows":
                os.startfile(path)
            elif self.system == "Darwin":  # macOS
                subprocess.run(["open", path], check=True)
            else:  # Linux
                subprocess.run(["xdg-open", path], check=True)
            
            return {"status": "success", "message": f"Opened {path}"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to open file: {str(e)}"}
    
    def _search_files(self, query: str, location: Optional[str] = None) -> Dict:
        """Search for files."""
        if not location:
            location = os.path.expanduser("~")
        
        try:
            results = []
            for root, dirs, files in os.walk(location):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for file in files:
                    if query.lower() in file.lower():
                        results.append(os.path.join(root, file))
                if len(results) >= 20:  # Limit results
                    break
            
            return {"status": "success", "message": f"Found {len(results)} files", "data": results}
        except Exception as e:
            return {"status": "error", "message": f"Search failed: {str(e)}"}
    
    def _execute_shell_command(self, command: str, requires_confirmation: bool = True) -> Dict:
        """Execute a shell command with safety checks."""
        if not command:
            return {"status": "error", "message": "No command provided"}
        
        # Check for dangerous commands
        for dangerous in self.dangerous_commands:
            if dangerous in command.lower():
                return {
                    "status": "blocked", 
                    "message": f"Command blocked for safety: contains '{dangerous}'",
                    "requires_confirmation": True
                }
        
        # Check if command is in allowed list
        is_allowed = any(allowed in command.lower() for allowed in self.allowed_shell_commands)
        
        if not is_allowed and requires_confirmation:
            return {
                "status": "pending_confirmation",
                "message": f"Command '{command}' requires confirmation",
                "command": command
            }
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=30
            )
            
            output = result.stdout if result.returncode == 0 else result.stderr
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "message": output[:500],  # Limit output length
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Command timed out"}
        except Exception as e:
            return {"status": "error", "message": f"Command failed: {str(e)}"}
    
    def _take_screenshot(self, save_path: Optional[str] = None) -> Dict:
        """Take a screenshot."""
        try:
            if not save_path:
                save_dir = os.path.expanduser("~/Pictures/Friday")
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, f"screenshot_{int(time.time())}.png")
            
            if self.system == "Linux":
                subprocess.run(["gnome-screenshot", "-f", save_path], capture_output=True)
            elif self.system == "Windows":
                # Use PIL for Windows screenshot
                try:
                    from PIL import ImageGrab
                    ImageGrab.grab().save(save_path)
                except ImportError:
                    return {"status": "error", "message": "PIL not installed for screenshots"}
            else:  # macOS
                subprocess.run(["screencapture", save_path], capture_output=True)
            
            return {"status": "success", "message": f"Screenshot saved to {save_path}", "path": save_path}
        except Exception as e:
            return {"status": "error", "message": f"Screenshot failed: {str(e)}"}
    
    def _lock_screen(self) -> Dict:
        """Lock the screen."""
        try:
            if self.system == "Linux":
                subprocess.run(["gnome-screensaver-command", "-l"], capture_output=True)
                # Fallback for systems without gnome-screensaver
                subprocess.run(["loginctl", "lock-session"], capture_output=True)
            elif self.system == "Windows":
                subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], capture_output=True)
            else:  # macOS
                subprocess.run(["/System/Library/CoreServices/Menu\ Extras/User.menu/Contents/Resources/CGSession", "-suspend"], capture_output=True)
            
            return {"status": "success", "message": "Screen locked"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to lock screen: {str(e)}"}
    
    def _mute_system(self, mute: bool = True) -> Dict:
        """Mute or unmute system audio."""
        action = "mute" if mute else "unmute"
        return self._volume_control(action, None)
    
    def _get_active_window(self) -> Dict:
        """Get the currently active window title."""
        try:
            if self.system == "Linux":
                result = subprocess.run(
                    ["xdotool", "getactivewindow", "getwindowname"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return {"status": "success", "message": result.stdout.strip()}
            elif self.system == "Windows":
                # Windows implementation would require win32gui
                return {"status": "success", "message": "Active window detection not implemented for Windows"}
            else:  # macOS
                script = 'tell application "System Events" to name of first application process whose frontmost is true'
                result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
                if result.returncode == 0:
                    return {"status": "success", "message": result.stdout.strip()}
            
            return {"status": "error", "message": "Could not get active window"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to get active window: {str(e)}"}
    
    def _click_screen(self, x: Optional[int], y: Optional[int]) -> Dict:
        """Click at screen coordinates."""
        if x is None or y is None:
            return {"status": "error", "message": "Coordinates required"}
        
        try:
            if self.system == "Linux":
                subprocess.run(["xdotool", "mousemove", str(x), str(y), "click", "1"], capture_output=True)
            else:
                # Try using pyautogui if available
                try:
                    import pyautogui
                    pyautogui.click(x, y)
                except ImportError:
                    return {"status": "error", "message": "pyautogui not installed for click automation"}
            
            return {"status": "success", "message": f"Clicked at ({x}, {y})"}
        except Exception as e:
            return {"status": "error", "message": f"Click failed: {str(e)}"}
    
    def _type_text(self, text: Optional[str]) -> Dict:
        """Type text at current cursor position."""
        if not text:
            return {"status": "error", "message": "No text provided"}
        
        try:
            if self.system == "Linux":
                subprocess.run(["xdotool", "type", text], capture_output=True)
            else:
                try:
                    import pyautogui
                    pyautogui.typewrite(text, interval=0.01)
                except ImportError:
                    return {"status": "error", "message": "pyautogui not installed for typing"}
            
            return {"status": "success", "message": f"Typed text: {text[:50]}..." if len(text) > 50 else f"Typed text: {text}"}
        except Exception as e:
            return {"status": "error", "message": f"Typing failed: {str(e)}"}
    
    def _get_app_map(self) -> Dict[str, str]:
        """Get application name to command mapping with OS detection."""
        system = self.system
        
        # Base mappings
        base_map = {
            # Browsers
            "chrome": "google-chrome" if system == "Linux" else "chrome" if system == "Windows" else "Google Chrome",
            "firefox": "firefox",
            "browser": "firefox",
            "edge": "microsoft-edge" if system == "Linux" else "msedge",
            "safari": "safari",
            "brave": "brave-browser" if system == "Linux" else "brave",
            
            # Code Editors
            "code": "code",
            "vscode": "code",
            "visual studio code": "code",
            "sublime": "subl",
            "atom": "atom",
            "vim": "vim",
            "nvim": "nvim",
            "nano": "nano",
            "pycharm": "pycharm",
            "intellij": "idea",
            
            # Terminals
            "terminal": "gnome-terminal" if system == "Linux" else "Terminal" if system == "Darwin" else "cmd",
            "konsole": "konsole",
            "alacritty": "alacritty",
            "kitty": "kitty",
            
            # Media
            "spotify": "spotify",
            "vlc": "vlc",
            "obs": "obs",
            "obs studio": "obs",
            
            # Communication
            "discord": "discord",
            "slack": "slack",
            "telegram": "telegram-desktop" if system == "Linux" else "telegram",
            "whatsapp": "whatsapp",
            
            # Tools - Ubuntu/Linux specific
            "file manager": "nautilus" if system == "Linux" else "Finder" if system == "Darwin" else "explorer",
            "files": "nautilus" if system == "Linux" else "Finder" if system == "Darwin" else "explorer",
            "nautilus": "nautilus",
            "settings": "gnome-control-center" if system == "Linux" else "System Preferences" if system == "Darwin" else "control",
            "system settings": "gnome-control-center" if system == "Linux" else "System Preferences" if system == "Darwin" else "control",
            
            # Calculator - multiple fallbacks for Linux
            "calculator": "gnome-calculator" if system == "Linux" else "Calculator" if system == "Darwin" else "calc",
            "gnome-calculator": "gnome-calculator",
            "xcalc": "xcalc",
            "galculator": "galculator",
            
            # Calendar
            "calendar": "gnome-calendar" if system == "Linux" else "Calendar" if system == "Darwin" else "outlookcal:",
            
            # Productivity
            "notion": "notion",
            "todoist": "todoist",
            "todo": "gnome-todo" if system == "Linux" else "Reminders" if system == "Darwin" else "",
            
            # System tools
            "monitor": "gnome-system-monitor" if system == "Linux" else "Activity Monitor" if system == "Darwin" else "taskmgr",
            "system monitor": "gnome-system-monitor" if system == "Linux" else "Activity Monitor" if system == "Darwin" else "taskmgr",
            "text editor": "gedit" if system == "Linux" else "TextEdit" if system == "Darwin" else "notepad",
            "gedit": "gedit",
        }
        
        return base_map
    
    def get_available_intents(self) -> List[str]:
        """Return list of available action intents."""
        return [
            "open_application", "close_application", "open_url", "search_web",
            "media_control", "volume_control", "system_shortcut", "file_operation",
            "shell_command", "create_folder", "open_file", "search_files",
            "screenshot", "click_screen", "type_text", "lock_screen", "mute_system",
            "get_active_window"
        ]
    
    def get_command_history(self) -> List[Dict]:
        """Return command execution history."""
        return self.command_history


# Utility functions for direct use
def quick_open(app_name: str) -> Dict:
    """Quick helper to open an application."""
    executor = ActionExecutor()
    return executor.execute("open_application", {"app_name": app_name})


def quick_search(query: str, engine: str = "google") -> Dict:
    """Quick helper to search the web."""
    executor = ActionExecutor()
    return executor.execute("search_web", {"query": query, "engine": engine})


def quick_shell(command: str, confirm: bool = True) -> Dict:
    """Quick helper to run shell command."""
    executor = ActionExecutor()
    return executor.execute("shell_command", {"command": command, "requires_confirmation": confirm})
