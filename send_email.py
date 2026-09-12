# -*- coding: utf-8 -*-
"""
邮件发送脚本
用法：python send_email.py <status> <build_url> <build_number> <report_path>
"""

import os
import sys
import io
import smtplib
import argparse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.header import Header
from datetime import datetime

# ============ 解决 Windows 控制台中文乱码 ============
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ============ SMTP 配置（QQ 邮箱） ============
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465
SMTP_USER = "3084714386@qq.com"
SMTP_PASSWORD = "anyamkciofdsdedd"
MAIL_TO = "3084714386@qq.com"


def log_info(msg):
    print(f"[INFO] {msg}")


def log_error(msg):
    print(f"[ERROR] {msg}")


def send_email(status, build_url, build_number, report_path):
    """发送测试报告邮件"""

    log_info(f"参数解析: status={status}, url={build_url}, number={build_number}, report={report_path}")

    if not os.path.exists(report_path):
        log_error(f"报告文件不存在：{report_path}")
        return False

    log_info(f"已添加附件：{report_path}")

    subject = f"天气接口自动化测试报告 - 构建 #{build_number}"

    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <p>您好，</p>
        <p>这是 Jenkins 自动发送的测试报告，构建信息如下：</p>
        <table style="border-collapse: collapse;">
            <tr>
                <td style="padding: 6px; border: 1px solid #ddd;">构建编号</td>
                <td style="padding: 6px; border: 1px solid #ddd;">#{build_number}</td>
            </tr>
            <tr>
                <td style="padding: 6px; border: 1px solid #ddd;">构建状态</td>
                <td style="padding: 6px; border: 1px solid #ddd;">{status}</td>
            </tr>
            <tr>
                <td style="padding: 6px; border: 1px solid #ddd;">构建时间</td>
                <td style="padding: 6px; border: 1px solid #ddd;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
            </tr>
            <tr>
                <td style="padding: 6px; border: 1px solid #ddd;">构建链接</td>
                <td style="padding: 6px; border: 1px solid #ddd;">
                    <a href="{build_url}">{build_url}</a>
                </td>
            </tr>
        </table>
        <p>详细测试报告请查看附件 report.html。</p>
        <p>此邮件由系统自动发送，请勿回复。</p>
    </body>
    </html>
    """

    # ===== 构建邮件（From 用纯邮箱地址，避免 QQ 邮箱报错） =====
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = MAIL_TO
    msg["Subject"] = Header(subject, "utf-8")
    msg.attach(MIMEText(body, "html", "utf-8"))

    # ===== 添加附件 =====
    try:
        with open(report_path, "rb") as f:
            attachment = MIMEApplication(f.read(), _subtype="html")
            attachment.add_header(
                "Content-Disposition",
                "attachment",
                filename=("utf-8", "", os.path.basename(report_path))
            )
            msg.attach(attachment)
    except Exception as e:
        log_error(f"读取附件失败：{e}")
        return False

    # ===== 发送邮件 =====
    log_info(f"正在发送邮件到 {MAIL_TO}...")
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, [MAIL_TO], msg.as_string())
        log_info("邮件发送成功！")
        return True
    except smtplib.SMTPAuthenticationError as e:
        log_error(f"SMTP 认证失败（请检查授权码）：{e}")
        return False
    except smtplib.SMTPException as e:
        log_error(f"SMTP 异常：{e}")
        return False
    except Exception as e:
        log_error(f"邮件发送失败：{e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="发送测试报告邮件")
    parser.add_argument("status", help="构建状态：SUCCESS / FAILURE / UNSTABLE")
    parser.add_argument("build_url", help="构建 URL")
    parser.add_argument("build_number", help="构建编号")
    parser.add_argument("report_path", help="HTML 报告路径")

    args = parser.parse_args()

    success = send_email(
        args.status,
        args.build_url,
        args.build_number,
        args.report_path
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
