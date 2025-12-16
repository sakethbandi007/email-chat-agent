# 📧 Email Chat Assistant

A conversational AI assistant for managing Gmail through natural language. Built with LangChain, OpenAI, and Streamlit.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://email-chat-agent-gjeq9yqncyucxcnsguct9t.streamlit.app/)

**🚀 Live Demo:** [https://email-chat-agent-gjeq9yqncyucxcnsguct9t.streamlit.app/](https://email-chat-agent-gjeq9yqncyucxcnsguct9t.streamlit.app/)

## Features

- 💬 **Natural Language Interface** - Chat with your emails
- 📧 **Email Management** - Read, summarize, reply
- 🤖 **Smart Replies** - AI-generated responses
- 📅 **Calendar Integration** - Schedule-aware replies
- ✍️ **Draft Revisions** - Iterate before sending

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/sakethbandi007/email-chat-agent.git
cd email-chat-agent
pip install -r requirements.txt
```

### 2. Set Up API Keys

Create `.env` file:
```
OPENAI_API_KEY=your_openai_api_key
```

### 3. Gmail Authentication

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable Gmail & Calendar APIs
3. Create OAuth credentials → Download as `credentials.json`
4. Run authentication:

```bash
cd code
python gmail_auth.py
```

### 4. Run the App

```bash
streamlit run code/email_chat_app.py
```

## Usage

| Command | Action |
|---------|--------|
| "Show my emails" | Fetch latest emails |
| "Read email [ID]" | View full email |
| "Reply to [ID]" | Draft a reply |
| "Make it shorter" | Revise draft |
| "Send" | Send email |
| "Summarize" | Inbox summary |

## Project Structure

```
├── README.md
├── PROJECT_REPORT.md
├── requirements.txt
├── .env                    # API keys (not committed)
├── credentials.json        # OAuth credentials (not committed)
└── code/
    ├── email_chat_app.py   # Streamlit app
    ├── gmail_auth.py       # Authentication
    ├── email_agent.py      # Core logic
    └── switch_account.py   # Account switching
```

## Requirements

- Python 3.10+
- OpenAI API key
- Google Cloud project with Gmail & Calendar APIs

## License

MIT
