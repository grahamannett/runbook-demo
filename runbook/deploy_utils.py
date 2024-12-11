import os
import subprocess


def check_db_exists():
    if not os.path.exists("reflex.db"):
        subprocess.run(["reflex", "db", "init"], check=True)
