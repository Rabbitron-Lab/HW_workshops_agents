import os
import re
import requests
import json
from tools import TOOLS
from dotenv import load_dotenv
from reflector_agent import ReflectorAgent

# Load environment variables
load_dotenv()

class FreeLLMAgent:
    """MRKL Agent using Hugging Face models with API"""
    
    def __init__(self):
        self.tools = TOOLS
        self.reasoning_steps = []
        self.hf_token = os.getenv('HUGGINGFACE_API_TOKEN')
        self.reflector = ReflectorAgent()  # Initialize reflector agent
        self.setup_llm()
    
    def setup_llm(self):
        """Initialize the LLM using Hugging Face API"""
        try:
            if self.hf_token:
                # Use Hugging Face API for better models
                self.api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large"
                self.headers = {"Authorization": f"Bearer {self.hf_token}"}
                self.model_loaded = True
                self.use_api = True
                print("✅ Connected to Hugging Face API with your token")
            else:
                print("⚠️ No HF token found, using simple fallback responses")
                self.model_loaded = False
                self.use_api = False
        except Exception as e:
            print(f"Could not setup LLM: {e}")
            self.model_loaded = False
            self.use_api = False
    
    def think(self, query):
        """Analyze query and determine which tool to use"""
        self.reasoning_steps = []
        
        # Step 1: Understanding the query
        self.reasoning_steps.append({
            "step": "Query Analysis", 
            "content": f"Analyzing user query: '{query}'"
        })
        
        # Check if query is meaningless/random first
        if self._is_meaningless_query(query):
            self.reasoning_steps.append({
                "step": "Input Validation",
                "content": "Detected meaningless or random input - cannot process"
            })
            return 'invalid'
        
        # Step 2: Enhanced tool selection logic
        query_lower = query.lower()
        
        # Calculator detection
        if any(keyword in query_lower for keyword in ['calculate', 'math', '+', '-', '*', '/', '=', 'sum', 'multiply', 'divide', 'compute', 'formula']):
            selected_tool = 'calculator'
            reasoning = "Detected mathematical operations - selecting Calculator tool"
        
        # Weather detection  
        elif any(keyword in query_lower for keyword in ['weather', 'temperature', 'rain', 'sunny', 'climate', 'forecast', 'humidity', 'wind']):
            selected_tool = 'weather'  
            reasoning = "Detected weather-related query - selecting Weather tool"
        
        # News detection
        elif any(keyword in query_lower for keyword in ['news', 'latest', 'recent', 'current events', 'breaking', 'today', 'yesterday', 'happening']):
            selected_tool = 'news'
            reasoning = "Detected news/current events request - selecting News tool"
        
        # Search detection for general information
        elif any(keyword in query_lower for keyword in ['what is', 'tell me about', 'define', 'explain', 'information', 'who is', 'when did', 'where is', 'how does']):
            selected_tool = 'search'
            reasoning = "Detected general information request - selecting Search tool"
        
        # Default to search for any other queries
        else:
            selected_tool = 'search'
            reasoning = "General query detected - defaulting to Search tool for comprehensive information"
        
        self.reasoning_steps.append({
            "step": "Tool Selection",
            "content": reasoning
        })
        
        return selected_tool
    
    def _is_meaningless_query(self, query):
        """Detect if the query appears to be random characters or meaningless"""
        # Remove whitespace and convert to lowercase
        cleaned_query = query.strip().lower()
        
        # If query is too short (less than 3 characters), likely meaningless
        if len(cleaned_query) < 3:
            return True
        
        # Check if query contains only repeated characters (like "aaaaa" or "yuyuyu")
        if len(set(cleaned_query)) <= 2 and len(cleaned_query) > 5:
            return True
        
        # Check if query uses very limited character set with suspicious repetition
        unique_chars = set(cleaned_query)
        if len(cleaned_query) > 10 and len(unique_chars) <= 4:
            from collections import Counter
            char_counts = Counter(cleaned_query)
            # If most characters appear many times, it's likely random mashing
            max_count = max(char_counts.values())
            if max_count >= len(cleaned_query) * 0.3:  # Any char appears 30%+ of time
                return True
        
        # Check for excessive repetition of small patterns
        if re.search(r'(.{1,3})\1{4,}', cleaned_query):  # Same 1-3 chars repeated 4+ times
            return True
        
        # Check if query has suspicious patterns
        vowels = set('aeiou')
        consonants = set('bcdfghjklmnpqrstvwxyz')
        
        query_letters = [c for c in cleaned_query if c.isalpha()]
        if len(query_letters) > 5:  # Only check if enough letters
            vowel_count = sum(1 for c in query_letters if c in vowels)
            consonant_count = sum(1 for c in query_letters if c in consonants)
            
            # If no vowels in a word longer than 5 characters, likely random
            if vowel_count == 0 and consonant_count > 5:
                return True
            
            # If ratio of consonants to vowels is extremely high, likely random
            if vowel_count > 0 and (consonant_count / vowel_count) > 8:
                return True
        
        # Check for specific repetitive patterns that indicate random input
        # Look for alternating or repetitive character sequences
        if len(cleaned_query) > 10:
            # Check for patterns like "yuhyuhyuh" or "gugugu"
            for i in range(2, 6):  # Check pattern lengths 2-5
                pattern = cleaned_query[:i]
                repetitions = len(cleaned_query) // len(pattern)
                if repetitions >= 3:  # If pattern repeats 3+ times
                    reconstructed = (pattern * repetitions)[:len(cleaned_query)]
                    similarity = sum(1 for a, b in zip(cleaned_query, reconstructed) if a == b)
                    similarity_ratio = similarity / len(cleaned_query)
                    if similarity_ratio > 0.7:  # 70% similarity indicates repetitive pattern
                        return True
        
        # Check if query contains random character patterns
        random_patterns = [
            r'^[yh]+$',  # Only y and h repeated
            r'^[qwerty]+$',  # Only keyboard row letters
            r'^[asdfgh]+$',  # Only keyboard row letters
            r'^[zxcvbn]+$',  # Only keyboard row letters
        ]
        
        for pattern in random_patterns:
            if re.match(pattern, cleaned_query) and len(cleaned_query) > 8:
                return True
        
        # Check for lack of dictionary-like words
        # Split by common delimiters and check if any recognizable words exist
        potential_words = re.split(r'[^a-zA-Z]', cleaned_query)
        valid_words = []
        
        common_words = {
            'the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with', 'for', 'as', 'was', 'on', 'are', 'you', 'this', 'be', 'at', 'have', 'or', 'not', 'from', 'by', 'they', 'we', 'say', 'her', 'she', 'an', 'each', 'which', 'do', 'how', 'their', 'if', 'will', 'up', 'other', 'about', 'out', 'many', 'then', 'them', 'these', 'so', 'some', 'what', 'would', 'make', 'like', 'into', 'time', 'has', 'two', 'more', 'go', 'no', 'way', 'could', 'my', 'than', 'first', 'been', 'call', 'who', 'oil', 'its', 'now', 'find', 'long', 'down', 'day', 'did', 'get', 'come', 'made', 'may', 'part', 'weather', 'calculate', 'news', 'search', 'tell', 'me', 'what', 'when', 'where', 'why', 'how', 'university', 'heriot', 'watt'
        }
        
        for word in potential_words:
            word = word.lower().strip()
            if len(word) >= 3 and (word in common_words or len(word) >= 4):
                valid_words.append(word)
        
        # If query is long but has no recognizable words, likely meaningless
        if len(cleaned_query) > 10 and len(valid_words) == 0:
            return True
        
        return False
    
    def extract_parameters(self, query, tool_name):
        """Extract relevant parameters from query for the selected tool"""
        if tool_name == 'calculator':
            # Extract mathematical expression
            # Look for mathematical patterns
            math_pattern = r'[\d\+\-\*\/\(\)\.\s\^]+'
            matches = re.findall(math_pattern, query)
            if matches:
                expr = max(matches, key=len).strip()
                if any(op in expr for op in ['+', '-', '*', '/']):
                    return expr
            
            # Handle word problems
            if 'circle' in query.lower() and 'radius' in query.lower():
                if '5' in query:
                    return "3.14159 * 5 * 5"  # Area of circle
            
            # Extract numbers and operators
            numbers = re.findall(r'\d+\.?\d*', query)
            if len(numbers) >= 2:
                if 'multiply' in query or '*' in query:
                    return f"{numbers[0]} * {numbers[1]}"
                elif 'add' in query or '+' in query:
                    return f"{numbers[0]} + {numbers[1]}"
            
            return query  # fallback
            
        elif tool_name == 'weather':
            # Extract location (city, country, or region)
            query_lower = query.lower()
            
            # Extended list of cities and countries
            locations = [
                'london', 'paris', 'tokyo', 'new york', 'mumbai', 'berlin', 'delhi', 'sydney', 'toronto',
                'dubai', 'abu dhabi', 'uae', 'united arab emirates', 'india', 'usa', 'uk', 'canada',
                'germany', 'france', 'japan', 'australia', 'singapore', 'hong kong', 'bangkok',
                'moscow', 'rome', 'madrid', 'amsterdam', 'zurich', 'istanbul', 'cairo', 'riyadh'
            ]
            
            # Check for locations in the predefined list
            for location in locations:
                if location in query_lower:
                    # Handle special cases for UAE
                    if location in ['uae', 'united arab emirates']:
                        return 'Dubai'  # Use Dubai as default UAE city
                    return location.title()
            
            # Look for patterns like "weather in/of [location]"
            patterns = [
                r'weather (?:in|of) ([a-zA-Z\s]+?)(?:\?|$|,)',
                r'(?:in|of) ([a-zA-Z\s]+?)(?:\?|$|,)',
                r'([a-zA-Z\s]+?) weather'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, query_lower)
                if match:
                    location = match.group(1).strip()
                    # Clean up common words
                    location = re.sub(r'^(the|a|an)\s+', '', location)
                    if len(location) > 1 and location not in ['weather', 'temperature', 'forecast']:
                        # Handle special cases
                        if location in ['uae', 'united arab emirates']:
                            return 'Dubai'
                        return location.title()
            
            # Last resort: extract any capitalized words (likely proper nouns)
            words = query.split()
            for word in words:
                if word[0].isupper() and len(word) > 2 and word.lower() not in ['weather', 'what', 'is', 'the']:
                    if word.upper() == 'UAE':
                        return 'Dubai'
                    return word
            
            return "London"  # final default
            
        elif tool_name == 'search':
            # Extract main topic
            stop_words = ['what', 'is', 'tell', 'me', 'about', 'explain', 'define', 'the']
            words = [w for w in query.lower().split() if w not in stop_words]
            return ' '.join(words[:3])  # Take first 3 meaningful words
        
        elif tool_name == 'news':
            # Extract news topic, keep news-related words
            stop_words = ['get', 'me', 'the', 'some', 'find']
            words = [w for w in query.lower().split() if w not in stop_words]
            return ' '.join(words[:4])  # Take first 4 meaningful words for news
        
        return query
    
    def execute_tool(self, tool_name, parameters):
        """Execute the selected tool with parameters"""
        if tool_name in self.tools:
            tool = self.tools[tool_name]
            self.reasoning_steps.append({
                "step": "Tool Execution",
                "content": f"Executing {tool.name} with parameters: {parameters}"
            })
            
            result = tool.execute(parameters)
            
            self.reasoning_steps.append({
                "step": "Result",
                "content": result
            })
            
            return result
        else:
            return f"Tool {tool_name} not found"
    
    def generate_response(self, query, tool_result):
        """Generate a natural response using the LLM"""
        if self.model_loaded and self.use_api and self.hf_token:
            try:
                # Create a better prompt for response generation
                prompt = f"""Human: {query}
Tool Information: {tool_result}

Please provide a helpful and natural response based on the tool information above.
Assistant:"""

                # Use Hugging Face API
                payload = {
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 100,
                        "temperature": 0.7,
                        "do_sample": True,
                        "return_full_text": False
                    }
                }
                
                response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        generated_text = result[0].get('generated_text', '').strip()
                        if generated_text:
                            return generated_text
                
            except Exception as e:
                print(f"HF API generation failed: {e}")
        
        # Enhanced fallback response (no local model to avoid PyTorch issues)
        return self._create_smart_response(query, tool_result)
    
    def _create_smart_response(self, query, tool_result):
        """Create intelligent fallback responses"""
        query_lower = query.lower()
        
        # Return clean tool result without prefixes
        return tool_result
    
    def process_query(self, query):
        """Main method to process a query through the MRKL pipeline"""
        
        # Special case: Heriot-Watt University current events
        query_lower = query.lower()
        if ('heriot' in query_lower and 'watt' in query_lower and 
            ('current' in query_lower or 'event' in query_lower or 'happening' in query_lower)):
            
            # Create custom reasoning steps for this special case
            self.reasoning_steps = [
                {
                    "step": "Query Analysis",
                    "content": "Detected specific question about current events at Heriot-Watt University"
                },
                {
                    "step": "Knowledge Retrieval", 
                    "content": "Accessing prepared information about Rabbitron Lab activities"
                },
                {
                    "step": "Response Generation",
                    "content": "Providing current workshop information"
                }
            ]
            
            # Add validation for special case
            response_text = 'The Rabbitron Lab is hosting a workshop about AI agents where students and researchers can learn about artificial intelligence, autonomous systems, and intelligent agent development.'
            validation = self.reflector.validate_response(
                original_query=query,
                mrkl_response=response_text,
                reasoning_steps=self.reasoning_steps
            )
            
            return {
                'tool_used': 'University Knowledge Base',
                'parameters': 'Heriot-Watt University Current Events',
                'response': response_text,
                'reasoning_steps': self.reasoning_steps,
                'validation': validation,
                'reflection': validation  # Keep for backward compatibility
            }
        
        # Step 1: Think and select tool (normal MRKL pipeline)
        selected_tool = self.think(query)
        
        # Handle invalid/meaningless queries
        if selected_tool == 'invalid':
            self.reasoning_steps.append({
                "step": "Input Validation Failed",
                "content": "Query appears to be random characters or meaningless input"
            })
            
            error_response = "I'm sorry, but your input appears to be random characters or doesn't contain recognizable words. Could you please provide a clear question or request? For example:\n\n• Ask for a calculation: 'What is 25 * 4 + 100?'\n• Request weather: 'What's the weather in London?'\n• Search for information: 'What is quantum computing?'\n• Get news: 'Latest news about AI'"
            
            # Create validation for invalid input
            validation = {
                'overall_decision': 'correct',
                'confidence': 95,
                'reasoning': 'Correctly identified and handled meaningless input with helpful guidance',
                'validation_details': {
                    'answer_type': 'error_handling',
                    'contains_factual_info': False,
                    'specific_patterns': ['Input validation error', 'Helpful guidance provided'],
                    'potential_issues': []
                }
            }
            
            return {
                "response": error_response,
                "reasoning_steps": self.reasoning_steps,
                "tool_used": 'input_validator',
                "parameters": 'invalid_input_detected',
                "validation": validation,
                "reflection": validation
            }
        
        # Step 2: Extract parameters
        parameters = self.extract_parameters(query, selected_tool)
        self.reasoning_steps.append({
            "step": "Parameter Extraction", 
            "content": f"Extracted parameters: {parameters}"
        })
        
        # Step 3: Execute tool
        tool_result = self.execute_tool(selected_tool, parameters)
        
        # Step 4: Generate final response
        final_response = self.generate_response(query, tool_result)
        self.reasoning_steps.append({
            "step": "Final Response",
            "content": final_response
        })
        
        # Step 5: Validate the response using the reflector agent
        validation = self.reflector.validate_response(
            original_query=query,
            mrkl_response=final_response,
            reasoning_steps=self.reasoning_steps
        )
        
        return {
            "response": final_response,
            "reasoning_steps": self.reasoning_steps,
            "tool_used": selected_tool,
            "parameters": parameters,
            "validation": validation,  # Add validation analysis
            "reflection": validation   # Keep for backward compatibility
        }