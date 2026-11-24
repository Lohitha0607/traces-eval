"""Flaky tests: failed at least once but not on every try."""


def flaky_tests(stats):
    out = []
    for name, rec in stats.items():
        if 0 < rec[0] < rec[1]:
            out.append(name)
    return sorted(out)
