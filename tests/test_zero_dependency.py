"""App-wide zero-dependency sweep (ingested from trading-app)."""
import ast, os, sys, unittest

WORKDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIRS = ("core", "data", "engines", "brokers", "kit", "strategies", "backtests",
            "risk", "execution", "utils", "web", "tests", "rfc", "deeptutor", "deeptutor_cli")
SKIP = {".git", "__pycache__", "node_modules"}


def _project_names():
    names = set()
    for dirpath, dirs, files in os.walk(WORKDIR):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for f in files:
            if f.endswith(".py"):
                names.add(f[:-3])
    for entry in os.listdir(WORKDIR):
        full = os.path.join(WORKDIR, entry)
        if not os.path.isdir(full) or entry in SKIP:
            continue
        for dirpath, dirs, files in os.walk(full):
            dirs[:] = [d for d in dirs if d not in SKIP]
            if any(f.endswith(".py") for f in files):
                names.add(entry)
                break
    return names


def _app_files():
    files = [os.path.join(WORKDIR, "run_all.py")]
    for d in APP_DIRS:
        p = os.path.join(WORKDIR, d)
        if not os.path.isdir(p):
            continue
        for dirpath, dirs, names in os.walk(p):
            dirs[:] = [x for x in dirs if x not in SKIP]
            files += [os.path.join(dirpath, n) for n in names if n.endswith(".py")]
    return sorted(files)


def _import_roots(source):
    roots = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                roots.add(node.module.split(".")[0])
    return roots


class ZeroDependency(unittest.TestCase):
    def test_no_third_party_imports(self):
        project = _project_names()
        offenders = []
        for path in _app_files():
            with open(path, encoding="utf-8") as fh:
                roots = _import_roots(fh.read())
            for root in sorted(roots):
                if root in sys.stdlib_module_names or root in project:
                    continue
                offenders.append("%s: %s" % (os.path.relpath(path, WORKDIR), root))
        self.assertEqual(offenders, [], "third-party import(s): %s" % offenders)

    def test_sweep_reads_app(self):
        files = _app_files()
        self.assertIn(os.path.join(WORKDIR, "run_all.py"), files)
        self.assertGreater(len(files), 40)

    def test_detector_flags_third_party(self):
        roots = _import_roots("import numpy\nimport json\n")
        self.assertIn("numpy", roots)