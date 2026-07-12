import ssl, socket
from datetime import datetime

def analyze_ssl(host: str) -> dict:
    result = {"https": False, "valid": False, "issuer": "Unknown",
              "expires": None, "days_to_expiry": None,
              "chain_complete": False, "tls": []}
    ctx = ssl.create_default_context()
    try:
        with socket.create_connection((host, 443), timeout=6) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                result["https"] = True
                cert = ssock.getpeercert()
                result["tls"] = [ssock.version()]
                # Issuer
                issuer = dict(x[0] for x in cert.get("issuer", []))
                result["issuer"] = issuer.get("organizationName",
                                              issuer.get("commonName", "Unknown"))
                # Expiry
                exp = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
                result["expires"] = exp.strftime("%Y-%m-%d")
                result["days_to_expiry"] = (exp - datetime.utcnow()).days
                result["valid"] = result["days_to_expiry"] > 0
                result["chain_complete"] = True
    except Exception as e:
        result["error"] = str(e)
    return result