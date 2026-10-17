#!/usr/bin/env python3
"""Nominal relative type tokens; heuristic defaults, not Apple specifications.

All geometry is in current body em (B). No font loading or actual line breaking.
Python 3.9+, standard library only. See ../references/adapters-and-examples.md.
"""

import argparse
import json
import math


PROFILES = {
    "compact": {
        "minor": 1.125, "section": 1.29,
        "title": (1.42, 1.65), "display": (1.8, 2.0),
        "body_lh": {"zh": 1.55, "mixed": 1.55, "en": 1.45},
    },
    "balanced": {
        "minor": 1.18, "section": 1.41,
        "title": (1.65, 2.0), "display": (2.2, 2.8),
        "body_lh": {"zh": 1.6, "mixed": 1.6, "en": 1.5},
    },
    "editorial": {
        "minor": 1.25, "section": 1.65,
        "title": (2.0, 2.5), "display": (2.8, 3.5),
        "body_lh": {"zh": 1.7, "mixed": 1.7, "en": 1.6},
    },
    "display": {
        "minor": 1.25, "section": 2.0,
        "title": (2.4, 3.2), "display": (3.2, 4.5),
        "body_lh": {"zh": 1.65, "mixed": 1.65, "en": 1.5},
    },
}


def positive_number(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("must be a finite positive number")
    return number


def positive_integer(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def interpolate(bounds, width_b):
    t = min(1.0, max(0.0, (width_b - 20.0) / 40.0))
    return bounds[0] + (bounds[1] - bounds[0]) * t


def make_scale(profile, language, width_b, title_width_b=None,
               title_advance_em=None, title_lines=2, minimum_ratio=0.82,
               body_value=None, unit=None):
    """Return nominal tokens. CLI validates inputs before invoking this helper."""
    p = PROFILES[profile]
    title_width_b = width_b if title_width_b is None else title_width_b
    title_ratio = interpolate(p["title"], title_width_b)
    warnings = []
    fit = {"status": "not_measured"}
    if title_advance_em is not None:
        fit_limit = title_lines * title_width_b / title_advance_em
        fit = {
            "status": "estimated_fit",
            "estimated_max_ratio": round(fit_limit, 4),
            "allowed_lines": title_lines,
            "requires_render_check": True,
        }
        if fit_limit < p["title"][0]:
            fit["status"] = "reflow_required"
            warnings.append(
                "Title needs more lines, width, or a revised composition. "
                "Kept the selected ratio; did not shrink below the profile minimum."
            )
        else:
            title_ratio = min(title_ratio, fit_limit)
        warnings.append(
            "Title fit uses total advance only; word boundaries, tracking, and "
            "optical sizing require a real render."
        )

    if width_b < 18:
        warnings.append("Narrow body measure: check wrapping and reflow before reducing B.")
    if width_b > 80:
        warnings.append("Wide body container: consider a measure cap or columns.")
    if minimum_ratio > 0.82:
        warnings.append("Small roles were raised to the supplied calibrated minimum ratio.")

    body_lh = p["body_lh"][language]
    title_lh = 1.1 if language == "en" else 1.2
    title_weight = "Medium" if profile == "editorial" else "Semibold"
    definitions = [
        ("caption", 0.82, "Regular", 1.4 if language == "en" else 1.5),
        ("secondary", 0.9, "Regular", body_lh),
        ("body", 1.0, "Regular", body_lh),
        ("label", 1.0, "Medium", 1.35),
        ("lead", 1.125, "Medium", body_lh),
        ("minor", p["minor"], "Semibold", 1.35),
        ("section", p["section"], "Semibold", 1.3),
        ("title", title_ratio, title_weight, title_lh),
        ("display", interpolate(p["display"], title_width_b), title_weight, title_lh),
    ]
    weights = {"Regular": 400, "Medium": 500, "Semibold": 600}
    tokens = {}
    for role, ratio, weight, line_height in definitions:
        ratio = max(ratio, minimum_ratio)
        token = {
            "ratio": round(ratio, 4),
            "optical_correction": 1.0,
            "weight_intent": weight,
            "css_weight_hint": weights[weight],
            "line_height_em": line_height,
            "line_height_b": round(ratio * line_height, 4),
        }
        if body_value is not None:
            token["resolved"] = {
                "unit": unit,
                "font_size": round(body_value * ratio, 4),
                "line_height": round(body_value * ratio * line_height, 4),
            }
        tokens[role] = token

    return {
        "schema_version": "1.0",
        "model": "relative-typography; project heuristics, not Apple specifications",
        "basis": "B is the current calibrated body size, including user preference",
        "inputs": {
            "profile": profile, "language": language, "width_b": width_b,
            "title_width_b": title_width_b, "minimum_ratio": minimum_ratio,
            "body_value": body_value, "unit": unit,
            "title_advance_em": title_advance_em, "title_lines": title_lines,
        },
        "tokens": tokens,
        "title_fit": fit,
        "notes": [
            "K=1 is nominal; calibrate actual font pairs in the target medium.",
            "Body width is geometry, not a guaranteed character count or readable B.",
            "Display role has not been measured for text fit.",
        ],
        "warnings": warnings,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=PROFILES, default="balanced")
    parser.add_argument("--language", choices=("zh", "en", "mixed"), default="mixed")
    parser.add_argument("--width-b", type=positive_number, required=True,
                        help="body container width / current body B")
    parser.add_argument("--title-width-b", type=positive_number,
                        help="title container width / B; defaults to --width-b")
    parser.add_argument("--title-advance-em", type=positive_number,
                        help="measured title advance at B, in the intended title face/weight")
    parser.add_argument("--title-lines", type=positive_integer, default=2)
    parser.add_argument("--minimum-ratio", type=positive_number, default=0.82)
    parser.add_argument("--body-value", type=positive_number)
    parser.add_argument("--unit", choices=("px", "pt", "mm", "rem", "frame-unit"))
    args = parser.parse_args()
    if args.minimum_ratio > 1:
        parser.error("--minimum-ratio must be <= 1; recalibrate B if body is too small")
    if (args.body_value is None) != (args.unit is None):
        parser.error("--body-value and --unit must be supplied together")
    print(json.dumps(make_scale(**vars(args)), indent=2, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
