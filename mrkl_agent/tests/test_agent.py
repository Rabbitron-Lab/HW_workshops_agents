from agent import FreeLLMAgent
import time

def test_agent():
    """Test the enhanced MRKL agent with real data"""
    agent = FreeLLMAgent()
    
    test_queries = [
        "What's 25 * 4 + 100?",  # Calculator
        "Weather in London?",     # Weather (free API)
        "Latest news about artificial intelligence",  # News (SerpAPI)
        "What is quantum computing?",  # Search (SerpAPI + Wikipedia)
    ]
    
    print("🧪 Testing Enhanced MRKL Agent with Real Data")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {query}")
        print("-" * 40)
        
        try:
            result = agent.process_query(query)
            
            print(f"🛠️ Tool Used: {result['tool_used']}")
            print(f"📊 Parameters: {result['parameters']}")
            print(f"✅ Response: {result['response'][:200]}...")
            
            if len(result['response']) > 200:
                print("   [Response truncated for display]")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        if i < len(test_queries):
            time.sleep(2)  # Pause between API calls
    
    print("\n" + "=" * 60)
    print("🎉 Testing complete! Your MRKL agent is ready for demonstration.")
    print("🚀 Run 'streamlit run app.py' to start the interactive demo!")

if __name__ == "__main__":
    test_agent()