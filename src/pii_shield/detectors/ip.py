"""IP address detector."""

import ipaddress
import re

from pii_shield.core import PIIMatch, PIIType
from pii_shield.detectors.base import Detector


class IPAddressDetector(Detector):
    """Detect IP addresses in text.

    Supports:
    - IPv4: 192.168.1.1
    - IPv6: 2001:0db8:85a3:0000:0000:8a2e:0370:7334
    """

    # IPv4 pattern
    IPV4_PATTERN = re.compile(
        r"\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b"
    )

    # IPv6 pattern (simplified - covers most formats)
    IPV6_PATTERN = re.compile(
        r"\b((?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|"  # Full
        r"(?:[0-9a-fA-F]{1,4}:){1,7}:|"  # With trailing ::
        r"(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|"  # ::x
        r"(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|"
        r"(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|"
        r"(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|"
        r"(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|"
        r"[0-9a-fA-F]{1,4}:(?::[0-9a-fA-F]{1,4}){1,6}|"
        r":(?::[0-9a-fA-F]{1,4}){1,7}|"  # ::x...
        r"::)\b",  # Just ::
        re.IGNORECASE,
    )

    def detect(self, text: str) -> list[PIIMatch]:
        """Find all IP addresses in text."""
        matches = []

        # Find IPv4 addresses
        for match in self.IPV4_PATTERN.finditer(text):
            ip_text = match.group(1)
            if self._is_valid_ipv4(ip_text):
                matches.append(
                    PIIMatch(
                        type=PIIType.IP_ADDRESS,
                        text=ip_text,
                        start=match.start(1),
                        end=match.end(1),
                        confidence=1.0,
                        detector="ip_address",
                    )
                )

        # Find IPv6 addresses
        for match in self.IPV6_PATTERN.finditer(text):
            ip_text = match.group(1)
            if self._is_valid_ipv6(ip_text):
                matches.append(
                    PIIMatch(
                        type=PIIType.IP_ADDRESS,
                        text=ip_text,
                        start=match.start(1),
                        end=match.end(1),
                        confidence=1.0,
                        detector="ip_address",
                    )
                )

        return matches

    def _is_valid_ipv4(self, ip: str) -> bool:
        """Validate IPv4 address using stdlib."""
        try:
            ipaddress.IPv4Address(ip)
            return True
        except ipaddress.AddressValueError:
            return False

    def _is_valid_ipv6(self, ip: str) -> bool:
        """Validate IPv6 address using stdlib."""
        try:
            ipaddress.IPv6Address(ip)
            return True
        except ipaddress.AddressValueError:
            return False
