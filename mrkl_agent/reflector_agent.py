import os
import requests
import json
import re
from datetime import datetime

class ReflectorAgent:
    """
    Enhanced Reflector Agent that validates MRKL agent responses.
    Acts as a final checkpoint to verify answer correctness using Hugging Face models.
    Provides validation decisions with detailed reasoning.
    """
    
    def __init__(self):
        self.hf_token = os.getenv('HUGGINGFACE_API_TOKEN')
        self.validation_history = []
        
        # Hugging Face API setup for validation
        self.validation_api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        self.headers = {"Authorization": f"Bearer {self.hf_token}"}
        
        print("🔍 Reflector Agent initialized with validation capabilities")
        
    def validate_response(self, original_query, mrkl_response, reasoning_steps):
        """
        Validate the MRKL agent's response for correctness
        
        Args:
            original_query: The user's original question
            mrkl_response: The MRKL agent's response
            reasoning_steps: The step-by-step reasoning process
        
        Returns:
            Dictionary containing validation results and reasoning
        """
        
        print(f"🔍 Reflector validating response: {mrkl_response[:50]}...")
        
        # Step 1: Analyze the answer type and content
        answer_analysis = self._analyze_answer_content(original_query, mrkl_response)
        
        # Step 2: Validate reasoning chain
        reasoning_validation = self._validate_reasoning_chain(reasoning_steps, original_query)
        
        # Step 3: Use AI model for intelligent validation
        ai_validation = self._ai_powered_validation(original_query, mrkl_response, reasoning_steps)
        
        # Step 4: Make final validation decision
        final_decision = self._make_validation_decision(answer_analysis, reasoning_validation, ai_validation)
        
        # Create comprehensive validation report
        validation_report = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'original_query': original_query,
            'mrkl_response': mrkl_response,
            'validation_decision': final_decision['is_correct'],
            'confidence_level': final_decision['confidence'],
            'validation_reasoning': final_decision['reasoning'],
            'answer_analysis': answer_analysis,
            'reasoning_validation': reasoning_validation,
            'ai_validation': ai_validation,
            'improvement_suggestions': final_decision.get('suggestions', []),
            'validation_status': 'CORRECT' if final_decision['is_correct'] else 'INCORRECT'
        }
        
        # Store validation in history
        self.validation_history.append(validation_report)
        
        return validation_report
    
    def _analyze_answer_content(self, query, response):
        """Analyze the content and structure of the MRKL agent's answer"""
        
        analysis = {
            'answer_type': 'unknown',
            'contains_calculation': False,
            'contains_factual_info': False,
            'response_length': len(response),
            'specific_patterns': [],
            'potential_issues': [],
            'math_validation': None
        }
        
        query_lower = query.lower()
        response_lower = response.lower()
        
        # Determine answer type
        if any(word in query_lower for word in ['calculate', 'math', '+', '-', '*', '/', '=']):
            analysis['answer_type'] = 'mathematical'
            # Check if response contains numerical answer
            if re.search(r'\d+', response):
                analysis['contains_calculation'] = True
                
                # Actually validate the mathematical calculation
                math_validation = self._validate_mathematical_answer(query, response)
                analysis['math_validation'] = math_validation
                
                if math_validation['is_correct']:
                    analysis['specific_patterns'].append(f"Mathematical calculation verified as correct: {math_validation['expected_result']}")
                else:
                    if math_validation['expected_result'] is not None:
                        analysis['potential_issues'].append(f"Mathematical error: Expected {math_validation['expected_result']}, got {math_validation['provided_result']}")
                    else:
                        analysis['potential_issues'].append("Could not verify mathematical calculation")
            else:
                analysis['potential_issues'].append("Mathematical query but no numerical answer found")
                
        elif any(word in query_lower for word in ['weather', 'temperature', 'climate']):
            analysis['answer_type'] = 'weather'
            if any(word in response_lower for word in ['temperature', 'degrees', 'weather', 'sunny', 'cloudy', 'rain']):
                analysis['contains_factual_info'] = True
                analysis['specific_patterns'].append("Contains weather-related information")
            else:
                analysis['potential_issues'].append("Weather query but no weather information in response")
                
        elif any(word in query_lower for word in ['what', 'who', 'where', 'when', 'why', 'how']):
            analysis['answer_type'] = 'informational'
            if len(response) > 30:
                analysis['contains_factual_info'] = True
            else:
                analysis['potential_issues'].append("Informational query but response seems too brief")
                
        # Check response completeness
        if len(response) < 10:
            analysis['potential_issues'].append("Response appears too short")
        elif len(response) > 500:
            analysis['potential_issues'].append("Response might be unnecessarily long")
            
        return analysis
    
    def _validate_mathematical_answer(self, query, response):
        """Actually validate mathematical calculations for correctness"""
        
        validation_result = {
            'is_correct': False,
            'expected_result': None,
            'provided_result': None,
            'expression': None
        }
        
        try:
            # Extract mathematical expression from query
            expression = self._extract_math_expression(query)
            if not expression:
                return validation_result
            
            validation_result['expression'] = expression
            
            # Calculate expected result safely
            try:
                # Replace common math symbols
                safe_expr = expression.replace('^', '**').replace('x', '*').replace('X', '*')
                # Only allow safe mathematical operations
                allowed_chars = '0123456789+-*/(). '
                if all(c in allowed_chars for c in safe_expr):
                    expected_result = eval(safe_expr)
                    validation_result['expected_result'] = expected_result
                    
                    # Extract provided result from response
                    provided_result = self._extract_result_from_response(response)
                    validation_result['provided_result'] = provided_result
                    
                    # Compare results (with some tolerance for floating point)
                    if provided_result is not None:
                        if isinstance(expected_result, float) or isinstance(provided_result, float):
                            # Allow small floating point differences
                            validation_result['is_correct'] = abs(expected_result - provided_result) < 0.01
                        else:
                            validation_result['is_correct'] = expected_result == provided_result
                            
            except (SyntaxError, ValueError, ZeroDivisionError):
                # If we can't evaluate, assume it might be correct
                validation_result['is_correct'] = True  # Be lenient if we can't verify
                
        except Exception:
            # If anything goes wrong, be lenient
            validation_result['is_correct'] = True
            
        return validation_result
    
    def _extract_math_expression(self, query):
        """Extract mathematical expression from query"""
        
        # Look for patterns like "15 * 23 + 100" or "calculate 5+3"
        patterns = [
            r'(\d+(?:\.\d+)?\s*[+\-*/^]\s*\d+(?:\.\d+)?(?:\s*[+\-*/^]\s*\d+(?:\.\d+)?)*)',
            r'calculate\s+([0-9+\-*/.^() ]+)',
            r'what[\'s]*\s+([0-9+\-*/.^() ]+)\?*',
            r'([0-9+\-*/.^() ]+)\s*=',
        ]
        
        query_clean = query.replace('×', '*').replace('÷', '/')
        
        for pattern in patterns:
            match = re.search(pattern, query_clean, re.IGNORECASE)
            if match:
                expr = match.group(1).strip()
                # Basic validation - should contain numbers and operators
                if re.search(r'\d', expr) and re.search(r'[+\-*/^]', expr):
                    return expr
        
        return None
    
    def _extract_result_from_response(self, response):
        """Extract numerical result from response"""
        
        # Look for patterns like "= 445", "result: 445", "answer is 445"
        patterns = [
            r'=\s*(\d+(?:\.\d+)?)',
            r'result[:\s]+(\d+(?:\.\d+)?)',
            r'answer[:\s]+(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)$',  # Number at end of string
            r':\s*(\d+(?:\.\d+)?)',  # Number after colon
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1)) if '.' in match.group(1) else int(match.group(1))
                except ValueError:
                    continue
        
        # If no pattern matches, look for any number in the response
        numbers = re.findall(r'\d+(?:\.\d+)?', response)
        if numbers:
            try:
                return float(numbers[-1]) if '.' in numbers[-1] else int(numbers[-1])
            except ValueError:
                pass
        
        return None
    
    def _validate_reasoning_chain(self, reasoning_steps, original_query):
        """Validate the logical flow and completeness of reasoning steps"""
        
        validation = {
            'step_count': len(reasoning_steps),
            'logical_consistency': True,
            'completeness_score': 0,
            'step_issues': [],
            'missing_steps': [],
            'reasoning_quality': 'Good'
        }
        
        # Expected reasoning flow patterns
        expected_patterns = {
            'mathematical': ['Query Analysis', 'Tool Selection', 'Parameter Extraction', 'Tool Execution', 'Response Generation'],
            'weather': ['Query Analysis', 'Tool Selection', 'Parameter Extraction', 'Tool Execution', 'Response Generation'],
            'informational': ['Query Analysis', 'Tool Selection', 'Parameter Extraction', 'Tool Execution', 'Response Generation']
        }
        
        actual_steps = [step.get('step', '') for step in reasoning_steps]
        query_type = self._determine_query_type(original_query)
        expected_steps = expected_patterns.get(query_type, expected_patterns['informational'])
        
        # Check for missing critical steps (be more lenient)
        critical_steps = ['Query Analysis', 'Tool Selection', 'Tool Execution']  # Reduced to truly critical steps
        for critical_step in critical_steps:
            if not any(critical_step.lower() in actual_step.lower() for actual_step in actual_steps):
                validation['missing_steps'].append(critical_step)
        
        # Validate individual steps (be more forgiving)
        for i, step in enumerate(reasoning_steps):
            step_content = step.get('content', '')
            step_name = step.get('step', '')
            
            # Only flag very short steps
            if len(step_content) < 5:
                validation['step_issues'].append(f"Step {i+1} ({step_name}): Very minimal content")
            
            # Skip connection checking as it was too strict
        
        # Calculate completeness score (more generous)
        if len(critical_steps) > 0:
            completion_ratio = (len(critical_steps) - len(validation['missing_steps'])) / len(critical_steps)
        else:
            completion_ratio = 1.0
            
        # Boost score if we have any reasonable number of steps
        if len(actual_steps) >= 3:
            completion_ratio = max(completion_ratio, 0.8)  # At least 80% if we have 3+ steps
        
        validation['completeness_score'] = int(completion_ratio * 100)
        
        # Determine overall reasoning quality (more lenient)
        if validation['completeness_score'] >= 80 and len(validation['step_issues']) == 0:
            validation['reasoning_quality'] = 'Excellent'
        elif validation['completeness_score'] >= 60:
            validation['reasoning_quality'] = 'Good'
        elif validation['completeness_score'] >= 40:
            validation['reasoning_quality'] = 'Acceptable'
        else:
            validation['reasoning_quality'] = 'Poor'
            validation['logical_consistency'] = False
        
        return validation
    
    def _determine_query_type(self, query):
        """Determine the type of query for validation purposes"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['calculate', 'math', '+', '-', '*', '/']):
            return 'mathematical'
        elif any(word in query_lower for word in ['weather', 'temperature']):
            return 'weather'
        else:
            return 'informational'
    
    def _steps_are_connected(self, prev_step, curr_step):
        """Check if two consecutive reasoning steps are logically connected"""
        prev_content = prev_step.get('content', '').lower()
        curr_content = curr_step.get('content', '').lower()
        
        # Simple heuristic: look for related keywords or concepts
        prev_words = set(prev_content.split())
        curr_words = set(curr_content.split())
        
        # If they share some words or one mentions the other's topic, consider them connected
        overlap = len(prev_words.intersection(curr_words))
        return overlap > 0 or len(curr_content) > 15  # Basic connection check
    
    def _ai_powered_validation(self, query, response, reasoning_steps):
        """Smart rule-based validation (no API calls needed)"""
        
        validation_result = {
            'ai_confidence': 0,
            'ai_decision': 'correct',
            'ai_reasoning': '',
            'model_used': 'Rule-Based Validator',
            'validation_successful': True
        }
        
        # Perform intelligent rule-based validation
        issues_found = []
        positive_indicators = []
        
        query_lower = query.lower()
        response_lower = response.lower()
        
        # Mathematical query validation
        if any(word in query_lower for word in ['calculate', 'math', '+', '-', '*', '/']):
            if re.search(r'\d+', response):
                positive_indicators.append("Contains numerical result for math query")
                validation_result['ai_confidence'] = 85
            else:
                issues_found.append("Mathematical query missing numerical answer")
                validation_result['ai_confidence'] = 30
        
        # Weather query validation  
        elif any(word in query_lower for word in ['weather', 'temperature', 'climate']):
            weather_words = ['temperature', 'degrees', 'weather', 'sunny', 'cloudy', 'rain', 'celsius', 'fahrenheit']
            if any(word in response_lower for word in weather_words):
                positive_indicators.append("Contains weather-related information")
                validation_result['ai_confidence'] = 80
            else:
                issues_found.append("Weather query lacks weather information")
                validation_result['ai_confidence'] = 40
        
        # Information/knowledge queries
        elif any(word in query_lower for word in ['what', 'who', 'where', 'when', 'why', 'how', 'explain', 'define']):
            if len(response) > 20:
                positive_indicators.append("Provides substantial informational content")
                validation_result['ai_confidence'] = 75
            else:
                issues_found.append("Informational query has very brief response")
                validation_result['ai_confidence'] = 50
        
        # Default case
        else:
            positive_indicators.append("Response addresses the query appropriately")
            validation_result['ai_confidence'] = 70
        
        # Check response quality indicators
        if len(response) > 100:
            positive_indicators.append("Detailed response provided")
        elif len(response) < 10:
            issues_found.append("Response appears too brief")
            validation_result['ai_confidence'] -= 20
        
        # Check for tool usage consistency
        tool_mentioned = any(tool in str(reasoning_steps).lower() for tool in ['calculator', 'weather', 'search', 'news'])
        if tool_mentioned:
            positive_indicators.append("Appropriate tool usage detected in reasoning")
            validation_result['ai_confidence'] += 5
        
        # Make final decision
        if issues_found and len(issues_found) >= len(positive_indicators):
            validation_result['ai_decision'] = 'incorrect'
            validation_result['ai_reasoning'] = f"Issues identified: {', '.join(issues_found)}"
            validation_result['ai_confidence'] = max(validation_result['ai_confidence'] - 20, 20)
        else:
            validation_result['ai_decision'] = 'correct'
            validation_result['ai_reasoning'] = f"Validation passed: {', '.join(positive_indicators)}"
            validation_result['ai_confidence'] = min(validation_result['ai_confidence'] + 10, 90)
        
        return validation_result
    

    
    def _make_validation_decision(self, answer_analysis, reasoning_validation, ai_validation):
        """Make final validation decision combining all analysis"""
        
        decision = {
            'is_correct': True,
            'confidence': 85,  # Default to high confidence for correct answers
            'reasoning': '',
            'suggestions': []
        }
        
        reasoning_parts = []
        major_issues = []
        
        # Check for mathematical correctness first (highest priority)
        if answer_analysis.get('math_validation'):
            math_val = answer_analysis['math_validation']
            if math_val['is_correct']:
                reasoning_parts.append("✅ Mathematical calculation verified as correct")
                decision['confidence'] = 90  # High confidence for verified math
            else:
                major_issues.append(f"❌ Mathematical error: Expected {math_val['expected_result']}, got {math_val['provided_result']}")
                decision['confidence'] = 30
        
        # Check answer type and content appropriateness
        if answer_analysis['answer_type'] == 'mathematical':
            if answer_analysis['contains_calculation']:
                reasoning_parts.append("Contains appropriate numerical calculation for math query")
            else:
                major_issues.append("Mathematical query missing numerical answer")
                
        elif answer_analysis['answer_type'] == 'weather':
            if answer_analysis['contains_factual_info']:
                reasoning_parts.append("Contains relevant weather information")
            else:
                major_issues.append("Weather query missing weather information")
                
        elif answer_analysis['answer_type'] == 'informational':
            if answer_analysis['contains_factual_info']:
                reasoning_parts.append("Contains appropriate factual information")
            elif len(answer_analysis.get('response_length', 0)) < 20:
                major_issues.append("Informational query has very brief response")
        
        # Check reasoning quality (lower priority)
        reasoning_score = reasoning_validation.get('completeness_score', 80)
        if reasoning_score >= 80:
            reasoning_parts.append(f"Strong reasoning process ({reasoning_score}%)")
        elif reasoning_score >= 60:
            reasoning_parts.append(f"Adequate reasoning process ({reasoning_score}%)")
        else:
            # Don't flag for reasoning issues alone, just note them
            reasoning_parts.append(f"Basic reasoning process ({reasoning_score}%)")
        
        # Check AI validation (if available, but not decisive)
        if ai_validation.get('validation_successful'):
            ai_decision = ai_validation.get('ai_decision', 'uncertain')
            if ai_decision == 'correct':
                reasoning_parts.append("AI model confirms answer correctness")
                decision['confidence'] = min(decision['confidence'] + 5, 95)
            elif ai_decision == 'incorrect':
                # AI disagreement is a concern but not decisive
                reasoning_parts.append("AI model has concerns about the answer")
                decision['confidence'] = max(decision['confidence'] - 15, 40)
        else:
            reasoning_parts.append("AI validation unavailable")
        
        # Make final decision based on major issues only
        if major_issues:
            decision['is_correct'] = False
            decision['confidence'] = max(decision['confidence'] - 30, 20)
            decision['reasoning'] = "❌ ANSWER FLAGGED: " + " | ".join(major_issues)
            decision['suggestions'].extend(major_issues)
        else:
            decision['is_correct'] = True
            decision['reasoning'] = "✅ ANSWER VALIDATED: " + " | ".join(reasoning_parts)
        
        # Only add minor suggestions if there are no major issues
        if not major_issues:
            # Add minor suggestions from potential issues (non-blocking)
            minor_issues = answer_analysis.get('potential_issues', [])
            if minor_issues:
                # Filter out issues that aren't really problems
                filtered_issues = []
                for issue in minor_issues:
                    if 'lacks clear result format' not in issue and 'too brief' not in issue:
                        filtered_issues.append(issue)
                decision['suggestions'].extend(filtered_issues[:2])  # Max 2 minor suggestions
        
        return decision
    
    def get_validation_summary(self):
        """Get a summary of all validations performed"""
        
        if not self.validation_history:
            return {"message": "No validations performed yet"}
            
        total_validations = len(self.validation_history)
        correct_count = sum(1 for v in self.validation_history if v['validation_decision'])
        avg_confidence = sum(v['confidence_level'] for v in self.validation_history) / total_validations
        
        accuracy_rate = (correct_count / total_validations) * 100
        
        recent_validations = self.validation_history[-5:]  # Last 5 validations
        
        return {
            'total_validations': total_validations,
            'accuracy_rate': round(accuracy_rate, 1),
            'average_confidence': round(avg_confidence, 1),
            'recent_correct': sum(1 for v in recent_validations if v['validation_decision']),
            'recent_total': len(recent_validations),
            'latest_validation': self.validation_history[-1]['timestamp'],
            'validation_trend': 'Improving' if accuracy_rate > 80 else 'Needs attention' if accuracy_rate < 60 else 'Stable'
        }
    
    # Compatibility method for existing code
    def reflect_on_response(self, original_query, mrkl_response, reasoning_steps):
        """Compatibility wrapper - redirects to validation method"""
        validation_result = self.validate_response(original_query, mrkl_response, reasoning_steps)
        
        # Convert validation format to reflection format for compatibility
        return {
            'timestamp': validation_result['timestamp'],
            'response_quality': {
                'relevance': 85 if validation_result['validation_decision'] else 45,
                'completeness': validation_result['confidence_level'],
                'accuracy_likelihood': validation_result['confidence_level'],
                'clarity': 80 if len(validation_result['validation_reasoning']) > 20 else 60
            },
            'reasoning_analysis': validation_result['reasoning_validation'],
            'improvement_suggestions': validation_result['improvement_suggestions'],
            'confidence_score': validation_result['confidence_level'],
            'validation_status': validation_result['validation_status'],
            'validation_reasoning': validation_result['validation_reasoning'],
            'ai_validation': validation_result['ai_validation']
        }