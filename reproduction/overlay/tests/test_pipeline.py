"""Tests for the example data pipeline."""

import hashlib
import json
import sys
from pathlib import Path

import pytest

from full_data_science_example import pipeline
from full_data_science_example.pipeline import calculate_mean, write_pipeline_outputs


def test_calculate_mean(shared_datadir: Path) -> None:
    """Calculate a deterministic mean from fixture data."""
    assert calculate_mean(shared_datadir / "observations.csv") == pytest.approx(2.5)


def test_calculate_mean_rejects_empty_data(tmp_path: Path) -> None:
    """Reject a CSV file without observation rows."""
    input_path = tmp_path / "empty.csv"
    input_path.write_text("value\n", encoding="utf-8")
    with pytest.raises(ValueError, match="dataset is empty"):
        calculate_mean(input_path)


def test_calculate_mean_applies_configured_precision(tmp_path: Path) -> None:
    """Apply the DVC-controlled precision to a non-terminating mean."""
    input_path = tmp_path / "observations.csv"
    input_path.write_text("value\n1\n2\n2\n", encoding="utf-8")
    assert calculate_mean(input_path, round_digits=3) == pytest.approx(1.667)


def test_write_pipeline_outputs(shared_datadir: Path, tmp_path: Path) -> None:
    """Write DVC outputs with metrics, plot data, and input provenance."""
    input_path = shared_datadir / "observations.csv"
    summary_path = tmp_path / "summary.json"
    metrics_path = tmp_path / "metrics.json"
    plot_path = tmp_path / "cumulative_mean.csv"

    write_pipeline_outputs(input_path, summary_path, metrics_path, plot_path, round_digits=3)

    assert json.loads(summary_path.read_text(encoding="utf-8")) == {
        "mean": 2.5,
        "record_count": 4,
        "round_digits": 3,
        "input_sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
    }
    assert json.loads(metrics_path.read_text(encoding="utf-8")) == {
        "mean": 2.5,
        "record_count": 4,
    }
    assert plot_path.read_text(encoding="utf-8").splitlines() == [
        "observation,value,cumulative_mean",
        "1,1.0,1.0",
        "2,2.0,1.5",
        "3,3.0,2.0",
        "4,4.0,2.5",
    ]


def test_pipeline_main(shared_datadir: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Run the example pipeline through its command-line entry point."""
    summary_path = tmp_path / "summary.json"
    metrics_path = tmp_path / "metrics.json"
    plot_path = tmp_path / "cumulative_mean.csv"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "full-data-science-example-pipeline",
            str(shared_datadir / "observations.csv"),
            str(summary_path),
            str(metrics_path),
            str(plot_path),
            "--round-digits",
            "3",
        ],
    )

    pipeline.main()

    assert json.loads(summary_path.read_text(encoding="utf-8"))["round_digits"] == 3
    assert json.loads(metrics_path.read_text(encoding="utf-8"))["mean"] == pytest.approx(2.5)
    assert plot_path.is_file()
