# -*- coding: utf-8 -*-
import smtplib
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import sys
from datetime import datetime

# ==================== 配置（163邮箱 + SSL） ====================
SMTP_SERVER = "smtp.163.com"
SMTP_PORT = 465  # SSL
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
    
    # ===== 附件处理（单独 try，附件失败不影响邮件正文发送） =====
    if report_path and os.path.exists(report_path):
        try:
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
        except Exception as e:
            print("[WARN] 附件添加失败，仅发送正文: " + str(e))
    elif report_path:
        print("[WARN] 报告文件不存在，跳过附件: " + str(report_path))
    
    # ===== 发送邮件 =====
    try:
        print("[INFO] 正在发送邮件到 " + RECEIVER_EMAIL + "...")
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("[SUCCESS] 邮件发送成功！")
        return True
    except Exception as e:
        print("[ERROR] 邮件发送失败: " + str(e))
        traceback.print_exc()
        return False


def parse_args():
    """
    智能解析参数，兼容两种调用方式：

    方式 1（Jenkins 当前用法，3 个参数）：
        python send_email.py <build_url> <build_number> <report_path>
        → 状态默认 SUCCESS

    方式 2（4 个参数）：
        python send_email.py <build_status> <build_url> <build_number> <report_path>
    """
    args = sys.argv[1:]  # 去掉脚本名

    if len(args) >= 4:
        # 4 个及以上参数：status, url, number, report_path
        build_status = args[0]
        build_url = args[1]
        build_number = args[2]
        report_path = args[3]
    elif len(args) == 3:
        # 3 个参数：url, number, report_path
        build_status = "SUCCESS"
        build_url = args[0]
        build_number = args[1]
        report_path = args[2]
    elif len(args) == 2:
        # 2 个参数：url, number
        build_status = "SUCCESS"
        build_url = args[0]
        build_number = args[1]
        report_path = None
    elif len(args) == 1:
        # 1 个参数：url
        build_status = "SUCCESS"
        build_url = args[0]
        build_number = "0"
        report_path = None
    else:
        # 无参数，全默认
        build_status = "UNKNOWN"
        build_url = "http://localhost:8080"
        build_number = "0"
        report_path = None

    return build_status, build_url, build_number, report_path


def main():
    """
    主入口：
    - 智能解析命令行参数
    - 调用 send_email
    - 无论成功失败，退出码永远为 0，避免影响 Jenkins 构建结果
    """
    try:
        build_status, build_url, build_number, report_path = parse_args()

        print(f"[INFO] 参数解析: status={build_status}, url={build_url}, "
              f"number={build_number}, report={report_path}")

        send_email(build_status, build_url, build_number, report_path)

    except Exception as e:
        # 兜底：任何异常都不应让 Jenkins 构建失败
        print("[WARN] 邮件脚本执行异常（不影响构建）: " + str(e))
        traceback.print_exc()

    # 关键：始终返回 0，保证 Jenkins 构建状态不受邮件影响
    sys.exit(0)


if __name__ == "__main__":
    main()
