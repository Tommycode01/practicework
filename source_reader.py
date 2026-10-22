import ipaddress
import socket
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

def fetch_source_text(url):
    """Fetch readable text from a public webpage safely."""

    # Only allow valid HTTP or HTTPS URLs.
    try:
        parsed = urlparse(url.strip())

        if parsed.scheme not in ("http", "https"):
            return None, "Please enter an HTTP or HTTPS URL."

        if not parsed.hostname:
            return None, "The URL is missing a hostname."

        if parsed.username or parsed.password:
            return None, "URLs containing login credentials are not allowed."

        hostname = parsed.hostname.lower()

        # Reject local hostnames.
        if hostname == "localhost" or hostname.endswith(".localhost"):
            return None, "Local addresses are not allowed."

        # Resolve the hostname and reject private or reserved IPs.
        try:
            addresses = socket.getaddrinfo(
                hostname,
                parsed.port or (443 if parsed.scheme == "https" else 80),
                type=socket.SOCK_STREAM,
            )
        except (socket.gaierror, OSError, ValueError):
            return None, "The website address could not be resolved."

        for address in addresses:
            ip = ipaddress.ip_address(address[4][0])

            if not ip.is_global:
                return None, "Private or non-public addresses are not allowed."

    except (ValueError, TypeError):
        return None, "Please enter a valid URL."

    headers = {
        "User-Agent": "ContextCheck/1.0 (public webpage text retrieval)"
    }

    try:
        with requests.Session() as session:
            # Do not follow redirects automatically. A redirect could
            # point to a private address that was not checked above.
            response = session.get(
                url.strip(),
                headers=headers,
                timeout=(5, 10),
                allow_redirects=False,
                stream=True,
            )

            with response:
                if response.status_code in (301, 302, 303, 307, 308):
                    return None, (
                        "This page redirects elsewhere. Open the destination "
                        "in your browser and enter its final public URL."
                    )

                response.raise_for_status()

                content_type = response.headers.get(
                    "Content-Type", ""
                ).lower()

                if "text/html" not in content_type and "text/plain" not in content_type:
                    return None, (
                        "This URL did not return an HTML or plain-text page."
                    )

                # Limit downloaded content to 1 MB.
                content_length = response.headers.get("Content-Length")
                if content_length:
                    try:
                        if int(content_length) > 1_000_000:
                            return None, "The webpage is too large to examine."
                    except ValueError:
                        pass

                chunks = []
                total_bytes = 0
                max_bytes = 1_000_000

                for chunk in response.iter_content(chunk_size=8192):
                    total_bytes += len(chunk)

                    if total_bytes > max_bytes:
                        return None, "The webpage exceeds the 1 MB size limit."

                    chunks.append(chunk)

                raw_content = b"".join(chunks)
                encoding = response.encoding or "utf-8"
                html = raw_content.decode(encoding, errors="replace")

    except requests.RequestException:
        return None, (
            "ContextCheck couldn't retrieve this page. It may be unavailable "
            "or may block automated requests."
        )

    if "text/plain" in content_type:
        text = html.strip()
    else:
        soup = BeautifulSoup(html, "html.parser")

        for element in soup([
            "script", "style", "nav", "footer", "header", "noscript"
        ]):
            element.decompose()

        text = soup.get_text(separator=" ", strip=True)

    if not text:
        return None, "No readable text was found on this page."

    # Keep the extracted text manageable for analysis.
    return text[:15000], None

