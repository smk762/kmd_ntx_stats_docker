#!/usr/bin/python3
import os

def update_dotenv():
    with open(".env", "r") as f:
        data = {}
        for line in f.readlines():
            item = line.split("=")
            k = item[0].strip()
            if len(item) == 1:
                continue
            if len(item) > 2:
                v = ''.join(item[1:]).strip()
            else:
                v = item[1].strip()
            data.update({k: v})

    for i in ["MM2_USERPASS", "userpass", "SECRET_KEY", "DJANGO_ALLOWED_HOSTS",
        "NAME", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_HOST", "POSTGRES_PORT",
        "SKIP_PAST_SEASONS", "SKIP_UNTIL_YESTERDAY", "OTHER_SERVER", "THIS_SERVER",
        "API_PAGE_BREAK", "TELEGRAM_TOKEN", "TELEGRAM_CHAT_ID", "ext_hostname",
        "ext_username", "ext_password", "ext_db", "DB_PATH", "GH_USER", "GH_TOKEN",
        "USER_ID", "GROUP_ID"]:
        with open(".env", "a+") as f:
            if i not in data:
                if i == "USER_ID":
                    q = os.geteuid()
                elif i == "GROUP_ID":
                    q = os.getegid()
                else:
                    q = input(f"Enter {i}: ")

                f.write(f"{i}={q}\n")

if __name__ == "__main__":
    update_dotenv()
