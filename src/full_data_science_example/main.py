"""Small example API for Full Data Science Example."""


def hello(name: str = "World") -> str:
    """Return a greeting.

    Args:
        name: Name to greet.

    Returns:
        A greeting string.
    """
    return f"Hello, {name}!"


def main() -> None:
    """Run the example command-line entry point."""
    print(hello())


if __name__ == "__main__":
    main()
