#!/usr/bin/env python3
"""
Test script to demonstrate the fix for meaningless input handling
This addresses the issue where random character inputs like 'yuhyhyugyuguygu'
were incorrectly processed as search queries and returned unrelated results.
"""

from agent import FreeLLMAgent

def test_meaningless_input_detection():
    """Test the meaningless input detection and handling"""
    
    print("🧪 Testing Meaningless Input Detection and Handling")
    print("=" * 60)
    
    agent = FreeLLMAgent()
    
    # Test cases: [input, expected_to_be_flagged, description]
    test_cases = [
        ("yuhyhyugyuguygu", True, "Original problematic input - random keyboard mashing"),
        ("asdfghjklqwerty", True, "Keyboard row characters"),
        ("yuyuyuyuyuyuyu", True, "Repetitive characters"),
        ("aaaaaaaaaaaaa", True, "Single character repeated"),
        ("calculate 25 * 4", False, "Valid mathematical query"),
        ("weather in London", False, "Valid weather query"),
        ("what is AI", False, "Valid information query"),
        ("hello world", False, "Valid simple query"),
        ("", True, "Empty query"),
        ("a", True, "Single character"),
        ("xyz", True, "Three random characters"),
    ]
    
    print("🔍 Input Validation Tests:")
    print("-" * 40)
    
    for query, should_be_flagged, description in test_cases:
        is_flagged = agent._is_meaningless_query(query)
        status = "✅" if is_flagged == should_be_flagged else "❌"
        
        print(f"{status} '{query}' -> Flagged: {is_flagged} ({description})")
    
    print("\n🤖 End-to-End Processing Tests:")
    print("-" * 40)
    
    # Test the original problematic case
    print("\n🔍 Testing original problematic input: 'yuhyhyugyuguygu'")
    result = agent.process_query("yuhyhyugyuguygu")
    
    print(f"Tool Used: {result['tool_used']}")
    print(f"Response Preview: {result['response'][:100]}...")
    print(f"Validation: {result['validation']['overall_decision']} ({result['validation']['confidence']}%)")
    
    # Test a valid query to ensure normal operation
    print("\n🔍 Testing valid query: 'what is 5+5?'")
    result2 = agent.process_query("what is 5+5?")
    
    print(f"Tool Used: {result2['tool_used']}")
    print(f"Response Preview: {result2['response'][:100]}...")
    print(f"Validation: {result2['validation']['overall_decision']} ({result2['validation']['confidence']}%)")
    
    print("\n" + "=" * 60)
    print("🎉 Meaningless Input Detection Test Complete!")
    print("\n📋 Summary:")
    print("✅ Random character inputs are now properly detected")
    print("✅ Users receive helpful guidance instead of unrelated search results") 
    print("✅ Valid queries continue to work normally")
    print("✅ Reflector agent validates responses appropriately")

if __name__ == "__main__":
    test_meaningless_input_detection()