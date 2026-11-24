#!/bin/bash
# Reference: filter unlisted products in suggest() AND in search() (which goes through the index).
python3 - <<'PY'
p = "/app/shop/catalog.py"
s = open(p).read()
s = s.replace("for pr in self._products.values() if pr.name.lower().startswith(p))",
              "for pr in self._products.values() if pr.is_listed() and pr.name.lower().startswith(p))")
s = s.replace("return sorted(self._products[s].name for s in skus)",
              "return sorted(self._products[s].name for s in skus if self._products[s].is_listed())")
open(p, "w").write(s)
PY
echo '{"fixed": true, "confidence": 95}' > /app/report.json
