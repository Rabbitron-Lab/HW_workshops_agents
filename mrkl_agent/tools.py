import requests
import math
import os
import wikipedia
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MRKLTool:
    """Base class for MRKL tools"""
    def __init__(self, name, description):
        self.name = name
        self.description = description
    
    def execute(self, *args, **kwargs):
        raise NotImplementedError

class Calculator(MRKLTool):
    def __init__(self):
        super().__init__(
            "calculator",
            "Useful for performing mathematical calculations. Input should be a mathematical expression like '2+2' or '3.14*5^2'"
        )
    
    def execute(self, expression):
        """Safely evaluate mathematical expressions"""
        try:
            # Replace common math functions
            safe_expression = expression.replace('^', '**')
            safe_expression = safe_expression.replace('π', str(math.pi))
            safe_expression = safe_expression.replace('pi', str(math.pi))
            
            # Only allow safe operations
            allowed_chars = set('0123456789+-*/.() ')
            if all(c in allowed_chars or c.isalnum() for c in safe_expression):
                result = eval(safe_expression)
                return f"Calculation: {expression} = {result}"
            else:
                return "Error: Invalid characters in expression"
        except Exception as e:
            return f"Error calculating {expression}: {str(e)}"

class Weather(MRKLTool):
    def __init__(self):
        super().__init__(
            "weather", 
            "Get current weather information for any city. Input should be a city name like 'London' or 'New York'"
        )
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
    
    def execute(self, city):
        """Get real weather info using OpenWeatherMap API"""
        if not self.api_key or self.api_key == 'your_openweather_api_key_here':
            # Fallback to free weather service
            return self._get_free_weather(city)
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                temp = data['main']['temp']
                desc = data['weather'][0]['description'].title()
                humidity = data['main']['humidity']
                feels_like = data['main']['feels_like']
                
                return f"Current weather in {city.title()}: {temp}°C (feels like {feels_like}°C), {desc}, Humidity: {humidity}%"
            else:
                return f"Could not get weather for {city}. Please check city name."
        except Exception as e:
            return f"Error getting weather for {city}: {str(e)}"
    
    def _get_free_weather(self, city):
        """Fallback free weather service using wttr.in"""
        try:
            # Use wttr.in free weather API
            url = f"http://wttr.in/{city}?format=%C+%t+%h"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                weather_data = response.text.strip()
                return f"Current weather in {city.title()}: {weather_data}"
            else:
                return f"Could not get weather for {city}"
        except Exception as e:
            return f"Weather service temporarily unavailable for {city}"

class Search(MRKLTool):
    def __init__(self):
        super().__init__(
            "search",
            "Search for real-time information about any topic using web search and Wikipedia. Input should be a topic or question like 'latest news about AI' or 'what is Python'"
        )
        self.serpapi_key = os.getenv('SERPAPI_KEY')
    
    def execute(self, query):
        """Search for real information using SerpAPI and Wikipedia"""
        # Try SerpAPI first for real-time web results
        if self.serpapi_key:
            serpapi_result = self._search_serpapi(query)
            if serpapi_result:
                return serpapi_result
        
        # Fallback to Wikipedia
        return self._search_wikipedia(query)
    
    def _search_serpapi(self, query):
        """Search using SerpAPI for real-time web results"""
        try:
            from serpapi import GoogleSearch
            
            params = {
                "q": query,
                "api_key": self.serpapi_key,
                "engine": "google",
                "num": 3
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            if "organic_results" in results and results["organic_results"]:
                # Format the top 3 results
                search_results = []
                for i, result in enumerate(results["organic_results"][:3], 1):
                    title = result.get("title", "No title")
                    snippet = result.get("snippet", "No description available")
                    link = result.get("link", "")
                    
                    search_results.append(f"{i}. {title}\n   {snippet}\n   Source: {link}")
                
                return f"Real-time search results for '{query}':\n\n" + "\n\n".join(search_results)
            
            return None
            
        except ImportError:
            # serpapi package not installed, try requests
            return self._search_serpapi_requests(query)
        except Exception as e:
            print(f"SerpAPI search failed: {e}")
            return None
    
    def _search_serpapi_requests(self, query):
        """Backup SerpAPI search using requests"""
        try:
            url = "https://serpapi.com/search"
            params = {
                "q": query,
                "api_key": self.serpapi_key,
                "engine": "google",
                "num": 3
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                results = response.json()
                
                if "organic_results" in results and results["organic_results"]:
                    search_results = []
                    for i, result in enumerate(results["organic_results"][:3], 1):
                        title = result.get("title", "No title")
                        snippet = result.get("snippet", "No description available")
                        link = result.get("link", "")
                        
                        search_results.append(f"{i}. {title}\n   {snippet}\n   Source: {link}")
                    
                    return f"Real-time search results for '{query}':\n\n" + "\n\n".join(search_results)
            
            return None
            
        except Exception as e:
            print(f"SerpAPI requests search failed: {e}")
            return None
    
    def _search_wikipedia(self, query):
        """Fallback Wikipedia search"""
        try:
            # Clean the query
            clean_query = self._clean_search_query(query)
            
            # Set Wikipedia language to English
            wikipedia.set_lang("en")
            
            # Search for the topic
            search_results = wikipedia.search(clean_query, results=3)
            
            if not search_results:
                return f"No information found for '{query}'. Try a different search term."
            
            # Get the first result
            try:
                page = wikipedia.page(search_results[0])
                summary = wikipedia.summary(search_results[0], sentences=3)
                
                return f"Wikipedia information about '{query}':\n\n{summary}\n\nSource: {page.url}"
                
            except wikipedia.DisambiguationError as e:
                # If there are multiple pages, try the first option
                try:
                    page = wikipedia.page(e.options[0])
                    summary = wikipedia.summary(e.options[0], sentences=3)
                    return f"Wikipedia information about '{query}' ({e.options[0]}):\n\n{summary}\n\nSource: {page.url}"
                except:
                    return f"Multiple articles found for '{query}'. Please be more specific. Options: {', '.join(e.options[:5])}"
            
            except wikipedia.PageError:
                return f"Could not find detailed information about '{query}'."
                
        except Exception as e:
            return f"Search error for '{query}': {str(e)}"
    
    def _clean_search_query(self, query):
        """Clean and optimize the search query"""
        # Remove question words but keep important context
        stop_words = ['tell', 'me', 'about', 'explain', 'define']
        
        words = query.lower().split()
        cleaned_words = [word for word in words if word not in stop_words]
        
        # If all words were removed, return original query
        if not cleaned_words:
            return query
        
        return ' '.join(cleaned_words)

class News(MRKLTool):
    def __init__(self):
        super().__init__(
            "news",
            "Get latest news and current events about any topic. Input should be a news topic like 'latest AI news' or 'current events in technology'"
        )
        self.serpapi_key = os.getenv('SERPAPI_KEY')
    
    def execute(self, query):
        """Get latest news using SerpAPI Google News"""
        if not self.serpapi_key:
            return "News search requires API key. Using general search instead."
        
        try:
            # Add 'news' to query if not present
            if 'news' not in query.lower() and 'latest' not in query.lower():
                query = f"latest news {query}"
            
            url = "https://serpapi.com/search"
            params = {
                "q": query,
                "api_key": self.serpapi_key,
                "engine": "google",
                "tbm": "nws",  # News search
                "num": 5
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                results = response.json()
                
                if "news_results" in results and results["news_results"]:
                    news_items = []
                    for i, news in enumerate(results["news_results"][:5], 1):
                        title = news.get("title", "No title")
                        snippet = news.get("snippet", "")
                        source = news.get("source", "Unknown source")
                        date = news.get("date", "")
                        link = news.get("link", "")
                        
                        news_item = f"{i}. {title}"
                        if date:
                            news_item += f" ({date})"
                        news_item += f"\n   Source: {source}"
                        if snippet:
                            news_item += f"\n   {snippet}"
                        if link:
                            news_item += f"\n   Link: {link}"
                        
                        news_items.append(news_item)
                    
                    return f"Latest news for '{query}':\n\n" + "\n\n".join(news_items)
                
                # Fallback to regular search results
                elif "organic_results" in results and results["organic_results"]:
                    search_results = []
                    for i, result in enumerate(results["organic_results"][:3], 1):
                        title = result.get("title", "No title")
                        snippet = result.get("snippet", "")
                        link = result.get("link", "")
                        
                        search_results.append(f"{i}. {title}\n   {snippet}\n   Source: {link}")
                    
                    return f"Recent information about '{query}':\n\n" + "\n\n".join(search_results)
            
            return f"Could not retrieve news for '{query}' at this time."
            
        except Exception as e:
            return f"News search error for '{query}': {str(e)}"

# Initialize tools
calculator_tool = Calculator()
weather_tool = Weather() 
search_tool = Search()
news_tool = News()

# Dictionary for easy access
TOOLS = {
    'calculator': calculator_tool,
    'weather': weather_tool,
    'search': search_tool,
    'news': news_tool
}
