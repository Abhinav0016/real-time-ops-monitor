import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

def test_sendgrid():
    api_key = os.getenv('SENDGRID_API_KEY')
    sender_email = os.getenv('SENDER_EMAIL', 'alerts@telecom-ops.ai')
    if not api_key:
        print("Error: SENDGRID_API_KEY not found in .env")
        return

    print(f"Using API Key: {api_key[:10]}...")
    print(f"Using Sender Email: {sender_email}")
    
    # Try sending to the user's email from the subscriptions
    message = Mail(
        from_email=sender_email,
        to_emails='abhisabs123@gmail.com', # User's email from subscriptions
        subject='TEST ALERT',
        plain_text_content='This is a test to verify SendGrid configuration.'
    )

    
    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.body}")
        print(f"Response Headers: {response.headers}")
        if response.status_code in [200, 201, 202]:
            print("SUCCESS: SendGrid accepted the email.")
        else:
            print(f"WARNING: Unexpected status code {response.status_code}")
    except Exception as e:
        print("\n--- SENDGRID ERROR ---")
        print(str(e))
        print("----------------------")
        if "The from address does not match a verified Sender Identity" in str(e):
            print("\nSUGGESTION: You need to verify 'alerts@telecom-ops.ai' in SendGrid or use a verified sender email.")

if __name__ == "__main__":
    test_sendgrid()
