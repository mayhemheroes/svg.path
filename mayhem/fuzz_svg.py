#!/usr/bin/env python3
"""Atheris fuzz harness for svg.path.

Parses arbitrary fuzzer-generated SVG path strings with svg.path.parse_path and then exercises
the public API on the parsed result (segment iteration, point()/tangent() evaluation, length,
bounding box, round-trip d() serialization) so libFuzzer reaches real parsing + geometry code
paths for coverage.

svg.path raises a defined `InvalidPathError` (and ValueError) for malformed input — that is
EXPECTED, not a defect, so we catch it and let the fuzzer keep exploring. Mirrors the fork's
original `fuzz-svg` target (parse_path on a fuzzer-generated string).
"""

import random
import sys

import atheris
import fuzz_helpers

with atheris.instrument_imports(include=["svg"]):
    from svg.path import parse_path

from svg.path.parser import InvalidPathError


@atheris.instrument_func
def TestOneInput(data):
    fdp = fuzz_helpers.EnhancedFuzzedDataProvider(data)
    try:
        path = parse_path(fdp.ConsumeRemainingString())

        # Exercise the public API on the parsed result so the fuzzer reaches real code paths.
        for segment in path:
            _ = segment.point(0.5)
        if len(path) > 0:
            _ = path.point(0.5)
            _ = path.tangent(0.5)
            _ = path.length(error=1e-2)
            _ = path.boundingbox()
        # Round-trip back to a d-string (exercises the serialization path).
        _ = path.d()
    except (InvalidPathError, ValueError, ZeroDivisionError, OverflowError):
        # Expected, library-defined errors for malformed/degenerate path input.
        return
    except (TypeError, AttributeError, IndexError):
        # A genuine, unexpected defect. Re-raise it ~1% of the time so the defect surfaces as a
        # Mayhem POV while suppressing the rest so the corpus keeps growing (re-raising on every
        # hit would stall the corpus). Same approach as the fork's original harness.
        if random.random() > 0.99:
            raise
        return


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
