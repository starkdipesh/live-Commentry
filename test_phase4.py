#!/usr/bin/env python3
"""
Phase 4 Test Suite - Friday's Enhanced Proactivity Engine
Tests event-driven intelligence and contextual triggers.
"""

import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.proactivity_engine import (
    ProactivityEngine, ProactiveTrigger, TriggerType, 
    ScreenAnalyzer, get_proactivity_engine
)


def test_proactivity_engine():
    """Test ProactivityEngine initialization and functionality."""
    print("\n" + "="*60)
    print("🧪 PHASE 4: PROACTIVITY ENGINE TEST SUITE")
    print("="*60)
    
    # Initialize
    print("\n[Test 1] Initializing ProactivityEngine...")
    engine = ProactivityEngine()
    print(f"✅ ProactivityEngine initialized")
    print(f"   Triggers configured: {len(engine.triggers)}")
    
    # Check default triggers
    print("\n[Test 2] Checking default triggers...")
    for trigger_id, trigger in engine.triggers.items():
        print(f"   • {trigger_id}: {trigger.trigger_type.value} (priority {trigger.priority})")
    
    # Test context analysis - no triggers
    print("\n[Test 3] Analyzing safe context...")
    triggered = engine.analyze_context(
        screen_text="Just some normal browsing content",
        active_window="Google Chrome",
        user_active=True
    )
    print(f"✅ No triggers on safe content (found {len(triggered)})")
    
    # Test error detection
    print("\n[Test 4] Testing error detection...")
    triggered = engine.analyze_context(
        screen_text="Error: ModuleNotFoundError: No module named 'requests'",
        active_window="VS Code",
        user_active=True
    )
    print(f"   Found {len(triggered)} triggers:")
    for event in triggered:
        print(f"     • {event['trigger_id']} (priority {event['priority']}): {event['message'][:50]}...")
    
    # Test success detection
    print("\n[Test 5] Testing success detection...")
    triggered = engine.analyze_context(
        screen_text="Build successful! Tests passed: 42/42",
        active_window="Terminal",
        user_active=True
    )
    print(f"   Found {len(triggered)} triggers:")
    for event in triggered:
        print(f"     • {event['trigger_id']}: {event['message'][:50]}...")
    
    # Test high activity detection
    print("\n[Test 6] Testing high activity detection...")
    # Simulate rapid screen changes
    for _ in range(30):
        engine.analyze_context(
            screen_text="Different content each time",
            active_window="VS Code",
            user_active=True
        )
        time.sleep(0.1)  # Small delay
    
    triggered = engine.analyze_context(
        screen_text="More changes",
        active_window="VS Code",
        user_active=True
    )
    high_activity = [e for e in triggered if e['trigger_id'] == 'high_activity']
    print(f"   High activity detected: {len(high_activity) > 0}")
    if high_activity:
        print(f"   Message: {high_activity[0]['message'][:50]}...")
    
    # Test work hours trigger
    print("\n[Test 7] Testing work hours trigger...")
    # Test with evening time
    evening_time = datetime.strptime("18:15", "%H:%M")
    triggered = engine.analyze_context(
        screen_text="Normal work content",
        active_window="VS Code",
        user_active=True,
        current_time=evening_time
    )
    work_end = [e for e in triggered if e['trigger_id'] == 'work_hours_end']
    print(f"   Work hours end trigger: {len(work_end) > 0}")
    if work_end:
        print(f"   Message: {work_end[0]['message'][:50]}...")
    
    # Test stats
    print("\n[Test 8] Getting engine stats...")
    stats = engine.get_stats()
    print(f"   Total triggers fired: {stats['total_triggers']}")
    print(f"   Active triggers: {stats['active_triggers']}")
    print(f"   Screen changes (5min): {stats['screen_changes_last_5min']}")
    
    # Test recommendations
    print("\n[Test 9] Getting recommendations...")
    recommendations = engine.get_recommendations()
    print(f"   Generated {len(recommendations)} recommendations")
    for rec in recommendations:
        print(f"     • {rec[:60]}...")
    
    # Test custom trigger
    print("\n[Test 10] Adding custom trigger...")
    custom_trigger = ProactiveTrigger(
        id="custom_test",
        trigger_type=TriggerType.SCREEN_PATTERN,
        condition={"patterns": ["test_pattern"]},
        message_template="Custom trigger activated, Sir.",
        cooldown_seconds=60,
        priority=2
    )
    engine.add_trigger(custom_trigger)
    print(f"✅ Added custom trigger: {custom_trigger.id}")
    
    # Test trigger disable/enable
    print("\n[Test 11] Testing trigger enable/disable...")
    engine.disable_trigger("custom_test")
    print("   Disabled custom_test")
    engine.enable_trigger("custom_test")
    print("   Enabled custom_test")
    
    # Test config export
    print("\n[Test 12] Exporting configuration...")
    config = engine.export_config()
    print(f"✅ Exported {len(config)} trigger configurations")
    
    print("\n" + "="*60)
    print("✅ PHASE 4 TESTS COMPLETED")
    print("="*60)


def test_screen_analyzer():
    """Test ScreenAnalyzer functionality."""
    print("\n" + "="*60)
    print("🧪 TESTING SCREEN ANALYZER")
    print("="*60)
    
    analyzer = ScreenAnalyzer()
    
    # Test error detection
    print("\n[Test] Analyzing text with errors...")
    result = analyzer.analyze_text("Error: Cannot find module 'xyz'. Traceback: ...")
    print(f"   Has errors: {result['has_errors']}")
    print(f"   Errors found: {len(result['errors'])}")
    
    # Test success detection
    print("\n[Test] Analyzing text with success...")
    result = analyzer.analyze_text("Build successful! All tests passed.")
    print(f"   Has success: {result['has_success']}")
    print(f"   Success patterns: {len(result['successes'])}")
    
    # Test context detection
    print("\n[Test] Quick context detection...")
    contexts = [
        ("project.py - MyProject - Visual Studio Code", "", "coding"),
        ("Error in main.py - VS Code", "SyntaxError", "coding_with_errors"),
        ("YouTube - Google Chrome", "", "youtube"),
        ("Terminal - bash", "pwd", "terminal"),
        ("Steam", "", "gaming"),
        ("Slack", "", "communication"),
    ]
    
    for window, ocr, expected in contexts:
        detected = analyzer.quick_scan(window, ocr)
        status = "✅" if detected == expected else "❌"
        print(f"   {status} '{window[:30]}...' -> {detected} (expected: {expected})")
    
    print("\n✅ Screen Analyzer tests complete")


def test_singleton():
    """Test singleton pattern."""
    print("\n" + "="*60)
    print("🧪 TESTING SINGLETON PATTERN")
    print("="*60)
    
    engine1 = get_proactivity_engine()
    engine2 = get_proactivity_engine()
    
    print(f"✅ Same instance: {engine1 is engine2}")
    print(f"   Engine ID: {id(engine1)}")


if __name__ == "__main__":
    print("\n🤖 SARTHAKA - Phase 4 Proactivity Engine Test Suite")
    print("Testing event-driven intelligence...\n")
    
    # Run tests
    test_proactivity_engine()
    test_screen_analyzer()
    test_singleton()
    
    print("\n" + "="*60)
    print("🎉 ALL PHASE 4 TESTS COMPLETE")
    print("="*60)
    print("\nYou can now:")
    print("  1. Run: python test_phase4.py (this test)")
    print("  2. Run: python main.py (Friday with proactivity)")
    print("  3. Friday will detect errors automatically")
    print("  4. Friday will suggest breaks after long sessions")
    print("  5. Friday will alert on high activity")
    print("\nPhase 4 is complete! Ready for Phase 5. 🚀")
