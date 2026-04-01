"""
Handles all Gmail API interactions - reading and sending emails
"""
import pickle
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
from typing import List, Dict, Any

class GmailService:
    def __init__(self, credentials_file='credentials.json'):
        """
        Initialize Gmail service with OAuth2 authentication
        """
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.modify',
                       'https://www.googleapis.com/auth/gmail.readonly',
                      'https://www.googleapis.com/auth/gmail.send']
        self.credentials_file = credentials_file
        self.service = self.authenticate()
    
    def authenticate(self):
        """
        Authenticate with Gmail API using OAuth2
        Returns: Authenticated Gmail service object
        """
        creds = None
        
        # Check if we already have valid credentials
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        # Build and return Gmail service
        return build('gmail', 'v1', credentials=creds)
    
    def get_unread_emails(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch unread emails from inbox
        """
        try:
            # Call Gmail API to get messages
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['INBOX', 'UNREAD'],
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for msg in messages:
                # Get full message details
                message = self.service.users().messages().get(
                    userId='me', 
                    id=msg['id'],
                    format='full'
                ).execute()
                
                # Extract headers
                headers = message['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                
                # Extract body (simplified - handles only plain text for now)
                body = ''
                if 'parts' in message['payload']:
                    for part in message['payload']['parts']:
                        if part['mimeType'] == 'text/plain':
                            data = part['body'].get('data', '')
                            body = base64.urlsafe_b64decode(data).decode('utf-8')
                            break
                else:
                    data = message['payload']['body'].get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                
                emails.append({
                    'id': msg['id'],
                    'subject': subject,
                    'from': sender,
                    'body': body,
                    'threadId': message['threadId']
                })
            
            return emails
            
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []
    
    def send_email(self, to: str, subject: str, body: str) -> bool:
        """
        Send an email using Gmail API
        Returns: True if successful
        """
        try:
            # Create email message
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            message['from'] = 'me'
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send message
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            print(f"Email sent successfully to {to}")
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def mark_as_read(self, message_id: str) -> bool:
        """
        Mark an email as read by removing the UNREAD label.
        Returns True if UNREAD label was removed (verified by API response).
        """
        try:
            result = self.service.users().messages().modify(
            userId='me',
            id=message_id,
            body={"removeLabelIds": ["UNREAD"]}
            ).execute()
    
            print(f"[mark_as_read] Updated labels: {result.get('labelIds', [])}")
            return "UNREAD" not in result.get("labelIds", [])
        
        except Exception as e:
            print(f"[mark_as_read] ERROR: {e}")
            return False
    def get_message_labels(self, message_id: str) -> List[str]:
       """
       Return list of label IDs for a message (useful for debugging).
       """
       try:
            msg = self.service.users().messages().get(
               userId='me',
               id=message_id,
               format='metadata'
               ).execute()
            labels = msg.get('labelIds', [])
            print(f"[get_message_labels] message_id={message_id} labels={labels}")
            return labels
       except Exception as e:
            print(f"[get_message_labels] Error: {e}")
            return []