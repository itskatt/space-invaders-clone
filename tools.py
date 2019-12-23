# tools script
import os
import shutil
import subprocess
import sys

import snakeviz.cli


if len(sys.argv) == 1:
    sys.exit("No args provided !")

if sys.argv[1] == "profile":
    subprocess.run("python -m cProfile -o out.prof run.py --timeout 10".split())
    snakeviz.cli.main(["out.prof"])
    os.remove("out.prof")

elif sys.argv[1] == "build":  # TODO: improve
    subprocess.run(f"pyinstaller run.py --name spaceinv --add-data \"space_invaders\\assets{os.pathsep}assets\" -y --noconsole")
    shutil.make_archive("dist/spaceinv", "zip", "dist/spaceinv")
    shutil.rmtree("__pycache__", True)

elif sys.argv[1] == "clean":
    shutil.rmtree("build")
    shutil.rmtree("dist")
    os.remove("spaceinv.spec")
