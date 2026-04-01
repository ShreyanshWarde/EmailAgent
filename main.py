"""
Main AI Email Agent - Orchestrates everything
"""
import os
from pyexpat.errors import messages
from typing import List, Dict, Any
from dotenv import load_dotenv
from pydantic_ai import Agent
from openai import OpenAI

from models import EmailContent, DraftResponse
from gmail_service import GmailService
import nest_asyncio
nest_asyncio.apply()
# Load environment variables
load_dotenv()

class EmailAIAgent:
    """
    Main AI agent that reads emails and generates responses
    """
    def __init__(self):
        """
        Initialize the AI agent and Gmail service
        """
        # Initialize OpenAI client
        self.openai_client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
        # Initialize Gmail service
        self.gmail_service = GmailService()
        
        # Create PydanticAI agent
        self.agent = Agent(
            model='openai:gpt-4o-mini',  # You can use gpt-3.5-turbo for cheaper testing
            system_prompt="""You are an intelligent email assistant. Your tasks:
            1. Analyze incoming emails
            2. Decide if a reply is needed
            3. Draft appropriate responses
            4. Use professional but friendly tone
            
            Guidelines:
            - Only reply to emails that need responses (not spam, not notifications)
            - Keep responses concise but helpful
            - Ask clarifying questions if needed
            - Never share sensitive information
            - Be polite and professional"""
        )

    def process_emails(self, max_emails: int = 5) -> None:
        """
        Main function: Fetch unread emails, process them, send replies
        """
        print("🔍 Fetching unread emails...")
        
        # Step 1: Get unread emails
        emails = self.gmail_service.get_unread_emails(max_results=max_emails)
        
        if not emails:
            print("No unread emails found.")
            return
        
        print(f"📧 Found {len(emails)} unread email(s)")
        
        # Step 2: Process each email
        for email in emails:
            print(f"\n{'='*50}")
            print(f"Processing email from: {email['from']}")
            print(f"Subject: {email['subject'][:50]}...")
            
            # Step 3: Use AI to analyze and draft response
            response = self._generate_response(email)
            
            # Step 4: Send reply if needed
            if response.should_reply:
                print(f"🤖 AI decided to reply. Reason: {response.reason}")
                
                # Extract email address from "Name <email@example.com>" format
                to_email = email['from'].split('<')[-1].split('>')[0] if '<' in email['from'] else email['from']
                
                # Send the reply
                success = self.gmail_service.send_email(
                    to=to_email,
                    subject=response.reply_subject,
                    body=response.reply_body
                )
                
                if success:
                    print("✅ Reply sent successfully!")
                    # Mark email as read
                    self.gmail_service.mark_as_read(email['id'])
                else:
                    print("❌ Failed to send reply")
            else:
                print(f"⏭️ Skipping reply. Reason: {response.reason}")
                
                # Still mark as read if it's spam/notification
                if "notification" in response.reason.lower() or "spam" in response.reason.lower():
                    self.gmail_service.mark_as_read(email['id'])
    
    def _generate_response(self, email: Dict[str, Any]) -> DraftResponse:
        """
        Use AI to analyze email and generate response
        """
        # Prepare the email content for AI
        email_content = f"""
        FROM: {email['from']}
        SUBJECT: {email['subject']}
        BODY: {email['body'][:1000]}  # Limit to first 1000 chars
        """
        
        try:
            # Use the agent to generate response
            result = self.agent.run_sync(
                f"""Analyze this email and decide if we should reply:
                
                {email_content}
                
                Provide:
                1. Should we reply? (yes/no with reason)
                2. If yes, draft a response
                3. Subject for reply (should reference original)
                4. Tone to use
                """
            )
            
            # Parse the response into our Pydantic model
            # Note: In a real app, you'd use structured output from the agent
            # For simplicity, we'll use a simplified approach
            
            # For now, let's use OpenAI directly for structured output
            completion = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an email assistant. Respond in JSON format."},
                    {"role": "user", "content": f"""Analyze this email and provide response in this exact JSON format:
                    {{
                        "should_reply": true/false,
                        "reason": "reason for decision",
                        "reply_subject": "Re: [Original Subject]",
                        "reply_body": "drafted response here",
                        "tone": "professional/friendly/formal/casual"
                    }}
                    
                    Email to analyze:
                    {email_content}
                    
                    Rules:
                    - Reply to important emails only
                    - Don't reply to spam, newsletters, or automated notifications
                    - Keep responses concise
                    """}
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse JSON response
            import json
            ai_response = json.loads(completion.choices[0].message.content)
            
            # Convert to Pydantic model
            return DraftResponse(**ai_response)
            
        except Exception as e:
            print(f"Error generating response: {e}")
            # Return a default response
            return DraftResponse(
                should_reply=False,
                reason="Error processing email with AI",
                reply_subject="",
                reply_body="",
                tone="professional"
            )
'''   
    def test_send_email(self, to_email: str, subject: str, body: str) -> None:
        """
        Test function to send an email directly
        """
        print(f"\n📤 Testing email send to: {to_email}")
        success = self.gmail_service.send_email(to_email, subject, body)
        if success:
            print("✅ Test email sent successfully!")
        else:
            print("❌ Failed to send test email")
'''
def main():
    """
    Main execution function
    """
    print("🚀 Starting Email AI Agent...")
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ ERROR: OPENAI_API_KEY not found in .env file")
        print("Please add your OpenAI API key to the .env file")
        return
    
    # Initialize agent
    agent = EmailAIAgent()
    try:
        #limit = input("Max emails to process (default 5): ").strip()
        #limit = int(limit) if limit else 5
        limit = len(agent.gmail_service.get_unread_emails())
        agent.process_emails(max_emails=limit)
    except ValueError:
        print("Invalid number, using default 5")
        agent.process_emails()
'''    
    # Menu for different operations
    while True:
        print("\n" + "="*50)
        print("EMAIL AI AGENT - MAIN MENU")
        print("="*50)
        print("1. Process unread emails (read and reply)")
        print("2. Send test email")
        print("3. Check unread emails (view only)")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            try:
                limit = input("Max emails to process (default 5): ").strip()
                limit = int(limit) if limit else 5
                agent.process_emails(max_emails=limit)
            except ValueError:
                print("Invalid number, using default 5")
                agent.process_emails()
                
        elif choice == '2':
            to_email = input("Recipient email: ").strip()
            subject = input("Subject: ").strip()
            body = input("Body (type 'AI' for AI-generated): ").strip()
            
            if body.upper() == 'AI':
                # Generate AI response
                completion = agent.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are writing a test email."},
                        {"role": "user", "content": f"Write a brief test email about: {subject}"}
                    ]
                )
                body = completion.choices[0].message.content
            
            agent.test_send_email(to_email, subject, body)
            
        elif choice == '3':
            emails = agent.gmail_service.get_unread_emails(max_results=10)
            print(f"\nFound {len(emails)} unread emails:")
            for i, email in enumerate(emails, 1):
                print(f"\n{i}. From: {email['from']}")
                print(f"   Subject: {email['subject']}")
                print(f"   Preview: {email['body'][:100]}...")
                
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please select 1-4.")
'''
        
if __name__ == "__main__":
    main()