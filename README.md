An intelligent email automation system that leverages AI to read, analyze, and intelligently respond to incoming Gmail messages. Built with FastAPI, OpenAI, and Gmail API integration.

---

## ✨ Features

- **🤖 AI-Powered Email Analysis** - Uses OpenAI's GPT-4 to analyze incoming emails and determine if a response is needed
- **📬 Gmail Integration** - Seamless OAuth2 integration with Gmail API for reading and sending emails
- **🔐 Smart Reply Generation** - Automatically drafts professional and contextually appropriate email responses
- **🚀 FastAPI Backend** - RESTful API for managing email operations with built-in authentication
- **📊 Email Threading** - Keeps track of email conversations and maintains proper threading
- **🔄 Automated Workflow** - Processes unread emails in batches with configurable limits
- **🎯 Intelligent Filtering** - Automatically skips spam, newsletters, and automated notifications
- **✅ Read Status Management** - Marks emails as read after processing

---

## 🛠️ Tech Stack

- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- **AI/LLM**: [OpenAI API](https://platform.openai.com/) - GPT-4o-mini for email analysis and response generation
- **Email Service**: [Gmail API](https://developers.google.com/gmail/api) - Gmail integration with OAuth2
- **Data Validation**: [Pydantic](https://docs.pydantic.dev/) - Data parsing and validation
- **AI Framework**: [Pydantic AI](https://docs.pydantic.dev/latest/concepts/agents/) - Agentic AI workflows
- **Environment Management**: [python-dotenv](https://github.com/theskumar/python-dotenv) - Environment variables

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Gmail account with OAuth2 credentials
- OpenAI API key

### Step 1: Clone the Repository
```bash
git clone https://github.com/ShreyanshWarde/EmailAgent.git
cd EmailAgent
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirement.txt
```

### Step 4: Set Up Environment Variables
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
GMAIL_CREDENTIALS_FILE=credentials.json
```

### Step 5: Set Up Gmail OAuth2
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth2 credentials (Desktop Application)
5. Download credentials as JSON and save as `credentials.json` in the project root

---

## 🚀 Usage

### Start the FastAPI Server
```bash
python app.py
```

The server will start at `http://localhost:8000`

**Available Endpoints:**
- `GET /` - Root endpoint with service information
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - ReDoc API documentation
- `POST /api/login` - User authentication
- `POST /api/process` - Process unread emails
- `POST /api/send-test` - Send test email
- `GET /api/status` - Service status

### Process Emails with Python Script
```bash
python main.py
```

This will:
1. Fetch all unread emails from your inbox
2. Analyze each email with AI to determine if a response is needed
3. Generate intelligent, contextually appropriate replies
4. Send the replies automatically
5. Mark processed emails as read

---

## 📁 Project Structure

```
EmailAgent/
├── app.py                  # FastAPI application setup and endpoints
├── main.py                # Main AI agent orchestrator
├── gmail_service.py       # Gmail API integration and email operations
├── models.py              # Pydantic data models for validation
├── check.py               # Utility functions for verification
├── test_mark_read.py      # Test suite for email marking functionality
├── requirement.txt        # Python dependencies
├── credentials.json       # Gmail OAuth2 credentials (not in repo)
├── token.pickle           # Gmail OAuth2 token cache (auto-generated)
├── .gitignore            # Git ignore configuration
├── api/                   # API routes and authentication modules
└── scripts/              # Utility scripts
```

---

## 🔧 Core Components

### EmailAIAgent (`main.py`)
The main orchestrator that:
- Initializes the OpenAI client and Gmail service
- Fetches unread emails from Gmail
- Analyzes emails using AI
- Generates responses using OpenAI's GPT-4o-mini model
- Sends replies through Gmail

```python
agent = EmailAIAgent()
agent.process_emails(max_emails=5)  # Process up to 5 unread emails
```

### GmailService (`gmail_service.py`)
Handles all Gmail API interactions:
- **`authenticate()`** - OAuth2 authentication with Gmail
- **`get_unread_emails(max_results=10)`** - Fetch unread messages
- **`send_email(to, subject, body)`** - Send email replies
- **`mark_as_read(message_id)`** - Mark emails as read
- **`get_message_labels(message_id)`** - Retrieve message labels

### Pydantic Models (`models.py`)
Data validation models:
- **`EmailContent`** - Validates incoming email data
- **`DraftResponse`** - Validates AI-generated responses
- **`EmailThread`** - Manages email conversation threads

---

## 🤖 AI Decision Logic

The AI agent uses the following guidelines to determine if a reply is needed:

✅ **Replies To:**
- Important work emails
- Customer inquiries
- Personal messages requiring response
- Professional requests

❌ **Skips:**
- Spam and unsolicited emails
- Newsletters and notifications
- Automated alerts
- Marketing emails

The response tone adapts based on the original email and can be:
- Professional
- Friendly
- Formal
- Casual

---

## 📊 Example Workflow

```
1. Fetch unread emails
   ↓
2. Analyze email with AI
   ↓
3. Determine if reply needed
   ↓
4. If yes: Generate response draft
   ↓
5. Send reply via Gmail
   ↓
6. Mark original email as read
   ↓
7. Log success/failure
```

---

## 🔐 Security & Best Practices

- ✅ OAuth2 authentication for Gmail
- ✅ Environment variables for sensitive data (API keys)
- ✅ Input validation with Pydantic models
- ✅ CORS middleware for API security
- ✅ Token caching to minimize authentication requests
- ✅ Error handling and logging throughout

---

## ⚙️ Configuration

### Email Processing Limits
Edit in `main.py`:
```python
agent.process_emails(max_emails=5)  # Adjust as needed
```

### AI Model Selection
Edit in `main.py` (line 36):
```python
self.agent = Agent(
    model='openai:gpt-4o-mini',  # Or use gpt-3.5-turbo for cheaper testing
    system_prompt="..."
)
```

### API CORS Origins
Edit in `app.py` (lines 26-32):
```python
allow_origins=["http://localhost:3000", "http://localhost:8000"]
```

---

## 🧪 Testing

### Test Email Marking
```bash
python test_mark_read.py
```

### Check Configuration
```bash
python check.py
```

---

## 📝 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🐛 Troubleshooting

### Issue: `OPENAI_API_KEY not found`
**Solution**: Ensure your `.env` file exists and contains `OPENAI_API_KEY=your_key_here`

### Issue: Gmail authentication fails
**Solution**: 
- Regenerate OAuth2 credentials from Google Cloud Console
- Delete `token.pickle` and re-authenticate
- Ensure `credentials.json` is in the project root

### Issue: Emails not being sent
**Solution**:
- Check Gmail API is enabled in Google Cloud Console
- Verify OAuth2 scopes include `gmail.send`
- Review API quota limits

### Issue: AI not generating responses
**Solution**:
- Verify OpenAI API key is valid and has credits
- Check internet connectivity
- Review OpenAI API status page

---

## 🚀 Future Enhancements

- [ ] Multi-language email support
- [ ] Advanced email classification system
- [ ] Email templates library
- [ ] Web UI dashboard
- [ ] Real-time email monitoring
- [ ] Email attachment handling
- [ ] Calendar integration for scheduling
- [ ] Analytics and reporting
- [ ] Multi-account support
- [ ] Custom AI response training

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests to improve the project.

---

## 👨‍💻 Author

**Shreyansh Warde**
- GitHub: [@ShreyanshWarde](https://github.com/ShreyanshWarde)

---

## 💡 Tips & Tricks

- Start with `max_emails=1` to test the workflow
- Use GPT-3.5-turbo model for faster (and cheaper) testing
- Monitor API costs regularly with OpenAI dashboard
- Implement rate limiting in production environments
- Use email filtering before processing with the AI agent

---

## 📞 Support

For issues, questions, or suggestions, please open an issue on GitHub or contact the maintainer.

---
