"""
Email Utilities Module.

This module provides functions for sending various types of emails from the application.
It includes support for modern HTML email templates with responsive design, tabular
data formatting, and consistent branding elements. All emails are sent with both
HTML and plain text alternatives for maximum compatibility.

The module handles different notification types including:
- Account approval notifications
- Enrollment summaries
- Password reset emails
- Slot confirmation emails
"""
import smtplib  # SMTP client for sending emails
from email.message import EmailMessage  # Email message container
from email.mime.multipart import MIMEMultipart  # For multipart email messages (HTML + plain text)
from email.mime.text import MIMEText  # For text content in emails
from typing import Optional, List, Dict, Any  # Type hints
import os  # For accessing environment variables
from dotenv import load_dotenv  # For loading environment variables from .env file
import logging  # For logging email sending status
from datetime import datetime  # For timestamp formatting

# Load environment variables from .env file
load_dotenv()

# Organization contact information constants
# Not using the ones in slots/models.py to avoid circular imports
ORG_FIRST_NAME = "Cesare"
ORG_LAST_NAME = "Casaletel"
ORG_TELEPHONE = "091 815 10 11"
ORG_EMAIL = "decs-cpt.trevano.promtec@edu.ti.ch"


# Configure logging for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_contact_info_html():
    """
    Generate HTML formatted contact information footer for emails.
    
    Creates a consistent, styled footer section with organization contact details
    that is used in all HTML emails sent by the system.
    
    Returns:
        str: HTML formatted contact information section ready to be included in email templates
    """
    return f"""
    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px;">
        <p>Per ulteriori informazioni, contattare:</p>
        <p>{ORG_FIRST_NAME} {ORG_LAST_NAME}<br>
        Tel: {ORG_TELEPHONE}<br>
        Email: <a href="mailto:{ORG_EMAIL}" style="color: #3366cc;">{ORG_EMAIL}</a></p>
        <p style="color: #999;">SAM Trevano - Centro Professionale Tecnico</p>
    </div>
    """

def send_email(
    to_email: str,
    subject: str,
    body: str,
    is_html: bool = False
    ) -> bool:
    """
    Send an email using SMTP with support for both HTML and plain text content.
    
    This is the core email sending function used by all specific email types.
    It handles the SMTP connection, message formatting, and error handling.
    When HTML content is provided, it creates a multipart MIME message with
    both HTML and plain text alternatives for maximum compatibility.
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject line
        body (str): Email body content (HTML or plain text)
        is_html (bool, optional): Whether the body is HTML formatted. Defaults to False.
        
    Returns:
        bool: True if email was sent successfully, False otherwise
        
    Environment Variables:
        SMTP_SERVER: SMTP server hostname (default: mail.infomaniak.com)
        SMTP_PORT: SMTP server port (default: 465 for SSL)
        SMTP_USER: SMTP username/from email (default: no-reply@samtrevano.ch)
        SMTP_PASSWORD: SMTP password for authentication
    """
    # Get SMTP configuration from environment variables with defaults
    smtp_server = os.getenv('SMTP_SERVER', 'mail.infomaniak.com')
    smtp_port = int(os.getenv('SMTP_PORT', '465'))
    smtp_user = os.getenv('SMTP_USER', 'no-reply@samtrevano.ch')
    smtp_password = os.getenv('SMTP_PASSWORD')  # No default for security reasons

    if not smtp_password:
        logger.error("SMTP_PASSWORD environment variable not set")
        return False

    msg = MIMEMultipart('alternative')
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg["Subject"] = subject
    
    # Always provide a plain text version
    plain_text = body
    if is_html:
        # Strip HTML for plain text alternative
        import re
        plain_text = re.sub('<.*?>', '', body)
        plain_text = plain_text.replace('&nbsp;', ' ')
    
    msg.attach(MIMEText(plain_text, 'plain'))
    
    if is_html:
        msg.attach(MIMEText(body, 'html'))

    logger.info(f"Attempting to send email to {to_email}")
    logger.info(f"Using SMTP server: {smtp_server}:{smtp_port}")
    logger.info(f"Using SMTP user: {smtp_user}")

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            logger.info("Connected to SMTP server")
            server.login(smtp_user, smtp_password)
            logger.info("Logged in successfully")
            server.send_message(msg)
            logger.info("Email sent successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        logger.error(f"SMTP Configuration - Server: {smtp_server}, Port: {smtp_port}, User: {smtp_user}")
        return False

def send_account_approval_email(user_email: str, user_name: str) -> bool:
    """
    Send account approval notification email with HTML formatting
    """
    subject = "Account Approvato - Promtec"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #3f51b5; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ padding: 20px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 5px 5px; }}
            .greeting {{ font-size: 16px; font-weight: bold; margin-bottom: 20px; }}
            .message {{ margin-bottom: 25px; }}
            .signature {{ margin-top: 30px; font-style: italic; }}
            .button {{ display: inline-block; background-color: #3f51b5; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>Promtec - Portale Iscrizioni</h2>
        </div>
        <div class="content">
            <p class="greeting">Gentile {user_name},</p>
            <p class="message">Siamo lieti di informarla che il Suo account Promtec è stato approvato.</p>
            <p>Ora può accedere alla piattaforma utilizzando le Sue credenziali.</p>
            
            <p class="signature">Cordiali saluti,<br>SAM Trevano</p>
            {get_contact_info_html()}
        </div>
    </body>
    </html>
    """
    
    return send_email(
        to_email=user_email,
        subject=subject,
        body=html_body,
        is_html=True
    )

def send_slot_confirmation_email(student_email: str, user_full_name: str, slot_info: Dict[str, Any]) -> bool:
    """
    Send a confirmation email to a student when a slot is confirmed.
    
    Args:
        student_email: Email address of the student
        student_name: Full name of the student
        slot_info: Dictionary containing details about the slot (date, time, department, etc.)
        
    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    logger.info(f"Sending slot confirmation email to {student_email}")
    
    # Format the date nicely
    slot_date = slot_info.get('date')
    if isinstance(slot_date, datetime):
        formatted_date = slot_date.strftime('%d/%m/%Y')
    else:
        # Try to parse the date string if it's not already a datetime object
        try:
            formatted_date = datetime.strptime(str(slot_date), '%Y-%m-%d').strftime('%d/%m/%Y')
        except ValueError:
            # If parsing fails, use the string as is
            formatted_date = str(slot_date)
    
    # Format the student list if available
    students = slot_info.get('students', [])
    student_list_html = ""
    if students:
        student_list_html = "<ul style='list-style-type: disc; padding-left: 20px;'>\n"
        for student in students:
            student_name = student.get('name', '')
            student_class = student.get('class', '')
            if student_name:
                student_list_html += f"<li>{student_name} ({student_class})</li>\n"
        student_list_html += "</ul>"
        
    subject = f"Conferma iscrizione Promtec - {slot_info.get('department', '')} - {formatted_date}"
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #3f51b5; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ padding: 20px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 5px 5px; }}
            .greeting {{ font-size: 16px; font-weight: bold; margin-bottom: 20px; }}
            .message {{ margin-bottom: 25px; }}
            .signature {{ margin-top: 30px; font-style: italic; }}
            ul {{ margin-top: 15px; margin-bottom: 20px; }}
            li {{ margin-bottom: 5px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>Conferma Iscrizione Promtec</h2>
        </div>
        <div class="content">
            <p class="greeting">Gentile {user_full_name},</p>
            <p>Le iscrizioni per lo slot del {formatted_date} ({slot_info.get('time_period', '')}) nel dipartimento {slot_info.get('department', '')} sono state confermate.</p>
            
            {"<p>Ecco la lista degli studenti della sua scuola che sono stati iscritti:</p>" if students else ""}
            {student_list_html}
            
            <p class="signature">Cordiali saluti,<br>SAM Trevano</p>
            
            {get_contact_info_html()}
        </div>
    </body>
    </html>
    """
    
    return send_email(
        to_email=student_email,
        subject=subject,
        body=html_body,
        is_html=True
    )

def send_password_reset_email(user_email: str, user_name: str, reset_link: str) -> bool:
    """
    Send password reset email with a link to reset password
    """
    subject = "Ripristino Password - Promtec"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #3f51b5; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ padding: 20px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 5px 5px; }}
            .greeting {{ font-size: 16px; font-weight: bold; margin-bottom: 20px; }}
            .message {{ margin-bottom: 25px; }}
            .button {{ display: inline-block; background-color: #3f51b5; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; margin: 20px 0; }}
            .warning {{ color: #e53935; font-size: 14px; margin-top: 20px; }}
            .signature {{ margin-top: 30px; font-style: italic; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>Promtec - Ripristino Password</h2>
        </div>
        <div class="content">
            <p class="greeting">Gentile {user_name},</p>
            <p class="message">Abbiamo ricevuto una richiesta di ripristino della password per il tuo account Promtec.</p>
            <p>Per completare il processo di ripristino, clicca sul pulsante qui sotto:</p>
            
            <div style="text-align: center;">
                <a href="{reset_link}" class="button">Ripristina Password</a>
            </div>
            
            <p class="warning">Questo link scadrà tra 24 ore. Se non hai richiesto il ripristino della password, puoi ignorare questa email.</p>
            
            <p class="signature">Cordiali saluti,<br>SAM Trevano</p>
            {get_contact_info_html()}
        </div>
    </body>
    </html>
    """
    
    return send_email(
        to_email=user_email,
        subject=subject,
        body=html_body,
        is_html=True
    )

def send_enrollment_summary_email(user_email: str, user_name: str, enrollments: list) -> bool:
    """
    Send a summary email with the list of students enrolled by a user in the last 30 minutes
    
    Args:
        user_email: The email address of the user
        enrollments: A list of enrollment objects containing student and slot information
        
    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    logger.info(f"Preparing enrollment summary email for {user_email}")
    
    # Format the student list as HTML table rows
    student_rows = ""
    for e in enrollments:
        student_rows += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{e.student.first_name} {e.student.last_name}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{e.student.school_class}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{e.slot.department.value}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{e.slot.date.strftime('%d/%m/%Y') if isinstance(e.slot.date, datetime) else datetime.strptime(str(e.slot.date), '%Y-%m-%d').strftime('%d/%m/%Y') if isinstance(e.slot.date, str) else str(e.slot.date)}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{e.slot.time_period.value}</td>
        </tr>
        """

    subject = "Riepilogo iscrizioni Promtec"
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #3f51b5; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ padding: 20px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 5px 5px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th {{ background-color: #f2f2f2; text-align: left; padding: 12px 8px; border-bottom: 2px solid #ddd; }}
            td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
            .greeting {{ font-size: 16px; margin-bottom: 20px; }}
            .note {{ margin-top: 15px; font-style: italic; color: #666; }}
            .signature {{ margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>Riepilogo Iscrizioni Promtec</h2>
        </div>
        <div class="content">
            <p class="greeting">Gentile {user_name},</p>
            <p>Ecco il riepilogo degli studenti che ha iscritto negli ultimi 30 minuti:</p>
            
            <table>
                <thead>
                    <tr>
                        <th>Nome e Cognome</th>
                        <th>Classe</th>
                        <th>Dipartimento</th>
                        <th>Data</th>
                        <th>Orario</th>
                    </tr>
                </thead>
                <tbody>
                    {student_rows}
                </tbody>
            </table>
            
            <p class="note">Questo è un messaggio automatico, si prega di non rispondere a questa email.</p>
            
            <p class="signature">Cordiali saluti,<br>SAM Trevano</p>
            
            {get_contact_info_html()}
        </div>
    </body>
    </html>
    """

    logger.info(f"Sending summary email to {user_email}")
    return send_email(
        to_email=user_email,
        subject=subject,
        body=html_body,
        is_html=True
    )
