"""
Different tools for automating my workflow
"""
import glob
import os
import pathlib
import shutil
import subprocess
import sys

try:
    from snakeviz import cli as sn_cli
except ImportError:
    sn_cli = None

HERE = pathlib.Path(__file__).parent
WINDOWS = "win" in sys.platform

if len(sys.argv) == 1:
    sys.exit("No args provided !")

if sys.argv[1] == "profile":
    subprocess.run("python -m cProfile -o out.prof run.py".split())
    sn_cli.main(["out.prof"])
    os.remove("out.prof")

elif sys.argv[1] == "build":
    cmd = (
        "pyinstaller run.py --name spaceinv --noconfirm "
        f"--add-data {HERE / 'space_invaders' / 'assets'}{os.pathsep}assets"
    ).split()

    if WINDOWS:
        cmd.extend(["--noconsole"])

    code = subprocess.run(cmd).returncode
    if code != 0:
        sys.exit(f"\nBuild exited with non-zero code: {code}")

    print("\nCompressing...")
    shutil.make_archive(HERE / "dist" / "spaceinv", "zip", HERE / "dist" / "spaceinv")
    shutil.rmtree("__pycache__", True)

elif sys.argv[1] == "clean":
    shutil.rmtree("build", True)
    shutil.rmtree("dist", True)
    os.remove("spaceinv.spec")
    for path in glob.iglob("**/__pycache__", recursive=True):
        shutil.rmtree(path, True)
