"""Print or save one safe local-machine observation for T9."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.local_collector import collect_local_observation


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect approved local AIOps metrics and logs")
    parser.add_argument("--output", type=Path, help="optional JSON output file")
    args = parser.parse_args(argv)
    project_root = Path(__file__).resolve().parents[1]
    observation, metadata = collect_local_observation(project_root)
    document = {"observation": observation, "collection": metadata}
    encoded = json.dumps(document, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
