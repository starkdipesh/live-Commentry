"""
Friday's Emotional Intelligence Module
Mood detection, adaptive personality, and contextual responsiveness.
"""

import time
import re
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field


class Mood(Enum):
    """User mood states."""
    FOCUSED = "focused"  # Deep work, coding
    RELAXED = "relaxed"  # Browsing, casual
    FRUSTRATED = "frustrated"  # Errors, stuck
    EXCITED = "excited"  # Success, celebration
    TIRED = "tired"  # Long session, fatigue
    STRESSED = "stressed"  # High activity, pressure
    NEUTRAL = "neutral"  # Default


class PersonalityMode(Enum):
    """Friday's personality adaptation modes."""
    PROFESSIONAL = "professional"  # Business-like, crisp
    SUPPORTIVE = "supportive"  # Encouraging, helpful
    CASUAL = "casual"  # Relaxed, friendly
    URGENT = "urgent"  # Direct, no fluff
    CELEBRATORY = "celebratory"  # Enthusiastic


@dataclass
class EmotionalState:
    """Current emotional context."""
    mood: Mood = Mood.NEUTRAL
    confidence: float = 1.0  # 0.0 to 1.0
    energy_level: float = 0.5  # 0.0 to 1.0
    stress_level: float = 0.0  # 0.0 to 1.0
    session_duration: float = 0.0  # seconds
    last_mood_change: float = field(default_factory=time.time)
    mood_history: List[Tuple[Mood, float]] = field(default_factory=list)


class EmotionalIntelligence:
    """
    Friday's Emotional Intelligence System.
    Detects user mood and adapts personality accordingly.
    """
    
    def __init__(self):
        """Initialize EmotionalIntelligence."""
        self.state = EmotionalState()
        self.session_start = time.time()
        self.interaction_times: List[float] = []
        self.error_times: List[float] = []
        self.success_times: List[float] = []
        
        # Mood detection patterns
        self.frustration_indicators = [
            "not working", "broken", "stupid", "annoying", "frustrated",
            "can't figure out", "waste of time", "why won't", "ugh", "argh",
            "error again", "still failing", "doesn't work"
        ]
        
        self.excitement_indicators = [
            "awesome", "great", "perfect", "excellent", "amazing",
            "it works", "solved it", "finally", "yes!", "hooray",
            "build successful", "tests passing", "deployed"
        ]
        
        self.tired_indicators = [
            "tired", "exhausted", "sleepy", "long day", "need break",
            "can't focus", "brain fog", "zoning out"
        ]
    
    def analyze_interaction(self, user_input: str, screen_context: str, 
                           success_detected: bool = False, 
                           error_detected: bool = False) -> Mood:
        """
        Analyze user interaction and detect mood.
        
        Args:
            user_input: User's speech or text input
            screen_context: Current screen content
            success_detected: Whether success was detected on screen
            error_detected: Whether error was detected on screen
            
        Returns:
            Detected mood
        """
        now = time.time()
        self.interaction_times.append(now)
        
        # Keep only last 30 minutes
        cutoff = now - 1800
        self.interaction_times = [t for t in self.interaction_times if t > cutoff]
        
        # Update session duration
        self.state.session_duration = now - self.session_start
        
        # Track errors and successes
        if error_detected:
            self.error_times.append(now)
            self.error_times = [t for t in self.error_times if t > cutoff]
        
        if success_detected:
            self.success_times.append(now)
            self.success_times = [t for t in self.success_times if t > cutoff]
        
        # Analyze text for mood indicators
        text_lower = (user_input + " " + screen_context).lower()
        
        # Check frustration
        if any(indicator in text_lower for indicator in self.frustration_indicators):
            return self._update_mood(Mood.FRUSTRATED)
        
        # Check excitement
        if any(indicator in text_lower for indicator in self.excitement_indicators):
            return self._update_mood(Mood.EXCITED)
        
        # Check tired
        if any(indicator in text_lower for indicator in self.tired_indicators):
            return self._update_mood(Mood.TIRED)
        
        # Screen-based detection
        if error_detected and len(self.error_times) > 2:
            return self._update_mood(Mood.FRUSTRATED)
        
        if success_detected and len(self.success_times) > 0:
            return self._update_mood(Mood.EXCITED)
        
        # Activity-based detection
        activity_level = len(self.interaction_times)
        
        if activity_level > 20:  # Very active
            if len(self.error_times) > 1:
                return self._update_mood(Mood.STRESSED)
            else:
                return self._update_mood(Mood.FOCUSED)
        
        # Session duration check
        if self.state.session_duration > 7200:  # 2 hours
            return self._update_mood(Mood.TIRED)
        
        # Default
        return self._update_mood(Mood.NEUTRAL)
    
    def _update_mood(self, new_mood: Mood) -> Mood:
        """Update mood state and track history."""
        now = time.time()
        
        if new_mood != self.state.mood:
            # Record mood change
            self.state.mood_history.append((self.state.mood, now))
            self.state.last_mood_change = now
            self.state.mood = new_mood
        
        # Calculate confidence based on data points
        self.state.confidence = min(1.0, 0.3 + (len(self.interaction_times) / 50))
        
        # Calculate energy (inverse of session duration and tired indicators)
        if self.state.mood == Mood.TIRED:
            self.state.energy_level = max(0.1, 0.5 - (self.state.session_duration / 14400))
        elif self.state.mood == Mood.EXCITED:
            self.state.energy_level = min(1.0, self.state.energy_level + 0.1)
        else:
            self.state.energy_level = 0.5 + (self.state.confidence * 0.3)
        
        # Calculate stress
        recent_errors = len([t for t in self.error_times if t > now - 300])  # Last 5 min
        self.state.stress_level = min(1.0, recent_errors * 0.2)
        
        return new_mood
    
    def get_personality_mode(self) -> PersonalityMode:
        """Get recommended personality mode based on current mood."""
        mood_to_personality = {
            Mood.FOCUSED: PersonalityMode.PROFESSIONAL,
            Mood.RELAXED: PersonalityMode.CASUAL,
            Mood.FRUSTRATED: PersonalityMode.SUPPORTIVE,
            Mood.EXCITED: PersonalityMode.CELEBRATORY,
            Mood.TIRED: PersonalityMode.SUPPORTIVE,
            Mood.STRESSED: PersonalityMode.URGENT,
            Mood.NEUTRAL: PersonalityMode.PROFESSIONAL
        }
        
        return mood_to_personality.get(self.state.mood, PersonalityMode.PROFESSIONAL)
    
    def adapt_response_style(self, base_response: str, mood: Optional[Mood] = None) -> str:
        """
        Adapt a response based on detected mood.
        
        Args:
            base_response: Original response text
            mood: Override mood (uses current state if None)
            
        Returns:
            Adapted response
        """
        mood = mood or self.state.mood
        personality = self.get_personality_mode()
        
        # Add mood-appropriate prefix/suffix
        if personality == PersonalityMode.SUPPORTIVE and mood == Mood.FRUSTRATED:
            prefixes = [
                "Don't worry, Sir. ",
                "We'll get this sorted. ",
                "Let me help you with that. "
            ]
            base_response = prefixes[0] + base_response
            
        elif personality == PersonalityMode.CELEBRATORY and mood == Mood.EXCITED:
            suffixes = [
                " Well done, Sir!",
                " Excellent work!",
                " That's the spirit!"
            ]
            base_response = base_response + suffixes[0]
            
        elif personality == PersonalityMode.URGENT and mood == Mood.STRESSED:
            # Keep it brief
            sentences = base_response.split('. ')
            if len(sentences) > 2:
                base_response = '. '.join(sentences[:2]) + '.'
        
        return base_response
    
    def should_proactively_engage(self) -> Tuple[bool, str]:
        """
        Determine if Friday should proactively engage based on mood.
        
        Returns:
            (should_engage, reason)
        """
        # Don't interrupt focused work
        if self.state.mood == Mood.FOCUSED:
            return False, "User is focused"
        
        # Check for frustration - should offer help
        if self.state.mood == Mood.FRUSTRATED:
            if len(self.error_times) >= 2:
                return True, "User appears frustrated with errors"
        
        # Check for tiredness - suggest break
        if self.state.mood == Mood.TIRED and self.state.session_duration > 3600:
            return True, "User may need a break"
        
        return False, "No proactive engagement needed"
    
    def get_mood_report(self) -> Dict:
        """Get a report of current emotional state."""
        return {
            "current_mood": self.state.mood.value,
            "confidence": round(self.state.confidence, 2),
            "energy_level": round(self.state.energy_level, 2),
            "stress_level": round(self.state.stress_level, 2),
            "session_duration_minutes": int(self.state.session_duration / 60),
            "recommended_mode": self.get_personality_mode().value,
            "should_proactively_engage": self.should_proactively_engage()[0],
            "recent_errors": len(self.error_times),
            "recent_successes": len(self.success_times),
            "interactions_last_30min": len(self.interaction_times),
            "mood_history": [m.value for m, _ in self.state.mood_history[-5:]]
        }
    
    def get_suggestion(self) -> Optional[str]:
        """Get a context-appropriate suggestion based on mood."""
        if self.state.mood == Mood.FRUSTRATED and len(self.error_times) > 2:
            return "Sir, you've hit a few errors. Would you like me to help debug or shall we take a quick break?"
        
        if self.state.mood == Mood.TIRED and self.state.session_duration > 3600:
            return "Sir, you've been working for over an hour. Perhaps a short break would help?"
        
        if self.state.stress_level > 0.6:
            return "Sir, things seem intense. Can I help streamline anything?"
        
        if self.state.mood == Mood.EXCITED:
            return "Great momentum, Sir! What's next on the agenda?"
        
        return None
    
    def reset_session(self):
        """Reset session tracking."""
        self.session_start = time.time()
        self.state = EmotionalState()
        self.interaction_times = []
        self.error_times = []
        self.success_times = []


# Voice tone suggestions based on mood
VOICE_TONE_MAP = {
    Mood.FOCUSED: {"rate": "+0%", "pitch": "+0Hz"},  # Normal
    Mood.RELAXED: {"rate": "-5%", "pitch": "-2Hz"},  # Slower, lower
    Mood.FRUSTRATED: {"rate": "+5%", "pitch": "+0Hz"},  # Slightly faster
    Mood.EXCITED: {"rate": "+10%", "pitch": "+3Hz"},  # Fast, higher
    Mood.TIRED: {"rate": "-8%", "pitch": "-3Hz"},  # Slower, lower, soothing
    Mood.STRESSED: {"rate": "+0%", "pitch": "+0Hz"},  # Normal but crisp
    Mood.NEUTRAL: {"rate": "+0%", "pitch": "+0Hz"}
}


def get_voice_settings_for_mood(mood: Mood) -> Dict[str, str]:
    """Get voice settings for a specific mood."""
    return VOICE_TONE_MAP.get(mood, VOICE_TONE_MAP[Mood.NEUTRAL])
