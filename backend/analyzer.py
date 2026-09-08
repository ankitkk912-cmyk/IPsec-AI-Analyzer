import re

def _has(text, pattern):
    return re.search(pattern, text, re.I | re.M) is not None

def _first(text, patterns):
    for p in patterns:
        m = re.search(p, text, re.I | re.M)
        if m:
            return m.group(1)
    return None

def analyze_config(config):
    text = config.replace("\r\n", "\n").replace("\r", "\n")
    findings = []
    checks = []

    def check(name, status, severity, detail, recommendation=""):
        checks.append({
            "name": name,
            "status": status,
            "severity": severity,
            "detail": detail,
            "recommendation": recommendation
        })

    # IKE version
    ikev2 = _has(text, r"\bcrypto ikev2\b|\bikev2\b")
    ikev1 = _has(text, r"\bcrypto isakmp\b|\bikev1\b|\bisakmp policy\b")
    if ikev2:
        check("IKE version", "PASS", "low", "IKEv2 configuration detected.",
              "Prefer IKEv2 for modern deployments when supported.")
    elif ikev1:
        check("IKE version", "WARN", "medium", "IKEv1/ISAKMP configuration detected.",
              "Plan migration to IKEv2 where platform compatibility allows.")
    else:
        check("IKE version", "INFO", "low", "No explicit IKE version marker was detected.",
              "Verify the actual IKE negotiation version on the device.")

    # Encryption
    weak_crypto = []
    for alg in ["des", "3des", "aes 128", "aes 192", "aes 256", "chacha20"]:
        if _has(text, rf"\b{re.escape(alg)}\b"):
            if alg in {"des", "3des"}:
                weak_crypto.append(alg.upper())
    if weak_crypto:
        check("Encryption", "FAIL", "high",
              f"Weak/legacy encryption detected: {', '.join(weak_crypto)}.",
              "Use AES-256 or another organization-approved modern cipher suite.")
    elif _has(text, r"\baes\b"):
        check("Encryption", "PASS", "low", "AES encryption detected.",
              "Keep algorithms aligned with current organizational standards.")
    else:
        check("Encryption", "WARN", "medium", "No AES/modern encryption marker detected.",
              "Verify the encryption proposal and remove legacy ciphers.")

    # Integrity / hashing
    if _has(text, r"\bmd5\b"):
        check("Integrity", "FAIL", "high", "MD5 is present.",
              "Replace MD5 with a modern integrity algorithm supported by the platform.")
    elif _has(text, r"\bsha1\b"):
        check("Integrity", "WARN", "medium", "SHA-1 is present.",
              "Prefer SHA-256 or stronger where supported.")
    elif _has(text, r"\bsha[- ]?256\b|\bsha2\b|\bsha[- ]?384\b|\bsha[- ]?512\b"):
        check("Integrity", "PASS", "low", "A modern SHA-2 family algorithm is present.",
              "")
    else:
        check("Integrity", "INFO", "low", "No explicit integrity algorithm detected.",
              "Verify the IKE/IPsec integrity settings.")

    # DH group
    dh = _first(text, [
        r"\bgroup\s+(\d+)\b",
        r"\bdh-group\s+(\d+)\b"
    ])
    if dh in {"1", "2", "5"}:
        check("Diffie-Hellman", "FAIL", "high", f"Legacy DH group {dh} detected.",
              "Use a modern approved DH group such as 14+ or an organization-approved equivalent.")
    elif dh:
        check("Diffie-Hellman", "PASS", "low", f"DH group {dh} detected.", "")
    else:
        check("Diffie-Hellman", "INFO", "low", "DH group was not confidently detected.",
              "Verify the negotiated DH group.")

    # PFS
    if _has(text, r"\bpfs\b"):
        check("Perfect Forward Secrecy", "PASS", "low", "PFS appears to be configured.",
              "Keep PFS enabled according to your security policy.")
    else:
        check("Perfect Forward Secrecy", "WARN", "medium", "PFS was not detected in the IPsec transform/profile.",
              "Enable PFS where supported and appropriate for the deployment.")

    # Authentication
    if _has(text, r"\bpre-share\b|\bpre-shared\b|\bpsk\b"):
        check("Authentication", "INFO", "medium",
              "Pre-shared-key authentication marker detected.",
              "Use strong, unique secrets and prefer certificate-based authentication for larger deployments.")
    elif _has(text, r"\brsa-sig\b|\bcertificate\b"):
        check("Authentication", "PASS", "low",
              "Certificate/RSA-signature authentication marker detected.", "")
    else:
        check("Authentication", "INFO", "low",
              "Authentication method was not confidently detected.",
              "Verify the IKE authentication method.")

    # NAT-T
    if _has(text, r"\bnat[- ]?traversal\b|\bforce[- ]?natt\b|\bnatt\b"):
        check("NAT traversal", "PASS", "low", "NAT traversal marker detected.", "")
    else:
        check("NAT traversal", "INFO", "low",
              "NAT traversal was not explicitly detected.",
              "Verify NAT-T if peers can be behind NAT.")

    # Tunnel / crypto map evidence
    tunnel_count = len(re.findall(r"^\s*(?:interface\s+Tunnel|crypto\s+map|tunnel\s+source|tunnel\s+destination)", text, re.I | re.M))
    if tunnel_count:
        check("IPsec tunnel evidence", "PASS", f"low",
              f"{tunnel_count} tunnel-related configuration marker(s) detected.", "")
    else:
        check("IPsec tunnel evidence", "WARN", "medium",
              "No common tunnel/crypto-map markers were detected.",
              "Confirm that the supplied file is the relevant IPsec configuration.")

    # Broad peer / ACL checks
    if _has(text, r"\b0\.0\.0\.0\s+0\.0\.0\.0\b"):
        check("Traffic selector scope", "WARN", "medium",
              "A broad 0.0.0.0/0-style selector appears in the configuration.",
              "Confirm that broad selectors are intentional and restricted by policy.")

    # Simple security score
    weights = {"critical": 25, "high": 18, "medium": 10, "low": 2}
    deductions = 0
    for c in checks:
        if c["status"] == "FAIL":
            deductions += weights.get(c["severity"], 10)
        elif c["status"] == "WARN":
            deductions += weights.get(c["severity"], 6)

    score = max(0, min(100, 100 - deductions))
    if score >= 85:
        risk = "LOW"
    elif score >= 65:
        risk = "MEDIUM"
    else:
        risk = "HIGH"

    failed = [c["name"] for c in checks if c["status"] == "FAIL"]
    warnings = [c["name"] for c in checks if c["status"] == "WARN"]

    if failed:
        summary = f"{len(failed)} high-priority security issue(s) require attention."
    elif warnings:
        summary = f"{len(warnings)} improvement area(s) were identified."
    else:
        summary = "No major issues were detected by the current ruleset."

    recommendations = []
    for c in checks:
        if c["recommendation"]:
            recommendations.append({
                "priority": c["severity"].upper(),
                "title": c["name"],
                "text": c["recommendation"]
            })

    return {
        "score": score,
        "risk": risk,
        "summary": summary,
        "checks": checks,
        "recommendations": recommendations,
        "stats": {
            "checks": len(checks),
            "passed": sum(c["status"] == "PASS" for c in checks),
            "warnings": sum(c["status"] == "WARN" for c in checks),
            "failed": sum(c["status"] == "FAIL" for c in checks),
            "info": sum(c["status"] == "INFO" for c in checks)
        }
    }
