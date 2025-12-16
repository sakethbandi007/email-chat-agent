"""
📧 Email Chat Assistant - Streamlit App
A beautiful chat interface for managing your Gmail with AI.
"""

import streamlit as st
import os
from typing import Dict, List, Any
from datetime import datetime, timedelta
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config - must be first Streamlit command
st.set_page_config(
    page_title="📧 Email Chat Assistant",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful dark theme
st.markdown("""
<style>
    /* Hide Streamlit header and make it dark */
    header[data-testid="stHeader"] {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
    }
    
    /* Top decoration bar */
    [data-testid="stDecoration"] {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    /* Top toolbar */
    [data-testid="stToolbar"] {
        background: transparent !important;
    }
    
    /* Main theme */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    /* App header area */
    .stApp > header {
        background: transparent !important;
    }
    
    /* Chat container */
    .chat-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 20px;
        margin: 10px 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* User message */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 20px 20px 5px 20px;
        margin: 10px 0;
        max-width: 80%;
        margin-left: auto;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Assistant message */
    .assistant-message {
        background: rgba(255, 255, 255, 0.1);
        color: #e0e0e0;
        padding: 15px 20px;
        border-radius: 20px 20px 20px 5px;
        margin: 10px 0;
        max-width: 80%;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Email card */
    .email-card {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 15px;
        margin: 8px 0;
        border-left: 4px solid #667eea;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .email-card:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
    }
    
    .email-unread {
        border-left-color: #00d4ff;
    }
    
    /* Draft box */
    .draft-box {
        background: rgba(102, 126, 234, 0.15);
        border: 2px dashed #667eea;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%) !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown span,
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
    }
    
    [data-testid="stSidebar"] .stExpander {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 25px;
        color: white;
        padding: 15px 20px;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 30px;
        font-weight: 600;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.5);
    }
    
    /* Quick action buttons */
    .quick-action {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 8px 16px;
        margin: 5px;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .quick-action:hover {
        background: rgba(102, 126, 234, 0.3);
        border-color: #667eea;
    }
    
    /* Status indicator */
    .status-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
    }
    
    .status-connected {
        background: #00d4ff;
        box-shadow: 0 0 10px #00d4ff;
    }
    
    .status-mock {
        background: #ffa726;
        box-shadow: 0 0 10px #ffa726;
    }
    
    /* Header */
    .main-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
        border-radius: 20px;
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    h1 {
        color: #ffffff !important;
        font-weight: 700;
    }
    
    h2, h3 {
        color: #e0e0e0 !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(102, 126, 234, 0.5);
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'email_cache' not in st.session_state:
    st.session_state.email_cache = {}
if 'current_draft' not in st.session_state:
    st.session_state.current_draft = {}
if 'gmail_connected' not in st.session_state:
    st.session_state.gmail_connected = False
if 'agent_initialized' not in st.session_state:
    st.session_state.agent_initialized = False

# ===================================
# Gmail Service Setup
# ===================================

gmail_service = None
calendar_service = None

def init_google_services():
    """Initialize Google services - supports both local files and Streamlit Cloud secrets"""
    global gmail_service, calendar_service
    
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        import pickle
        
        SCOPES = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/calendar.readonly'
        ]
        
        creds = None
        
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Method 1: Try Streamlit Cloud secrets first
        try:
            if "google_token" in st.secrets:
                token_data = st.secrets["google_token"]
                creds = Credentials(
                    token=token_data.get("token", ""),
                    refresh_token=token_data.get("refresh_token", ""),
                    token_uri=token_data.get("token_uri", "https://oauth2.googleapis.com/token"),
                    client_id=token_data.get("client_id", ""),
                    client_secret=token_data.get("client_secret", ""),
                    scopes=SCOPES
                )
                # Refresh if token is expired
                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                if creds.valid:
                    print("✅ Loaded credentials from Streamlit secrets")
        except Exception as e:
            print(f"⚠️ Error loading from Streamlit secrets: {e}")
            creds = None
        
        # Method 2: Try local token.pickle file from multiple locations
        if not creds:
            token_paths = [
                os.path.join(script_dir, 'token.pickle'),  # Same dir as script
                'token.pickle',  # Current working directory
                'code/email_agent/token.pickle',  # From project root
            ]
            for token_path in token_paths:
                if os.path.exists(token_path):
                    with open(token_path, 'rb') as token:
                        creds = pickle.load(token)
                    break
        
        # Refresh if expired
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        
        # Method 3: Try local credentials.json for new auth (local only)
        if not creds or not creds.valid:
            cred_paths = [
                os.path.join(script_dir, 'credentials.json'),
                'credentials.json',
                'code/email_agent/credentials.json',
            ]
            for cred_path in cred_paths:
                if os.path.exists(cred_path):
                    flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                    # Save token in the script directory
                    token_save_path = os.path.join(script_dir, 'token.pickle')
                    with open(token_save_path, 'wb') as token:
                        pickle.dump(creds, token)
                    break
        
        if not creds or not creds.valid:
            return None, None, False
        
        gmail_service = build('gmail', 'v1', credentials=creds)
        calendar_service = build('calendar', 'v3', credentials=creds)
        return gmail_service, calendar_service, True
        
    except Exception as e:
        print(f"Google services error: {e}")
        return None, None, False

# ===================================
# Email Functions
# ===================================

def get_mock_emails():
    """Return mock emails for demo"""
    return [
        {
            "id": "mock_001",
            "from": "john.doe@company.com",
            "subject": "Q4 Project Meeting Request",
            "snippet": "Hi, I would like to schedule a meeting to discuss the Q4 project timeline...",
            "body": """Hi,

I would like to schedule a meeting next week to discuss the Q4 project timeline and deliverables. 
Do you have availability on Tuesday or Wednesday afternoon?

We need to review:
- Current progress on Phase 1
- Budget allocation for Phase 2
- Team resource planning

Looking forward to hearing from you.

Best regards,
John Doe
Senior Project Manager""",
            "date": "Dec 12, 2024 10:30 AM",
            "unread": True
        },
        {
            "id": "mock_002",
            "from": "sarah.smith@startup.io",
            "subject": "Partnership Opportunity",
            "snippet": "We're interested in exploring a potential partnership with your team...",
            "body": """Hello,

We're interested in exploring a potential partnership with your team. Our startup focuses on AI-powered solutions and we believe there could be great synergy.

Would you be available for a 30-minute call next week?

Best,
Sarah Smith""",
            "date": "Dec 12, 2024 9:15 AM",
            "unread": True
        },
        {
            "id": "mock_003",
            "from": "newsletter@techdigest.com",
            "subject": "Weekly Tech Digest: AI Updates",
            "snippet": "This week in AI: New breakthroughs in language models...",
            "body": "Weekly Tech Digest\n\nThis week in AI:\n- OpenAI announces new updates\n- Google releases Gemini improvements\n\nUnsubscribe | Manage Preferences",
            "date": "Dec 11, 2024 6:00 PM",
            "unread": False
        },
        {
            "id": "mock_004",
            "from": "hr@mycompany.com",
            "subject": "Holiday Schedule Reminder",
            "snippet": "Please note the office will be closed from Dec 24-26...",
            "body": "Dear Team,\n\nPlease note the office will be closed from December 24-26 for the holidays.\n\nHappy Holidays!\nHR Team",
            "date": "Dec 11, 2024 2:30 PM",
            "unread": False
        },
        {
            "id": "mock_005",
            "from": "mike.wilson@client.com",
            "subject": "Invoice #1234 - Urgent",
            "snippet": "Please review and approve the attached invoice for November services...",
            "body": """Hi,

Please review and approve the attached invoice for November services.

Invoice Details:
- Invoice #: 1234
- Amount: $5,450.00
- Due Date: December 20, 2024

Thanks,
Mike Wilson""",
            "date": "Dec 11, 2024 11:00 AM",
            "unread": True
        }
    ]


def fetch_emails(count=5):
    """Fetch emails from Gmail or return mock data"""
    global gmail_service
    
    if not gmail_service:
        emails = get_mock_emails()[:count]
        for email in emails:
            st.session_state.email_cache[email['id']] = email
        return emails
    
    try:
        results = gmail_service.users().messages().list(
            userId='me', maxResults=count, labelIds=['INBOX']
        ).execute()
        
        messages = results.get('messages', [])
        emails = []
        
        for msg in messages:
            msg_data = gmail_service.users().messages().get(
                userId='me', id=msg['id'], format='full'
            ).execute()
            
            headers = {h['name']: h['value'] for h in msg_data['payload']['headers']}
            
            # Extract body
            body = ""
            if 'parts' in msg_data['payload']:
                for part in msg_data['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        body = base64.urlsafe_b64decode(part['body'].get('data', '')).decode('utf-8')
                        break
            else:
                body_data = msg_data['payload']['body'].get('data', '')
                if body_data:
                    body = base64.urlsafe_b64decode(body_data).decode('utf-8')
            
            email = {
                "id": msg['id'],
                "from": headers.get('From', 'Unknown'),
                "subject": headers.get('Subject', 'No Subject'),
                "snippet": msg_data.get('snippet', '')[:100],
                "body": body,
                "date": headers.get('Date', ''),
                "unread": 'UNREAD' in msg_data.get('labelIds', [])
            }
            emails.append(email)
            st.session_state.email_cache[email['id']] = email
        
        return emails
        
    except Exception as e:
        st.error(f"Error fetching emails: {e}")
        return get_mock_emails()[:count]


def get_calendar_info():
    """Get calendar information"""
    global calendar_service
    
    if not calendar_service:
        return """📅 **Calendar** (Mock Data)

**Upcoming:**
- Mon: Team Standup (10:00 AM)
- Tue: Client Presentation (2:00 PM)
- Wed: Budget Review (11:00 AM)

**Available:**
- Tue: 3:30 PM - 5:00 PM
- Wed: 1:00 PM - 5:00 PM
- Thu: 9:00 AM - 2:30 PM"""
    
    try:
        now = datetime.utcnow()
        events_result = calendar_service.events().list(
            calendarId='primary',
            timeMin=now.isoformat() + 'Z',
            timeMax=(now + timedelta(days=7)).isoformat() + 'Z',
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return "📅 No upcoming events this week."
        
        result = "📅 **Upcoming Events:**\n"
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            result += f"- {start}: {event.get('summary', 'No title')}\n"
        
        return result
        
    except Exception as e:
        return f"❌ Calendar error: {e}"


# ===================================
# LLM Setup
# ===================================

@st.cache_resource
def init_llm():
    """Initialize the LLM - supports both env vars and Streamlit secrets"""
    try:
        from langchain_openai import ChatOpenAI
        
        # Try to get API key from multiple sources
        api_key = None
        
        # 1. Try Streamlit secrets first
        try:
            if "openai" in st.secrets:
                api_key = st.secrets["openai"]["api_key"]
            elif "OPENAI_API_KEY" in st.secrets:
                api_key = st.secrets["OPENAI_API_KEY"]
        except Exception:
            pass
        
        # 2. Try environment variable
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")
        
        # 3. Try loading from .env files in different locations
        if not api_key:
            env_paths = ['.env', '../.env', '../../.env']
            for env_path in env_paths:
                if os.path.exists(env_path):
                    load_dotenv(env_path)
                    api_key = os.getenv("OPENAI_API_KEY")
                    if api_key:
                        break
        
        if not api_key:
            st.error("❌ OpenAI API key not found. Please add it to .env file or Streamlit secrets.")
            return None
        
        return ChatOpenAI(model="gpt-4o", temperature=0.7, api_key=api_key)
    except Exception as e:
        st.error(f"Error initializing LLM: {e}")
        return None

llm = init_llm()


def generate_reply(email_id: str, instructions: str = "") -> str:
    """Generate a reply to an email"""
    if email_id not in st.session_state.email_cache:
        return "❌ Email not found. Please fetch emails first."
    
    email = st.session_state.email_cache[email_id]
    calendar = get_calendar_info()
    
    prompt = f"""Draft a professional email reply.

Original Email:
From: {email['from']}
Subject: {email['subject']}
Body: {email['body']}

Calendar: {calendar}

{"Instructions: " + instructions if instructions else ""}

Write a professional, helpful reply. Include only the email body text."""

    try:
        from langchain_core.messages import HumanMessage
        response = llm.invoke([HumanMessage(content=prompt)])
        
        st.session_state.current_draft = {
            "email_id": email_id,
            "to": email['from'],
            "subject": f"Re: {email['subject']}",
            "body": response.content
        }
        
        return response.content
    except Exception as e:
        return f"❌ Error generating reply: {e}"


def revise_draft(feedback: str) -> str:
    """Revise the current draft"""
    if not st.session_state.current_draft:
        return "❌ No draft to revise."
    
    prompt = f"""Revise this email draft based on feedback.

Current Draft:
{st.session_state.current_draft['body']}

Feedback: {feedback}

Provide the revised email body only."""

    try:
        from langchain_core.messages import HumanMessage
        response = llm.invoke([HumanMessage(content=prompt)])
        st.session_state.current_draft['body'] = response.content
        return response.content
    except Exception as e:
        return f"❌ Error revising: {e}"


from pydantic import BaseModel, Field
from typing import Literal, Optional
from enum import Enum

class ActionType(str, Enum):
    FETCH_EMAILS = "fetch_emails"
    READ_EMAIL = "read_email"
    DRAFT_REPLY = "draft_reply"
    REVISE_DRAFT = "revise_draft"
    SEND_EMAIL = "send_email"
    CANCEL_DRAFT = "cancel_draft"
    CHECK_CALENDAR = "check_calendar"
    SUMMARIZE = "summarize"
    CHAT = "chat"

class EmailAction(BaseModel):
    """Structured response for email assistant actions"""
    action: ActionType = Field(description="The action to perform")
    email_id: Optional[str] = Field(default=None, description="Email ID for read/reply actions. Use 'latest' for most recent, '1' for first, '2' for second, etc.")
    instructions: Optional[str] = Field(default=None, description="Instructions for drafting or feedback for revision")
    chat_response: Optional[str] = Field(default=None, description="Response text for chat action")


def execute_action(action: EmailAction, user_input: str) -> str:
    """Execute the action decided by LLM"""
    
    action_handlers = {
        ActionType.FETCH_EMAILS: lambda: format_email_list(fetch_emails(5)),
        
        ActionType.READ_EMAIL: lambda: _handle_read_email(action.email_id),
        
        ActionType.DRAFT_REPLY: lambda: _handle_draft_reply(action.email_id, action.instructions or user_input),
        
        ActionType.REVISE_DRAFT: lambda: _handle_revise_draft(action.instructions or user_input),
        
        ActionType.SEND_EMAIL: lambda: send_email() if st.session_state.current_draft else "❌ No draft to send. Create a draft first.",
        
        ActionType.CANCEL_DRAFT: lambda: _handle_cancel_draft(),
        
        ActionType.CHECK_CALENDAR: lambda: get_calendar_info(),
        
        ActionType.SUMMARIZE: lambda: _handle_summarize(),
        
        ActionType.CHAT: lambda: action.chat_response or chat_with_llm(user_input)
    }
    
    handler = action_handlers.get(action.action)
    return handler() if handler else chat_with_llm(user_input)


def _handle_read_email(email_id: Optional[str]) -> str:
    """Handle read email action"""
    if not email_id or email_id == "latest":
        if st.session_state.email_cache:
            email_id = list(st.session_state.email_cache.keys())[0]
    elif email_id in ["1", "first"]:
        keys = list(st.session_state.email_cache.keys())
        email_id = keys[0] if keys else None
    elif email_id in ["2", "second"]:
        keys = list(st.session_state.email_cache.keys())
        email_id = keys[1] if len(keys) > 1 else None
    elif email_id in ["3", "third"]:
        keys = list(st.session_state.email_cache.keys())
        email_id = keys[2] if len(keys) > 2 else None
    return format_full_email(email_id) if email_id else "❌ No emails loaded."


def _handle_draft_reply(email_id: Optional[str], instructions: str) -> str:
    """Handle draft reply action"""
    cache = st.session_state.email_cache

    # Resolve by index or "latest"
    if not email_id or email_id == "latest":
        if cache:
            email_id = list(cache.keys())[0]
    elif email_id in ["1", "first"]:
        keys = list(cache.keys())
        email_id = keys[0] if keys else None
    elif email_id in ["2", "second"]:
        keys = list(cache.keys())
        email_id = keys[1] if len(keys) > 1 else None

    # If LLM couldn't pick an id explicitly, try matching by subject text from instructions
    if (not email_id or email_id not in cache) and instructions and cache:
        instr_lower = instructions.lower()
        best_match_id = None
        best_score = 0
        for eid, em in cache.items():
            subj = str(em.get("subject", "")).lower()
            if not subj:
                continue
            # Simple heuristic: longest common substring via containment
            if subj in instr_lower or instr_lower in subj:
                score = len(subj)
                if score > best_score:
                    best_score = score
                    best_match_id = eid
        if best_match_id:
            email_id = best_match_id

    if email_id and email_id in st.session_state.email_cache:
        draft = generate_reply(email_id, instructions)
        return format_draft(draft)
    return "❌ Email not found. Please fetch emails first."


def _handle_revise_draft(feedback: str) -> str:
    """Handle revise draft action"""
    if not st.session_state.current_draft:
        return "❌ No draft to revise. Create a draft first."
    revised = revise_draft(feedback)
    return format_draft(revised)


def _handle_cancel_draft() -> str:
    """Handle cancel draft action"""
    st.session_state.current_draft = {}
    return "✅ Draft discarded."


def _handle_summarize() -> str:
    """Handle summarize action"""
    if not st.session_state.email_cache:
        fetch_emails(5)
    return summarize_emails()


def process_user_message(user_input: str) -> str:
    """Process user input using LLM with structured JSON output"""
    from langchain_core.messages import HumanMessage, SystemMessage
    
    # Build context for LLM
    cache = st.session_state.email_cache
    available_emails = list(cache.keys()) if cache else []
    # Build a numbered list so the LLM can refer to emails by index
    if cache:
        numbered_list_lines = []
        for idx, (eid, em) in enumerate(cache.items(), start=1):
            subj = str(em.get("subject", "No Subject"))
            sender = str(em.get("from", "Unknown"))
            numbered_list_lines.append(f"{idx}. id={eid} | from={sender} | subject={subj}")
        email_list_text = "\n".join(numbered_list_lines)
    else:
        email_list_text = "No emails loaded yet."

    has_draft = bool(st.session_state.current_draft)
    
    # Create LLM with structured output
    structured_llm = llm.with_structured_output(EmailAction)
    
    system_prompt = """You are an email assistant. Analyze the user's message and decide what action to take.
Return a JSON object with:
- action: One of fetch_emails, read_email, draft_reply, revise_draft, send_email, cancel_draft, check_calendar, summarize, chat
- email_id: (optional) For read/reply - use "latest" OR a numeric index ("1", "2", "3") from the email list below
- instructions: (optional) For draft/revise - the user's instructions or feedback
- chat_response: (optional) For chat - your helpful response

Always choose the email that best matches the user's intent based on **subject and sender** from the email list.
If the user mentions a phrase from a subject (e.g. "Submit your education loan application"),
select the corresponding email and set email_id to its numeric index from the list.

Examples:
- "show my emails" → {"action": "fetch_emails"}
- "read the latest" → {"action": "read_email", "email_id": "latest"}
- "reply to first email saying thanks" → {"action": "draft_reply", "email_id": "1", "instructions": "say thanks"}
- "draft reply to 'Submit your education loan application'" → {"action": "draft_reply", "email_id": "1", "instructions": "draft a reply about my loan application"}
- "make it shorter" → {"action": "revise_draft", "instructions": "make it shorter"}
- "send it" → {"action": "send_email"}
- "what can you do?" → {"action": "chat", "chat_response": "I can help you..."}"""

    context = f"""
Email list (use these indices in email_id):
{email_list_text}

Available email IDs: {available_emails if available_emails else "None - need to fetch first"}
Current draft exists: {has_draft}
{f"Draft is for: {st.session_state.current_draft.get('to', 'unknown')}" if has_draft else ""}

User message: "{user_input}"
"""

    try:
        # LLM returns structured EmailAction object
        action = structured_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=context)
        ])
        
        # Execute the action
        return execute_action(action, user_input)
    
    except Exception as e:
        # Fallback to chat if structured output fails
        return chat_with_llm(user_input)


def chat_with_llm(message: str) -> str:
    """General chat with LLM"""
    try:
        from langchain_core.messages import HumanMessage, SystemMessage
        
        context = f"""You are an email assistant. The user has these emails loaded:
{list(st.session_state.email_cache.keys()) if st.session_state.email_cache else 'No emails loaded yet'}

Current draft: {'Yes - ready to send or revise' if st.session_state.current_draft else 'None'}

Help the user with their email tasks. Be concise and helpful."""
        
        response = llm.invoke([
            SystemMessage(content=context),
            HumanMessage(content=message)
        ])
        return response.content
    except Exception as e:
        return f"❌ Error: {e}"


def format_email_list(emails: List[Dict]) -> str:
    """Format email list for display"""
    return emails  # Return raw for special rendering


def format_full_email(email_id: str) -> str:
    """Format full email for display"""
    email = st.session_state.email_cache.get(email_id)
    if not email:
        return "❌ Email not found."
    
    # Escape email content to prevent HTML issues
    subject = str(email.get('subject', 'No Subject'))
    sender = str(email.get('from', 'Unknown'))
    date = str(email.get('date', ''))
    body = str(email.get('body', ''))
    status = '🔵 Unread' if email.get('unread') else '✓ Read'
    
    return f"""📧 **{subject}**

**From:** `{sender}`
**Date:** {date}
**Status:** {status}

---

{body}

---
*[ID: {email_id}]*"""


def format_draft(body: str) -> str:
    """Format draft for display"""
    if not st.session_state.current_draft:
        return body
    
    to_addr = str(st.session_state.current_draft.get('to', ''))
    subject = str(st.session_state.current_draft.get('subject', ''))
    
    return f"""✍️ **Draft Reply**

**To:** `{to_addr}`
**Subject:** {subject}

---

{body}

---
💡 *Say "send" to send, provide feedback to revise, or "cancel" to discard*"""


def send_email() -> str:
    """Send the current draft"""
    global gmail_service
    
    if not st.session_state.current_draft:
        return "❌ No draft to send."
    
    draft = st.session_state.current_draft
    
    if not gmail_service:
        result = f"""✅ **Email Sent!** (Demo Mode)

**To:** {draft['to']}
**Subject:** {draft['subject']}

{draft['body']}

---
⚠️ *Mock mode - Gmail not connected*"""
        st.session_state.current_draft = {}
        return result
    
    try:
        from email.mime.text import MIMEText
        
        message = MIMEText(draft['body'])
        message['to'] = draft['to']
        message['subject'] = draft['subject']
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        send_result = gmail_service.users().messages().send(
            userId='me', body={'raw': raw}
        ).execute()
        
        result = f"""✅ **Email Sent Successfully!**

**To:** {draft['to']}
**Subject:** {draft['subject']}
**Message ID:** {send_result['id']}"""
        
        st.session_state.current_draft = {}
        return result
        
    except Exception as e:
        return f"❌ Error sending: {e}"


def summarize_emails() -> str:
    """Summarize loaded emails"""
    if not st.session_state.email_cache:
        return "❌ No emails to summarize."
    
    emails_text = ""
    for email in st.session_state.email_cache.values():
        emails_text += f"\n- From: {email['from']}, Subject: {email['subject']}"
    
    try:
        from langchain_core.messages import HumanMessage
        
        prompt = f"""Summarize these emails briefly, grouping by priority:

{emails_text}

Format:
🔴 Urgent:
🟡 Action needed:
🟢 FYI:"""
        
        response = llm.invoke([HumanMessage(content=prompt)])
        return f"📊 **Email Summary**\n\n{response.content}"
    except:
        return "📊 Summary not available"


# ===================================
# UI Components
# ===================================

def render_email_card(email: Dict):
    """Render an email as a card"""
    import html
    
    unread_class = "email-unread" if email.get('unread') else ""
    unread_badge = "🔵 " if email.get('unread') else ""
    
    # Escape HTML to prevent rendering issues with email addresses
    subject = html.escape(str(email.get('subject', 'No Subject')))
    sender = html.escape(str(email.get('from', 'Unknown')))
    date = html.escape(str(email.get('date', '')))
    snippet = html.escape(str(email.get('snippet', ''))[:80])
    
    with st.container():
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            st.markdown(f"""
            <div class="email-card {unread_class}">
                <strong>{unread_badge}{subject}</strong><br>
                <span style="color: #a0a0a0; font-size: 0.9em;">From: {sender}</span><br>
                <span style="color: #808080; font-size: 0.85em;">{date}</span><br>
                <span style="color: #909090; font-size: 0.85em;">{snippet}...</span>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("📖", key=f"read_{email['id']}", help="Read email"):
                st.session_state.messages.append({
                    "role": "user",
                    "content": f"Read email {email['id']}"
                })
                response = format_full_email(email['id'])
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
                st.rerun()


def render_sidebar():
    """Render the sidebar"""
    with st.sidebar:
        st.markdown("### 📧 Email Assistant")
        
        # Connection status
        gmail_svc, cal_svc, connected = init_google_services()
        global gmail_service, calendar_service
        gmail_service = gmail_svc
        calendar_service = cal_svc
        
        if connected:
            st.markdown('<span class="status-dot status-connected"></span> Gmail Connected', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-dot status-mock"></span> Demo Mode', unsafe_allow_html=True)
            # Debug info for cloud
            with st.expander("🔧 Debug Info"):
                has_secrets = False
                try:
                    has_secrets = "google_token" in st.secrets
                except:
                    pass
                st.write(f"Secrets available: {has_secrets}")
                if has_secrets:
                    try:
                        st.write(f"Token present: {'token' in st.secrets['google_token']}")
                        st.write(f"Refresh token: {'refresh_token' in st.secrets['google_token']}")
                    except Exception as e:
                        st.write(f"Error: {e}")
        
        st.divider()
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        
        if st.button("📬 Fetch Emails", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Show my latest emails"})
            emails = fetch_emails(5)
            st.session_state.messages.append({"role": "assistant", "content": emails, "type": "email_list"})
            st.rerun()
        
        if st.button("📊 Summarize Inbox", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Summarize my emails"})
            if not st.session_state.email_cache:
                fetch_emails(5)
            summary = summarize_emails()
            st.session_state.messages.append({"role": "assistant", "content": summary})
            st.rerun()
        
        if st.button("📅 Check Calendar", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Check my calendar"})
            calendar = get_calendar_info()
            st.session_state.messages.append({"role": "assistant", "content": calendar})
            st.rerun()
        
        st.divider()
        
        # Email list
        if st.session_state.email_cache:
            st.markdown("### 📥 Loaded Emails")
            for email in list(st.session_state.email_cache.values())[:5]:
                unread = "🔵 " if email.get('unread') else ""
                if st.button(f"{unread}{email['subject'][:25]}...", key=f"side_{email['id']}", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": f"Read {email['id']}"})
                    st.session_state.messages.append({"role": "assistant", "content": format_full_email(email['id'])})
                    st.rerun()
        
        st.divider()
        
        # Draft status
        if st.session_state.current_draft:
            st.markdown("### ✍️ Current Draft")
            st.info(f"To: {st.session_state.current_draft['to'][:30]}...")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Send", use_container_width=True):
                    result = send_email()
                    st.session_state.messages.append({"role": "assistant", "content": result})
                    st.rerun()
            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.current_draft = {}
                    st.session_state.messages.append({"role": "assistant", "content": "✅ Draft discarded."})
                    st.rerun()
        
        st.divider()
        
        if st.button("🔄 Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.current_draft = {}
            st.rerun()


def main():
    """Main app"""
    render_sidebar()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📧 Email Chat Assistant</h1>
        <p style="color: #a0a0a0;">Chat naturally to manage your emails</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                # Check if it's an email list
                if message.get("type") == "email_list" and isinstance(message["content"], list):
                    st.markdown('<div class="assistant-message">📬 Here are your latest emails:</div>', unsafe_allow_html=True)
                    for email in message["content"]:
                        render_email_card(email)
                else:
                    st.markdown(f'<div class="assistant-message">{message["content"]}</div>', unsafe_allow_html=True)
    
    # Chat input
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        user_input = st.chat_input("Type a message... (e.g., 'show my emails', 'reply to mock_001')")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        response = process_user_message(user_input)
        
        if isinstance(response, list):
            st.session_state.messages.append({"role": "assistant", "content": response, "type": "email_list"})
        else:
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        st.rerun()
    
    # Welcome message
    if not st.session_state.messages:
        st.markdown("""
        <div class="assistant-message">
            👋 <strong>Welcome!</strong> I'm your email assistant. Here's what I can do:
            <br><br>
            📬 <strong>Show my emails</strong> - Fetch your latest emails<br>
            📖 <strong>Read [email_id]</strong> - Read a specific email<br>
            ✍️ <strong>Reply to [email_id]</strong> - Draft a reply<br>
            📊 <strong>Summarize</strong> - Get an inbox summary<br>
            📅 <strong>Check calendar</strong> - See your schedule<br>
            <br>
            Try saying <em>"Show me my latest emails"</em> to get started!
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

