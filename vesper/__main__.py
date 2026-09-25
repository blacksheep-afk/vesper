import sys
if len(sys.argv) > 1 and sys.argv[1] == 'baseline':
    from .baseline import main
else:
    from .workflow import main
raise SystemExit(main())
