#!/usr/bin/env python3
import atheris
import sys
import fuzz_helpers
import random

with atheris.instrument_imports():
    from svg.path import parse_path

from svg.path.parser import InvalidPathError

def TestOneInput(data):
    fdp = fuzz_helpers.EnhancedFuzzedDataProvider(data)
    try:
        parse_path(fdp.ConsumeRemainingString())
    except (InvalidPathError, ValueError):
        return -1
    except (TypeError, AttributeError, IndexError):
        if random.random() > 0.999:
            raise
        return -1
def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
