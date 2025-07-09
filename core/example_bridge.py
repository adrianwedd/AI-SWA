"""Example usage of the Rust Bridge service."""
from .bridge_client import reverse


def example() -> None:
    text = "abc"
    print("Reversed:", reverse(text))


if __name__ == "__main__":
    example()
