import sys
if len(sys.argv) > 1 and sys.argv[1] == 'baseline':
    from .baseline import main
elif len(sys.argv) > 1 and sys.argv[1] == 'workspace':
    from .workspace import main
    raise SystemExit(main(sys.argv[2:]))
else:
    from .workflow import main
raise SystemExit(main())
