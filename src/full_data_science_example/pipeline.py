"""Small deterministic data pipeline used by the full template example."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


def read_values(input_path: Path) -> list[float]:
    """Read numeric observations from a CSV file.

    Args:
        input_path: CSV file containing a numeric ``value`` column.

    Returns:
        Parsed values in input order.

    Raises:
        ValueError: If the input does not contain any data rows.
    """
    with input_path.open(newline="", encoding="utf-8") as input_file:
        values = [float(row["value"]) for row in csv.DictReader(input_file)]

    if not values:
        raise ValueError("The input dataset is empty.")

    return values


def calculate_mean(input_path: Path, *, round_digits: int | None = None) -> float:
    """Calculate the mean of the ``value`` column in a CSV file.

    Args:
        input_path: CSV file containing a numeric ``value`` column.
        round_digits: Optional decimal precision for the result.

    Returns:
        Arithmetic mean of the input values.
    """
    values = read_values(input_path)
    mean = sum(values) / len(values)
    return round(mean, round_digits) if round_digits is not None else mean


def write_pipeline_outputs(
    input_path: Path,
    summary_path: Path,
    metrics_path: Path,
    plot_path: Path,
    *,
    round_digits: int,
) -> None:
    """Write deterministic summary, metric, plot, and provenance outputs.

    Args:
        input_path: Source CSV dataset.
        summary_path: Destination for the detailed JSON summary.
        metrics_path: Destination for DVC scalar metrics.
        plot_path: Destination for cumulative-mean plot data.
        round_digits: Decimal precision applied to reported values.
    """
    values = read_values(input_path)
    mean = round(sum(values) / len(values), round_digits)
    input_digest = hashlib.sha256(input_path.read_bytes()).hexdigest()

    summary = {
        "mean": mean,
        "record_count": len(values),
        "round_digits": round_digits,
        "input_sha256": input_digest,
    }
    metrics = {
        "mean": mean,
        "record_count": len(values),
    }

    for output_path, payload in ((summary_path, summary), (metrics_path, metrics)):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    plot_path.parent.mkdir(parents=True, exist_ok=True)
    with plot_path.open("w", newline="", encoding="utf-8") as plot_file:
        writer = csv.DictWriter(plot_file, fieldnames=("observation", "value", "cumulative_mean"))
        writer.writeheader()
        cumulative_total = 0.0
        for index, value in enumerate(values, start=1):
            cumulative_total += value
            writer.writerow(
                {
                    "observation": index,
                    "value": value,
                    "cumulative_mean": round(cumulative_total / index, round_digits),
                }
            )


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_path", type=Path)
    parser.add_argument("summary_path", type=Path)
    parser.add_argument("metrics_path", type=Path)
    parser.add_argument("plot_path", type=Path)
    parser.add_argument("--round-digits", type=int, required=True)
    return parser.parse_args()


def main() -> None:
    """Run the example data pipeline."""
    arguments = parse_arguments()
    write_pipeline_outputs(
        arguments.input_path,
        arguments.summary_path,
        arguments.metrics_path,
        arguments.plot_path,
        round_digits=arguments.round_digits,
    )


if __name__ == "__main__":
    main()
