#!/usr/bin/env python3
"""Supplier liveness probe. Run from the docs repo root:

    python3 scripts/supplier-probe.py --probe wovar.nl doleweerd.nl
    python3 scripts/supplier-probe.py --classify facts.json

Answers one question per host - is this supplier still trading - and refuses to
answer a second one it cannot: what the supplier sells. That distinction is the
reason this file exists. The first version of 10-architecture/supplier-landscape.md
recorded a scooter-parts wholesaler as an ijzerwaren wholesaler, because the
description came from a search-result summary about a different company. A
supplier's vertical is a claim about the supplier and needs the supplier's own
page; this tool therefore reports the live <title> and the last archived
<title> verbatim and draws no conclusion from either.

NOT a CI check. It talks to third-party sites over the network, so it runs on
demand. `--classify` is the pure half: it maps recorded facts to a verdict with
no network at all, which is what scripts/tests/test-supplier-probe.sh exercises.

Verdicts:
  LIVE       a 2xx response and an unexpired certificate
  INSECURE   a 2xx response behind an expired certificate
  SUSPECT    no 2xx, but archived recently - transient outage, block, or a
             notice worth reading. Read wayback_last_title before concluding.
  DEAD       no DNS, or no 2xx and nothing archived for over a year
"""
import argparse, json, re, ssl, socket, subprocess, sys, datetime

ARCHIVE_STALE_DAYS = 365
NOW = datetime.datetime.now(datetime.timezone.utc)
UA = "Mozilla/5.0 (compatible; marketplace-docs supplier probe)"

# TLS verification is deliberately off in this file, in `curl -k` and in the
# unverified SSL context below. An expired certificate is one of the signals
# being measured, and a verifying client aborts the handshake before the expiry
# date can be read - the check would lose exactly the evidence it exists to
# collect. This is safe only because of what the probe does: it fetches public
# home pages of third-party sites, sends no credentials, no cookies and no
# personal data, and treats every response as untrusted text. Do not copy this
# pattern into anything that transmits or trusts data.


def curl(url, *extra):
    """Status code and body of a URL, following redirects. Empty on failure."""
    out = subprocess.run(
        ["curl", "-sk", "--max-time", "25", "-A", UA, "-L", url,
         "-w", "\n__STATUS__%{http_code}", *extra],
        capture_output=True, text=True, errors="replace",
    ).stdout
    match = re.search(r"__STATUS__(\d+)$", out)
    return (int(match.group(1)) if match else 0), out[: match.start()] if match else ""


def cert_not_after(host):
    """Certificate expiry as a UTC datetime, or None if it cannot be read."""
    context = ssl._create_unverified_context()
    try:
        with socket.create_connection((host, 443), timeout=15) as raw:
            with context.wrap_socket(raw, server_hostname=host) as tls:
                der = tls.getpeercert(binary_form=True)
    except Exception:
        return None
    text = subprocess.run(["openssl", "x509", "-inform", "DER", "-noout", "-enddate"],
                          input=der, capture_output=True).stdout.decode(errors="replace")
    match = re.search(r"notAfter=(.+)", text)
    if not match:
        return None
    try:
        return datetime.datetime.strptime(match.group(1).strip(), "%b %d %H:%M:%S %Y %Z") \
            .replace(tzinfo=datetime.timezone.utc)
    except ValueError:
        return None


def title_of(html):
    match = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
    return re.sub(r"\s+", " ", match.group(1)).strip()[:120] if match else None


def wayback(host):
    """(last capture date, title of that capture) from the Internet Archive."""
    out = subprocess.run(
        ["curl", "-s", "--max-time", "40",
         f"https://web.archive.org/cdx/search/cdx?url={host}&fl=timestamp,statuscode&limit=-1"],
        capture_output=True, text=True, errors="replace").stdout.strip()
    stamp = out.split()[0] if out and out.split() else None
    if not stamp or not stamp.isdigit():
        return None, None
    _, body = curl(f"https://web.archive.org/web/{stamp}/https://{host}/")
    return stamp, title_of(body)


def probe(host):
    try:
        ip = socket.gethostbyname(host)
    except socket.gaierror:
        ip = None
    https_status, https_body = curl(f"https://{host}/") if ip else (0, "")
    http_status, _ = curl(f"http://{host}/") if ip else (0, "")
    not_after = cert_not_after(host) if ip else None
    stamp, arch_title = wayback(host) if ip else (None, None)
    return {
        "host": host,
        "dns": ip,
        "https_status": https_status,
        "http_status": http_status,
        "cert_not_after": not_after.date().isoformat() if not_after else None,
        "cert_expired_days": (NOW - not_after).days if not_after and not_after < NOW else 0,
        "live_title": title_of(https_body),
        "wayback_last": stamp,
        "wayback_last_title": arch_title,
    }


def classify(f):
    """Facts to (verdict, reasons). Pure - no network, no clock beyond NOW."""
    reasons = []
    if not f.get("dns"):
        return "DEAD", ["does not resolve"]

    ok = any(200 <= (f.get(k) or 0) < 300 for k in ("https_status", "http_status"))
    expired = f.get("cert_expired_days") or 0
    if expired:
        reasons.append(f"certificate expired {expired} days ago")

    if ok:
        return ("INSECURE" if expired else "LIVE"), reasons or ["responds 2xx"]

    reasons.append(f"no 2xx (https {f.get('https_status')}, http {f.get('http_status')})")
    stamp = f.get("wayback_last")
    if not stamp:
        return "DEAD", reasons + ["never archived"]
    age = (NOW - datetime.datetime.strptime(stamp[:8], "%Y%m%d")
           .replace(tzinfo=datetime.timezone.utc)).days
    reasons.append(f"last archived {age} days ago")
    return ("SUSPECT" if age <= ARCHIVE_STALE_DAYS else "DEAD"), reasons


def report(rows):
    for f in rows:
        verdict, reasons = classify(f)
        print(f"\n{verdict:8} {f['host']}")
        print(f"         {'; '.join(reasons)}")
        for label, key in (("live title", "live_title"),
                           ("archived  ", "wayback_last_title")):
            if f.get(key):
                print(f"         {label}: {f[key]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--probe", nargs="+", metavar="HOST")
    ap.add_argument("--classify", metavar="FILE", help="JSON list of recorded facts")
    ap.add_argument("-o", "--out", metavar="FILE", help="write probed facts as JSON")
    args = ap.parse_args()

    if args.classify:
        rows = json.load(open(args.classify))
    elif args.probe:
        rows = []
        for host in args.probe:
            print(f"probing {host} ...", file=sys.stderr, flush=True)
            rows.append(probe(host))
        if args.out:
            json.dump(rows, open(args.out, "w"), indent=1)
    else:
        ap.error("one of --probe or --classify is required")

    report(rows)


if __name__ == "__main__":
    main()
