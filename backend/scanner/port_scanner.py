
import socket
from concurrent.futures import ThreadPoolExecutor

CONNECT_TIMEOUT = 0.8

# port -> (service name, severity if exposed, why it matters)
RISKY_PORTS = {
    21:    ("FTP",           "high",     "Unencrypted file transfer; credentials sent in plaintext."),
    22:    ("SSH",           "medium",   "Remote admin access; ensure key-based auth and rate limiting."),
    23:    ("Telnet",        "critical", "Unencrypted remote access; should never be internet-facing."),
    25:    ("SMTP",          "low",      "Expected on mail servers; confirm this host is actually meant to send mail."),
    3306:  ("MySQL",         "critical", "Database port exposed to the internet; should be firewalled to trusted IPs only."),
    5432:  ("PostgreSQL",    "critical", "Database port exposed to the internet; should be firewalled to trusted IPs only."),
    6379:  ("Redis",         "critical", "Redis has no authentication by default; an exposed instance can be fully compromised."),
    27017: ("MongoDB",       "critical", "Database port exposed to the internet; should be firewalled to trusted IPs only."),
    3389:  ("RDP",           "high",     "Remote desktop exposed to the internet is a common ransomware entry point."),
    9200:  ("Elasticsearch", "critical", "Often has no authentication by default; exposed instances leak indexed data."),
}


def _check_port(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=CONNECT_TIMEOUT):
            return True
    except Exception:
        return False


def scan_ports(host: str) -> dict:
    with ThreadPoolExecutor(max_workers=len(RISKY_PORTS)) as pool:
        results = list(pool.map(lambda p: (p, _check_port(host, p)), RISKY_PORTS))

    open_ports = []
    for port, is_open in results:
        if is_open:
            name, severity, reason = RISKY_PORTS[port]
            open_ports.append({"port": port, "service": name, "severity": severity, "reason": reason})

    return {
        "checked": len(RISKY_PORTS),
        "open_ports": open_ports,
        "all_closed": len(open_ports) == 0,
    }