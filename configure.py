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

    required_keys = [
        "MM2_IP", "MM2_PORT", "MM2_USERPASS", "SECRET_KEY", "DJANGO_ALLOWED_HOSTS",
        "NAME", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_HOST", "POSTGRES_PORT",
        "SKIP_PAST_SEASONS", "SKIP_UNTIL_YESTERDAY", "OTHER_SERVER", "THIS_SERVER",
        "API_PAGE_BREAK", "TELEGRAM_TOKEN", "TELEGRAM_CHAT_ID", "ext_hostname",
        "ext_username", "ext_password", "ext_db", "DB_PATH", "GH_USER", "GH_TOKEN",
        "KMD_RPC_IP", "KMD_RPC_PORT", "KMD_RPC_USERNAME", "KMD_RPC_PASSWORD",
        "USER_ID", "GROUP_ID"
    ]

    extra_keys = sorted(set(data.keys()) - set(required_keys))
    if extra_keys:
        print("\nNOTE: The following .env keys are not expected/used by this app:")
        for k in extra_keys:
            print(f"  - {k}")
        print("Consider cleaning them up if they are leftovers or typos.\n")

    # Prefill KMD RPC from local komodo.conf (host path, not inside containers)
    kmd_conf_path = os.path.expanduser("~/.komodo/komodo.conf")
    kmd_defaults = {}
    if os.path.exists(kmd_conf_path):
        try:
            rpcuser = rpcpassword = rpcport = rpcbind = None
            with open(kmd_conf_path, "r", encoding="utf-8") as f:
                for line in f:
                    l = line.strip()
                    if not l or l.startswith("#"):
                        continue
                    if l.startswith("rpcuser="):
                        rpcuser = l.replace("rpcuser=", "", 1)
                    elif l.startswith("rpcpassword="):
                        rpcpassword = l.replace("rpcpassword=", "", 1)
                    elif l.startswith("rpcport="):
                        rpcport = l.replace("rpcport=", "", 1)
                    elif l.startswith("rpcbind="):
                        rpcbind = l.replace("rpcbind=", "", 1)
            # defaults
            rpc_ip = rpcbind or "127.0.0.1"
            if rpc_ip == "0.0.0.0":
                rpc_ip = "127.0.0.1"
            rpc_port = rpcport or "7771"
            if rpcuser and rpcpassword:
                kmd_defaults["KMD_RPC_USERNAME"] = rpcuser
                kmd_defaults["KMD_RPC_PASSWORD"] = rpcpassword
            kmd_defaults["KMD_RPC_IP"] = rpc_ip
            kmd_defaults["KMD_RPC_PORT"] = rpc_port
            print(f"INFO: Found {kmd_conf_path}. Prefilled KMD_RPC_IP/KMD_RPC_PORT (defaults 127.0.0.1:7771) and credentials if present.")
        except Exception as e:
            print(f"WARNING: Found {kmd_conf_path} but could not read it ({e}). Ensure KMD_RPC_IP/KMD_RPC_PORT/KMD_RPC_USERNAME/KMD_RPC_PASSWORD are set in .env.")
    else:
        missing_kmd = any((k not in data or data.get(k, "") == "") for k in ["KMD_RPC_IP", "KMD_RPC_PORT", "KMD_RPC_USERNAME", "KMD_RPC_PASSWORD"])
        if missing_kmd:
            print(f"WARNING: {kmd_conf_path} not found and KMD_RPC_* not set in .env. Add them for KMD RPC connectivity.")

    # Hint for local MM2 config (host path, not inside containers)
    mm2_conf_path = os.path.expanduser("~/.kdf/MM2.json")
    mm2_defaults = {}
    if os.path.exists(mm2_conf_path):
        try:
            import json
            with open(mm2_conf_path, "r", encoding="utf-8") as f:
                mm2_cfg = json.load(f)
            mm2_ip = mm2_cfg.get("rpc_ip") or mm2_cfg.get("rpchost") or mm2_cfg.get("rpcip") or "127.0.0.1"
            mm2_port = mm2_cfg.get("rpc_port") or mm2_cfg.get("rpcport") or "7783"
            mm2_userpass = mm2_cfg.get("rpc_password") or mm2_cfg.get("userpass") or mm2_cfg.get("rpc_userpass")
            mm2_defaults["MM2_IP"] = str(mm2_ip)
            mm2_defaults["MM2_PORT"] = str(mm2_port)
            if mm2_userpass:
                mm2_defaults["MM2_USERPASS"] = str(mm2_userpass)
            if mm2_defaults:
                print(f"INFO: Found {mm2_conf_path}. Prefilled MM2_IP/MM2_PORT/MM2_USERPASS from it (fallbacks: 127.0.0.1:7783).")
        except Exception as e:
            print(f"WARNING: Found {mm2_conf_path} but could not read it ({e}). Ensure MM2_IP/MM2_PORT/MM2_USERPASS are set in .env.")
    else:
        missing_mm2 = any((k not in data or data.get(k, "") == "") for k in ["MM2_IP", "MM2_PORT", "MM2_USERPASS"])
        if missing_mm2:
            print(f"WARNING: {mm2_conf_path} not found and MM2_IP/MM2_PORT/MM2_USERPASS not set in .env. Add them for MM2/atomicdex connectivity.")

    # Apply mm2 defaults into data so we don't prompt again
    for k, v in mm2_defaults.items():
        if k not in data or data[k] == "":
            data[k] = v

    # Apply KMD defaults into data so we don't prompt again
    for k, v in kmd_defaults.items():
        if k not in data or data[k] == "":
            data[k] = v

    # Normalize KMD RPC defaults (host process)
    if data.get("KMD_RPC_IP", "") in ["", "0.0.0.0"]:
        data["KMD_RPC_IP"] = "127.0.0.1"
    if data.get("KMD_RPC_PORT", "") == "":
        data["KMD_RPC_PORT"] = "7771"

    for i in required_keys:
        with open(".env", "a+") as f:
            if i not in data or data[i] == "":
                if i == "USER_ID":
                    q = os.geteuid()
                elif i == "GROUP_ID":
                    q = os.getegid()
                else:
                    q = input(f"Enter {i}: ")

                f.write(f"{i}={q}\n")

if __name__ == "__main__":
    update_dotenv()
