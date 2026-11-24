"""Messages sent to the team chat."""


def ready_message(mr):
    """A 'ready to merge' message once a reviewer or the bot has signed off, else None."""
    signed_off = [t for t in mr["labels"] if t.lower() == "approved"]
    if signed_off:
        return f"MR !{mr['id']} is ready to merge"
    return None
