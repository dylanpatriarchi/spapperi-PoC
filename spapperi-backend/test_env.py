
import asyncio
import os
import aiosmtplib
from email.message import EmailMessage

async def test_env():
    host = os.getenv("EMAIL_HOST", "smtp.zoho.eu")
    port = int(os.getenv("EMAIL_PORT", 465))
    user = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")
    sender = os.getenv("EMAIL_FROM", user)
    
    print(f"--- EMAIL CONFIGURATION TEST ---")
    print(f"HOST: {host}")
    print(f"PORT: {port}")
    print(f"USER: {user}")
    print(f"SENDER: {sender}")
    print(f"PASS: {'*' * 8 if password else 'MISSING'}")

    if not user or not password:
        print("!! FAILURE: EMAIL_USER or EMAIL_PASSWORD missing.")
        return

    print(f"Attempting connection to {host}...")
    try:
        smtp_client = aiosmtplib.SMTP(hostname=host, port=port, use_tls=True)
        await smtp_client.connect()
        print("Connected.")
        await smtp_client.login(user, password)
        print("Logged in successfully.")
        
        # Send check
        msg = EmailMessage()
        msg["From"] = sender
        msg["To"] = sender
        msg["Subject"] = "Spapperi Env Config Test"
        msg.set_content("If you receive this, the environment variables are correctly mapped.")
        
        await smtp_client.send_message(msg)
        print("Test email sent successfully.")
        await smtp_client.quit()
        print("--- TEST PASSED ---")
        
    except Exception as e:
        print(f"!! FAILURE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_env())
