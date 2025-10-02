import streamlit as st
from groq import Groq
import json
import time
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_api_key():
    """Get API key from session state, environment, or user input"""
    # Check if API key is in session state
    if 'groq_api_key' in st.session_state and st.session_state.groq_api_key:
        return st.session_state.groq_api_key
    
    # Check environment variables
    env_key = os.getenv("GROQ_API_KEY")
    if env_key:
        st.session_state.groq_api_key = env_key
        return env_key
    
    return None

class ContentGeneratorAgent:
    def __init__(self, api_key=None):
        try:
            if not api_key:
                self.client = None
                return
                
            self.client = Groq(api_key=api_key)
            self.model = "llama-3.1-8b-instant"
            # Test the connection
            self.client.models.list()
            
        except Exception as e:
            st.error(f"❌ Error loading Content Generator: {str(e)}")
            self.client = None
    
    def generate_content(self, prompt, max_tokens=300):
        """Generate content based on the given prompt using Groq"""
        try:
            if self.client is None:
                return self._template_based_generation(prompt)
            
            # Create a detailed prompt for blog content generation
            system_prompt = """You are a professional blog writer. Generate well-structured, informative, and engaging blog content based on the user's topic. 
            Make sure the blog content is:
            - Well-organized with clear introduction, body, and conclusion
            - Informative and accurate with real insights
            - Engaging and easy to read
            - Appropriate length (150-400 words)
            - Professional yet conversational tone
            - Includes practical examples or insights where relevant"""
            
            user_prompt = f"Write a comprehensive and engaging blog post about: {prompt}. Make it informative, well-structured, and interesting to read."
            
            # Generate content using Groq
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.8,
                top_p=0.9
            )
            
            # Extract generated content
            generated_content = chat_completion.choices[0].message.content
            return generated_content.strip()
            
        except Exception as e:
            st.error(f"Error generating content with Groq: {str(e)}")
            return self._template_based_generation(prompt)
    
    def improve_content(self, original_content, criticism, max_tokens=300):
        """Improve content based on criticism using Groq"""
        try:
            if self.client is None:
                return self._template_based_improvement(original_content, criticism)
            
            # Create a detailed prompt for content improvement
            system_prompt = """You are a professional content editor and writer. Your job is to improve existing content based on specific criticism and feedback.
            
            Instructions:
            - Carefully read the original content and the criticism provided
            - Address all the specific issues mentioned in the criticism
            - Maintain the original topic and intent while making improvements
            - Enhance clarity, engagement, structure, and overall quality
            - Keep the improved version within a similar length range
            - Make the content more polished and professional"""
            
            user_prompt = f"""Please improve the following content based on the criticism provided:

ORIGINAL CONTENT:
{original_content}

CRITICISM TO ADDRESS:
{criticism}

Please provide an improved version that addresses all the points mentioned in the criticism while maintaining the core message and topic."""
            
            # Generate improved content using Groq
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.7,
                top_p=0.9
            )
            
            # Extract improved content
            improved_content = chat_completion.choices[0].message.content
            return improved_content.strip()
            
        except Exception as e:
            st.error(f"Error improving content with Groq: {str(e)}")
            return self._template_based_improvement(original_content, criticism)
    
    def _template_based_improvement(self, content, criticism):
        """Fallback template-based content improvement"""
        # Simple improvements based on common issues
        improved = content
        
        # Add more structure if needed
        if "structure" in criticism.lower() or "organization" in criticism.lower():
            improved = f"# Introduction\n\n{improved}\n\n# Conclusion\n\nIn summary, this topic demonstrates important considerations for further exploration."
        
        # Add examples if mentioned in criticism
        if "example" in criticism.lower() or "specific" in criticism.lower():
            improved += "\n\n**Example:** This concept can be applied in real-world scenarios where practical implementation brings measurable benefits."
        
        # Add engagement elements
        if "engaging" in criticism.lower() or "engagement" in criticism.lower():
            improved = improved.replace(".", ". This is particularly important because")
        
        return improved
    
    def _template_based_generation(self, prompt):
        """Fallback template-based content generation"""
        templates = {
            "technology": f"# {prompt}\n\nIn today's rapidly evolving technological landscape, {prompt.lower()} has emerged as a significant factor shaping our digital future. This innovation brings both opportunities and challenges that organizations must carefully consider.\n\n## Key Benefits\n- Enhanced efficiency and productivity\n- Improved user experience\n- Cost-effective solutions\n- Scalable implementation\n\n## Challenges to Address\n- Security considerations\n- Integration complexity\n- Training requirements\n- Change management\n\n## Looking Forward\nAs we continue to embrace {prompt.lower()}, it's crucial to maintain a balanced approach that maximizes benefits while mitigating potential risks.",
            
            "business": f"# {prompt}\n\nIn the competitive business environment, {prompt.lower()} has become increasingly important for organizational success. Companies that embrace this concept often find themselves better positioned for growth and sustainability.\n\n## Strategic Importance\n- Competitive advantage\n- Market differentiation\n- Revenue optimization\n- Operational excellence\n\n## Implementation Considerations\n- Resource allocation\n- Timeline planning\n- Risk assessment\n- Performance metrics\n\n## Best Practices\nSuccessful implementation of {prompt.lower()} requires careful planning, stakeholder buy-in, and continuous monitoring to ensure desired outcomes.",
            
            "general": f"# {prompt}\n\n{prompt} is an fascinating topic that deserves our attention and understanding. This subject encompasses various aspects that can impact different areas of our lives.\n\n## Key Points\n- Fundamental concepts and principles\n- Practical applications and use cases\n- Benefits and potential advantages\n- Common challenges and solutions\n\n## Why It Matters\nUnderstanding {prompt.lower()} can help us make better decisions and navigate related situations more effectively.\n\n## Conclusion\nAs we explore {prompt.lower()} further, it becomes clear that this topic offers valuable insights that can be applied in various contexts."
        }
        
        # Simple keyword matching for template selection
        prompt_lower = prompt.lower()
        if any(word in prompt_lower for word in ['tech', 'ai', 'software', 'digital', 'computer', 'algorithm']):
            return templates['technology']
        elif any(word in prompt_lower for word in ['business', 'market', 'company', 'strategy', 'management']):
            return templates['business']
        else:
            return templates['general']

class CriticAgent:
    def __init__(self, api_key=None):
        try:
            if not api_key:
                self.client = None
                return
                
            self.client = Groq(api_key=api_key)
            self.model = "llama-3.1-8b-instant"
            # Test the connection
            self.client.models.list()
            
        except Exception as e:
            st.error(f"❌ Error loading Critic Agent: {str(e)}")
            self.client = None
    
    def analyze_content(self, content, max_tokens=400):
        """Analyze and critique content using Groq"""
        try:
            if self.client is None:
                return self._template_based_criticism(content)
            
            # Create a detailed prompt for content analysis
            system_prompt = """You are an expert content critic and editor. Your job is to provide comprehensive, constructive criticism of written content. 
            
            Analyze the content across these dimensions:
            1. CLARITY & READABILITY: Is the writing clear and easy to understand?
            2. STRUCTURE & ORGANIZATION: Is the content well-organized with logical flow?
            3. ENGAGEMENT & TONE: Is it engaging and appropriate for the target audience?
            4. ACCURACY & DEPTH: Does it provide valuable, accurate information?
            5. COMPLETENESS: Are there missing elements or areas that need expansion?
            
            At the end of your analysis, provide a QUALITY SCORE from 1-10 where:
            - 1-4: Poor quality, needs major improvements
            - 5-6: Average quality, needs moderate improvements  
            - 7-8: Good quality, minor improvements needed
            - 9-10: Excellent quality, ready for publication
            
            Format your response with the score at the end like: "QUALITY SCORE: X/10"
            
            Provide specific, actionable feedback with examples. Be constructive and helpful, not just critical."""
            
            user_prompt = f"Please analyze and critique this content in detail. Provide specific feedback on strengths, weaknesses, and suggestions for improvement:\n\n{content}"
            
            # Generate criticism using Groq
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.7,
                top_p=0.9
            )
            
            # Extract criticism
            criticism = chat_completion.choices[0].message.content
            return criticism.strip()
            
        except Exception as e:
            st.error(f"Error analyzing content with Groq: {str(e)}")
            return self._template_based_criticism(content)
    
    def extract_quality_score(self, criticism):
        """Extract quality score from criticism text"""
        try:
            # Look for quality score pattern
            score_pattern = r"QUALITY SCORE:\s*(\d+(?:\.\d+)?)"
            match = re.search(score_pattern, criticism, re.IGNORECASE)
            if match:
                return float(match.group(1))
            
            # Fallback: analyze criticism sentiment for scoring
            criticism_lower = criticism.lower()
            negative_words = ['poor', 'weak', 'lacking', 'needs improvement', 'unclear', 'confusing']
            positive_words = ['excellent', 'great', 'good', 'clear', 'engaging', 'well-written']
            
            negative_count = sum(1 for word in negative_words if word in criticism_lower)
            positive_count = sum(1 for word in positive_words if word in criticism_lower)
            
            # Simple scoring based on word sentiment
            base_score = 5.0
            score = base_score + (positive_count * 0.5) - (negative_count * 0.5)
            return max(1.0, min(10.0, score))
            
        except Exception:
            return 5.0  # Default score if extraction fails
    
    def _template_based_criticism(self, content):
        """Fallback template-based content criticism"""
        word_count = len(content.split())
        
        # Calculate a basic quality score based on word count and structure
        base_score = 5.0
        
        # Word count scoring
        if 150 <= word_count <= 400:
            base_score += 1.5
        elif 100 <= word_count < 150 or 400 < word_count <= 600:
            base_score += 0.5
        
        # Structure scoring (basic checks)
        if any(header in content for header in ['#', '##', '###']):
            base_score += 1.0
        if len(content.split('\n\n')) >= 3:  # Multiple paragraphs
            base_score += 0.5
        
        quality_score = min(10.0, base_score)
        
        feedback = f"""## Content Analysis Report

### Overview
The content has been analyzed across multiple dimensions to provide constructive feedback.

### Strengths Identified
✅ **Word Count**: The content contains {word_count} words, which is {'appropriate for most blog posts' if 100 <= word_count <= 600 else 'outside the typical range (100-600 words)'}
✅ **Structure**: The content appears to have a clear organizational structure
✅ **Readability**: The writing style seems accessible to readers

### Areas for Improvement
🔍 **Engagement**: Consider adding more specific examples or case studies to make the content more engaging
🔍 **Depth**: Some sections could benefit from more detailed explanations or supporting evidence
🔍 **Call to Action**: Consider adding a clear call to action for readers

### Specific Recommendations
1. **Introduction**: Strengthen the opening to immediately capture reader attention
2. **Examples**: Include more concrete examples or real-world applications
3. **Conclusion**: Add a stronger concluding statement that reinforces key takeaways
4. **Flow**: Ensure smooth transitions between sections

**QUALITY SCORE: {quality_score:.1f}/10**

The content shows good potential with solid fundamentals. Implementing the suggested improvements would significantly enhance its impact and reader engagement.
"""
        return feedback

class SelfCriticSystem:
    def __init__(self):
        st.title("🤖 Self-Critic Agent System")
        st.markdown("*An AI system that generates content and iteratively improves it through self-critique*")
        
        # Educational info box
        with st.expander("📚 How Iterative Improvement Works", expanded=False):
            st.markdown("""
            **The Self-Critic Agent demonstrates autonomous improvement through iteration:**
            
            1. **🤖 Generation**: Creates initial content based on your prompt
            2. **🔍 Analysis**: Critically evaluates the content and assigns a quality score (1-10)
            3. **🔄 Improvement**: If score < threshold, generates improved version based on criticism
            4. **♻️ Repeat**: Continues until quality threshold is met or max iterations reached
            5. **✅ Completion**: Stops when content meets quality standards
            
            **Key Features:**
            - **Quality Threshold**: Set minimum acceptable quality (6-10)
            - **Max Iterations**: Prevent infinite loops (2-10 iterations)
            - **Live Progress**: Watch the AI improve in real-time
            - **Color Coding**: 🟢 Excellent (8+), 🟡 Good (6-7.9), 🔴 Needs Work (<6)
            
            This demonstrates how AI can autonomously improve its output through self-reflection and iteration!
            """)
        
        # Session state for storing iterations
        if 'iterations' not in st.session_state:
            st.session_state.iterations = []
        if 'current_content' not in st.session_state:
            st.session_state.current_content = ""
        if 'iterative_mode' not in st.session_state:
            st.session_state.iterative_mode = True
        if 'quality_threshold' not in st.session_state:
            st.session_state.quality_threshold = 8.0
        if 'max_iterations' not in st.session_state:
            st.session_state.max_iterations = 5
        
        # Initialize agents (will be created after API key is provided)
        self.generator = None
        self.critic = None
    
    def run(self):
        # Sidebar for API key and controls
        st.sidebar.header("🔑 API Configuration")
        
        # API Key input
        api_key = get_api_key()
        
        if not api_key:
            st.sidebar.warning("⚠️ Please enter your Groq API key to continue")
            api_key_input = st.sidebar.text_input(
                "Groq API Key:",
                type="password",
                placeholder="Enter your Groq API key here...",
                help="Get your API key from https://console.groq.com/keys"
            )
            
            if st.sidebar.button("🔐 Set API Key"):
                if api_key_input.strip():
                    st.session_state.groq_api_key = api_key_input.strip()
                    st.rerun()
                else:
                    st.sidebar.error("❌ Please enter a valid API key")
            
            # Show instructions if no API key
            st.info("🔑 **API Key Required**")
            st.markdown("""
            To use this application, you need a Groq API key:
            
            1. **Get API Key**: Visit [Groq Console](https://console.groq.com/keys)
            2. **Create Account**: Sign up for a free Groq account
            3. **Generate Key**: Create a new API key
            4. **Enter Key**: Paste it in the sidebar and click "Set API Key"
            
            Your API key is stored securely in your browser session and is not saved permanently.
            """)
            return
        
        # Initialize agents with API key
        if self.generator is None or self.critic is None:
            with st.spinner("🔄 Initializing AI agents..."):
                self.generator = ContentGeneratorAgent(api_key)
                self.critic = CriticAgent(api_key)
                
                # Check if agents loaded successfully
                if self.generator.client and self.critic.client:
                    st.sidebar.success("✅ Agents initialized successfully!")
                else:
                    st.sidebar.error("❌ Failed to initialize agents. Please check your API key.")
                    if st.sidebar.button("🔄 Reset API Key"):
                        del st.session_state.groq_api_key
                        st.rerun()
                    return
        
        # System controls sidebar
        st.sidebar.header("⚙️ System Controls")
        
        # Show API key status (masked)
        masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "••••••••"
        st.sidebar.text(f"🔑 API Key: {masked_key}")
        
        if st.sidebar.button("🔄 Change API Key"):
            del st.session_state.groq_api_key
            st.rerun()
        
        # Iterative improvement settings
        st.sidebar.header("🔄 Iterative Settings")
        
        st.session_state.iterative_mode = st.sidebar.checkbox(
            "Enable Iterative Improvement", 
            value=st.session_state.iterative_mode,
            help="Automatically improve content until it reaches the quality threshold"
        )
        
        if st.session_state.iterative_mode:
            st.session_state.quality_threshold = st.sidebar.slider(
                "Quality Threshold", 
                min_value=6.0, 
                max_value=10.0, 
                value=st.session_state.quality_threshold, 
                step=0.5,
                help="Stop iterating when content reaches this quality score"
            )
            
            st.session_state.max_iterations = st.sidebar.slider(
                "Max Iterations", 
                min_value=2, 
                max_value=10, 
                value=st.session_state.max_iterations,
                help="Maximum number of improvement iterations"
            )
        
        # Input section
        st.header("📝 Content Generation")
        prompt = st.text_area(
            "Enter your topic or prompt:",
            height=100,
            placeholder="e.g., 'The future of artificial intelligence in healthcare'"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            max_tokens_gen = st.slider("Generation Length", 150, 500, 300)
        with col2:
            max_tokens_crit = st.slider("Criticism Length", 200, 600, 400)
        
        # Generate button
        button_text = "🚀 Generate & Iterate" if st.session_state.iterative_mode else "🚀 Generate & Analyze"
        if st.button(button_text, type="primary"):
            if prompt.strip():
                if st.session_state.iterative_mode:
                    self.iterative_improvement(prompt, max_tokens_gen, max_tokens_crit)
                else:
                    self.generate_and_analyze(prompt, max_tokens_gen, max_tokens_crit)
            else:
                st.warning("⚠️ Please enter a prompt first!")
        
        # Display current iteration
        if st.session_state.current_content:
            st.header("📄 Current Content")
            st.markdown(st.session_state.current_content)
        
        # Display iterations history
        if st.session_state.iterations:
            st.header("📚 Iteration History")
            
            for i, iteration in enumerate(reversed(st.session_state.iterations), 1):
                iteration_num = len(st.session_state.iterations) - i + 1
                quality_score = iteration.get('quality_score', 5.0)
                
                # Color code iterations based on quality
                if quality_score >= 8:
                    status_emoji = "🟢"
                elif quality_score >= 6:
                    status_emoji = "🟡"
                else:
                    status_emoji = "🔴"
                
                with st.expander(f"{status_emoji} Iteration {iteration_num}: Score {quality_score:.1f}/10"):
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Generated Content")
                        st.markdown(iteration['content'])
                        
                        # Content metrics
                        word_count = len(iteration['content'].split())
                        st.metric("Word Count", word_count)
                        
                        # Show improvement type
                        if iteration.get('iteration_type'):
                            st.info(f"Type: {iteration['iteration_type']}")
                    
                    with col2:
                        st.subheader("AI Criticism")
                        st.markdown(iteration['criticism'])
                        
                        # Quality metrics
                        st.metric("Quality Score", f"{quality_score:.1f}/10")
                        
                        # Show if this was the final iteration
                        if iteration.get('is_final'):
                            st.success("✅ Final Result - Quality Threshold Reached!")
                        elif iteration.get('stopped_at_max'):
                            st.warning("⚠️ Stopped at Maximum Iterations")
        
        # Clear history button
        if st.session_state.iterations:
            if st.sidebar.button("🗑️ Clear History"):
                st.session_state.iterations = []
                st.session_state.current_content = ""
                st.rerun()
        
        # System status
        st.sidebar.header("📊 System Status")
        st.sidebar.success("🟢 Generator: Ready")
        st.sidebar.success("🟢 Critic: Ready")
        
        # Show iteration statistics
        if st.session_state.iterations:
            total_iterations = len(st.session_state.iterations)
            latest_score = st.session_state.iterations[-1].get('quality_score', 0)
            
            st.sidebar.info(f"💾 Total Iterations: {total_iterations}")
            
            if latest_score >= 8:
                st.sidebar.success(f"🎯 Latest Score: {latest_score:.1f}/10")
            elif latest_score >= 6:
                st.sidebar.warning(f"🎯 Latest Score: {latest_score:.1f}/10")
            else:
                st.sidebar.error(f"🎯 Latest Score: {latest_score:.1f}/10")
            
            # Show iteration mode
            if st.session_state.iterative_mode:
                st.sidebar.info(f"🔄 Mode: Iterative (Target: {st.session_state.quality_threshold}/10)")
            else:
                st.sidebar.info("📝 Mode: Single Generation")
        else:
            st.sidebar.info("💾 No iterations yet")
    
    def iterative_improvement(self, prompt, max_tokens_gen, max_tokens_crit):
        """Generate content and iteratively improve it until quality threshold is met"""
        
        # Check if agents are initialized
        if not self.generator or not self.critic:
            st.error("❌ AI agents not initialized. Please check your API key.")
            return
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        iteration_container = st.empty()
        
        try:
            current_content = None
            iteration_count = 0
            quality_threshold = st.session_state.quality_threshold
            max_iterations = st.session_state.max_iterations
            
            # Clear previous iterations for this run
            st.session_state.iterations = []
            
            while iteration_count < max_iterations:
                iteration_count += 1
                progress_percentage = (iteration_count / max_iterations) * 100
                
                if iteration_count == 1:
                    # First iteration: Generate initial content
                    status_text.text(f"🤖 Iteration {iteration_count}: Generating initial content...")
                    progress_bar.progress(int(progress_percentage * 0.5))
                    
                    current_content = self.generator.generate_content(prompt, max_tokens_gen)
                    iteration_type = "Initial Generation"
                else:
                    # Subsequent iterations: Improve based on criticism
                    status_text.text(f"🔄 Iteration {iteration_count}: Improving content...")
                    progress_bar.progress(int(progress_percentage * 0.5))
                    
                    if previous_criticism:
                        current_content = self.generator.improve_content(
                            current_content, previous_criticism, max_tokens_gen
                        )
                        iteration_type = "Iterative Improvement"
                    else:
                        break
                
                if not current_content:
                    st.error(f"❌ Failed to generate content in iteration {iteration_count}")
                    return
                
                # Analyze the content
                status_text.text(f"🔍 Iteration {iteration_count}: Analyzing content quality...")
                progress_bar.progress(int(progress_percentage * 0.75))
                
                criticism = self.critic.analyze_content(current_content, max_tokens_crit)
                
                if not criticism:
                    st.error(f"❌ Failed to analyze content in iteration {iteration_count}")
                    return
                
                # Extract quality score
                quality_score = self.critic.extract_quality_score(criticism)
                
                # Determine if this is the final iteration
                is_final = quality_score >= quality_threshold
                stopped_at_max = iteration_count >= max_iterations and not is_final
                
                # Store iteration data
                iteration_data = {
                    'prompt': prompt,
                    'content': current_content,
                    'criticism': criticism,
                    'quality_score': quality_score,
                    'iteration_type': iteration_type,
                    'iteration_number': iteration_count,
                    'is_final': is_final,
                    'stopped_at_max': stopped_at_max,
                    'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                st.session_state.iterations.append(iteration_data)
                st.session_state.current_content = current_content
                
                # Show live progress
                with iteration_container.container():
                    st.write(f"**Iteration {iteration_count}** - Quality Score: **{quality_score:.1f}/10**")
                    if is_final:
                        st.success(f"🎉 Quality threshold reached! ({quality_score:.1f} ≥ {quality_threshold})")
                    elif iteration_count < max_iterations:
                        st.info(f"🔄 Continuing to improve... (Target: {quality_threshold}/10)")
                    
                # Store criticism for next iteration
                previous_criticism = criticism
                
                # Check if we should stop
                if is_final:
                    status_text.text(f"✅ Complete! Quality threshold reached in {iteration_count} iterations")
                    break
                elif iteration_count >= max_iterations:
                    status_text.text(f"⚠️ Reached maximum iterations ({max_iterations})")
                    break
                
                # Add a small delay to show progress
                time.sleep(0.5)
            
            progress_bar.progress(100)
            
            # Show final summary
            with iteration_container.container():
                final_score = st.session_state.iterations[-1]['quality_score']
                if final_score >= quality_threshold:
                    st.success(f"🎉 **Successfully reached quality threshold!**")
                    st.write(f"Final Score: **{final_score:.1f}/10** (Target: {quality_threshold}/10)")
                    st.write(f"Iterations needed: **{iteration_count}**")
                else:
                    st.warning(f"⚠️ **Reached maximum iterations without meeting threshold**")
                    st.write(f"Final Score: **{final_score:.1f}/10** (Target: {quality_threshold}/10)")
                    st.write(f"Total Iterations: **{iteration_count}**")
                    st.info("💡 Try lowering the quality threshold or increasing max iterations")
            
            # Clear progress indicators after delay
            time.sleep(2)
            progress_bar.empty()
            status_text.empty()
            
            # Force rerun to update the display
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error during iterative improvement: {str(e)}")
            progress_bar.empty()
            status_text.empty()
            iteration_container.empty()
    
    def generate_and_analyze(self, prompt, max_tokens_gen, max_tokens_crit):
        """Generate content and analyze it (single iteration mode)"""
        
        # Check if agents are initialized
        if not self.generator or not self.critic:
            st.error("❌ AI agents not initialized. Please check your API key.")
            return
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Generate content
            status_text.text("🤖 Generating content...")
            progress_bar.progress(25)
            
            generated_content = self.generator.generate_content(prompt, max_tokens_gen)
            
            if not generated_content:
                st.error("❌ Failed to generate content")
                return
            
            progress_bar.progress(50)
            
            # Step 2: Analyze content
            status_text.text("🔍 Analyzing content...")
            progress_bar.progress(75)
            
            criticism = self.critic.analyze_content(generated_content, max_tokens_crit)
            
            if not criticism:
                st.error("❌ Failed to analyze content")
                return
            
            # Extract quality score
            quality_score = self.critic.extract_quality_score(criticism)
            
            progress_bar.progress(100)
            status_text.text("✅ Complete!")
            
            # Store iteration
            iteration_data = {
                'prompt': prompt,
                'content': generated_content,
                'criticism': criticism,
                'quality_score': quality_score,
                'iteration_type': "Single Generation",
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            st.session_state.iterations.append(iteration_data)
            st.session_state.current_content = generated_content
            
            # Clear progress indicators after a short delay
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
            
            # Force rerun to update the display
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error during generation and analysis: {str(e)}")
            progress_bar.empty()
            status_text.empty()

def main():
    # Page configuration
    st.set_page_config(
        page_title="Self-Critic Agent System",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main > div {
        padding-top: 1rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize and run the system
    system = SelfCriticSystem()
    system.run()

if __name__ == "__main__":
    main()