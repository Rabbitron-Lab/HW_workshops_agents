from agent import FreeLLMAgent
import time

def demo_scenarios():
    """Run predefined demo scenarios"""
    scenarios = [
        "What's 15 * 23 + 100?",
        "What's the weather like in Tokyo?", 
        "Tell me about artificial intelligence",
        "Calculate the area of a circle with radius 5"
    ]
    
    agent = FreeLLMAgent()
    
    print("🤖 MRKL Agent Demo (Command Line Version)")
    print("=" * 60)
    print("This demo shows a MRKL agent using FREE LLM + modular tools")
    print("For interactive web demo, run: streamlit run app.py")
    print("=" * 60)
    
    for i, query in enumerate(scenarios, 1):
        print(f"\n📝 Demo Scenario {i}")
        print(f"Student Question: {query}")
        print("🧠 Agent is thinking...")
        
        # Process query
        result = agent.process_query(query)
        
        # Show reasoning process
        print("\n🔍 Reasoning Steps:")
        for j, step in enumerate(result['reasoning_steps'], 1):
            print(f"  {j}. {step['step']}: {step['content']}")
        
        print(f"\n✅ Final Response: {result['response']}")
        print("-" * 60)
        
        if i < len(scenarios):
            time.sleep(1)  # Pause between demos

def interactive_mode():
    """Interactive chat mode"""
    agent = FreeLLMAgent()
    
    print("\n🤖 MRKL Agent - Interactive Mode")
    print("Type 'quit' to exit, 'demo' for predefined scenarios")
    print("=" * 50)
    
    while True:
        query = input("\n💬 Your question: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        elif query.lower() == 'demo':
            demo_scenarios()
            continue
        elif not query:
            continue
        
        print("🧠 Processing...")
        result = agent.process_query(query)
        
        print(f"\n🔧 Tool: {result['tool_used']}")
        print(f"📊 Parameters: {result['parameters']}")
        print(f"✅ Response: {result['response']}")
        
        # Option to see detailed reasoning
        show_details = input("Show reasoning steps? (y/n): ").strip().lower()
        if show_details == 'y':
            print("\n🔍 Detailed Reasoning:")
            for i, step in enumerate(result['reasoning_steps'], 1):
                print(f"  {i}. {step['step']}: {step['content']}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'interactive':
        interactive_mode()
    else:
        demo_scenarios()
        
        print("\n🌐 For web interface: streamlit run app.py")
        print("🔄 For interactive mode: python main.py interactive")
