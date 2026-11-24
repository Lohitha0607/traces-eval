"""Render a summary dict as text (unrelated to the format change)."""


def render(summary):
    return f"{summary['tests']} tests, {summary['failures']} failures over {summary['tries']} tries"
