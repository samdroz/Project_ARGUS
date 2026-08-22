import ipaddress
import socket
import urllib.parse
from typing import Tuple


BLOCKED_HOSTNAMES = {
    "localhost", "127.0.0.1", "0.0.0.0", "::1", "metadata.google.internal",
    "instance-data", "metadata"
}


def is_safe_url(url_str: str) -> Tuple[bool, str]:
    """
    Strict SSRF validation.
    Verifies URL scheme, validates hostname, and checks resolved IP against private / internal subnets.
    """
    try:
        parsed = urllib.parse.urlparse(str(url_str).strip())
    except Exception as e:
        return False, f"Malformed URL: {e}"

    if parsed.scheme.lower() not in ("http", "https"):
        return False, f"Unsupported scheme '{parsed.scheme}'. Only http:// and https:// are permitted."

    hostname = parsed.hostname
    if not hostname:
        return False, "Missing hostname in URL."

    if hostname.lower() in BLOCKED_HOSTNAMES:
        return False, f"Access to internal or loopback host '{hostname}' is forbidden."

    # Prevent direct IP attempts in hostname (e.g. http://127.0.0.1/ or http://169.254.169.254/)
    try:
        ip_obj = ipaddress.ip_address(hostname)
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast or ip_obj.is_reserved:
            return False, f"Access to private/internal IP '{hostname}' is forbidden."
    except ValueError:
        pass  # Hostname is a domain name, proceed to DNS resolution check

    # Resolve hostname to verify against DNS rebinding / private IP ranges
    try:
        addr_info = socket.getaddrinfo(hostname, None)
        for entry in addr_info:
            ip_str = entry[4][0]
            ip_obj = ipaddress.ip_address(ip_str)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast or ip_obj.is_reserved:
                return False, f"URL resolves to protected/private IP space ({ip_str}). Access denied."
    except socket.gaierror as e:
        return False, f"DNS resolution failed for hostname '{hostname}': {e}"
    except Exception as e:
        return False, f"Validation error for '{hostname}': {e}"

    return True, "URL is safe."
