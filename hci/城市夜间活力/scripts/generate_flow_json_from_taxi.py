import argparse
import csv
import json
from datetime import datetime
from pathlib import Path


def parse_time(value: str) -> datetime:
    value = value.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unsupported datetime format: {value}")


def is_night_window(dt: datetime, start_minutes: int, end_minutes: int) -> bool:
    minutes = dt.hour * 60 + dt.minute
    if start_minutes <= end_minutes:
        return start_minutes <= minutes < end_minutes
    return minutes >= start_minutes or minutes < end_minutes


def parse_bbox(value: str | None) -> tuple[float, float, float, float] | None:
    if not value:
        return None
    parts = [float(item) for item in value.split(",")]
    if len(parts) != 4:
        raise ValueError("bbox must be min_lon,min_lat,max_lon,max_lat")
    return parts[0], parts[1], parts[2], parts[3]


def in_bbox(lon: float, lat: float, bbox: tuple[float, float, float, float] | None) -> bool:
    if bbox is None:
        return True
    min_lon, min_lat, max_lon, max_lat = bbox
    return min_lon <= lon <= max_lon and min_lat <= lat <= max_lat


def finalize_line(lines: list[list[list[float]]], current: list[list[float]], min_points: int) -> None:
    if len(current) >= min_points:
        lines.append(current)


def process_file(
    file_path: Path,
    lines: list[list[list[float]]],
    stats: dict,
    start_minutes: int,
    end_minutes: int,
    bbox: tuple[float, float, float, float] | None,
    max_gap_minutes: int,
    stride: int,
    min_points: int,
) -> None:
    current: list[list[float]] = []
    last_dt: datetime | None = None
    point_index = 0

    with file_path.open("r", encoding="utf-8", newline="") as source:
        reader = csv.reader(source, skipinitialspace=True)
        for row in reader:
            if len(row) < 4:
                continue
            stats["rows_total"] += 1

            dt = parse_time(row[1])
            if not is_night_window(dt, start_minutes, end_minutes):
                continue

            lon = float(row[2])
            lat = float(row[3])
            if not in_bbox(lon, lat, bbox):
                continue

            stats["rows_kept"] += 1
            stats["min_lon"] = min(stats["min_lon"], lon)
            stats["max_lon"] = max(stats["max_lon"], lon)
            stats["min_lat"] = min(stats["min_lat"], lat)
            stats["max_lat"] = max(stats["max_lat"], lat)

            if stats["first_time"] is None or dt < stats["first_time"]:
                stats["first_time"] = dt
            if stats["last_time"] is None or dt > stats["last_time"]:
                stats["last_time"] = dt

            if last_dt is not None:
                gap = (dt - last_dt).total_seconds() / 60
                if gap > max_gap_minutes:
                    finalize_line(lines, current, min_points)
                    current = []

            if point_index % stride == 0:
                current.append([round(lon, 6), round(lat, 6)])

            point_index += 1
            last_dt = dt

    finalize_line(lines, current, min_points)


def build_report(stats: dict, output_report: Path) -> None:
    first_time = stats["first_time"].isoformat(sep=" ") if stats["first_time"] else "N/A"
    last_time = stats["last_time"].isoformat(sep=" ") if stats["last_time"] else "N/A"

    content = (
        "# Taxi Flow Dataset Report\n\n"
        f"Files scanned: {stats['files_total']}\n\n"
        f"Rows total: {stats['rows_total']}\n\n"
        f"Rows kept (night window + bbox): {stats['rows_kept']}\n\n"
        f"Polylines generated: {stats['lines_total']}\n\n"
        f"Time range: {first_time} -> {last_time}\n\n"
        "Bounding box:\n\n"
        f"- min_lon: {stats['min_lon']:.6f}\n"
        f"- max_lon: {stats['max_lon']:.6f}\n"
        f"- min_lat: {stats['min_lat']:.6f}\n"
        f"- max_lat: {stats['max_lat']:.6f}\n"
    )

    output_report.parent.mkdir(parents=True, exist_ok=True)
    output_report.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate flow JSON for flow.md from taxi CSV files.")
    parser.add_argument("input_dir", help="Directory with Taxi_* files.")
    parser.add_argument("output_json", help="Output JSON file path.")
    parser.add_argument(
        "--start",
        default="20:00",
        help="Night window start time (HH:MM).",
    )
    parser.add_argument(
        "--end",
        default="02:00",
        help="Night window end time (HH:MM).",
    )
    parser.add_argument(
        "--bbox",
        default="120.85,30.70,122.20,31.90",
        help="Filter to bounding box min_lon,min_lat,max_lon,max_lat.",
    )
    parser.add_argument(
        "--max-gap",
        type=int,
        default=20,
        help="Split line when gap minutes exceed this value.",
    )
    parser.add_argument(
        "--stride",
        type=int,
        default=3,
        help="Keep every Nth point to reduce size.",
    )
    parser.add_argument(
        "--min-points",
        type=int,
        default=6,
        help="Minimum points for a polyline to be kept.",
    )
    parser.add_argument(
        "--report",
        default="c:/Users/12900/Desktop/code/data/synthetic/figs/flow_dataset_report.md",
        help="Path to write a simple analysis report.",
    )
    args = parser.parse_args()

    start_minutes = int(args.start.split(":")[0]) * 60 + int(args.start.split(":")[1])
    end_minutes = int(args.end.split(":")[0]) * 60 + int(args.end.split(":")[1])
    bbox = parse_bbox(args.bbox)

    input_dir = Path(args.input_dir)
    output_json = Path(args.output_json)
    report_path = Path(args.report)

    taxi_files = sorted(p for p in input_dir.iterdir() if p.is_file())

    stats = {
        "files_total": len(taxi_files),
        "rows_total": 0,
        "rows_kept": 0,
        "lines_total": 0,
        "min_lon": float("inf"),
        "max_lon": float("-inf"),
        "min_lat": float("inf"),
        "max_lat": float("-inf"),
        "first_time": None,
        "last_time": None,
    }

    lines: list[list[list[float]]] = []
    for file_path in taxi_files:
        process_file(
            file_path,
            lines,
            stats,
            start_minutes,
            end_minutes,
            bbox,
            args.max_gap,
            args.stride,
            args.min_points,
        )

    stats["lines_total"] = len(lines)

    output_json.parent.mkdir(parents=True, exist_ok=True)
    with output_json.open("w", encoding="utf-8") as target:
        json.dump(lines, target, ensure_ascii=False)

    build_report(stats, report_path)

    print(f"Wrote lines: {output_json}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
