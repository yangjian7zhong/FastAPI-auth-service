import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import asyncio
from app.core.config import settings

async def send_activation_email(email: str, username: str, token: str):
    activation_link = f"http://localhost:8000/api/v1/activate?token={token}"
    print(f'\n激活链接(请激活到浏览器打开):{activation_link}\n')
    print(f'收件人:{email},用户名:{username}')



def _send_sync(email: str, msg: MIMEMultipart):
    try:
        with smtplib.SMTP_SSL(settings.MAIL_HOST, settings.MAIL_PORT) as server:
            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            server.sendmail(settings.MAIL_FROM, [email], msg.as_string())
        print(f"✅ 邮件发送成功 -> {email}")
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")