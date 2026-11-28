#!/usr/bin/env python3
"""Validate abandoned.json."""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

FILE = Path(__file__).resolve().parent.parent / "abandoned.json"
NAME = FILE.name
IN_CI = os.environ.get("GITHUB_ACTIONS") == "true"


def report(level, message):
    # Package names come from untrusted PRs: keep them from injecting workflow commands or terminal escapes.
    message = "".join(c if c.isprintable() else repr(c)[1:-1] for c in message)
    if IN_CI:
        message = message.replace("%", "%25")
        print(f"::{level} file={NAME}::{message}")
    else:
        print(f"{level}: {message}", file=sys.stderr)


def serialize(data):
    return json.dumps(dict(sorted(data.items())), indent=2) + "\n"


def reject_duplicates(pairs):
    keys = [key for key, _ in pairs]
    duplicates = sorted({key for key in keys if keys.count(key) > 1})
    if duplicates:
        raise ValueError(f"Duplicate entries for: {', '.join(duplicates)}.")
    return dict(pairs)


def structure_errors(data):
    if not isinstance(data, dict):
        return [f"{NAME} must contain a JSON object, got {type(data).__name__}."]

    errors = []
    for key, value in data.items():
        if "/" not in key:
            errors.append(f"Key '{key}' does not look like a composer package name (expected vendor/package).")
        if not isinstance(value, dict):
            errors.append(f"Value for '{key}' must be an object, got {type(value).__name__}.")
            continue
        if "replacement" in value and not isinstance(value["replacement"], str):
            errors.append(f"'replacement' for '{key}' must be a string.")
        for extra_key in value:
            if extra_key != "replacement":
                errors.append(f"Unknown field '{extra_key}' in entry for '{key}'. Only 'replacement' is allowed.")
    return errors


def packagist_warning(package):
    url = f"https://packagist.org/packages/{package}.json"
    try:
        urllib.request.urlopen(url, timeout=10)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return f"Package '{package}' was not found on Packagist. If this is a private package, this warning can be ignored."
        return f"Could not check '{package}' on Packagist (HTTP {e.code})."
    except Exception as e:
        return f"Could not check '{package}' on Packagist: {e}"
    return None


def main():
    parser = argparse.ArgumentParser(description="Validate abandoned.json.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--fix", action="store_true", help="rewrite the file sorted and formatted")
    mode.add_argument("--packagist", action="store_true", help="only warn about packages not found on Packagist")
    args = parser.parse_args()

    text = FILE.read_text(encoding="utf-8", newline="")
    try:
        data = json.loads(text, object_pairs_hook=reject_duplicates)
    except json.JSONDecodeError as e:
        report("error", f"{NAME} contains invalid JSON: {e}")
        return 1
    except ValueError as e:
        report("error", str(e))
        return 1

    errors = structure_errors(data)
    if errors:
        for error in errors:
            report("error", error)
        return 1

    if args.packagist:
        packages = sorted(data)
        with ThreadPoolExecutor(max_workers=8) as pool:
            warnings = [w for w in pool.map(packagist_warning, packages) if w]
        for warning in warnings:
            report("warning", warning)
        print(f"Checked {len(packages)} packages on Packagist, {len(warnings)} warning(s).")
        return 0

    expected = serialize(data)
    if text == expected:
        print(f"{NAME} is valid.")
        return 0

    if args.fix:
        FILE.write_text(expected, encoding="utf-8", newline="")
        print(f"{NAME} was sorted and reformatted.")
        return 0

    report("error", f"{NAME} is not sorted alphabetically or not formatted with 2-space indentation and LF line endings. Run `python3 scripts/validate.py --fix` and commit the result.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
