#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STEAM 社群活動成果 Gmail 寄送模組
支援：
1. SMTP 直接寄送（附帶成果表與簽到表 PDF/DOCX）
2. 瀏覽器 Gmail Compose 一鍵開啟（預填收件人、主旨、內文）
"""

import os
import sys
import json
import smtplib
import urllib.parse
import subprocess
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == 'scripts' else SCRIPT_DIR

CONFIG_PATHS = [
    os.path.join(SCRIPT_DIR, 'gmail_config.json'),
    os.path.join(PROJECT_DIR, 'scripts', 'gmail_config.json'),
    os.path.expanduser('~/.gemini/config/skills/steam-community-docs/references/gmail_config.json'),
    os.path.expanduser('~/.gemini/config/gmail_config.json')
]

DEFAULT_RECIPIENT = "tc.steam114@gmail.com"

def get_gmail_config():
    # 1. Environment variables
    sender = os.environ.get('GMAIL_SENDER')
    app_pwd = os.environ.get('GMAIL_APP_PASSWORD')
    if sender and app_pwd:
        return {'sender': sender, 'app_password': app_pwd}
    
    # 2. Config files
    for path in CONFIG_PATHS:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                    if cfg.get('sender') and cfg.get('app_password'):
                        return cfg
            except:
                pass
    return None

def build_email_content(roc_year, month, day, activity_name=""):
    date_str = f"{roc_year}年{month}月{day}日"
    subject = f"【成果繳交】臺中市梧棲區中正國小「STEAM校內教師社群」{date_str}活動執行成果"
    body = (
        f"承辦人員您好：\n\n"
        f"檢附本校「STEAM校內教師社群」{date_str}活動執行成果相關資料，包含：\n\n"
        f"一、活動執行成果表\n"
        f"二、活動簽到表\n\n"
        f"敬請查收。\n\n"
        f"若資料尚有需補充或修正之處，亦請不吝告知，謝謝。\n\n"
        f"敬祝\n"
        f"順心\n\n"
        f"臺中市梧棲區中正國民小學 STEAM教師社群\n"
        f"召集人：謝敦元 老師 敬上"
    )
    return subject, body

def find_submission_attachments(target_dir):
    """
    Finds 成果表 and 簽到表 (prefers PDF, fallbacks to docx).
    Excludes 領據 (which is for school accounting).
    """
    attachments = []
    if not os.path.exists(target_dir):
        return attachments

    files = os.listdir(target_dir)
    
    # 1. 成果表
    pdf_cg = [os.path.join(target_dir, f) for f in files if '成果' in f and f.endswith('.pdf')]
    docx_cg = [os.path.join(target_dir, f) for f in files if '成果' in f and f.endswith('.docx')]
    if pdf_cg:
        attachments.append(pdf_cg[0])
    elif docx_cg:
        attachments.append(docx_cg[0])

    # 2. 簽到表
    pdf_qd = [os.path.join(target_dir, f) for f in files if '簽到' in f and f.endswith('.pdf')]
    docx_qd = [os.path.join(target_dir, f) for f in files if '簽到' in f and f.endswith('.docx')]
    if pdf_qd:
        attachments.append(pdf_qd[0])
    elif docx_qd:
        attachments.append(docx_qd[0])

    return attachments

def send_via_smtp(sender, app_password, recipient, subject, body, attachment_paths):
    """
    Sends email with attachments using Gmail SMTP (smtp.gmail.com:587)
    """
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    for filepath in attachment_paths:
        if os.path.exists(filepath):
            filename = os.path.basename(filepath)
            with open(filepath, 'rb') as f:
                part = MIMEApplication(f.read(), Name=filename)
            part['Content-Disposition'] = f'attachment; filename="{filename}"'
            msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, app_password.replace(' ', ''))
    server.sendmail(sender, [recipient], msg.as_string())
    server.quit()
    return True

def open_gmail_web(recipient, subject, body, open_dir=None):
    """
    Opens Gmail Compose web page in default browser with pre-filled To/Subject/Body.
    Also opens Finder to reveal attachments.
    """
    encoded_to = urllib.parse.quote(recipient)
    encoded_su = urllib.parse.quote(subject)
    encoded_body = urllib.parse.quote(body)
    
    url = f"https://mail.google.com/mail/?view=cm&fs=1&to={encoded_to}&su={encoded_su}&body={encoded_body}"
    subprocess.run(['open', url])
    
    if open_dir and os.path.exists(open_dir):
        subprocess.run(['open', open_dir])
    return True

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Gmail 成果繳交寄送工具")
    parser.add_argument('--dir', required=True, help="活動目錄 (如 ./0810 或 ./0926)")
    parser.add_argument('--date', help="活動日期 (如 115.08.10 或 0810)")
    parser.add_argument('--to', default=DEFAULT_RECIPIENT, help="收件者信箱")
    parser.add_argument('--open-web', action='store_true', help="直接開啟瀏覽器 Gmail 撰寫頁面")
    parser.add_argument('--sender', help="寄件者 Gmail")
    parser.add_argument('--password', help="Gmail 應用程式密碼")

    args = parser.parse_args()

    # Parse date from dir if not given
    dir_name = os.path.basename(os.path.abspath(args.dir))
    if not args.date and len(dir_name) == 4 and dir_name.isdigit():
        m = int(dir_name[:2])
        d = int(dir_name[2:])
        roc_y = 115
    elif args.date:
        parts = args.date.replace('/', '-').replace('.', '-').split('-')
        if len(parts) == 3:
            roc_y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
        elif len(parts) == 2:
            roc_y, m, d = 115, int(parts[0]), int(parts[1])
        else:
            roc_y, m, d = 115, int(args.date[:2]), int(args.date[2:])
    else:
        roc_y, m, d = 115, 8, 10

    subject, body = build_email_content(roc_y, m, d)
    attachments = find_submission_attachments(args.dir)

    print("\n================ 信件內容預覽 ================")
    print(f"收件者：{args.to}")
    print(f"主旨  ：{subject}")
    print(f"附件  ：{[os.path.basename(a) for a in attachments]}")
    print("---------------- 內文 ----------------")
    print(body)
    print("==============================================\n")

    cfg = get_gmail_config()
    sender = args.sender or (cfg.get('sender') if cfg else None)
    app_pwd = args.password or (cfg.get('app_password') if cfg else None)

    if args.open_web or not (sender and app_pwd):
        print("💡 正在為您開啟瀏覽器 Gmail 撰寫視窗與活動資料夾...")
        open_gmail_web(args.to, subject, body, args.dir)
        print("✅ 已開啟 Gmail 撰寫視窗與檔案資料夾，請將附件拖曳入視窗後發送！")
    else:
        print(f"📨 正在透過 SMTP 發送信件至 {args.to}...")
        try:
            send_via_smtp(sender, app_pwd, args.to, subject, body, attachments)
            print("🎉 信件發送成功！")
        except Exception as e:
            print(f"❌ SMTP 發送失敗 ({e})，切換為開啟瀏覽器 Gmail 視窗...")
            open_gmail_web(args.to, subject, body, args.dir)
