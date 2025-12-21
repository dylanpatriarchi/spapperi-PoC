
import os
import aiosmtplib
from email.message import EmailMessage
from typing import List, Optional

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("EMAIL_HOST")
        self.smtp_port = int(os.getenv("EMAIL_PORT", 465))
        self.username = os.getenv("EMAIL_USER")
        self.sender_email = os.getenv("EMAIL_FROM", self.username)
        self.password = os.getenv("EMAIL_PASSWORD")

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
        if not self.password or not self.username:
            print("Error: EMAIL_PASSWORD or EMAIL_USER not set.")
            return False

        message = EmailMessage()
        message["From"] = self.sender_email
        message["To"] = to_email
        message["Subject"] = subject
        
        # Set HTML content
        message.set_content(body, subtype="html")

        # Add Logo as CID inline image
        logo_path = "/app/source/logo_spapperi.svg"
        print(f"DEBUG EMAIL: Checking logo at {logo_path}, exists: {os.path.exists(logo_path)}")
        if os.path.exists(logo_path):
             with open(logo_path, "rb") as img:
                 logo_data = img.read()
                 print(f"DEBUG EMAIL: Logo data size: {len(logo_data)} bytes")
                 # Use add_related for inline images with CID
                 message.add_related(
                     logo_data,
                     maintype="image",
                     subtype="svg+xml",
                     filename="logo_spapperi.svg",
                     cid="logo"
                 )
                 print("DEBUG EMAIL: Logo attached successfully")

        # Add PDF attachments
        print(f"DEBUG EMAIL: Processing {len(attachment_paths)} attachments: {attachment_paths}")
        for i, path in enumerate(attachment_paths):
            print(f"DEBUG EMAIL: Attachment {i}: {path}, exists: {os.path.exists(path)}")
            if os.path.exists(path):
                filename = os.path.basename(path)
                with open(path, "rb") as f:
                    file_data = f.read()
                    print(f"DEBUG EMAIL: Attachment {i} ({filename}) size: {len(file_data)} bytes")
                    message.add_attachment(
                        file_data,
                        maintype="application",
                        subtype="pdf",
                        filename=filename
                    )
                    print(f"DEBUG EMAIL: Attachment {i} ({filename}) attached successfully")

        try:
            await aiosmtplib.send(
                message,
                hostname=self.smtp_server,
                port=self.smtp_port,
                username=self.username,
                password=self.password,
                use_tls=True if self.smtp_port == 465 else False,
                start_tls=True if self.smtp_port == 587 else False
            )
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

email_service = EmailService()
