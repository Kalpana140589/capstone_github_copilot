def hello(name: str = "world"):
    """Return a greeting message.

    Args:
        name: name to greet

    Returns:
        A greeting string.
    """
    return f"Hello, {name}!"


class Greeter:
    """Simple greeter class."""

    def greet(self, who: str):
        """Greet a person by name."""
        return f"Hi, {who}!"
