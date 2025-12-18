
import os
import aiosmtplib
from email.message import EmailMessage
from typing import List, Optional

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.zoho.eu"
        self.smtp_port = 465  # SSL
        self.username = "info@rayo.consulting" # Placeholder, will be overriden by env if needed but user didn't provide one.
        # Ideally we read from env
        self.sender_email = os.getenv("ZOHO_USER", "info@rayo.consulting") 
        self.password = os.getenv("ZOHO_PW")

    async def send_email_with_attachments(
        self,
        to_email: str,
        subject: str,
        body: str,
        attachment_paths: List[str]
    ) -> bool:
        """
        Send an email with PDF attachments via Zoho SMTP.
        """
        if not self.password:
            print("Error: ZOHO_PW not set. Cannot send email.")
            return False

        message = EmailMessage()
        message["From"] = self.sender_email
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)

        # Add attachments
        for path in attachment_paths:
            if os.path.exists(path):
                filename = os.path.basename(path)
                # Guess mime type or just application/pdf
                with open(path, "rb") as f:
                    file_data = f.read()
                    message.add_attachment(
                        file_data,
                        maintype="application",
                        subtype="pdf",
                        filename=filename
                    )
            else:
                print(f"Warning: Attachment not found: {path}")

        try:
            print(f"Connecting to {self.smtp_server}...")
            await aiosmtplib.send(
                message,
                hostname=self.smtp_server,
                port=self.smtp_port,
                username=self.sender_email,
                password=self.password,
                use_tls=True
            )
            print(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

email_service = EmailService()
