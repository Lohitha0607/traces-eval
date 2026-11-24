#!/bin/bash
# Reference: filter hidden items in BOTH list_items and search.
python3 - <<'PY'
p = "/app/catalog.py"
s = open(p).read()
s = s.replace("return sorted(n for n in self._items if n.startswith(prefix))",
              "return sorted(n for n, it in self._items.items() if n.startswith(prefix) and not it.hidden)")
s = s.replace("for n, it in self._items.items() if q in n.lower() or q in it.description.lower())",
              "for n, it in self._items.items() if not it.hidden and (q in n.lower() or q in it.description.lower()))")
open(p, "w").write(s)
PY
echo '{"fixed": true, "confidence": 95}' > /app/report.json
