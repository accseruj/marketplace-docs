#!/usr/bin/env bash
# Verifies the classifier in scripts/supplier-probe.py against recorded fact-sets.
# Run from the docs repo root. No network: --classify is the pure half of the tool,
# and a test that reached the real sites would fail for reasons that are not bugs.
#
# Cases 1-3 are the three hosts actually probed on 2026-08-05, which is what makes
# this a test rather than a restatement: the classifier's whole purpose is to have
# called gereedschapdropshipping.nl dead and wovar.nl live, and it must keep doing so.
# Archive timestamps are generated relative to today so the fixtures do not rot.
set -uo pipefail
DOCS="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
fail=0

ago() { python3 -c "import datetime,sys;print((datetime.date.today()-datetime.timedelta(days=int(sys.argv[1]))).strftime('%Y%m%d%H%M%S'))" "$1"; }
RECENT="$(ago 90)"
STALE="$(ago 1600)"

# $1 = json array of facts -> path to a temp file
mkfacts() { local f; f="$(mktemp)"; printf '%s\n' "$1" > "$f"; echo "$f"; }
verdict() { python3 "$DOCS/scripts/supplier-probe.py" --classify "$1" 2>&1 | awk 'NF{print $1; exit}'; }

check() { # $1 = label, $2 = expected verdict, $3 = facts json
  local f got; f="$(mkfacts "$3")"; got="$(verdict "$f")"
  if [ "$got" != "$2" ]; then
    echo "FAIL $1: expected $2, got $got"
    python3 "$DOCS/scripts/supplier-probe.py" --classify "$f" 2>&1
    fail=1
  fi
  rm -f "$f"
}

# case 1: a trading supplier - wovar.nl as observed
check "case 1 (live shop)" LIVE \
  '[{"host":"a.nl","dns":"1.2.3.4","https_status":200,"http_status":200,"cert_expired_days":0,"live_title":"Wovar","wayback_last":"'"$RECENT"'"}]'

# case 2: no 2xx but archived recently - doleweerd.nl as observed, HTTP 500 with a
# bankruptcy notice in the last capture. The tool must NOT call this dead on its own;
# it must hand the archived title to a human.
check "case 2 (down, recently archived)" SUSPECT \
  '[{"host":"b.nl","dns":"1.2.3.4","https_status":500,"http_status":500,"cert_expired_days":0,"wayback_last":"'"$RECENT"'","wayback_last_title":"failliet verklaard"}]'

# case 3: gereedschapdropshipping.nl as observed - 403 everywhere, certificate long
# expired, nothing archived for years. This is the case the first survey got wrong
# by reading it as "blocks automated access".
check "case 3 (defunct)" DEAD \
  '[{"host":"c.nl","dns":"1.2.3.4","https_status":403,"http_status":403,"cert_expired_days":665,"wayback_last":"'"$STALE"'"}]'

# case 4: a host that does not resolve is dead regardless of anything else
check "case 4 (no DNS)" DEAD \
  '[{"host":"d.nl","dns":null,"https_status":0,"http_status":0,"cert_expired_days":0,"wayback_last":"'"$RECENT"'"}]'

# case 5: serving fine behind an expired certificate is not dead, it is INSECURE.
# Collapsing this into DEAD would discard a usable supplier over a renewal lapse.
check "case 5 (2xx, expired cert)" INSECURE \
  '[{"host":"e.nl","dns":"1.2.3.4","https_status":200,"http_status":200,"cert_expired_days":40,"wayback_last":"'"$RECENT"'"}]'

# case 6: never archived and not responding
check "case 6 (never archived)" DEAD \
  '[{"host":"f.nl","dns":"1.2.3.4","https_status":404,"http_status":404,"cert_expired_days":0,"wayback_last":null}]'

# case 7: plain HTTP answering while HTTPS fails still counts as trading
check "case 7 (http only)" LIVE \
  '[{"host":"g.nl","dns":"1.2.3.4","https_status":0,"http_status":200,"cert_expired_days":0,"wayback_last":"'"$RECENT"'"}]'

# case 8: the archived title must reach the report, or case 2 is undiagnosable
f="$(mkfacts '[{"host":"h.nl","dns":"1.2.3.4","https_status":500,"http_status":500,"cert_expired_days":0,"wayback_last":"'"$RECENT"'","wayback_last_title":"Doleweerd B.V. is failliet verklaard"}]')"
if ! python3 "$DOCS/scripts/supplier-probe.py" --classify "$f" 2>&1 | grep -q "failliet verklaard"; then
  echo "FAIL case 8: archived title is not surfaced in the report"; fail=1
fi
rm -f "$f"

[ "$fail" = "0" ] && echo "supplier-probe: all cases pass"
exit "$fail"
