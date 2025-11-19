"""
Test script for enhanced time parsing functionality

This script tests the new time parsing capabilities including:
1. Date only expressions
2. Date + time expressions
3. Deadline expressions (before, by, after)
4. Date range expressions (weekend, next week)
5. Flexible date expressions
"""

import sys
from datetime import datetime
from services.tools.conversation_tools import PreferenceExtractorTool


def test_time_parsing():
    """Test various time parsing scenarios"""

    extractor = PreferenceExtractorTool()

    test_cases = [
        # Date only
        ("I need a haircut next thursday", "next thursday"),
        ("I need a haircut tomorrow", "tomorrow"),
        ("I need a haircut next week", "next week"),

        # Date + time (numeric)
        ("I need a haircut next thursday at 3 pm", "next thursday 3pm"),
        ("I need a haircut tomorrow at 5:30pm", "tomorrow 5:30pm"),

        # Date + time (spoken/word numbers) - NEW!
        ("I need a haircut next thursday three pm", "next thursday three pm (spoken)"),
        ("I need a haircut tomorrow at five thirty pm", "tomorrow five thirty pm (spoken)"),
        ("I need a haircut friday at ten am", "friday ten am (spoken)"),
        ("I need a haircut next monday eleven o'clock", "next monday eleven o'clock (spoken)"),

        # Deadlines
        ("I need a haircut before next thursday", "before next thursday"),
        ("I need a haircut by friday 5pm", "by friday 5pm"),
        ("I need a haircut after monday", "after monday"),
        ("I need a haircut before next thursday 3 pm", "before next thursday 3pm"),

        # Deadlines with spoken numbers - NEW!
        ("I need a haircut before next thursday three pm", "before next thursday three pm (spoken)"),
        ("I need a haircut by friday five pm", "by friday five pm (spoken)"),

        # Date ranges
        ("I need a haircut next weekend", "next weekend"),
        ("I need a haircut this weekend", "this weekend"),
        ("I need a haircut by end of week", "by end of week"),

        # Budget + time combinations
        ("I need a haircut under $50 before next thursday", "$50 before next thursday"),
        ("I need a haircut for around fifty dollars next weekend", "fifty dollars next weekend"),

        # Budget + spoken time - NEW!
        ("I need a haircut under fifty dollars next thursday three pm", "fifty dollars + three pm (spoken)"),
    ]

    print("\n" + "="*80)
    print("ENHANCED TIME PARSING TEST RESULTS")
    print("="*80 + "\n")
    print(f"Current date/time: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}\n")

    for message, description in test_cases:
        print(f"\n{'─'*80}")
        print(f"Test: {description}")
        print(f"Input: '{message}'")
        print(f"{'─'*80}")

        result = extractor.execute({
            "message": message,
            "current_preferences": {}
        })

        # Extract relevant fields
        preferred_date = result.get("preferred_date")
        preferred_time = result.get("preferred_time")
        time_constraint = result.get("time_constraint")
        time_urgency = result.get("time_urgency")
        budget_max = result.get("budget_max")
        budget_min = result.get("budget_min")

        print("\nExtracted Information:")
        if preferred_date:
            # Convert to readable format
            date_obj = datetime.fromisoformat(preferred_date)
            print(f"  ✓ Date: {date_obj.strftime('%A, %B %d, %Y')} ({preferred_date})")

        if preferred_time:
            print(f"  ✓ Time: {preferred_time}")

        if time_constraint:
            print(f"  ✓ Constraint: {time_constraint}")

        if time_urgency:
            print(f"  ✓ Urgency: {time_urgency}")

        if budget_max:
            print(f"  ✓ Budget Max: ${budget_max:.0f}")

        if budget_min:
            print(f"  ✓ Budget Min: ${budget_min:.0f}")

        # Check if time info was extracted
        has_time_info = bool(
            preferred_date or preferred_time or time_constraint or time_urgency
        )

        if has_time_info:
            print(f"\n  ✅ SUCCESS: Time information extracted")
        else:
            print(f"\n  ❌ FAILED: No time information extracted")

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")


def test_readiness_detection():
    """Test readiness detection with new time formats"""

    from services.tools.conversation_tools import ReadinessDetectorTool

    detector = ReadinessDetectorTool()

    print("\n" + "="*80)
    print("READINESS DETECTION TEST")
    print("="*80 + "\n")

    test_scenarios = [
        {
            "name": "Complete with date only",
            "prefs": {
                "service_type": "haircut",
                "budget_max": 50,
                "preferred_date": "2025-11-21"
            }
        },
        {
            "name": "Complete with date + time",
            "prefs": {
                "service_type": "haircut",
                "budget_max": 50,
                "preferred_date": "2025-11-21",
                "preferred_time": "15:00"
            }
        },
        {
            "name": "Complete with deadline constraint",
            "prefs": {
                "service_type": "haircut",
                "budget_max": 50,
                "preferred_date": "2025-11-21",
                "time_constraint": "before"
            }
        },
        {
            "name": "Complete with time urgency (old format)",
            "prefs": {
                "service_type": "haircut",
                "budget_max": 50,
                "time_urgency": "week"
            }
        },
        {
            "name": "Incomplete - missing time info",
            "prefs": {
                "service_type": "haircut",
                "budget_max": 50
            }
        }
    ]

    for scenario in test_scenarios:
        print(f"\nScenario: {scenario['name']}")
        print(f"Preferences: {scenario['prefs']}")

        result = detector.execute({
            "current_preferences": scenario["prefs"]
        })

        ready = result.get("ready_to_match")
        missing = result.get("missing_fields")
        completeness = result.get("completeness")

        status = "✅ READY" if ready else "❌ NOT READY"
        print(f"  {status}")
        print(f"  Completeness: {completeness*100:.0f}%")

        if missing:
            print(f"  Missing: {', '.join(missing)}")

        print()


if __name__ == "__main__":
    print("\n🚀 Starting Enhanced Time Parsing Tests...\n")

    try:
        test_time_parsing()
        test_readiness_detection()

        print("\n✨ All tests completed successfully!\n")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
