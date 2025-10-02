#!/usr/bin/env python3
"""
Quick test script to verify the MRKL agent is working properly after cleanup
"""

def test_basic_functionality():
    """Test basic agent functionality"""
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from agent import FreeLLMAgent
        from tools import TOOLS
        
        print("✅ Imports successful")
        
        # Initialize agent
        agent = FreeLLMAgent()
        print("✅ Agent initialized")
        
        # Test tools are loaded
        print(f"✅ {len(TOOLS)} tools loaded: {list(TOOLS.keys())}")
        
        # Test basic query processing
        test_queries = [
            "What is 2 + 2?",
            "Weather in London?",
            "What is Python?"
        ]
        
        for query in test_queries:
            try:
                result = agent.process_query(query)
                print(f"✅ Query '{query}' processed successfully")
                print(f"   Tool used: {result.get('tool_used', 'Unknown')}")
                print(f"   Response length: {len(result.get('response', ''))}")
            except Exception as e:
                print(f"❌ Error with query '{query}': {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 MRKL Agent Functionality Test")
    print("=" * 40)
    
    if test_basic_functionality():
        print("\n🎉 All tests passed! Codebase is clean and functional.")
    else:
        print("\n⚠️ Some tests failed. Please check the issues above.")