"""Apply compatibility fixes required by the upstream Alexa SDK stack."""

from pathlib import Path
from sysconfig import get_paths


SITE_PACKAGES = Path(get_paths()["purelib"])


def patch_file(relative_path: str, old: str, new: str) -> None:
    """Replace an exact dependency code block when the installed version needs it."""
    path = SITE_PACKAGES / relative_path
    if not path.exists():
        print(f"Dependency patch skipped; {path} was not installed")
        return

    source = path.read_text(encoding="utf-8")
    if old not in source:
        print(f"Dependency patch not needed for {path}")
        return

    path.write_text(source.replace(old, new), encoding="utf-8")
    print(f"Patched {path}")


patch_file(
    "ask_sdk_webservice_support/verifier.py",
    """        now = datetime.utcnow()
        if not (x509_cert.not_valid_before <= now <=
                x509_cert.not_valid_after):
            raise VerificationException("Signing Certificate expired")""",
    """        from datetime import timezone
        now = datetime.now(timezone.utc)
        not_valid_before = (getattr(x509_cert, 'not_valid_before_utc', None)
                            or x509_cert.not_valid_before.replace(tzinfo=timezone.utc))
        not_valid_after = (getattr(x509_cert, 'not_valid_after_utc', None)
                           or x509_cert.not_valid_after.replace(tzinfo=timezone.utc))
        if not (not_valid_before <= now <= not_valid_after):
            raise VerificationException("Signing Certificate expired")""",
)

patch_file(
    "certvalidator/registry.py",
    """        for trust_root in trust_roots:
            hashable = trust_root.subject.hashable
            if hashable not in self._subject_map:
                self._subject_map[hashable] = []
            self._subject_map[hashable].append(trust_root)
            if trust_root.key_identifier:
                self._key_identifier_map[trust_root.key_identifier] = trust_root
            self._ca_lookup[trust_root.signature] = True""",
    """        for trust_root in trust_roots:
            try:
                hashable = trust_root.subject.hashable
            except Exception:
                # certvalidator 0.11.1 cannot hash some modern OS trust roots
                # when used with asn1crypto >= 1.5.1.
                continue
            if hashable not in self._subject_map:
                self._subject_map[hashable] = []
            self._subject_map[hashable].append(trust_root)
            if trust_root.key_identifier:
                self._key_identifier_map[trust_root.key_identifier] = trust_root
            self._ca_lookup[trust_root.signature] = True""",
)
