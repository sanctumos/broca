#!/usr/bin/env python3
"""
Test script to verify the markdown formatting fix.
This script tests the new preserve_markdown function to ensure it properly handles
markdown from Letta/Broca responses without flattening them.
"""

import os
import sys

# Add the broca2 directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common.telegram_markdown import preserve_telegram_markdown


def test_markdown_preservation():
    """Test that markdown formatting is preserved correctly."""

    def format_response(text: str) -> str:
        return preserve_telegram_markdown(text)

    # Test cases: typical Letta/Broca responses
    test_cases = [
        {
            "name": "Basic markdown with headers and lists",
            "input": """# Welcome to the System

Here's what you can do:
- **Feature 1**: Description
- **Feature 2**: Description

Let me know if you need help!""",
            "expected_contains": ["Welcome to the System", "Feature 1", "Feature 2"],
        },
        {
            "name": "Code blocks and formatting",
            "input": """Here's some code:

```python
def hello():
    print("Hello, World!")
```

And some **bold** and *italic* text.""",
            "expected_contains": ["def hello()", "bold", "italic"],
        },
        {
            "name": "Mixed formatting",
            "input": """**Important Notice**

This is a *test* message with:
1. Numbered list
2. More items
3. And a `code snippet`

> This is a quote block""",
            "expected_contains": [
                "Important Notice",
                "test",
                "Numbered list",
                "code snippet",
            ],
        },
    ]

    print("🧪 Testing markdown preservation fix...")
    print("=" * 50)

    all_passed = True

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print("-" * 30)

        # Format the response using the new method
        formatted = format_response(test_case["input"])

        print("Input:")
        print(test_case["input"])
        print("\nFormatted Output:")
        print(formatted)

        # Check if expected content is preserved
        preserved = True
        for expected in test_case["expected_contains"]:
            if expected not in formatted:
                preserved = False
                print(f"❌ Missing expected content: '{expected}'")

        # Check if newlines are preserved (not flattened)
        if "\n" not in formatted:
            preserved = False
            print("❌ Newlines were flattened!")

        if preserved:
            print("✅ Test PASSED - Markdown preserved correctly")
        else:
            print("❌ Test FAILED - Markdown was flattened or corrupted")
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests PASSED! Markdown formatting is preserved.")
        return True
    else:
        print("💥 Some tests FAILED! Markdown formatting issues detected.")
        return False


def test_old_vs_new_behavior():
    """Compare old sanitize_text behavior vs new preserve_markdown behavior."""

    from runtime.core.message import MessageFormatter

    formatter = MessageFormatter()

    test_input = """# Header

**Bold text** and *italic text*

- List item 1
- List item 2

`Code snippet`"""

    print("\n🔄 Comparing old vs new behavior...")
    print("=" * 50)

    print("Original input:")
    print(test_input)
    print("\n" + "-" * 30)

    # Old behavior (what was happening before)
    old_result = formatter.sanitize_text(test_input)
    print("OLD behavior (sanitize_text):")
    print(old_result)
    print("\n" + "-" * 30)

    # New behavior (what should happen now)
    new_result = preserve_telegram_markdown(test_input)
    print("NEW behavior (format_response):")
    print(new_result)

    print("\n" + "=" * 50)
    if old_result != new_result:
        print("✅ SUCCESS: New behavior is different from old behavior!")
        print("✅ Markdown formatting should now be preserved.")
    else:
        print("❌ WARNING: New behavior is the same as old behavior.")
        print("❌ The fix may not be working correctly.")


if __name__ == "__main__":
    print("🚀 Testing Telegram Markdown Fix")
    print("This script tests the fix for markdown flattening in the Telegram plugin.")

    # Run the main test
    success = test_markdown_preservation()

    # Run the comparison test
    test_old_vs_new_behavior()

    if success:
        print("\n🎯 SUMMARY: The markdown fix appears to be working correctly!")
        print("Markdown from Letta/Broca responses should now be preserved.")
    else:
        print("\n⚠️  SUMMARY: Issues detected with the markdown fix.")
        print("Please review the implementation.")

    sys.exit(0 if success else 1)
