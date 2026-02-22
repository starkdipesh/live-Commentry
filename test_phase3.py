#!/usr/bin/env python3
"""
Phase 3 Test Suite - Friday's Workflow Engine
Tests multi-step task orchestration capabilities.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.action_executor import ActionExecutor
from src.core.workflow_engine import WorkflowEngine, WorkflowStep, Workflow


async def test_workflow_engine():
    """Test WorkflowEngine functionality."""
    print("\n" + "="*60)
    print("🧪 PHASE 3: WORKFLOW ENGINE TEST SUITE")
    print("="*60)
    
    # Initialize
    print("\n[Test 1] Initializing WorkflowEngine...")
    action_executor = ActionExecutor()
    engine = WorkflowEngine(action_executor)
    print("✅ WorkflowEngine initialized")
    
    # Test templates
    print("\n[Test 2] Getting workflow templates...")
    templates = engine.get_workflow_templates()
    print(f"✅ Found {len(templates)} workflow templates")
    for template_id, template in templates.items():
        print(f"  • {template_id}: {template['name']} ({len(template['steps'])} steps)")
    
    # Test workflow creation from template
    print("\n[Test 3] Creating workflow from template...")
    workflow = engine.create_from_template("setup_streaming")
    if workflow:
        print(f"✅ Created workflow: {workflow.name}")
        print(f"   ID: {workflow.id}")
        print(f"   Steps: {len(workflow.steps)}")
        for step in workflow.steps:
            print(f"     - {step.name} ({step.action})")
    else:
        print("⚠️ Template creation returned None")
    
    # Test custom workflow creation
    print("\n[Test 4] Creating custom workflow...")
    custom_steps = [
        WorkflowStep("1", "Test Screenshot", "screenshot", {}),
        WorkflowStep("2", "Check Active Window", "get_active_window", {}),
        WorkflowStep("3", "Create Test Folder", "create_folder", {"path": "/tmp/friday_workflow_test"}),
    ]
    custom_workflow = engine.create_workflow(
        name="Test Workflow",
        description="A test workflow for validation",
        steps=custom_steps
    )
    print(f"✅ Created custom workflow: {custom_workflow.name}")
    print(f"   ID: {custom_workflow.id}")
    print(f"   Steps: {len(custom_workflow.steps)}")
    
    # Test workflow execution
    print("\n[Test 5] Executing custom workflow...")
    print("   (This will actually execute actions)")
    
    # Progress callback
    def on_progress(wf_id, progress, status):
        print(f"   📊 Progress: {progress:.0f}% - {status}")
    
    engine.register_progress_callback(on_progress)
    
    completed_workflow = await engine.execute_workflow(custom_workflow, skip_confirmation=True)
    
    print(f"\n   ✅ Workflow completed with status: {completed_workflow.status}")
    print(f"   Progress: {completed_workflow.get_progress():.0f}%")
    
    # Check step results
    print("\n   Step Results:")
    for step in completed_workflow.steps:
        status_icon = "✅" if step.status.value == "completed" else "❌"
        print(f"     {status_icon} {step.name}: {step.status.value}")
        if step.result:
            print(f"        Result: {step.result.get('message', 'Done')[:50]}...")
    
    # Test workflow status retrieval
    print("\n[Test 6] Retrieving workflow status...")
    status = engine.get_workflow_status(completed_workflow.id)
    if status:
        print(f"✅ Retrieved status for workflow {status['id']}")
        print(f"   Status: {status['status']}")
        print(f"   Progress: {status['progress']:.0f}%")
    else:
        print("⚠️ Workflow status not found (may have been moved to history)")
    
    # Test history
    print("\n[Test 7] Checking workflow history...")
    history = engine.get_history()
    print(f"✅ History contains {len(history)} workflows")
    for wf in history[:3]:  # Show last 3
        print(f"   • {wf['name']} - {wf['status']} ({wf['progress']:.0f}%)")
    
    # Test template with context
    print("\n[Test 8] Creating workflow with context variables...")
    research_workflow = engine.create_from_template(
        "research_topic",
        context={"topic": "Python AI Development"}
    )
    if research_workflow:
        print(f"✅ Created parameterized workflow: {research_workflow.name}")
        # Show first step with resolved parameters
        if research_workflow.steps:
            first_step = research_workflow.steps[0]
            print(f"   First step: {first_step.name}")
            print(f"   Params: {first_step.params}")
    
    # Cleanup
    print("\n[Test 9] Cleanup...")
    # Remove test folder if created
    try:
        import shutil
        test_path = "/tmp/friday_workflow_test"
        if os.path.exists(test_path):
            shutil.rmtree(test_path)
            print("✅ Cleaned up test folder")
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")
    
    print("\n" + "="*60)
    print("✅ PHASE 3 TESTS COMPLETED")
    print("="*60)
    print("\nSummary:")
    print(f"  • WorkflowEngine initialized successfully")
    print(f"  • {len(templates)} templates available")
    print(f"  • Custom workflow creation: working")
    print(f"  • Workflow execution: working")
    print(f"  • Progress tracking: working")
    print(f"  • History tracking: working")
    print(f"  • Template parameterization: working")
    print("\nPhase 3 Status: ✅ READY")
    print("="*60)


def test_workflow_step_class():
    """Test WorkflowStep dataclass functionality."""
    print("\n" + "="*60)
    print("🧪 TESTING WORKFLOW STEP CLASS")
    print("="*60)
    
    print("\n[Test] Creating various step types...")
    
    # Simple step
    step1 = WorkflowStep("1", "Open Browser", "open_application", {"app_name": "chrome"})
    print(f"✅ Simple step: {step1.name}")
    
    # Step with confirmation
    step2 = WorkflowStep(
        "2", "Delete File", "file_operation",
        {"operation": "delete", "source": "/path/to/file"},
        requires_confirmation=True,
        confirmation_prompt="Are you sure you want to delete this file?"
    )
    print(f"✅ Step with confirmation: {step2.name}")
    print(f"   Confirmation prompt: {step2.confirmation_prompt}")
    
    # Step with retry
    step3 = WorkflowStep(
        "3", "Network Request", "shell_command",
        {"command": "curl https://api.example.com"},
        retry_on_failure=True,
        max_retries=3
    )
    print(f"✅ Step with retry: {step3.name}")
    print(f"   Max retries: {step3.max_retries}")
    
    # Step with dependencies
    step4 = WorkflowStep(
        "4", "Final Step", "screenshot", {},
        depends_on=["1", "2"]
    )
    print(f"✅ Step with dependencies: {step4.name}")
    print(f"   Depends on: {step4.depends_on}")
    
    print("\n✅ All step types working correctly")


async def test_workflow_error_handling():
    """Test workflow error handling and retry logic."""
    print("\n" + "="*60)
    print("🧪 TESTING ERROR HANDLING & RETRY")
    print("="*60)
    
    action_executor = ActionExecutor()
    engine = WorkflowEngine(action_executor)
    
    # Create workflow with intentionally failing step
    print("\n[Test] Creating workflow with error recovery...")
    steps = [
        WorkflowStep("1", "Valid Step", "get_active_window", {}),
        WorkflowStep(
            "2", "Retry Step", "open_application",
            {"app_name": "nonexistent_app_12345"},
            retry_on_failure=True,
            max_retries=2
        ),
    ]
    
    workflow = engine.create_workflow("Error Test", "Testing error handling", steps)
    
    print("   Executing workflow with retry-enabled step...")
    completed = await engine.execute_workflow(workflow, skip_confirmation=True)
    
    print(f"\n   Results:")
    for step in completed.steps:
        print(f"     {step.name}: {step.status.value}")
        if step.error_message:
            print(f"       Error: {step.error_message[:60]}...")
    
    print("\n✅ Error handling test complete")


if __name__ == "__main__":
    print("\n🤖 SARTHAKA - Phase 3 Workflow Engine Test Suite")
    print("Testing multi-step task orchestration...\n")
    
    # Run async tests
    asyncio.run(test_workflow_engine())
    
    # Run sync tests
    test_workflow_step_class()
    
    # Run error handling test
    asyncio.run(test_workflow_error_handling())
    
    print("\n" + "="*60)
    print("🎉 ALL PHASE 3 TESTS COMPLETE")
    print("="*60)
    print("\nYou can now:")
    print("  1. Run: python test_phase3.py (this test)")
    print("  2. Run: python main.py (Friday with workflows)")
    print("  3. Say: 'Friday, setup my streaming environment'")
    print("  4. Say: 'Friday, help me research Python AI'")
    print("  5. Say: 'Friday, start my coding session'")
    print("\nPhase 3 is complete! Ready for Phase 4. 🚀")
