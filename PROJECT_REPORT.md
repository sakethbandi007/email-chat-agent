# Email Chat Assistant - Project Report

## Project Overview

**Project Title:** Email Chat Assistant  
**Description:** An AI-powered conversational assistant for Gmail management  
**Live Demo:** [https://email-chat-agent-gjeq9yqncyucxcnsguct9t.streamlit.app/](https://email-chat-agent-gjeq9yqncyucxcnsguct9t.streamlit.app/)  
**Repository:** [https://github.com/sakethbandi007/email-chat-agent](https://github.com/sakethbandi007/email-chat-agent)

---

## 1. Introduction

The Email Chat Assistant is a conversational AI application that allows users to manage their Gmail inbox using natural language commands. Instead of navigating through traditional email interfaces, users can simply chat with the assistant to read, reply, and manage emails.

### Key Features
- Natural language email management
- AI-generated smart replies
- Calendar integration for scheduling context
- Draft revision with feedback
- Real-time Gmail integration via OAuth2

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     STREAMLIT WEB UI                          │
│                   (email_chat_app.py)                        │
└─────────────────────────┬────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                    LLM DECISION ENGINE                        │
│  ┌────────────────┐  ┌─────────────────────────────────────┐ │
│  │ Pydantic Model │  │         OpenAI GPT-4o               │ │
│  │ (EmailAction)  │  │   with structured JSON output       │ │
│  └────────────────┘  └─────────────────────────────────────┘ │
└─────────────────────────┬────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                    ACTION HANDLERS                            │
│  fetch_emails │ read_email │ draft_reply │ send_email │ ... │
└─────────────────────────┬────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                    GOOGLE APIS                                │
│         Gmail API              │        Calendar API          │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit |
| LLM | OpenAI GPT-4o |
| Framework | LangChain |
| Email API | Gmail API |
| Calendar API | Google Calendar API |
| Authentication | OAuth 2.0 |
| Deployment | Streamlit Cloud |

---

## 3. Implementation Details

### 3.1 Structured Output with Pydantic

The system uses Pydantic models for type-safe LLM responses:

```python
class ActionType(str, Enum):
    FETCH_EMAILS = "fetch_emails"
    READ_EMAIL = "read_email"
    DRAFT_REPLY = "draft_reply"
    SEND_EMAIL = "send_email"
    # ... more actions

class EmailAction(BaseModel):
    action: ActionType
    email_id: Optional[str]
    instructions: Optional[str]
    chat_response: Optional[str]
```

### 3.2 LLM Decision Making

Instead of keyword matching, the LLM analyzes user intent:

```python
# LLM returns typed EmailAction object
structured_llm = llm.with_structured_output(EmailAction)
action = structured_llm.invoke(messages)

# Execute using handler map
action_handlers = {
    ActionType.FETCH_EMAILS: lambda: fetch_emails(),
    ActionType.DRAFT_REPLY: lambda: draft_reply(action.email_id),
    # ...
}
return action_handlers[action.action]()
```

### 3.3 OAuth2 Authentication

The application supports both local and cloud authentication:

- **Local:** Uses `credentials.json` and `token.pickle`
- **Cloud:** Uses Streamlit secrets (`st.secrets`)

---

## 4. Project Structure

```
email-chat-agent/
├── README.md                    # Project documentation
├── PROJECT_REPORT.md            # This report
├── requirements.txt             # Dependencies
├── .gitignore                   # Git ignore rules
└── code/
    ├── email_chat_app.py        # Main Streamlit application
    ├── gmail_auth.py            # Gmail authentication
    ├── email_agent.py           # Core agent logic
    ├── switch_account.py        # Account switching utility
    └── export_secrets_for_streamlit.py  # Secrets export
```

---

## 5. User Commands

| Command | Action |
|---------|--------|
| "Show my emails" | Fetch latest 5 emails |
| "Read email [ID]" | View full email content |
| "Reply to [ID]" | Generate AI draft reply |
| "Make it shorter" | Revise current draft |
| "Send" | Send approved email |
| "Summarize inbox" | Get AI summary |
| "Check calendar" | View schedule |

---

## 6. Setup Instructions

### Local Development

```bash
# Clone repository
git clone https://github.com/sakethbandi007/email-chat-agent.git
cd email-chat-agent

# Install dependencies
pip install -r requirements.txt

# Set up environment
echo "OPENAI_API_KEY=your_key" > .env

# Authenticate with Gmail
cd code && python gmail_auth.py

# Run application
streamlit run code/email_chat_app.py
```

### Streamlit Cloud Deployment

Add these secrets in Streamlit Cloud:

```toml
[google_token]
token = "..."
refresh_token = "..."
token_uri = "https://oauth2.googleapis.com/token"
client_id = "..."
client_secret = "..."

[openai]
api_key = "sk-..."
```

---

## 7. Security Considerations

- OAuth tokens stored securely (not in version control)
- Email sending requires explicit user confirmation
- Credentials excluded via `.gitignore`
- Streamlit secrets for cloud deployment

---

## 8. Future Enhancements

1. **Email Search** - Search by keyword, sender, date
2. **Attachments** - Handle file attachments
3. **Labels** - Manage Gmail labels
4. **Multi-account** - Support multiple Gmail accounts
5. **Voice Input** - Voice command support

---

## 9. Conclusion

The Email Chat Assistant demonstrates how LLM-powered applications can simplify everyday tasks like email management. By combining structured outputs, OAuth authentication, and a modern web interface, the application provides a seamless conversational experience for Gmail users.

---

**Author:** Saketh Bandi  
**Date:** December 2024  
**License:** MIT

