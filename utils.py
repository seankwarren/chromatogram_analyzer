from numpy.typing import NDArray
import numpy as np
from slugify import slugify

def parse_key_value_pairs(content: str):
    """
    Parses a tab-delimited string of key-value pairs into a dictionary. Assumes
    each line is a key-value pair separated by a tab. If a line has no tab, the
    entire line is considered the key and the value is set to None.

    Args:
    - content: String with key-value pairs separated by tabs.

    Returns:
    - dict: Dictionary with key-value pairs
    """
    lines = content.split("\n")
    data = {}
    for line in lines:
        kv = line.split("\t") # split line into key-value pair
        if len(kv) == 2:
            data[slugify_key(kv[0])] = kv[1]
        elif len(kv) == 1: # TODO: decide how to handle key-value pairs with no value
            data[slugify_key(kv[0])] = None
        else:
            print(f"Unknown line format: {line}")
    return data

def slugify_key(text: str, separator: str = '_') -> str:
    """
    Slugifies a string and replaces spaces with the specified separator.

    Args:
    - text: String to slugify
    - separator: Separator to use in place of spaces

    Returns:
    - Slugified string
    """
    return slugify(text, separator=separator)

def normalize(values: NDArray) -> NDArray:
    """
    Normalizes a list of values to the range [0, inf].

    Args:
    - values: List of values to normalize

    Returns:
    - List of normalized values
    """
    min = np.min(values)
    return np.array([value - min for value in values])
