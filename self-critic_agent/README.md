# Self-Critic Agent System

A multi-agent orchestration system that coordinates multiple specialized agents to work together on complex tasks. Each agent handles specific functions while a central orchestrator manages workflow, delegates tasks, and ensures smooth collaboration.

## Features

🤖 **Multi-Agent Architecture**
- **Content Generator Agent**: Creates well-structured blog content using Groq's LLaMA models
- **Critic Agent**: Provides detailed analysis and critique of generated content
- **Orchestration System**: Coordinates workflow between agents

📊 **Comprehensive Analysis**
- Content quality assessment
- Structural analysis (clarity, organization, engagement)
- Actionable improvement suggestions
- Real-time feedback and metrics

🎯 **Smart Interface**
- Clean, intuitive Streamlit UI
- Multiple iteration support
- Progress tracking
- Interactive controls and settings

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Groq API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/sush0677/self_critic_agent.git
cd self_critic_agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory:
```
GROQ_API_KEY=your_groq_api_key_here
```

4. Run the application:
```bash
streamlit run app.py
```

5. Open your browser to `http://localhost:8501`

## Usage

1. **Enter Your Topic**: Type any topic you want a blog post about
2. **Adjust Settings**: Use sliders to control generation and criticism length
3. **Generate & Analyze**: Click the button to start the multi-agent process
4. **View Results**: Get comprehensive analysis including:
   - Generated blog content
   - Detailed critique and feedback
   - Quality metrics and suggestions
   - Iteration history

## Configuration

### Environment Variables
- `GROQ_API_KEY`: Your Groq API key (required)

### Model Configuration
The app uses Groq's `llama-3.1-8b-instant` model for both content generation and analysis. The system includes fallback template-based generation when the API is unavailable.

## Project Structure

```
self_critic_agent/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies  
├── .env               # Environment variables (not committed)
├── .gitignore         # Git ignore file
└── README.md          # Project documentation
```

## Multi-Agent Orchestration

This system demonstrates key principles of multi-agent coordination:

- **Specialization**: Each agent has a specific role and expertise
- **Communication**: Agents share data and feedback through defined interfaces
- **Orchestration**: Central system manages the workflow and timing
- **Scalability**: Architecture supports adding new agents and capabilities
- **Resilience**: Fallback mechanisms ensure system reliability

## Technology Stack

- **Frontend**: Streamlit
- **AI Models**: Groq (LLaMA 3.1 8B Instant)
- **Language**: Python 3.8+
- **Environment Management**: python-dotenv
- **Version Control**: Git with security best practices

## Example Prompts

Try these topics for content generation:
- "The future of artificial intelligence in healthcare"
- "Sustainable living practices for urban environments"
- "Remote work trends and productivity tips"
- "Machine learning applications in business"
- "Climate change solutions and innovations"

## Security Features

✅ **API Key Protection**: Environment variables prevent credential exposure
✅ **Git Security**: `.gitignore` protects sensitive files
✅ **Error Handling**: Graceful fallbacks when services are unavailable
✅ **Input Validation**: Safe handling of user inputs

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Troubleshooting

### Common Issues

**API Key Not Found**
- Ensure `.env` file exists in the project root
- Verify `GROQ_API_KEY` is set correctly
- Restart the application after adding the key

**Import Errors**
- Run `pip install -r requirements.txt`
- Ensure Python 3.8+ is installed
- Check virtual environment activation

**Connection Issues**
- Verify internet connection
- Check Groq API service status
- System will fallback to template generation if API is unavailable

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the troubleshooting section

---

*Built with ❤️ using Streamlit and Groq AI*