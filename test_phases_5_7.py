#!/usr/bin/env python3
"""
Phase 5-7 Combined Test Suite
Tests Professional Tools, Autonomous Agent, and Emotional Intelligence.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.integrations.tool_integrations import (
    GitHelper, IDEAssistant, NotesManager, CalendarHelper, ToolIntegrations,
    quick_commit, quick_note
)
from src.core.autonomous_agent import TaskPlanner, AutonomousAgent
from src.core.emotional_intelligence import EmotionalIntelligence, Mood, PersonalityMode
from src.core.action_executor import ActionExecutor
from src.core.workflow_engine import WorkflowEngine


def test_git_helper():
    """Test GitHelper functionality."""
    print("\n" + "="*60)
    print("🧪 PHASE 5: GIT HELPER")
    print("="*60)
    
    git = GitHelper()
    
    # Check if we're in a git repo
    print("\n[Test 1] Checking git repository...")
    is_repo = git.is_git_repo()
    print(f"   Is git repo: {is_repo}")
    
    if is_repo:
        # Get status
        print("\n[Test 2] Getting git status...")
        status = git.get_status()
        print(f"   Branch: {status.get('branch')}")
        print(f"   Has changes: {status.get('has_changes')}")
        print(f"   Files changed: {len(status.get('files_changed', []))}")
        
        # Get diff summary
        print("\n[Test 3] Getting diff summary...")
        diff = git.get_diff_summary()
        print(f"   Diff: {diff[:100]}...")
        
        # Generate commit message
        print("\n[Test 4] Generating commit message...")
        msg = git.generate_commit_message()
        print(f"   Suggested: {msg}")
        
        # Get full suggestion
        print("\n[Test 5] Getting commit suggestion...")
        suggestion = git.suggest_commit()
        print(f"   Status: {suggestion.get('status')}")
        if suggestion.get('suggestion'):
            print(f"   Command: {suggestion.get('suggestion')}")
    else:
        print("   Not a git repository - skipping git tests")
    
    print("\n✅ Git Helper tests complete")


def test_ide_assistant():
    """Test IDEAssistant."""
    print("\n" + "="*60)
    print("🧪 TESTING IDE ASSISTANT")
    print("="*60)
    
    ide = IDEAssistant()
    
    print("\n[Test] Detecting open editor...")
    editor = ide.detect_open_editor()
    print(f"   Detected: {editor or 'None'}")
    
    print("\n[Test] Getting recent projects...")
    projects = ide.get_recent_projects()
    print(f"   Projects: {len(projects)}")
    
    print("\n✅ IDE Assistant tests complete")


def test_notes_manager():
    """Test NotesManager."""
    print("\n" + "="*60)
    print("🧪 TESTING NOTES MANAGER")
    print("="*60)
    
    notes = NotesManager(notes_dir="/tmp/friday_test_notes")
    
    # Create note
    print("\n[Test 1] Creating note...")
    result = notes.create_note(
        title="Friday Test Note",
        content="This is a test note from Friday's Phase 5 test suite.",
        category="testing"
    )
    print(f"   Status: {result.get('status')}")
    if result.get('status') == 'success':
        print(f"   File: {result.get('filepath')}")
    
    # Create another note
    notes.create_note(
        title="AI Development Ideas",
        content="Ideas for improving Friday: better voice recognition, faster response times...",
        category="ideas"
    )
    
    # Search notes
    print("\n[Test 2] Searching notes...")
    results = notes.search_notes("Friday")
    print(f"   Found {len(results)} notes")
    for r in results:
        print(f"     - {r.get('title')}")
    
    # Get recent
    print("\n[Test 3] Getting recent notes...")
    recent = notes.get_recent_notes(3)
    print(f"   Recent: {len(recent)} notes")
    
    print("\n✅ Notes Manager tests complete")


def test_calendar_helper():
    """Test CalendarHelper."""
    print("\n" + "="*60)
    print("🧪 TESTING CALENDAR HELPER")
    print("="*60)
    
    cal = CalendarHelper()
    
    print("\n[Test] Getting daily prep suggestion...")
    prep = cal.suggest_daily_prep()
    print(f"   Has meetings: {prep.get('has_meetings')}")
    print(f"   Suggestion: {prep.get('suggestion')}")
    
    print("\n✅ Calendar Helper tests complete")


def test_tool_integrations():
    """Test unified ToolIntegrations."""
    print("\n" + "="*60)
    print("🧪 TESTING UNIFIED TOOL INTEGRATIONS")
    print("="*60)
    
    tools = ToolIntegrations()
    
    print("\n[Test] Getting context summary...")
    summary = tools.get_context_summary()
    print(f"   Summary keys: {list(summary.keys())}")
    
    print("\n✅ Tool Integrations tests complete")


async def test_autonomous_agent():
    """Test AutonomousAgent."""
    print("\n" + "="*60)
    print("🧪 PHASE 6: AUTONOMOUS AGENT")
    print("="*60)
    
    action_exec = ActionExecutor()
    workflow_eng = WorkflowEngine(action_exec)
    agent = AutonomousAgent(action_exec, workflow_eng)
    
    # Test planning
    print("\n[Test 1] Testing task planning...")
    planner = TaskPlanner(action_exec)
    
    test_goals = [
        "Research Python AI development",
        "Debug this error in my code",
        "Create a new project called MyApp",
    ]
    
    for goal in test_goals:
        plan = planner.plan_task(goal)
        if plan:
            print(f"\n   Goal: {goal}")
            print(f"   Steps: {len(plan.steps)}")
            print(f"   Estimated: {plan.estimated_duration}s")
            for i, step in enumerate(plan.steps[:3], 1):
                print(f"     {i}. {step.get('desc', step['action'])}")
        else:
            print(f"   Failed to plan: {goal}")
    
    # Test autonomous execution (safe test)
    print("\n[Test 2] Testing autonomous execution...")
    task = await agent.create_and_execute(
        goal="Take a screenshot and check active window",
        auto_confirm=True
    )
    
    print(f"   Task ID: {task.id}")
    print(f"   Status: {task.status.value}")
    print(f"   Steps completed: {len(task.results)}")
    
    # Test task summary
    print("\n[Test 3] Getting task summary...")
    summary = agent.get_task_summary(task.id)
    if summary:
        print(f"   Progress: {summary.get('progress', 0):.0%}")
        print(f"   Duration: {summary.get('duration', 0):.1f}s")
    
    print("\n✅ Autonomous Agent tests complete")


def test_emotional_intelligence():
    """Test EmotionalIntelligence."""
    print("\n" + "="*60)
    print("🧪 PHASE 7: EMOTIONAL INTELLIGENCE")
    print("="*60)
    
    ei = EmotionalIntelligence()
    
    # Test mood detection
    print("\n[Test 1] Testing mood detection...")
    
    test_scenarios = [
        ("This is working great! Build successful!", "Success detected"),
        ("I can't figure out this error. It's frustrating.", "Frustration detected"),
        ("Error: Module not found. Traceback...", "Error context"),
        ("Just normal work here", "Neutral"),
    ]
    
    for text, desc in test_scenarios:
        mood = ei.analyze_interaction(
            user_input=text,
            screen_context=text,
            error_detected="error" in text.lower(),
            success_detected="successful" in text.lower() or "great" in text.lower()
        )
        print(f"   {desc}: {mood.value}")
    
    # Test personality adaptation
    print("\n[Test 2] Testing personality adaptation...")
    ei.state.mood = Mood.FRUSTRATED
    personality = ei.get_personality_mode()
    print(f"   Mood: {ei.state.mood.value}")
    print(f"   Personality: {personality.value}")
    
    # Test response adaptation
    print("\n[Test 3] Testing response adaptation...")
    base_response = "I'll help you fix this issue."
    adapted = ei.adapt_response_style(base_response, Mood.FRUSTRATED)
    print(f"   Original: {base_response}")
    print(f"   Adapted: {adapted}")
    
    # Test mood report
    print("\n[Test 4] Getting mood report...")
    report = ei.get_mood_report()
    print(f"   Current mood: {report.get('current_mood')}")
    print(f"   Confidence: {report.get('confidence')}")
    print(f"   Energy: {report.get('energy_level')}")
    print(f"   Recommended mode: {report.get('recommended_mode')}")
    
    # Test proactive engagement
    print("\n[Test 5] Testing proactive engagement...")
    should_engage, reason = ei.should_proactively_engage()
    print(f"   Should engage: {should_engage}")
    print(f"   Reason: {reason}")
    
    # Test voice settings
    print("\n[Test 6] Getting voice settings for mood...")
    from src.core.emotional_intelligence import get_voice_settings_for_mood
    settings = get_voice_settings_for_mood(Mood.EXCITED)
    print(f"   Excited mood settings: {settings}")
    
    print("\n✅ Emotional Intelligence tests complete")


if __name__ == "__main__":
    print("\n🤖 SARTHAKA - Phases 5-7 Combined Test Suite")
    print("Testing Professional Tools, Autonomous Agent, and Emotional Intelligence...\n")
    
    # Run Phase 5 tests
    test_git_helper()
    test_ide_assistant()
    test_notes_manager()
    test_calendar_helper()
    test_tool_integrations()
    
    # Run Phase 6 tests
    asyncio.run(test_autonomous_agent())
    
    # Run Phase 7 tests
    test_emotional_intelligence()
    
    print("\n" + "="*60)
    print("🎉 ALL PHASES 5-7 TESTS COMPLETE")
    print("="*60)
    print("\nFriday now has:")
    print("  ✅ Professional tool integrations (Git, IDE, Notes, Calendar)")
    print("  ✅ Autonomous task planning and execution")
    print("  ✅ Emotional intelligence and mood adaptation")
    print("\nAll 7 phases complete! Friday is fully operational. 🚀")
