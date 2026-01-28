import unittest
import socket
from urllib.parse import urlparse
import ipaddress

def is_safe_url(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return False, "Invalid URL scheme. Only HTTP and HTTPS are allowed."
        
        hostname = parsed.hostname
        if not hostname:
            return False, "Invalid URL: No hostname found."
            
        try:
            ip = socket.gethostbyname(hostname)
        except socket.gaierror:
             return False, "Could not resolve hostname."

        ip_addr = ipaddress.ip_address(ip)
        
        if ip_addr.is_private or ip_addr.is_loopback:
            return False, "Access to local or private network resources is restricted."
            
        return True, ""
    except Exception as e:
        return False, f"URL Validation Error: {str(e)}"

class TestSecurity(unittest.TestCase):
    def test_safe_url(self):
        valid, msg = is_safe_url("https://www.google.com")
        self.assertTrue(valid, f"Google should be valid: {msg}")
        
    def test_unsafe_schemes(self):
        valid, msg = is_safe_url("ftp://example.com")
        self.assertFalse(valid, "FTP should be invalid")

        valid, msg = is_safe_url("file:///etc/passwd")
        self.assertFalse(valid, "File scheme should be invalid")

    def test_local_addresses(self):
        valid, msg = is_safe_url("http://localhost:8080")
        self.assertFalse(valid, "Localhost should be blocked")
        
        valid, msg = is_safe_url("http://127.0.0.1")
        self.assertFalse(valid, "Loopback IP should be blocked")
        
    def test_private_networks(self):
        valid, msg = is_safe_url("http://192.168.1.1")
        self.assertFalse(valid, "192.168.x.x should be blocked")
        
    def test_invalid_urls(self):
        valid, msg = is_safe_url("not_a_url")
        self.assertFalse(valid)

if __name__ == '__main__':
    unittest.main()
