# SRM Auto-Block Investigation — 62.60.131.152

**Report date**: 2026-03-14
**Blocked by**: Synology Router Manager (SRM) auto-block

---

## Summary

SRM auto-blocked **62.60.131.152** due to repeated failed login attempts consistent with SSH brute force and web credential stuffing. The IP belongs to **Feo Prest SRL** (AS208137), a Romanian-registered hosting provider that came online in August 2025 and began generating mass abuse within weeks of activation. Every neighbouring IP in the `/24` subnet has been mass-reported across global threat feeds — one neighbour alone has over **326,000 AbuseIPDB reports**. The block is fully justified. Blocking the entire `62.60.131.0/24` subnet is recommended.

---

## IP Details

| Field | Value |
|-------|-------|
| **IP** | 62.60.131.152 |
| **Reverse DNS** | None |
| **ASN** | AS208137 |
| **Organisation** | Feo Prest SRL |
| **Registered** | Romania (Constanta — VALU LUI TRAIAN, Str. PLUGARILOR, Nr. 5A) |
| **Hosted in** | Netherlands (Kerkrade, Limburg) — via Dutch peering |
| **Upstream/Transit** | AS49581 — Ferdinand Zink trading as Tube-Hosting (Germany) |
| **ASN created** | 2025-08-05 (less than 7 months old) |
| **Abuse contact** | admin@feoprest.life |
| **RIPE sponsor** | ORG-IML22-RIPE |

---

## ASN Red Flags

AS208137 is a tiny, recently created hosting ASN controlling only 768 total IPv4 addresses across 3 prefixes:

| Prefix | Attribution |
|--------|-------------|
| `62.60.131.0/24` | Feo Prest SRL |
| `213.177.179.0/24` | "Ali Moradi" — suspicious attribution discrepancy |
| `213.209.159.0/24` | Feo Prest SRL |

- Created August 2025 — already generating one of the highest abuse volumes on AbuseIPDB
- Single upstream (Tube-Hosting / AS49581) — itself documented for hosting abusive customers
- Abuse contact uses `.life` TLD (`feoprest.life`), not the company's registered business domain
- One prefix attributed to a different individual — suggests routing on behalf of third parties
- BitTorrent DHT activity tagged on IPs within the ASN

---

## Subnet Abuse Profile (62.60.131.0/24)

All abuse activity across the subnet began **September–October 2025** — immediately after the ASN's August 2025 activation.

| Neighbour IP | AbuseIPDB Reports | Distinct Reporters | Confidence |
|---|---|---|---|
| 62.60.131.157 | **326,115** | 1,167 | 100% |
| 62.60.131.151 | 25,821 | 898 | Active |
| 62.60.131.158 | 25,496 | 621 | Active |
| 62.60.131.29 | 3,905 | 284 | Active |
| 62.60.131.218 | 1,186 | 374 | 100% |
| 62.60.131.125 | Multiple | Multiple | Bad Web Bot |
| 62.60.131.74/168 | Reported | Multiple | Active |

---

## Attack Categories

| Category | Detail |
|----------|--------|
| **SSH Brute Force** | Credential stuffing / dictionary attacks on TCP/22 |
| **Web Credential Stuffing** | Automated attacks on DSM, QuickConnect, web interfaces |
| **Port Scanning** | Systematic reconnaissance across internet-facing hosts |
| **Bad Web Bot** | HTTP/HTTPS automated scanning (confirmed on 62.60.131.125) |
| **IDS Triggers** | ET CINS Active Threat Intelligence Poor Reputation IP feed |

**Why SRM triggered**: Synology's auto-block fires on repeated failed login attempts via SSH or DSM web interface. This subnet's primary attack pattern — SSH brute force + web credential stuffing — maps exactly to that trigger condition.

---

## Threat Feed Presence

| Feed | Status |
|------|--------|
| AbuseIPDB | Entire /24 heavily indexed; multiple IPs at 100% confidence |
| ET CINS (Emerging Threats) | Flagged under "Active Threat Intelligence Poor Reputation IP" group |
| CleanTalk | AS208137 tracked for spam and abusive activity |
| IPFire IDS community blocklist | Subnet triggered alerts in community IDS report |
| SniffCat | Web bot activity confirmed on 62.60.131.125 |

---

## Confidence Assessment

| Factor | Assessment |
|--------|------------|
| IP is malicious | ✅ **Very high confidence** |
| False positive risk | ✅ **Very low** — SRM block was correctly triggered |
| Legitimate use present | ❌ No — no reverse DNS, no hosted services, no legitimate attribution |

---

## Recommendation

1. **Keep the block** — fully justified
2. **Block the full subnet**: `62.60.131.0/24` at the SRM/firewall level
3. **Consider blocking AS208137 entirely** — all 3 prefixes show the same behaviour pattern

---

## Sources

- [62.60.131.151 — AbuseIPDB](https://www.abuseipdb.com/check/62.60.131.151)
- [62.60.131.157 — AbuseIPDB](https://www.abuseipdb.com/check/62.60.131.157)
- [62.60.131.218 — AbuseIPDB](https://www.abuseipdb.com/check/62.60.131.218)
- [AS208137 Feo Prest SRL — IPinfo.io](https://ipinfo.io/AS208137)
- [AS208137 — BGPView](https://bgpview.io/asn/208137)
- [Feo Prest SRL — Scamalytics](https://scamalytics.com/ip/isp/feo-prest-srl)
- [62.60.131.125 — SniffCat](https://sniffcat.com/reports/62.60.131.125)
- [AS49581 Tube-Hosting — PeeringDB](https://www.peeringdb.com/asn/49581)
- [AS208137 Spam Stats — CleanTalk](https://cleantalk.org/blacklists/as208137)
- Team Cymru BGP: `62.60.131.0/24 | IR | ripencc | 2001-06-13`
