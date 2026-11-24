from ci_report.load import load_stats, records


def summarize(path):
    """{'tests': n, 'failures': f, 'tries': t} for a stats file."""
    rows = list(records(load_stats(path)))
    return {"tests": len(rows), "failures": sum(r[1] for r in rows), "tries": sum(r[2] for r in rows)}
