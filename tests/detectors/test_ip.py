"""Tests for IP address detector."""

from pii_shield.core import PIIType
from pii_shield.detectors.ip import IPAddressDetector


class TestIPAddressDetector:
    """Tests for IPAddressDetector."""

    # === IPv4 Tests ===

    def test_detects_ipv4(self):
        detector = IPAddressDetector()
        matches = detector.detect("Server: 192.168.1.1")
        assert len(matches) == 1
        assert matches[0].type == PIIType.IP_ADDRESS
        assert matches[0].text == "192.168.1.1"
        assert matches[0].confidence == 1.0

    def test_detects_localhost(self):
        detector = IPAddressDetector()
        matches = detector.detect("Localhost: 127.0.0.1")
        assert len(matches) == 1
        assert matches[0].text == "127.0.0.1"

    def test_detects_public_ip(self):
        detector = IPAddressDetector()
        matches = detector.detect("Public: 8.8.8.8")
        assert len(matches) == 1
        assert matches[0].text == "8.8.8.8"

    def test_detects_private_ip(self):
        detector = IPAddressDetector()
        matches = detector.detect("Private: 10.0.0.1")
        assert len(matches) == 1

    # === IPv6 Tests ===

    def test_detects_ipv6_full(self):
        detector = IPAddressDetector()
        matches = detector.detect("IPv6: 2001:0db8:85a3:0000:0000:8a2e:0370:7334")
        assert len(matches) == 1
        assert matches[0].text == "2001:0db8:85a3:0000:0000:8a2e:0370:7334"

    def test_detects_ipv6_compressed(self):
        detector = IPAddressDetector()
        matches = detector.detect("IPv6: 2001:db8::1")
        assert len(matches) == 1

    def test_detects_ipv6_loopback(self):
        detector = IPAddressDetector()
        # Full loopback address
        matches = detector.detect("Loopback: 0:0:0:0:0:0:0:1")
        assert len(matches) == 1
        assert matches[0].text == "0:0:0:0:0:0:0:1"

    # === Context Tests ===

    def test_ip_in_sentence(self):
        detector = IPAddressDetector()
        text = "Connect to 192.168.1.1 on port 80."
        matches = detector.detect(text)
        assert len(matches) == 1
        assert matches[0].start == 11
        assert matches[0].end == 22

    def test_multiple_ips(self):
        detector = IPAddressDetector()
        text = "From 192.168.1.1 to 10.0.0.1"
        matches = detector.detect(text)
        assert len(matches) == 2

    # === Invalid IP Tests ===

    def test_no_match_invalid_octet(self):
        detector = IPAddressDetector()
        # 999 is not valid (max 255)
        matches = detector.detect("Invalid: 999.168.1.1")
        assert len(matches) == 0

    def test_no_match_incomplete_ip(self):
        detector = IPAddressDetector()
        matches = detector.detect("Partial: 192.168.1")
        assert len(matches) == 0

    # === No Match Tests ===

    def test_no_match_plain_text(self):
        detector = IPAddressDetector()
        matches = detector.detect("Hello world, no IP here")
        assert len(matches) == 0

    def test_no_match_version_number(self):
        detector = IPAddressDetector()
        # Version numbers shouldn't match if invalid
        matches = detector.detect("Version 1.2.3")
        assert len(matches) == 0

    # === Metadata Tests ===

    def test_detector_name(self):
        detector = IPAddressDetector()
        matches = detector.detect("192.168.1.1")
        assert matches[0].detector == "ip_address"
