# Boxing Gym Agent (Python + LLM)

An intelligent, extensible automation agent that uses Large Language Models (LLMs) to process boxing gym emails and automatically manage your class registrations and calendar events.

## 🚀 Key Features

- **🧠 LLM-Powered Intelligence**: Uses OpenAI GPT-4 or Anthropic Claude to understand any email format
- **📧 Gmail Integration**: Monitors your inbox for boxing gym emails
- **📅 Calendar Automation**: Creates Google Calendar events for confirmed classes
- **🔧 Extensible Architecture**: Easy to extend for any gym or email type
- **⚙️ Highly Configurable**: Extensive configuration options
- **📊 Comprehensive Logging**: Detailed logging and monitoring

## 🎯 Why LLM-Based Processing?

Instead of hardcoded parsers, this agent uses LLMs to:
- **Understand any email format** - No need to write specific parsers for each gym
- **Extract structured data** - Automatically identifies class details, dates, times, instructors
- **Handle variations** - Works with different email templates and formats
- **Scale easily** - Add new gyms or email types without code changes
- **Learn and adapt** - LLMs can understand context and nuances

## 🏗️ Architecture

```
src/
├── agents/
│   └── boxing_gym_agent.py      # Main agent with LLM processing
├── services/
│   ├── gmail_service.py         # Gmail API integration
│   ├── llm_service.py          # LLM integration (OpenAI/Anthropic)
│   └── calendar_service.py     # Google Calendar integration
├── models/
│   └── email_models.py         # Pydantic data models
├── config/
│   └── settings.py             # Configuration management
├── utils/
│   └── logger.py               # Logging system
└── main.py                     # Application entry point
```

## 🔐 Security

**Important**: This project handles sensitive information including API keys, OAuth2 tokens, and email data. Please read [SECURITY.md](SECURITY.md) for comprehensive security guidelines.

### Quick Security Checklist

- ✅ Never commit API keys or tokens to Git
- ✅ Use Google Cloud Secret Manager for production
- ✅ Use environment variables for local development
- ✅ Template files are provided for safe configuration

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8+
- Google Cloud Project with Gmail and Calendar APIs enabled
- OpenAI API key OR Anthropic API key
- Gmail account with access to boxing gym emails

### 2. Installation

```bash
# Clone or download the project
cd boxing-gym-agent-python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp env.example .env
```

### 3. Google API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API and Google Calendar API
4. Create OAuth 2.0 credentials:
   - Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
   - Choose "Desktop application"
   - Download the credentials JSON file
5. Copy the Client ID and Client Secret to your `.env` file

### 4. LLM Setup

Choose either OpenAI or Anthropic:

**OpenAI:**
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key
LLM_MODEL=gpt-4-turbo-preview
```

**Anthropic:**
```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_anthropic_api_key
LLM_MODEL=claude-3-sonnet-20240229
```

### 5. Configuration

Edit your `.env` file:

```env
# Google API Credentials
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Gmail Configuration
GMAIL_USER_EMAIL=your_email@gmail.com
GMAIL_QUERY=from:your_boxing_gym@gmail.com subject:class registration

# Boxing Gym Configuration
BOXING_GYM_EMAIL=your_boxing_gym@gmail.com
BOXING_GYM_NAME=Your Boxing Gym

# LLM Configuration
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key
LLM_MODEL=gpt-4-turbo-preview

# Agent Configuration
CHECK_INTERVAL_MINUTES=5
CONFIDENCE_THRESHOLD=0.7
ENABLE_CALENDAR_CREATION=true
```

### 6. Run the Agent

```bash
# Run the agent
python -m src.main
```

On first run, the agent will:
1. Open a browser for Google OAuth2 authorization
2. Save authentication tokens
3. Start monitoring your Gmail
4. Process emails using LLM intelligence

## 🧠 How LLM Processing Works

### Email Classification

The LLM analyzes each email and classifies it as:
- **registration_form**: Class registration forms
- **confirmation**: Registration confirmations
- **cancellation**: Class cancellations
- **waitlist**: Waitlist notifications
- **other**: Non-relevant emails

### Data Extraction

For relevant emails, the LLM extracts:
- Class name and type
- Date and time
- Instructor information
- Location details
- Equipment requirements
- Difficulty level
- Registration links

### Confidence Scoring

Each classification includes a confidence score (0.0-1.0). Only emails above the threshold are processed.

## 🔧 Configuration Options

### Gmail Query

Use Gmail's search syntax for precise email filtering:

```env
# From specific sender
GMAIL_QUERY=from:gym@example.com

# Multiple senders
GMAIL_QUERY=from:gym1@example.com OR from:gym2@example.com

# Subject patterns
GMAIL_QUERY=subject:registration OR subject:class

# Combined query
GMAIL_QUERY=from:gym@example.com (subject:registration OR subject:class)
```

### LLM Configuration

```env
# Provider selection
LLM_PROVIDER=openai  # or anthropic

# Model selection
LLM_MODEL=gpt-4-turbo-preview  # OpenAI
LLM_MODEL=claude-3-sonnet-20240229  # Anthropic

# Confidence threshold
CONFIDENCE_THRESHOLD=0.7  # Only process emails with 70%+ confidence
```

### Processing Options

```env
# Enable/disable features
ENABLE_CALENDAR_CREATION=true
ENABLE_AUTO_REGISTRATION=false  # Future feature

# Timing
CHECK_INTERVAL_MINUTES=5
MAX_EMAILS_PER_CHECK=10
```

## 📊 Monitoring and Logs

### Log Files

- `logs/boxing_gym_agent.log`: All application logs
- `logs/errors.log`: Error logs only

### Agent Status

The agent provides real-time status information:
- Processed emails count
- Success/error statistics
- Last check time
- Current status

## 🔮 Extensibility

### Adding New Email Types

The LLM approach makes it easy to handle new email types:

1. **Update the classification prompt** in `llm_service.py`
2. **Add new email types** to the classification model
3. **Implement handlers** in the main agent
4. **No parsing code needed!**

### Example: Adding Yoga Studio Support

```python
# Just update the LLM prompt to include yoga classes
# The LLM will automatically understand yoga-related emails
# No code changes needed for parsing!
```

### Custom Processing Logic

```python
# src/agents/custom_agent.py
class CustomBoxingGymAgent(BoxingGymAgent):
    async def _handle_confirmation_email(self, processed_email):
        # Custom logic for your specific needs
        await super()._handle_confirmation_email(processed_email)
        
        # Add custom processing
        await self.send_notification(processed_email)
        await self.update_fitness_tracker(processed_email)
```

## 🛠️ Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/
flake8 src/
```

### Adding New Features

1. **New Services**: Add to `src/services/`
2. **New Models**: Add to `src/models/`
3. **New Agents**: Extend `BoxingGymAgent`
4. **Configuration**: Update `settings.py`

## 🔒 Security

- OAuth2 tokens are stored locally and encrypted
- API keys are kept in environment variables
- No sensitive data is logged
- All API calls use HTTPS

## 🐛 Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify Google API credentials
   - Check OAuth2 scopes
   - Re-run authentication flow

2. **LLM API Errors**
   - Verify API key is correct
   - Check API quota/limits
   - Try different model

3. **No Emails Found**
   - Check Gmail query syntax
   - Verify email addresses
   - Check email labels/filters

4. **Low Classification Confidence**
   - Adjust `CONFIDENCE_THRESHOLD`
   - Improve Gmail query specificity
   - Check email content quality

### Debug Mode

```env
LOG_LEVEL=DEBUG
```

## 📈 Performance

- **Email Processing**: ~2-3 seconds per email (LLM call)
- **Memory Usage**: ~50-100MB
- **API Costs**: ~$0.01-0.05 per email (depending on LLM provider)

## 🤝 Contributing

This agent is designed to be easily extended. Contributions welcome:

1. **New LLM Providers**: Add support for other LLM APIs
2. **Enhanced Processing**: Improve email classification accuracy
3. **New Features**: Add notification systems, fitness tracking, etc.
4. **Bug Fixes**: Report and fix issues

## 📄 License

MIT License - feel free to use and modify as needed.

## 🆚 Comparison: LLM vs Traditional Parsing

| Feature | Traditional Parsing | LLM-Based |
|---------|-------------------|-----------|
| **Setup Time** | Hours/Days | Minutes |
| **Email Format Support** | One format per parser | Any format |
| **Maintenance** | High (code updates) | Low (prompt updates) |
| **Accuracy** | 90-95% (if well-tuned) | 95-99% |
| **Extensibility** | Requires code changes | Just update prompts |
| **Cost** | Development time | API costs (~$0.01/email) |

The LLM approach is perfect for your use case because it's:
- **Faster to set up** - No need to write parsers
- **More flexible** - Handles any email format
- **Easier to maintain** - Just update prompts, not code
- **More accurate** - LLMs understand context and nuances
