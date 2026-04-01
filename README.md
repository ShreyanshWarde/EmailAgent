# Email AI Agent

An intelligent email assistant powered by AI (GPT-4o-mini) and Gmail API. This FastAPI-based application automatically reads, analyzes, and responds to emails using OpenAI's language models.

## Features

- 📧 **Gmail Integration**: Seamlessly read and send emails via Gmail API
- 🤖 **AI-Powered Responses**: Automatically draft intelligent email replies using GPT-4o-mini
- 🔐 **OAuth2 Authentication**: Secure Gmail authentication with OAuth2 flow
- 🚀 **RESTful API**: FastAPI backend with comprehensive endpoints
- 📊 **Email Analysis**: Classify emails and determine if responses are needed
- 🔄 **Automatic Processing**: Batch process unread emails with intelligent filtering

## Prerequisites

- Python 3.11 or higher
- Google Gmail API credentials
- OpenAI API key
- pip or poetry for package management

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/EmailAgent.git
cd EmailAgent
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
OPENAI_API_KEY=your_openai_api_key_here
GMAIL_CREDENTIALS_FILE=credentials.json
```

### 5. Set Up Gmail API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop application)
5. Download credentials as JSON
6. Save as `credentials.json` in the project root
7. First run will prompt for Gmail authentication

## Usage

### Start the Server
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Server runs on: `http://localhost:8000`

### API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints

#### Health Check
```bash
GET /health
```

#### Process Emails
```bash
POST /api/process?max_emails=5
Authorization: Bearer {token}
```

#### Get Unread Emails
```bash
GET /api/emails/unread?max_results=10
Authorization: Bearer {token}
```

#### Send Test Email
```bash
POST /api/send-test
Authorization: Bearer {token}
Content-Type: application/json

{
  "to": "recipient@example.com",
  "subject": "Test Email",
  "body": "This is a test email"
}
```

#### Login
```bash
POST /api/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=password
```

## Project Structure

```
EmailAgent/
├── app.py                  # FastAPI application
├── main.py                 # Main AI agent orchestration
├── gmail_service.py        # Gmail API integration
├── models.py               # Pydantic data models
├── api/
│   ├── routes.py          # API route handlers
│   ├── auth.py            # Authentication logic
│   └── __init__.py
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore patterns
└── README.md               # This file
```

## How It Works

1. **Email Fetching**: Retrieves unread emails from Gmail inbox
2. **AI Analysis**: Sends email content to GPT-4o-mini for analysis
3. **intelligent Decision**: AI decides whether a reply is needed
4. **Response Drafting**: If reply needed, AI generates appropriate response
5. **Sending**: Replies are automatically sent via Gmail API
6. **Marking**: Processed emails are marked as read

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |
| `GMAIL_CREDENTIALS_FILE` | Path to Gmail credentials JSON | Yes |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiration time | No (default: 30) |

### API Response Format

All responses follow this format:
```json
{
  "success": true,
  "message": "Operation completed",
  "data": {}
}
```

## Development

### Running Tests
```bash
pytest
```

### Code Quality
```bash
# Lint with flake8
flake8 .

# Format with black
black .
```

## Troubleshooting

### Gmail Authentication Fails
- Ensure credentials.json is in project root
- Delete token.pickle to re-authenticate
- Check Google Cloud permissions

### OpenAI API Errors
- Verify OPENAI_API_KEY is correct
- Check API quota limits
- Ensure account has sufficient credits

### Import Errors
- Verify venv is activated
- Run `pip install -r requirements.txt` again
- Check Python version (3.11+)

## Security Notes

- Never commit `.env` or `credentials.json`
- Keep OpenAI API key private
- Rotate credentials periodically
- Use environment variables in production
- Implement rate limiting for API endpoints

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Open an [Issue](https://github.com/yourusername/EmailAgent/issues)
- Check existing documentation
- Review API docs at `/docs`

---

**Last Updated**: April 2026
