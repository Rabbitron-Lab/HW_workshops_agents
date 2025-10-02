# 🤖 MRKL Agent Demo with Free LLM & Streamlit UI

This project demonstrates a **MRKL (Modular Reasoning, Knowledge and Language)** agent using completely **free components**:
- **Free LLM**: Hugging Face Transformers (no API keys required!)
- **Modular Tools**: Calculator, Weather, Search
- **Interactive UI**: Streamlit web interface
- **Step-by-step Reasoning**: Shows agent's thinking process

Perfect for educational demonstrations - **100% free!**

## 🎯 Features
- **Free LLM Integration**: Uses Hugging Face models locally
- **Interactive Streamlit UI**: Web-based demonstration interface  
- **Real-time Reasoning**: Shows step-by-step agent thinking
- **Modular Tools**: Calculator, Weather, Knowledge Search
- **Educational Focus**: Designed for classroom presentations
- **No API Keys**: Everything runs locally and for free

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Streamlit App
```bash
streamlit run app.py
```

### 3. Open Browser
The app will open automatically at `http://localhost:8501`

## 📁 Project Structure
```
mrkl_agent/
├── app.py              # Streamlit web interface
├── agent.py            # MRKL Agent with free LLM
├── tools.py            # Modular tools (Calculator, Weather, Search)
├── main.py             # Command-line demo (alternative)
├── requirements.txt    # Dependencies (all free!)
└── README.md          # This file
```

## 🛠️ Available Tools

### Calculator
- Mathematical operations: `+`, `-`, `*`, `/`, `^`
- Example: "What's 15 * 23 + 100?"

### Weather  
- City weather information (demo data)
- Example: "Weather in Tokyo?"

### Search
- Knowledge base queries
- Example: "Tell me about machine learning"

## 💡 Sample Queries for Demo
1. **Math**: "Calculate 25 * 4 + 100"
2. **Weather**: "What's the weather in London?"  
3. **Knowledge**: "Tell me about artificial intelligence"
4. **Complex**: "Calculate the area of a circle with radius 5"

## 🎓 For Educators

### Presentation Tips:
1. **Start with Simple Query**: Show basic calculator function
2. **Explain Reasoning**: Use the reasoning panel to show agent thinking
3. **Try Different Tools**: Demonstrate tool selection logic
4. **Interactive Session**: Let students suggest queries
5. **Extend in Real-time**: Add new tools or modify existing ones

### Key Learning Points:
- **Modular Design**: How agents combine LLMs with tools
- **Reasoning Process**: Step-by-step decision making
- **Tool Selection**: How agents choose appropriate tools
- **Parameter Extraction**: How agents parse user input
- **Response Generation**: Combining tool results with natural language

## 🔧 Customization

### Add New Tools
1. Create new tool class in `tools.py`
2. Add to `TOOLS` dictionary
3. Update agent's `think()` method for tool selection

### Modify LLM
- Current: `microsoft/DialoGPT-small` (lightweight)
- Alternatives: `gpt2`, `distilgpt2`, or any Hugging Face model
- Edit `agent.py` → `setup_llm()` method

### Enhance UI
- Modify `app.py` for different layouts
- Add new Streamlit components
- Customize styling and themes

## 🔑 API Keys Setup

### Required APIs:
1. **Hugging Face Token**: Get free token from https://huggingface.co/settings/tokens
2. **SerpAPI Key**: Get free tier (100 searches/month) from https://serpapi.com/
3. **OpenWeatherMap** (Optional): Free tier from https://openweathermap.org/

### Setup Instructions:
1. Create `.env` file in project root
2. Add your API keys:
```env
HUGGINGFACE_API_TOKEN=your_hf_token_here
SERPAPI_KEY=your_serpapi_key_here
OPENWEATHER_API_KEY=your_weather_key_here
```

## 🆓 Free Components Used

### Real Data Sources:
- **Hugging Face API**: Better LLM responses with your token
- **SerpAPI**: Real-time Google search results (100 free searches/month)
- **Wikipedia API**: Completely free knowledge base
- **wttr.in**: Free weather service (no API key needed)

### Alternative Free LLMs:
- **Ollama**: Run Llama2, CodeLlama locally
- **GPT4All**: Local GPT models
- **Transformers**: Any HF model

## 🚀 Advanced Setup (Optional)

### Use Ollama for Better Performance:
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2

# Update agent.py to use Ollama API
```

### Add Real APIs (Still Free):
- **OpenWeatherMap**: Free tier (1000 calls/day)
- **NewsAPI**: Free tier (1000 requests/day)  
- **Wikipedia API**: Completely free

## 🎬 Demo Script for Presentations

### Introduction (2 minutes)
"Today I'll show you a MRKL agent - it combines language models with tools..."

### Live Demo (5 minutes)
1. Run: `streamlit run app.py`
2. Query: "What's 25 * 4?"
3. Show reasoning steps
4. Try: "Weather in Tokyo?"
5. Demonstrate: "Tell me about AI"

### Code Walkthrough (5 minutes)
- Show `tools.py`: Modular design
- Show `agent.py`: Reasoning process  
- Show `app.py`: UI components

### Student Interaction (3 minutes)
- "What would you like to ask the agent?"
- Take suggestions and demonstrate
- Show how to add new tools

## 🔍 Troubleshooting

### Model Download Issues:
```bash
# Manual model download
python -c "from transformers import AutoModel; AutoModel.from_pretrained('microsoft/DialoGPT-small')"
```

### Streamlit Issues:
```bash
# Restart Streamlit
streamlit run app.py --server.port 8502
```

### Memory Issues:
- Use smaller models: `distilgpt2`, `gpt2-small`  
- Reduce `max_length` in agent.py
- Close other applications

## 📚 Educational Resources

### Learn More About:
- **MRKL Framework**: [Original Paper](https://arxiv.org/abs/2205.00445)
- **LangChain**: Tool integration patterns
- **Hugging Face**: Model documentation
- **Streamlit**: UI development guide

---

**🎓 Perfect for CS courses, AI workshops, and student projects!**  
**💝 100% free, no subscriptions or API keys needed!**
