import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import sys
from datetime import datetime

# ==================== 配置 ====================
SMTP_SERVER = "smtp.163.com"
SMTP_PORT = 465
SENDER_EMAIL = "13632044480@163.com"
SENDER_PASSWORD = "ADezFuMt7MhaUxa9"
RECEIVER_EMAIL = "3084714386@qq.com"


def send_email(build_status, build_url, build_number, report_path=None):
    subject = f"构建结果: {build_status} - weather-auto-test - #{build_number}"
    
    body = f"""
    <html>
    <body>
    <h2>Jenkins 构建报告</h2>
    <p><b>项目名称：</b>weather-auto-test</p>
    <p><b>构建编号：</b>#{build_number}</p>
    <p><b>构建状态：</b> <span style="color:{'green' if build_status == 'SUCCESS' else 'red'};font-weight:bold;">{build_status}</span></p>
    <p><b>执行时间：</b>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p><b>查看详情：</b><a href="{build_url}">{build_url}</a></p>
    <hr>
    <p style="color:gray;font-size:12px;">Jenkins 自动发送，请勿回复</p>
    </body>
    </html>
    """
    
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html", "utf-8"))
    
    if report_path and os.path.exists(report_path):
        with open(report_path, "rb") as f:
            attachment = MIMEBase("application", "octet-stream")
            attachment.set_payload(f.read())
            encoders.encode_base64(attachment)
            attachment.add_header(
                "Content-Disposition",
                f"attachment; filename={os.path.basename(report_path)}"
            )
            msg.attach(attachment)
            print("[INFO] 已添加附件: " + report_path)
    
    try:
        print("[INFO] 正在发送邮件到 " + RECEIVER_EMAIL + "...")
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("[SUCCESS] 邮件发送成功！")
        return True
    except Exception as e:
        print("[ERROR] 邮件发送失败: " + str(e))
        return False


if __name__ == "__main__":
    build_status = sys.argv[1] if len(sys.argv) > 1 else "SUCCESS"
    build_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8080"
    build_number = sys.argv[3] if len(sys.argv) > 3 else "0"
    report_path = sys.argv[4] if len(sys.argv) > 4 else None
    send_email(build_status, build_url, build_number, report_path)
