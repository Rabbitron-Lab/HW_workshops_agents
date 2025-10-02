import streamlit as st
import time
from agent import FreeLLMAgent

# Page configuration
st.set_page_config(
    page_title="MRKL Agent Demo", 
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = FreeLLMAgent()
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Title
st.title("🤖 MRKL Agent with Real-Time Data")
st.markdown("### *Modular Reasoning, Knowledge and Language System*")

# Sidebar with information
with st.sidebar:
    st.header("🛠️ Available Tools")
    st.markdown("**Calculator**: Mathematical operations")
    st.markdown("**Weather**: Real-time city weather (free API)")
    st.markdown("**Search**: Real-time web search & Wikipedia")
    st.markdown("**News**: Latest news & current events")
    
    st.header("🔍 Reflector Agent")
    st.markdown("**Meta-Analysis**: Quality assessment & improvement suggestions")
    st.markdown("**Confidence Scoring**: Response reliability analysis")
    st.markdown("**Alternative Approaches**: Different solution strategies")
    
    st.header("💡 Sample Queries")
    sample_queries = [
        "What's 15 * 23 + 100?",
        "Weather in Tokyo?",
        "Latest news about AI",
        "What is quantum computing?",
        "Current events in technology",
        "Calculate 3.14159 * 5 * 5",
        "What is the current event happening in Heriot Watt University?"
    ]
    
    for idx, query in enumerate(sample_queries):
        if st.button(f"📝 {query}", key=f"sample_btn_{idx}"):
            st.session_state.current_query = query

# Main interface
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Chat with MRKL Agent")
    
    # Query input
    query = st.text_input(
        "Ask me anything:", 
        value=st.session_state.get('current_query', ''),
        placeholder="e.g., What's 25 * 4? or Weather in London?",
        key="main_query_input"
    )
    
    if st.button("🚀 Send Query", type="primary", key="send_query_btn") and query:
        with st.spinner("🧠 Agent is thinking..."):
            # Process the query
            result = st.session_state.agent.process_query(query)
            
            # Add to chat history
            st.session_state.chat_history.append({
                'query': query,
                'result': result,
                'timestamp': time.strftime("%H:%M:%S")
            })
            
            # Clear the input
            st.session_state.current_query = ""
            
            # Show success message
            st.success(f"✅ Query processed successfully! Check the conversation below.")
            st.rerun()

with col2:
    st.header("🔍 Current Reasoning")
    
    if st.session_state.chat_history:
        latest = st.session_state.chat_history[-1]
        
        # Show current query info
        st.info(f"**Latest Query:** {latest['query']}")
        
        # Tool and parameters in a nice format
        st.metric("🛠️ Tool Selected", latest['result']['tool_used'])
        st.code(f"Parameters: {latest['result']['parameters']}", language="text")
        
        # Validation quick summary
        if 'validation' in latest['result']:
            validation = latest['result']['validation']
            st.subheader("🔍 Validation Status")
            
            # Show validation decision with color coding
            if validation['validation_decision']:
                st.success(f"✅ VALIDATED")
                st.metric("Confidence", f"{validation['confidence_level']}%")
            else:
                st.error(f"❌ FLAGGED")
                st.metric("Issues Found", len(validation.get('improvement_suggestions', [])))
                
            # Show AI validation status if available
            if validation.get('ai_validation', {}).get('validation_successful'):
                ai_decision = validation['ai_validation']['ai_decision']
                if ai_decision == 'correct':
                    st.success("🤖 AI Agrees")
                elif ai_decision == 'incorrect':
                    st.warning("🤖 AI Disagrees") 
                else:
                    st.info("🤖 AI Uncertain")
        
        # Point to main response area
        st.subheader("👇 Complete Response")
        st.write("The full answer, reasoning steps, and reflector analysis are shown below!")
    else:
        st.write("Ask a question to see the reasoning process!")
        
        # Show example reasoning flow
        st.subheader("📋 How MRKL Reasoning Works:")
        st.write("1. **Query Analysis** - Understand user input")
        st.write("2. **Tool Selection** - Choose appropriate tool") 
        st.write("3. **Parameter Extraction** - Get tool parameters")
        st.write("4. **Tool Execution** - Run the selected tool")
        st.write("5. **Response Generation** - Create final answer")

# Latest Response Highlight
if st.session_state.chat_history:
    latest = st.session_state.chat_history[-1]
    st.header("🎯 Latest Agent Response")
    
    with st.container():
        # User question
        st.markdown("### 🔸 Your Question:")
        st.info(f"**{latest['query']}**")
        
        # Agent response prominently displayed
        st.markdown("### 🤖 Answer:")
        
        # Highlighted response box
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            margin: 20px 0;
            font-size: 18px;
            line-height: 1.8;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
            border-left: 5px solid #ffd700;
        ">
            <strong>{latest['result']['response']}</strong>
        </div>
        """, unsafe_allow_html=True)
        
        # Validation Status Section - Show prominently
        if 'validation' in latest['result']:
            validation = latest['result']['validation']
            st.markdown("### 🔍 **Reflector Agent Validation:**")
            
            # Create validation status with big visual indicator
            if validation['validation_decision']:
                st.success(f"✅ **ANSWER VALIDATED** - Confidence: {validation['confidence_level']}%")
                st.markdown(f"**Validation Reasoning:** {validation['validation_reasoning']}")
            else:
                st.error(f"❌ **ANSWER FLAGGED** - Confidence: {validation['confidence_level']}%") 
                st.markdown(f"**Issues Found:** {validation['validation_reasoning']}")
                
                # Show improvement suggestions prominently if answer is flagged
                if validation['improvement_suggestions']:
                    st.warning("**Suggested Improvements:**")
                    for suggestion in validation['improvement_suggestions']:
                        st.write(f"• {suggestion}")
            
            # Show AI validation details if available
            if validation.get('ai_validation', {}).get('validation_successful'):
                ai_val = validation['ai_validation']
                st.info(f"🤖 **AI Model Says:** {ai_val['ai_decision'].title()} ({ai_val['ai_confidence']}% confidence)")
        
        # Reasoning steps section
        st.markdown("### 🧠 How I Got This Answer:")
        for i, step in enumerate(latest['result']['reasoning_steps'], 1):
            with st.expander(f"Step {i}: {step['step']}", expanded=False):
                st.write(step['content'])
        
        # Detailed Validation Analysis (Expandable)
        if 'validation' in latest['result']:
            validation = latest['result']['validation']
            
            with st.expander("📊 **Detailed Validation Analysis**", expanded=False):
                tab1, tab2, tab3 = st.tabs(["Answer Analysis", "Reasoning Check", "AI Validation"])
                
                with tab1:
                    st.markdown("**Answer Content Analysis:**")
                    answer_analysis = validation.get('answer_analysis', {})
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"**Answer Type:** {answer_analysis.get('answer_type', 'Unknown').title()}")
                        st.info(f"**Response Length:** {answer_analysis.get('response_length', 0)} characters")
                    
                    with col2:
                        if answer_analysis.get('contains_calculation'):
                            st.success("✅ Contains Mathematical Calculation")
                        if answer_analysis.get('contains_factual_info'):
                            st.success("✅ Contains Factual Information")
                    
                    if answer_analysis.get('potential_issues'):
                        st.warning("**Potential Issues Detected:**")
                        for issue in answer_analysis['potential_issues']:
                            st.write(f"⚠️ {issue}")
                
                with tab2:
                    st.markdown("**Reasoning Chain Validation:**")
                    reasoning_val = validation.get('reasoning_validation', {})
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Steps Count", reasoning_val.get('step_count', 0))
                    with col2:
                        st.metric("Completeness", f"{reasoning_val.get('completeness_score', 0)}%")
                    with col3:
                        quality = reasoning_val.get('reasoning_quality', 'Unknown')
                        if quality == 'Excellent':
                            st.success(f"Quality: {quality}")
                        elif quality == 'Good':
                            st.info(f"Quality: {quality}")
                        else:
                            st.warning(f"Quality: {quality}")
                    
                    if reasoning_val.get('missing_steps'):
                        st.warning("**Missing Steps:**")
                        for step in reasoning_val['missing_steps']:
                            st.write(f"❌ {step}")
                
                with tab3:
                    st.markdown("**AI Model Validation:**")
                    ai_val = validation.get('ai_validation', {})
                    
                    if ai_val.get('validation_successful'):
                        decision = ai_val.get('ai_decision', 'uncertain')
                        confidence = ai_val.get('ai_confidence', 0)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if decision == 'correct':
                                st.success(f"✅ AI Decision: {decision.title()}")
                            elif decision == 'incorrect':
                                st.error(f"❌ AI Decision: {decision.title()}")
                            else:
                                st.info(f"🤔 AI Decision: {decision.title()}")
                        
                        with col2:
                            st.metric("AI Confidence", f"{confidence}%")
                        
                        st.text_area("AI Reasoning:", ai_val.get('ai_reasoning', 'No reasoning provided'), height=100)
                    else:
                        st.warning("AI validation was not available")
                        st.write(ai_val.get('ai_reasoning', 'No details available'))
        
        # Tool info
        col_a, col_b = st.columns(2)
        with col_a:
            st.success(f"🛠️ **Tool Used:** {latest['result']['tool_used']}")
        with col_b:
            st.info(f"📝 **Parameters:** {latest['result']['parameters']}")
    
    st.markdown("---")

# Full Chat History
st.header("💬 Conversation History")

if st.session_state.chat_history:
    for i, chat in enumerate(reversed(st.session_state.chat_history)):
        is_latest = (i == 0)  # First item in reversed list is latest
        
        with st.container():
            # Skip the latest one since it's already shown above
            if is_latest and len(st.session_state.chat_history) > 1:
                continue
            elif is_latest:
                # If only one message, don't duplicate
                st.info("👆 Your latest interaction is shown above!")
                break
            
            # User message
            with st.chat_message("user"):
                st.markdown(f"**{chat['query']}**")
                st.caption(f"🕐 {chat['timestamp']}")
            
            # Agent response (condensed for history)
            with st.chat_message("assistant"):
                # Show condensed version
                response_preview = chat['result']['response'][:200] + "..." if len(chat['result']['response']) > 200 else chat['result']['response']
                st.markdown(response_preview)
                
                # Tool info as caption
                st.caption(f"🔧 {chat['result']['tool_used']} • {chat['result']['parameters']}")
                
                # Expandable reasoning steps
                with st.expander("🧠 Show Reasoning Steps", expanded=False):
                    for j, step in enumerate(chat['result']['reasoning_steps'], 1):
                        st.write(f"**Step {j}: {step['step']}**")
                        st.write(f"└─ {step['content']}")
                        if j < len(chat['result']['reasoning_steps']):
                            st.write("---")
            
            st.divider()
else:
    st.info("👋 Start by asking a question above! Try the sample queries from the sidebar.")

# Clear chat button
if st.button("🗑️ Clear Chat History", key="clear_chat_btn"):
    st.session_state.chat_history = []
    st.rerun()