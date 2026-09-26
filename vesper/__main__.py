import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m vesper <baseline|workflow> [options]", file=sys.stderr)
        return 2
    action = sys.argv[1]
    if action == "baseline":
        from .baseline import main as _main
        return _main()
    if action == "workflow":
        from .workflow import main as _main
        return _main()
    print(f"Unknown action: {action}", file=sys.stderr)
    return 2

raise SystemExit(main())
