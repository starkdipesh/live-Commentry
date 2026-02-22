"""
Friday's Enhanced Proactivity Engine
Event-driven intelligence that triggers based on screen content, time, and patterns.
Moves beyond timer-based proactivity to true contextual awareness.
"""

import time
import re
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta


class TriggerType(Enum):
    ERROR_DETECTED = "error_detected"
    SUCCESS_DETECTED = "success_detected"
    SCREEN_PATTERN = "screen_pattern"
    TIME_BASED = "time_based"
    INACTIVITY = "inactivity"
    HIGH_ACTIVITY = "high_activity"
    MEETING_SOON = "meeting_soon"
    WORK_HOURS_END = "work_hours_end"
    BREAK_REMINDER = "break_reminder"
    PROJECT_SWITCH = "project_switch"


@dataclass
class ProactiveTrigger:
    """A proactive trigger definition."""
    id: str
    trigger_type: TriggerType
    condition: Dict[str, Any]
    message_template: str
    cooldown_seconds: int = 300  # 5 minutes default
    priority: int = 1  # 1=low, 2=medium, 3=high, 4=critical
    enabled: bool = True
    last_triggered: Optional[float] = None
    trigger_count: int = 0


class ProactivityEngine:
    """
    Friday's Enhanced Proactivity Engine.
    Monitors context and triggers intelligent interventions.
    """
    
    def __init__(self):
        """Initialize the ProactivityEngine."""
        self.triggers: Dict[str, ProactiveTrigger] = {}
        self.trigger_history: List[Dict] = []
        self.on_trigger_callback: Optional[Callable[[str, str, int], None]] = None
        
        # State tracking
        self.last_screen_text: str = ""
        self.last_active_window: str = ""
        self.last_interaction_time: float = time.time()
        self.interaction_count: int = 0
        self.screen_change_times: List[float] = []
        self.error_detected_time: Optional[float] = None
        
        # Initialize default triggers
        self._init_default_triggers()
    
    def _init_default_triggers(self):
        """Initialize default proactive triggers."""
        defaults = [
            # Error detection - high priority
            ProactiveTrigger(
                id="error_detected",
                trigger_type=TriggerType.ERROR_DETECTED,
                condition={"patterns": ["error", "exception", "traceback", "failed", "crash"]},
                message_template="Sir, I've detected an error on screen. Would you like me to help debug it?",
                cooldown_seconds=60,
                priority=4
            ),
            
            # Build success
            ProactiveTrigger(
                id="build_success",
                trigger_type=TriggerType.SUCCESS_DETECTED,
                condition={"patterns": ["build successful", "tests passed", "deployed", "completed"]},
                message_template="Build successful, Sir. Well done.",
                cooldown_seconds=300,
                priority=2
            ),
            
            # Long coding session - break reminder
            ProactiveTrigger(
                id="break_reminder",
                trigger_type=TriggerType.BREAK_REMINDER,
                condition={"inactivity_threshold": 1800, "active_window_contains": ["code", "Code", "vim", "nvim"]},
                message_template="Sir, you've been coding for 30 minutes. Consider a brief break.",
                cooldown_seconds=1800,
                priority=1
            ),
            
            # Work hours ending
            ProactiveTrigger(
                id="work_hours_end",
                trigger_type=TriggerType.WORK_HOURS_END,
                condition={"time_ranges": [("18:00", "18:30"), ("17:30", "18:00")]},
                message_template="Sir, it's getting late. Shall I help you wrap up for the day?",
                cooldown_seconds=3600,
                priority=1
            ),
            
            # Meeting soon (would integrate with calendar)
            ProactiveTrigger(
                id="meeting_soon",
                trigger_type=TriggerType.MEETING_SOON,
                condition={"minutes_before": 10},
                message_template="Sir, you have a meeting in 10 minutes. Shall I open the conference link?",
                cooldown_seconds=1800,
                priority=3
            ),
            
            # Project context switch
            ProactiveTrigger(
                id="project_switch",
                trigger_type=TriggerType.PROJECT_SWITCH,
                condition={"track_window_changes": True},
                message_template="I see you've switched to a different project, Sir. Would you like me to load relevant context?",
                cooldown_seconds=600,
                priority=2
            ),
            
            # High activity detection
            ProactiveTrigger(
                id="high_activity",
                trigger_type=TriggerType.HIGH_ACTIVITY,
                condition={"screen_changes_per_minute": 20},
                message_template="Sir, you seem quite busy. Let me know if I can assist with anything.",
                cooldown_seconds=900,
                priority=1
            ),
        ]
        
        for trigger in defaults:
            self.triggers[trigger.id] = trigger
    
    def register_trigger_callback(self, callback: Callable[[str, str, int], None]):
        """
        Register callback for trigger activation.
        
        Args:
            callback: Function receiving (trigger_id, message, priority)
        """
        self.on_trigger_callback = callback
    
    def add_trigger(self, trigger: ProactiveTrigger):
        """Add a custom trigger."""
        self.triggers[trigger.id] = trigger
    
    def enable_trigger(self, trigger_id: str):
        """Enable a trigger."""
        if trigger_id in self.triggers:
            self.triggers[trigger_id].enabled = True
    
    def disable_trigger(self, trigger_id: str):
        """Disable a trigger."""
        if trigger_id in self.triggers:
            self.triggers[trigger_id].enabled = False
    
    def analyze_context(self, screen_text: str, active_window: str, 
                       user_active: bool, current_time: Optional[datetime] = None) -> List[Dict]:
        """
        Analyze current context and return triggered events.
        
        Args:
            screen_text: OCR or extracted text from screen
            active_window: Current active window title
            user_active: Whether user has been recently active
            current_time: Optional current datetime
            
        Returns:
            List of triggered events with messages and priorities
        """
        current_time = current_time or datetime.now()
        now = time.time()
        triggered = []
        
        # Update state
        self._update_state(screen_text, active_window, now, user_active)
        
        # Check each trigger
        for trigger in self.triggers.values():
            if not trigger.enabled:
                continue
            
            # Check cooldown
            if trigger.last_triggered and (now - trigger.last_triggered) < trigger.cooldown_seconds:
                continue
            
            # Evaluate trigger condition
            if self._evaluate_trigger(trigger, screen_text, active_window, current_time, user_active):
                # Trigger!
                trigger.last_triggered = now
                trigger.trigger_count += 1
                
                event = {
                    "trigger_id": trigger.id,
                    "type": trigger.trigger_type.value,
                    "message": trigger.message_template,
                    "priority": trigger.priority,
                    "timestamp": now
                }
                
                triggered.append(event)
                self.trigger_history.append(event)
                
                # Notify callback
                if self.on_trigger_callback:
                    self.on_trigger_callback(trigger.id, trigger.message_template, trigger.priority)
        
        # Keep only last 100 triggers in history
        if len(self.trigger_history) > 100:
            self.trigger_history = self.trigger_history[-100:]
        
        return triggered
    
    def _update_state(self, screen_text: str, active_window: str, now: float, user_active: bool):
        """Update internal state tracking."""
        # Track screen changes
        if screen_text != self.last_screen_text:
            self.screen_change_times.append(now)
            self.last_screen_text = screen_text
        
        # Keep only last 5 minutes of changes
        cutoff = now - 300
        self.screen_change_times = [t for t in self.screen_change_times if t > cutoff]
        
        # Track project/window changes
        if active_window != self.last_active_window:
            self.last_active_window = active_window
        
        # Track user activity
        if user_active:
            self.last_interaction_time = now
            self.interaction_count += 1
    
    def _evaluate_trigger(self, trigger: ProactiveTrigger, screen_text: str,
                         active_window: str, current_time: datetime, user_active: bool) -> bool:
        """Evaluate if a trigger condition is met."""
        condition = trigger.condition
        
        if trigger.trigger_type == TriggerType.ERROR_DETECTED:
            return self._check_patterns(screen_text, condition.get("patterns", []))
        
        elif trigger.trigger_type == TriggerType.SUCCESS_DETECTED:
            return self._check_patterns(screen_text, condition.get("patterns", []))
        
        elif trigger.trigger_type == TriggerType.BREAK_REMINDER:
            inactive_time = time.time() - self.last_interaction_time
            if inactive_time > condition.get("inactivity_threshold", 1800):
                for pattern in condition.get("active_window_contains", []):
                    if pattern in active_window:
                        return True
            return False
        
        elif trigger.trigger_type == TriggerType.WORK_HOURS_END:
            return self._check_time_ranges(current_time, condition.get("time_ranges", []))
        
        elif trigger.trigger_type == TriggerType.HIGH_ACTIVITY:
            changes_per_minute = len(self.screen_change_times) / 5  # 5 minute window
            return changes_per_minute > condition.get("screen_changes_per_minute", 20)
        
        elif trigger.trigger_type == TriggerType.MEETING_SOON:
            # Would integrate with calendar API
            return False  # Placeholder
        
        elif trigger.trigger_type == TriggerType.PROJECT_SWITCH:
            # Detected in state update, but message should be contextual
            # This would need more sophisticated logic
            return False  # Placeholder
        
        return False
    
    def _check_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if any pattern exists in text."""
        text_lower = text.lower()
        return any(pattern.lower() in text_lower for pattern in patterns)
    
    def _check_time_ranges(self, current_time: datetime, time_ranges: List[tuple]) -> bool:
        """Check if current time falls within any time range."""
        current_str = current_time.strftime("%H:%M")
        current_minutes = self._time_to_minutes(current_str)
        
        for start, end in time_ranges:
            start_minutes = self._time_to_minutes(start)
            end_minutes = self._time_to_minutes(end)
            
            if start_minutes <= current_minutes <= end_minutes:
                return True
        
        return False
    
    def _time_to_minutes(self, time_str: str) -> int:
        """Convert HH:MM to minutes since midnight."""
        hour, minute = map(int, time_str.split(":"))
        return hour * 60 + minute
    
    def get_stats(self) -> Dict:
        """Get proactivity engine statistics."""
        now = time.time()
        
        return {
            "total_triggers": len(self.trigger_history),
            "active_triggers": sum(1 for t in self.triggers.values() if t.enabled),
            "trigger_counts": {
                trigger_id: trigger.trigger_count
                for trigger_id, trigger in self.triggers.items()
            },
            "recent_triggers": [
                {
                    "id": t["trigger_id"],
                    "type": t["type"],
                    "priority": t["priority"],
                    "ago_seconds": int(now - t["timestamp"])
                }
                for t in self.trigger_history[-10:]
            ],
            "screen_changes_last_5min": len(self.screen_change_times),
            "time_since_last_interaction": int(now - self.last_interaction_time)
        }
    
    def get_recommendations(self) -> List[str]:
        """Get proactive recommendations based on context."""
        recommendations = []
        
        # High activity recommendation
        if len(self.screen_change_times) > 50:
            recommendations.append("You're very active. Consider batching similar tasks.")
        
        # Error pattern recommendation
        error_triggers = [t for t in self.trigger_history if t["type"] == "error_detected"]
        if len(error_triggers) > 3:
            recommendations.append("Multiple errors detected recently. Consider taking a debugging break.")
        
        # Inactivity recommendation
        inactive_time = time.time() - self.last_interaction_time
        if inactive_time > 3600:
            recommendations.append("You've been away for over an hour. Welcome back!")
        elif inactive_time > 600:
            recommendations.append("You've been inactive for 10 minutes. Need help getting back on track?")
        
        return recommendations
    
    def reset_trigger(self, trigger_id: str):
        """Reset a trigger's last_triggered time."""
        if trigger_id in self.triggers:
            self.triggers[trigger_id].last_triggered = None
    
    def export_config(self) -> Dict:
        """Export trigger configuration."""
        return {
            trigger_id: {
                "type": trigger.trigger_type.value,
                "enabled": trigger.enabled,
                "cooldown": trigger.cooldown_seconds,
                "priority": trigger.priority,
                "trigger_count": trigger.trigger_count
            }
            for trigger_id, trigger in self.triggers.items()
        }


class ScreenAnalyzer:
    """
    Helper class for analyzing screen content for patterns.
    Can use OCR or window title analysis.
    """
    
    def __init__(self):
        """Initialize ScreenAnalyzer."""
        self.error_patterns = [
            r"error[:\s]",
            r"exception[:\s]",
            r"traceback",
            r"failed[:\s]",
            r"failure[:\s]",
            r"crash[:\s]",
            r"cannot find",
            r"not found",
            r"permission denied",
            r"access denied",
            r"404",
            r"500",
            r"syntax error",
            r"runtime error",
        ]
        
        self.success_patterns = [
            r"success[:\s]",
            r"completed[:\s]",
            r"finished[:\s]",
            r"done[:\s]",
            r"build successful",
            r"tests passed",
            r"deployed successfully",
            r"saved successfully",
        ]
    
    def analyze_text(self, text: str) -> Dict:
        """
        Analyze text for error/success patterns.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with detected patterns
        """
        text_lower = text.lower()
        
        errors_found = []
        for pattern in self.error_patterns:
            if re.search(pattern, text_lower):
                errors_found.append(pattern)
        
        successes_found = []
        for pattern in self.success_patterns:
            if re.search(pattern, text_lower):
                successes_found.append(pattern)
        
        return {
            "has_errors": len(errors_found) > 0,
            "errors": errors_found,
            "has_success": len(successes_found) > 0,
            "successes": successes_found,
            "length": len(text),
            "word_count": len(text.split())
        }
    
    def quick_scan(self, window_title: str, ocr_text: str = "") -> str:
        """
        Quick scan to determine screen context type.
        
        Returns:
            Context type string
        """
        combined = f"{window_title} {ocr_text}".lower()
        
        # IDE detection
        ide_patterns = ["code", "jetbrains", "pycharm", "intellij", "eclipse", "sublime", "atom"]
        if any(pattern in combined for pattern in ide_patterns):
            if any(err in combined for err in ["error", "exception", "failed"]):
                return "coding_with_errors"
            return "coding"
        
        # Browser patterns
        if "chrome" in combined or "firefox" in combined or "browser" in combined:
            if "youtube" in combined:
                return "youtube"
            if any(err in combined for err in ["404", "error", "failed"]):
                return "browser_error"
            return "browsing"
        
        # Terminal patterns
        if "terminal" in combined or "bash" in combined or "zsh" in combined or "cmd" in combined:
            return "terminal"
        
        # Gaming patterns
        game_patterns = ["steam", "game", "unity", "unreal"]
        if any(pattern in combined for pattern in game_patterns):
            return "gaming"
        
        # Communication
        comm_patterns = ["slack", "discord", "telegram", "whatsapp"]
        if any(pattern in combined for pattern in comm_patterns):
            return "communication"
        
        return "general"


# Singleton instance for easy access
_proactivity_engine: Optional[ProactivityEngine] = None


def get_proactivity_engine() -> ProactivityEngine:
    """Get or create singleton ProactivityEngine instance."""
    global _proactivity_engine
    if _proactivity_engine is None:
        _proactivity_engine = ProactivityEngine()
    return _proactivity_engine
