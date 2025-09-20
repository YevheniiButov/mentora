"""
Email client utility for POP/IMAP operations
"""

import poplib
import imaplib
import email
import ssl
import os
import json
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
import logging

logger = logging.getLogger(__name__)

class EmailClient:
    """Email client for POP/IMAP operations"""
    
    def __init__(self, config):
        """
        Initialize email client with configuration
        
        Args:
            config (dict): Email configuration containing:
                - pop_host, pop_port, pop_username, pop_password
                - imap_host, imap_port, imap_username, imap_password
                - smtp_host, smtp_port, smtp_username, smtp_password
        """
        self.config = config
        self.pop_connection = None
        self.imap_connection = None
        
    def connect_pop(self):
        """Connect to POP server"""
        try:
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect to POP server
            if self.config.get('pop_port') == 995:
                # SSL connection
                self.pop_connection = poplib.POP3_SSL(
                    self.config['pop_host'], 
                    self.config['pop_port'],
                    context=context
                )
            else:
                # Regular connection
                self.pop_connection = poplib.POP3(
                    self.config['pop_host'], 
                    self.config['pop_port']
                )
            
            # Authenticate
            self.pop_connection.user(self.config['pop_username'])
            self.pop_connection.pass_(self.config['pop_password'])
            
            logger.info(f"Connected to POP server {self.config['pop_host']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to POP server: {str(e)}")
            return False
    
    def connect_imap(self):
        """Connect to IMAP server"""
        try:
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect to IMAP server
            if self.config.get('imap_port') == 993:
                # SSL connection
                self.imap_connection = imaplib.IMAP4_SSL(
                    self.config['imap_host'], 
                    self.config['imap_port'],
                    ssl_context=context
                )
            else:
                # Regular connection
                self.imap_connection = imaplib.IMAP4(
                    self.config['imap_host'], 
                    self.config['imap_port']
                )
            
            # Authenticate
            self.imap_connection.login(
                self.config['imap_username'], 
                self.config['imap_password']
            )
            
            logger.info(f"Connected to IMAP server {self.config['imap_host']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to IMAP server: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from email servers"""
        try:
            if self.pop_connection:
                self.pop_connection.quit()
                self.pop_connection = None
                
            if self.imap_connection:
                self.imap_connection.logout()
                self.imap_connection = None
                
            logger.info("Disconnected from email servers")
            
        except Exception as e:
            logger.error(f"Error disconnecting: {str(e)}")
    
    def fetch_emails_pop(self, limit=50):
        """
        Fetch emails using POP3
        
        Args:
            limit (int): Maximum number of emails to fetch
            
        Returns:
            list: List of email data dictionaries
        """
        if not self.pop_connection:
            if not self.connect_pop():
                return []
        
        try:
            emails = []
            
            # Get number of messages
            num_messages = len(self.pop_connection.list()[1])
            messages_to_fetch = min(limit, num_messages)
            
            # Fetch messages
            for i in range(1, messages_to_fetch + 1):
                try:
                    # Get message
                    raw_email = b'\n'.join(self.pop_connection.retr(i)[1])
                    email_message = email.message_from_bytes(raw_email)
                    
                    # Parse email
                    email_data = self._parse_email(email_message)
                    if email_data:
                        emails.append(email_data)
                        
                except Exception as e:
                    logger.error(f"Error fetching message {i}: {str(e)}")
                    continue
            
            logger.info(f"Fetched {len(emails)} emails via POP3")
            return emails
            
        except Exception as e:
            logger.error(f"Error fetching emails via POP3: {str(e)}")
            return []
    
    def fetch_emails_imap(self, limit=50, folder='INBOX'):
        """
        Fetch emails using IMAP
        
        Args:
            limit (int): Maximum number of emails to fetch
            folder (str): IMAP folder to fetch from
            
        Returns:
            list: List of email data dictionaries
        """
        if not self.imap_connection:
            if not self.connect_imap():
                return []
        
        try:
            emails = []
            
            # Select folder
            self.imap_connection.select(folder)
            
            # Search for all emails
            status, messages = self.imap_connection.search(None, 'ALL')
            
            if status != 'OK':
                logger.error("Failed to search emails")
                return []
            
            # Get message IDs
            message_ids = messages[0].split()
            messages_to_fetch = message_ids[-limit:] if len(message_ids) > limit else message_ids
            
            # Fetch messages
            for msg_id in messages_to_fetch:
                try:
                    # Get message
                    status, msg_data = self.imap_connection.fetch(msg_id, '(RFC822)')
                    
                    if status != 'OK':
                        continue
                    
                    # Parse email
                    email_message = email.message_from_bytes(msg_data[0][1])
                    email_data = self._parse_email(email_message)
                    
                    if email_data:
                        emails.append(email_data)
                        
                except Exception as e:
                    logger.error(f"Error fetching message {msg_id}: {str(e)}")
                    continue
            
            logger.info(f"Fetched {len(emails)} emails via IMAP")
            return emails
            
        except Exception as e:
            logger.error(f"Error fetching emails via IMAP: {str(e)}")
            return []
    
    def _parse_email(self, email_message):
        """
        Parse email message into dictionary
        
        Args:
            email_message: Email message object
            
        Returns:
            dict: Parsed email data
        """
        try:
            # Get basic headers
            subject = self._decode_header(email_message.get('Subject', ''))
            sender = self._decode_header(email_message.get('From', ''))
            recipient = self._decode_header(email_message.get('To', ''))
            message_id = email_message.get('Message-ID', '')
            date_str = email_message.get('Date', '')
            
            # Parse date
            try:
                date_received = email.utils.parsedate_to_datetime(date_str)
            except:
                date_received = datetime.utcnow()
            
            # Extract sender email and name
            sender_email, sender_name = self._parse_email_address(sender)
            
            # Get content
            html_content = None
            text_content = None
            
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get('Content-Disposition', ''))
                    
                    # Skip attachments
                    if 'attachment' in content_disposition:
                        continue
                    
                    # Get text content
                    if content_type == 'text/plain' and not text_content:
                        text_content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    
                    # Get HTML content
                    elif content_type == 'text/html' and not html_content:
                        html_content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
            else:
                # Single part message
                content_type = email_message.get_content_type()
                content = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                
                if content_type == 'text/html':
                    html_content = content
                else:
                    text_content = content
            
            # Calculate size
            size_bytes = len(email_message.as_bytes())
            
            # Check for attachments
            has_attachments = False
            attachment_count = 0
            
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_disposition() == 'attachment':
                        has_attachments = True
                        attachment_count += 1
            
            return {
                'message_id': message_id,
                'subject': subject,
                'sender_email': sender_email,
                'sender_name': sender_name,
                'recipient_email': recipient,
                'html_content': html_content,
                'text_content': text_content,
                'date_received': date_received,
                'size_bytes': size_bytes,
                'has_attachments': has_attachments,
                'attachment_count': attachment_count
            }
            
        except Exception as e:
            logger.error(f"Error parsing email: {str(e)}")
            return None
    
    def _decode_header(self, header):
        """Decode email header"""
        try:
            decoded_parts = decode_header(header)
            decoded_string = ''
            
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    if encoding:
                        decoded_string += part.decode(encoding)
                    else:
                        decoded_string += part.decode('utf-8', errors='ignore')
                else:
                    decoded_string += part
            
            return decoded_string
        except:
            return str(header)
    
    def _parse_email_address(self, address_string):
        """Parse email address string into email and name"""
        try:
            # Try to parse with email.utils
            name, email_addr = email.utils.parseaddr(address_string)
            
            if not email_addr:
                # Fallback: extract email from string
                import re
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', address_string)
                email_addr = email_match.group() if email_match else address_string
                name = address_string.replace(email_addr, '').strip('<>"')
            
            return email_addr, name if name else None
            
        except:
            return address_string, None
    
    def mark_as_read_imap(self, message_id, folder='INBOX'):
        """Mark email as read in IMAP"""
        if not self.imap_connection:
            return False
        
        try:
            self.imap_connection.select(folder)
            self.imap_connection.store(message_id, '+FLAGS', '\\Seen')
            return True
        except Exception as e:
            logger.error(f"Error marking email as read: {str(e)}")
            return False
    
    def delete_email_imap(self, message_id, folder='INBOX'):
        """Delete email in IMAP"""
        if not self.imap_connection:
            return False
        
        try:
            self.imap_connection.select(folder)
            self.imap_connection.store(message_id, '+FLAGS', '\\Deleted')
            self.imap_connection.expunge()
            return True
        except Exception as e:
            logger.error(f"Error deleting email: {str(e)}")
            return False


def get_email_config():
    """Get email configuration from environment or config"""
    return {
        'pop_host': os.getenv('POP_HOST', 'webhost.dynadot.com'),
        'pop_port': int(os.getenv('POP_PORT', 995)),
        'pop_username': os.getenv('POP_USERNAME', 'info@mentora.com.in'),
        'pop_password': os.getenv('POP_PASSWORD', '59620372'),
        
        'imap_host': os.getenv('IMAP_HOST', 'webhost.dynadot.com'),
        'imap_port': int(os.getenv('IMAP_PORT', 993)),
        'imap_username': os.getenv('IMAP_USERNAME', 'info@mentora.com.in'),
        'imap_password': os.getenv('IMAP_PASSWORD', '59620372'),
        
        'smtp_host': os.getenv('SMTP_HOST', 'webhost.dynadot.com'),
        'smtp_port': int(os.getenv('SMTP_PORT', 587)),
        'smtp_username': os.getenv('SMTP_USERNAME', 'info@mentora.com.in'),
        'smtp_password': os.getenv('SMTP_PASSWORD', '59620372')
    }
