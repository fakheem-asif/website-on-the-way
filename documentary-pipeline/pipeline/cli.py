"""Command-line entry point.

Stages map to subcommands:
    research   subject -> unverified dossier (then STOP for human review)
    review     verify claims + approve a dossier (the gate)
    produce    approved dossier -> documentary.mp4 (+ srt, manifest)
    run        research then produce IF an approved dossier already exists
    demo       render the bundled fictional example end-to-end
"""
from __future__ import annotations

import argparse
import os
import sys

from .config import Config
from .models import Dossier
from .stages import research as research_stage
from .stages import review as review_stage
from .util.text import slugify

_DEMO = os.path.join(os.path.dirname(os.path.dirname(__file__)), "examples", "lakeview.reviewed.json")


def _summary(result: dict) -> None:
    print("\n  Documentary ready")
    print(f"   video    : {result['video']}")
    print(f"   captions : {result['srt']}")
    print(f"   manifest : {result['manifest']}")
    print(f"   duration : {result['duration']}s across {result['scenes']} scenes")
    if result.get("excluded_claims"):
        print(f"   excluded : {len(result['excluded_claims'])} unverified claim(s) "
              f"({', '.join(result['excluded_claims'])})")


def cmd_research(args) -> int:
    cfg = Config.load(args.config)
    dossier = research_stage.run(args.subject, cfg)
    out_dir = args.out or cfg.output_dir
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{slugify(args.subject)}.dossier.json")
    dossier.save(path)
    print(f"Wrote unverified dossier: {path}")
    print("\nNEXT — the review gate (required before any video is made):")
    print(f"  1. Open {path} and replace every placeholder with a real, cited fact.")
    print(f"  2. python -m pipeline review --dossier {path}")
    print("  3. python -m pipeline produce --dossier "
          f"{path.replace('.dossier.json', '.reviewed.json')}")
    return 0


def cmd_review(args) -> int:
    dossier = Dossier.load(args.dossier)
    dossier = review_stage.interactive(dossier, reviewer=args.reviewer, approve_all=args.approve_all)
    out = args.out or args.dossier.replace(".dossier.json", ".reviewed.json")
    if out == args.dossier:
        out = args.dossier.replace(".json", ".reviewed.json")
    dossier.save(out)
    status = "APPROVED" if dossier.approved else "NOT approved"
    print(f"\n{status}. Wrote: {out}")
    return 0 if dossier.approved else 2


def cmd_produce(args) -> int:
    from . import orchestrator
    from .stages.review import ReviewGateError
    cfg = Config.load(args.config)
    dossier = Dossier.load(args.dossier)
    out_dir = args.out or cfg.output_dir
    try:
        result = orchestrator.produce(dossier, cfg, out_dir)
    except ReviewGateError as exc:
        print(f"\nREVIEW GATE: {exc}", file=sys.stderr)
        return 2
    _summary(result)
    return 0


def cmd_run(args) -> int:
    from . import orchestrator
    from .stages.review import ReviewGateError
    cfg = Config.load(args.config)
    out_dir = args.out or cfg.output_dir
    os.makedirs(out_dir, exist_ok=True)
    reviewed = os.path.join(out_dir, f"{slugify(args.subject)}.reviewed.json")
    if not os.path.exists(reviewed):
        dossier = research_stage.run(args.subject, cfg)
        path = os.path.join(out_dir, f"{slugify(args.subject)}.dossier.json")
        dossier.save(path)
        print(f"Wrote unverified dossier: {path}")
        print("STOP — review required. Run `review` to verify + approve, then re-run.")
        return 2
    try:
        result = orchestrator.produce(Dossier.load(reviewed), cfg, out_dir)
    except ReviewGateError as exc:
        print(f"\nREVIEW GATE: {exc}", file=sys.stderr)
        return 2
    _summary(result)
    return 0


def cmd_demo(args) -> int:
    from . import orchestrator
    cfg = Config.load(args.config)
    out_dir = args.out or os.path.join(cfg.output_dir, "demo")
    dossier = Dossier.load(_DEMO)
    print(f"Rendering bundled demo (fictional subject: {dossier.subject}) ...")
    result = orchestrator.produce(dossier, cfg, out_dir)
    _summary(result)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="pipeline", description="Fact-based documentary pipeline")
    # Shared options usable either before or after the subcommand.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--config", help="path to a JSON config (see config.example.json)")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("research", parents=[common], help="produce an unverified dossier for a subject")
    r.add_argument("--subject", required=True)
    r.add_argument("--out")
    r.set_defaults(func=cmd_research)

    v = sub.add_parser("review", parents=[common], help="verify claims and approve a dossier (the gate)")
    v.add_argument("--dossier", required=True)
    v.add_argument("--out")
    v.add_argument("--reviewer", default="")
    v.add_argument("--approve-all", action="store_true",
                   help="TESTING ONLY: approve without human fact-checking")
    v.set_defaults(func=cmd_review)

    pr = sub.add_parser("produce", parents=[common], help="render video from an approved dossier")
    pr.add_argument("--dossier", required=True)
    pr.add_argument("--out")
    pr.set_defaults(func=cmd_produce)

    rn = sub.add_parser("run", parents=[common], help="research, then produce if an approved dossier exists")
    rn.add_argument("--subject", required=True)
    rn.add_argument("--out")
    rn.set_defaults(func=cmd_run)

    d = sub.add_parser("demo", parents=[common], help="render the bundled fictional example end-to-end")
    d.add_argument("--out")
    d.set_defaults(func=cmd_demo)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
