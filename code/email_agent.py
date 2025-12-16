"""
Supervised Multi AI Agent Architecture for Email Management
This implements a supervisor-based multi-agent system for email reading and replying:
- Email Reader: Reads and analyzes incoming emails using Gmail API
- Calendar Checker: Checks user's calendar for availability and context
- Reply Composer: Drafts email replies based on email content and user context
- User Confirmation Handler: Gets user approval and incorporates feedback
- Email Sender: Sends approved emails using Gmail API

Uses Google Gmail API and Calendar API for all operations
"""

import os
from typing import TypedDict, Annotated, List, Literal, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END, MessagesState
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Set API keys
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Initialize LLM
from langchain.chat_models import init_chat_model
llm = init_chat_model("openai:gpt-4o")

# Gmail and Calendar API setup placeholders
# These will need proper OAuth2 setup in production
gmail_service = None
calendar_service = None

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    import pickle
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/calendar.readonly'
    ]
    
    def authenticate_google_services():
        """Authenticate with Google APIs"""
        global gmail_service, calendar_service
        
        creds = None
        # Token file stores user's access and refresh tokens
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no valid credentials, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if os.path.exists('credentials.json'):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                else:
                    print("⚠️ credentials.json not found. Please set up Google OAuth2 credentials.")
                    return False
            
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        # Build services
        gmail_service = build('gmail', 'v1', credentials=creds)
        calendar_service = build('calendar', 'v3', credentials=creds)
        
        print("✅ Google services initialized successfully")
        return True
        
except ImportError:
    print("⚠️ Google API libraries not installed. Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")


# ===================================
# State Definition
# ===================================

class EmailState(MessagesState):
    """State for the email management multi-agent system"""
    next_agent: str = ""
    email_id: str = ""
    email_subject: str = ""
    email_from: str = ""
    email_body: str = ""
    email_date: str = ""
    email_analysis: str = ""
    calendar_context: str = ""
    draft_reply: str = ""
    user_feedback: str = ""
    final_reply: str = ""
    email_sent: bool = False
    task_complete: bool = False
    current_task: str = ""
    user_approved: bool = False
    revision_count: int = 0


# ===================================
# Supervisor Agent
# ===================================

def create_supervisor_chain():
    """Creates the supervisor decision chain for email management"""
    
    supervisor_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a supervisor managing a team of email management agents:
        
1. Email Reader - Reads and analyzes incoming emails
2. Calendar Checker - Checks user's calendar for relevant information
3. Reply Composer - Drafts email replies based on context
4. User Confirmation Handler - Gets user approval and feedback
5. Email Sender - Sends approved emails

Based on the current state, decide which agent should work next.
If user has approved and email is sent, respond with 'DONE'.

Current state:
- Has email analysis: {has_email_analysis}
- Has calendar context: {has_calendar_context}
- Has draft reply: {has_draft_reply}
- User approved: {user_approved}
- Email sent: {email_sent}

IMPORTANT: If an agent encountered an error, still proceed to the next logical agent.
Respond with ONLY the agent name (email_reader/calendar_checker/reply_composer/user_confirmation/email_sender) or 'DONE'.
"""),
        ("human", "{task}")
    ])
    
    return supervisor_prompt | llm


def supervisor_agent(state: EmailState) -> Dict:
    """Supervisor decides next agent using LLM"""
    
    messages = state["messages"]
    task = messages[-1].content if messages else "No task"
    
    # Check what's been completed
    has_email_analysis = bool(state.get("email_analysis", ""))
    has_calendar_context = bool(state.get("calendar_context", ""))
    has_draft_reply = bool(state.get("draft_reply", ""))
    user_approved = state.get("user_approved", False)
    email_sent = state.get("email_sent", False)
    user_feedback = state.get("user_feedback", "")  # Check for pending feedback
    
    # Get LLM decision
    chain = create_supervisor_chain()
    decision = chain.invoke({
        "task": task,
        "has_email_analysis": has_email_analysis,
        "has_calendar_context": has_calendar_context,
        "has_draft_reply": has_draft_reply,
        "user_approved": user_approved,
        "email_sent": email_sent
    })
    
    # Parse decision
    decision_text = decision.content.strip().lower()
    print(f"\n📋 Supervisor decision: {decision_text}")
    
    # Determine next agent with strict progression
    if "done" in decision_text or email_sent:
        next_agent = "end"
        supervisor_msg = "✅ Supervisor: Email workflow complete! Email sent successfully."
    elif not has_email_analysis:
        next_agent = "email_reader"
        supervisor_msg = "📋 Supervisor: Starting with email reading and analysis. Assigning to Email Reader..."
    elif not has_calendar_context:
        next_agent = "calendar_checker"
        supervisor_msg = "📋 Supervisor: Email analyzed. Checking calendar context. Assigning to Calendar Checker..."
    elif not has_draft_reply:
        next_agent = "reply_composer"
        supervisor_msg = "📋 Supervisor: Context gathered. Drafting reply. Assigning to Reply Composer..."
    elif user_feedback and not user_approved:
        # User provided feedback - need to revise the draft
        next_agent = "reply_composer"
        supervisor_msg = f"📋 Supervisor: User feedback received. Revising draft. Assigning to Reply Composer..."
    elif not user_approved:
        next_agent = "user_confirmation"
        supervisor_msg = "📋 Supervisor: Draft ready. Getting user approval. Assigning to User Confirmation Handler..."
    elif not email_sent:
        next_agent = "email_sender"
        supervisor_msg = "📋 Supervisor: User approved! Sending email. Assigning to Email Sender..."
    else:
        next_agent = "end"
        supervisor_msg = "✅ Supervisor: Email workflow complete."
    
    return {
        "messages": [AIMessage(content=supervisor_msg)],
        "next_agent": next_agent,
        "current_task": task
    }


# ===================================
# Agent 1: Email Reader
# ===================================

def email_reader(state: EmailState) -> Dict:
    """Reads and analyzes incoming email"""
    
    email_id = state.get("email_id", "")
    print(f"\n📧 Email Reader working on email ID: {email_id}...")
    
    try:
        if not gmail_service:
            # Mock data for testing without Gmail API
            email_data = {
                "subject": "Meeting Request for Project Discussion",
                "from": "john.doe@example.com",
                "body": """Hi,

I would like to schedule a meeting next week to discuss the Q4 project timeline and deliverables. 
Do you have availability on Tuesday or Wednesday afternoon?

Looking forward to hearing from you.

Best regards,
John""",
                "date": datetime.now().isoformat()
            }
            print("⚠️ Using mock email data (Gmail API not initialized)")
        else:
            # Fetch email from Gmail
            message = gmail_service.users().messages().get(
                userId='me', 
                id=email_id,
                format='full'
            ).execute()
            
            # Extract email details
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            # Extract body
            if 'parts' in message['payload']:
                parts = message['payload']['parts']
                body = ''
                for part in parts:
                    if part['mimeType'] == 'text/plain':
                        body = part['body'].get('data', '')
                        break
            else:
                body = message['payload']['body'].get('data', '')
            
            # Decode body (base64)
            import base64
            if body:
                body = base64.urlsafe_b64decode(body).decode('utf-8')
            
            email_data = {
                "subject": subject,
                "from": from_email,
                "body": body,
                "date": date
            }
        
        # Analyze email with LLM
        analysis_prompt = f"""As an email analyst, analyze this incoming email:

Subject: {email_data['subject']}
From: {email_data['from']}
Date: {email_data['date']}

Body:
{email_data['body']}

Provide a comprehensive analysis including:
1. Main purpose/intent of the email
2. Key requests or action items
3. Urgency level (High/Medium/Low)
4. Sentiment/tone (Formal/Casual/Urgent/Friendly)
5. Important dates or deadlines mentioned
6. What kind of response is expected
7. Calendar check needed? (Yes/No and why)

Be specific and actionable."""
        
        response = llm.invoke([HumanMessage(content=analysis_prompt)])
        analysis = response.content
        
        agent_message = f"""📧 Email Reader: Analyzed incoming email
        
Subject: {email_data['subject']}
From: {email_data['from']}

Analysis: {analysis[:300]}..."""
        
        return {
            "messages": [AIMessage(content=agent_message)],
            "email_subject": email_data['subject'],
            "email_from": email_data['from'],
            "email_body": email_data['body'],
            "email_date": email_data['date'],
            "email_analysis": analysis,
            "next_agent": "supervisor"
        }
        
    except Exception as e:
        error_msg = f"📧 Email Reader: Error reading email: {str(e)}"
        print(error_msg)
        return {
            "messages": [AIMessage(content=error_msg)],
            "email_analysis": f"Error: {str(e)}",
            "next_agent": "supervisor"
        }


# ===================================
# Agent 2: Calendar Checker
# ===================================

def calendar_checker(state: EmailState) -> Dict:
    """Checks user's calendar for relevant information"""
    
    print(f"\n📅 Calendar Checker analyzing schedule...")
    
    try:
        if not calendar_service:
            # Mock calendar data for testing
            calendar_data = f"""Calendar Status (Mock Data):
            
Available slots this week:
- Monday: 2:00 PM - 4:00 PM
- Tuesday: 10:00 AM - 12:00 PM, 3:00 PM - 5:00 PM
- Wednesday: 1:00 PM - 4:00 PM
- Thursday: 9:00 AM - 11:00 AM
- Friday: 2:00 PM - 3:00 PM

Upcoming commitments:
- Monday 10:00 AM: Team standup
- Tuesday 2:00 PM: Client presentation
- Wednesday 11:00 AM: Budget review
- Thursday 3:00 PM: Project deadline review
"""
            print("⚠️ Using mock calendar data (Calendar API not initialized)")
        else:
            # Fetch calendar events
            now = datetime.utcnow()
            time_min = now.isoformat() + 'Z'
            time_max = (now + timedelta(days=7)).isoformat() + 'Z'
            
            events_result = calendar_service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=20,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Format calendar data
            calendar_data = "Calendar Events (Next 7 days):\n\n"
            if not events:
                calendar_data += "No upcoming events scheduled.\n"
            else:
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    summary = event.get('summary', 'No title')
                    calendar_data += f"- {start}: {summary}\n"
        
        # Get email context
        email_analysis = state.get("email_analysis", "")
        email_body = state.get("email_body", "")
        
        # Analyze calendar context with LLM
        context_prompt = f"""As a calendar analyst, review the email and calendar to provide context for reply:

Email Analysis:
{email_analysis}

Email Body:
{email_body}

Calendar:
{calendar_data}

Provide:
1. Relevant availability based on email request
2. Conflicting commitments (if any)
3. Best time slots to offer
4. Calendar-related context to mention in reply
5. Suggested scheduling approach

Be specific with dates and times."""
        
        response = llm.invoke([HumanMessage(content=context_prompt)])
        context_analysis = response.content
        
        agent_message = f"""📅 Calendar Checker: Calendar context gathered
        
{context_analysis[:400]}..."""
        
        return {
            "messages": [AIMessage(content=agent_message)],
            "calendar_context": f"{calendar_data}\n\nContext Analysis:\n{context_analysis}",
            "next_agent": "supervisor"
        }
        
    except Exception as e:
        error_msg = f"📅 Calendar Checker: Error checking calendar: {str(e)}"
        print(error_msg)
        return {
            "messages": [AIMessage(content=error_msg)],
            "calendar_context": f"Error: {str(e)}",
            "next_agent": "supervisor"
        }


# ===================================
# Agent 3: Reply Composer
# ===================================

def reply_composer(state: EmailState) -> Dict:
    """Drafts email reply based on context"""
    
    print(f"\n✍️ Reply Composer drafting response...")
    
    try:
        email_subject = state.get("email_subject", "")
        email_from = state.get("email_from", "")
        email_body = state.get("email_body", "")
        email_analysis = state.get("email_analysis", "")
        calendar_context = state.get("calendar_context", "")
        user_feedback = state.get("user_feedback", "")
        revision_count = state.get("revision_count", 0)
        
        # Compose reply with LLM
        if user_feedback:
            compose_prompt = f"""As an email writer, revise the previous draft based on user feedback:

Original Email:
Subject: {email_subject}
From: {email_from}
Body: {email_body}

Previous Draft:
{state.get("draft_reply", "")}

User Feedback:
{user_feedback}

Create a REVISED email reply that:
1. Incorporates ALL user feedback
2. Maintains professional tone
3. Addresses all points from original email
4. Is clear and concise

Provide ONLY the email body (no subject line needed)."""
        else:
            compose_prompt = f"""As an email writer, draft a professional reply to this email:

Original Email:
Subject: {email_subject}
From: {email_from}
Body: {email_body}

Email Analysis:
{email_analysis}

Calendar Context:
{calendar_context}

Draft a professional email reply that:
1. Acknowledges their request/message
2. Provides relevant information based on calendar
3. Suggests specific times/dates if applicable
4. Is warm, professional, and helpful
5. Includes appropriate greeting and closing

Provide ONLY the email body (no subject line needed)."""
        
        response = llm.invoke([HumanMessage(content=compose_prompt)])
        draft = response.content
        
        if user_feedback:
            agent_message = f"""✍️ Reply Composer: Draft revised (Revision #{revision_count + 1})
            
{draft}

---
Please review and provide feedback or approve to send."""
        else:
            agent_message = f"""✍️ Reply Composer: Draft ready for review
            
{draft}

---
Please review and provide feedback or approve to send."""
        
        return {
            "messages": [AIMessage(content=agent_message)],
            "draft_reply": draft,
            "revision_count": revision_count + 1 if user_feedback else 0,
            "user_feedback": "",  # Clear feedback after revision
            "next_agent": "supervisor"
        }
        
    except Exception as e:
        error_msg = f"✍️ Reply Composer: Error drafting reply: {str(e)}"
        print(error_msg)
        return {
            "messages": [AIMessage(content=error_msg)],
            "draft_reply": f"Error: {str(e)}",
            "user_feedback": "",  # Clear feedback on error too
            "next_agent": "supervisor"
        }


# ===================================
# Agent 4: User Confirmation Handler
# ===================================

def user_confirmation(state: EmailState) -> Dict:
    """Gets user approval and handles feedback"""
    
    print(f"\n👤 User Confirmation Handler: Awaiting user input...")
    
    draft_reply = state.get("draft_reply", "")
    email_subject = state.get("email_subject", "")
    email_from = state.get("email_from", "")
    
    # Display draft to user
    confirmation_message = f"""👤 User Confirmation Handler: Please review the draft reply

To: {email_from}
Re: {email_subject}

Draft:
{draft_reply}

---
Options:
1. Type 'APPROVE' to send the email as is
2. Type your feedback/changes and the draft will be revised
3. Type 'CANCEL' to cancel the email

Your response: """
    
    print(confirmation_message)
    
    # In a real application, this would wait for user input
    # For now, we'll return to indicate user input is needed
    
    return {
        "messages": [AIMessage(content=confirmation_message)],
        "next_agent": "waiting_for_user",
        "user_approved": False
    }


def process_user_input(state: EmailState, user_input: str) -> Dict:
    """Process user's confirmation or feedback"""
    
    user_input_clean = user_input.strip().upper()
    
    if user_input_clean == "APPROVE":
        # User approved the draft
        return {
            "messages": [AIMessage(content="✅ User approved the email. Proceeding to send...")],
            "user_approved": True,
            "final_reply": state.get("draft_reply", ""),
            "next_agent": "supervisor"
        }
    elif user_input_clean == "CANCEL":
        # User cancelled
        return {
            "messages": [AIMessage(content="❌ Email cancelled by user.")],
            "task_complete": True,
            "next_agent": "end"
        }
    else:
        # User provided feedback for revision
        return {
            "messages": [AIMessage(content=f"📝 User feedback received: {user_input}\nRevising draft...")],
            "user_feedback": user_input,
            "user_approved": False,
            "next_agent": "reply_composer"  # Go back to composer with feedback
        }


# ===================================
# Agent 5: Email Sender
# ===================================

def email_sender(state: EmailState) -> Dict:
    """Sends the approved email"""
    
    print(f"\n📤 Email Sender: Sending email...")
    
    try:
        email_from = state.get("email_from", "")
        email_subject = state.get("email_subject", "")
        final_reply = state.get("final_reply", "")
        email_id = state.get("email_id", "")
        
        if not gmail_service:
            # Mock sending for testing
            send_result = f"""✅ EMAIL SENT (Mock):
To: {email_from}
Subject: Re: {email_subject}

Body:
{final_reply}

---
⚠️ Note: This is a simulation. Gmail API not initialized.
"""
            print("⚠️ Mock email send (Gmail API not initialized)")
        else:
            # Create email message
            from email.mime.text import MIMEText
            import base64
            
            message = MIMEText(final_reply)
            message['to'] = email_from
            message['subject'] = f"Re: {email_subject}"
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send email
            send_message = gmail_service.users().messages().send(
                userId='me',
                body={'raw': raw_message, 'threadId': email_id}
            ).execute()
            
            send_result = f"""✅ EMAIL SENT SUCCESSFULLY:
To: {email_from}
Subject: Re: {email_subject}
Message ID: {send_message['id']}

Body:
{final_reply}
"""
        
        return {
            "messages": [AIMessage(content=send_result)],
            "email_sent": True,
            "task_complete": True,
            "next_agent": "supervisor"
        }
        
    except Exception as e:
        error_msg = f"📤 Email Sender: Error sending email: {str(e)}"
        print(error_msg)
        return {
            "messages": [AIMessage(content=error_msg)],
            "email_sent": False,
            "task_complete": True,
            "next_agent": "end"
        }


# ===================================
# Router Function
# ===================================

def router(state: EmailState) -> Literal["supervisor", "email_reader", "calendar_checker", "reply_composer", "user_confirmation", "email_sender", "__end__"]:
    """Routes to next agent based on state"""
    
    next_agent = state.get("next_agent", "supervisor")
    
    if next_agent == "end" or state.get("task_complete", False):
        return END
    
    if next_agent == "waiting_for_user":
        # Special case: waiting for user input
        # In real implementation, this would pause execution
        return END
        
    if next_agent in ["supervisor", "email_reader", "calendar_checker", "reply_composer", "user_confirmation", "email_sender"]:
        return next_agent
        
    return "supervisor"


# ===================================
# Build the Workflow
# ===================================

def create_email_workflow():
    """Create the supervised email management multi-agent workflow"""
    
    # Create workflow
    workflow = StateGraph(EmailState)
    
    # Add nodes
    workflow.add_node("supervisor", supervisor_agent)
    workflow.add_node("email_reader", email_reader)
    workflow.add_node("calendar_checker", calendar_checker)
    workflow.add_node("reply_composer", reply_composer)
    workflow.add_node("user_confirmation", user_confirmation)
    workflow.add_node("email_sender", email_sender)
    
    # Set entry point
    workflow.set_entry_point("supervisor")
    
    # Add routing
    for node in ["supervisor", "email_reader", "calendar_checker", "reply_composer", "user_confirmation", "email_sender"]:
        workflow.add_conditional_edges(
            node,
            router,
            {
                "supervisor": "supervisor",
                "email_reader": "email_reader",
                "calendar_checker": "calendar_checker",
                "reply_composer": "reply_composer",
                "user_confirmation": "user_confirmation",
                "email_sender": "email_sender",
                END: END
            }
        )
    
    # Compile graph with recursion limit
    graph = workflow.compile()
    return graph


# ===================================
# Helper Functions
# ===================================

def process_email_with_confirmation(email_id: str = None):
    """
    Process an email with full workflow including user confirmation
    
    Args:
        email_id: Gmail message ID (optional, will use mock data if not provided)
    
    Returns:
        Interactive session that requires user input
    """
    
    # Initialize Google services if not already done
    if not gmail_service and not calendar_service:
        try:
            authenticate_google_services()
        except:
            print("⚠️ Continuing with mock data (Google services not available)")
    
    graph = create_email_workflow()
    
    # Start the workflow
    initial_state = {
        "messages": [HumanMessage(content=f"Process email and prepare reply")],
        "email_id": email_id or "mock_email_001"
    }
    
    # Run until user confirmation needed
    response = graph.invoke(
        initial_state,
        config={"recursion_limit": 50}
    )
    
    return response


def continue_with_user_input(previous_state: EmailState, user_input: str):
    """
    Continue workflow after user provides input
    
    Args:
        previous_state: The state from previous workflow execution
        user_input: User's approval, feedback, or cancellation
    """
    
    # Process user input
    update = process_user_input(previous_state, user_input)
    
    # Merge with previous state
    new_state = {**previous_state, **update}
    
    # Continue workflow
    graph = create_email_workflow()
    response = graph.invoke(
        new_state,
        config={"recursion_limit": 50}
    )
    
    return response


# ===================================
# Interactive Session Manager
# ===================================

class EmailAgentSession:
    """Manages interactive email agent session"""
    
    def __init__(self, email_id: str = None):
        self.email_id = email_id
        self.current_state = None
        self.graph = create_email_workflow()
        
        # Initialize Google services
        try:
            authenticate_google_services()
        except:
            print("⚠️ Continuing with mock data (Google services not available)")
    
    def start(self):
        """Start the email processing workflow"""
        print("\n" + "="*60)
        print("📧 Email Agent Session Started")
        print("="*60 + "\n")
        
        initial_state = {
            "messages": [HumanMessage(content=f"Process email and prepare reply")],
            "email_id": self.email_id or "mock_email_001"
        }
        
        # Run until user input needed
        self.current_state = self.graph.invoke(
            initial_state,
            config={"recursion_limit": 50}
        )
        
        # Print conversation history
        self._print_messages()
        
        # Check if waiting for user
        if self.current_state.get("next_agent") == "waiting_for_user":
            return "WAITING_FOR_USER"
        else:
            return "COMPLETE"
    
    def submit_feedback(self, user_input: str):
        """Submit user feedback or approval"""
        
        if not self.current_state:
            print("❌ No active session. Call start() first.")
            return
        
        # Process user input
        update = process_user_input(self.current_state, user_input)
        
        # Merge with current state
        new_state = {**self.current_state, **update}
        
        # Continue workflow
        self.current_state = self.graph.invoke(
            new_state,
            config={"recursion_limit": 50}
        )
        
        # Print conversation history
        self._print_messages()
        
        # Check if waiting for user again (in case of revision)
        if self.current_state.get("next_agent") == "waiting_for_user":
            return "WAITING_FOR_USER"
        else:
            return "COMPLETE"
    
    def _print_messages(self):
        """Print conversation messages"""
        print("\n" + "="*60)
        print("📋 WORKFLOW MESSAGES")
        print("="*60 + "\n")
        
        for msg in self.current_state["messages"]:
            if hasattr(msg, 'content'):
                print(msg.content)
                print("-"*60 + "\n")


# ===================================
# Main Execution
# ===================================

if __name__ == "__main__":
    import sys
    
    print("\n" + "="*60)
    print("📧 Email Management Multi-Agent System")
    print("="*60 + "\n")
    
    print("📝 SETUP INSTRUCTIONS:")
    print("-" * 60)
    print("To use with real Gmail and Calendar:")
    print("1. Install required packages:")
    print("   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    print("2. Set up Google OAuth2 credentials (credentials.json)")
    print("3. Run this script and authenticate when prompted")
    print("\nFor now, running with MOCK DATA for demonstration...\n")
    print("="*60 + "\n")
    
    # Interactive session
    session = EmailAgentSession()
    
    # Start processing
    status = session.start()
    
    # If waiting for user input, start interactive loop
    while status == "WAITING_FOR_USER":
        user_input = input("\n👤 Your response: ").strip()
        
        if not user_input:
            print("⚠️ Please provide input (APPROVE/CANCEL/feedback)")
            continue
        
        status = session.submit_feedback(user_input)
    
    print("\n" + "="*60)
    print("✅ Email Workflow Complete!")
    print("="*60 + "\n")

