import subprocess
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]

    env_path = repo_root / "ingestion-api" / ".env"

    if not env_path.exists():
        print(f"❌ .env not found at: {env_path}")
        return 1

    print(f"Loading env from: {env_path}")
    load_dotenv(env_path, override=True)

    # debug print (safe)
    print("DB_USER =", os.getenv("DB_USER"))
    print("DB_HOST =", os.getenv("DB_HOST"))
    print("DB_PORT =", os.getenv("DB_PORT"))
    print("DB_NAME =", os.getenv("DB_NAME"))
    print("DB_PASSWORD loaded:", bool(os.getenv("DB_PASSWORD")))

    env = os.environ.copy()

    cmd = ["dbt"] + sys.argv[1:] + ["--profiles-dir", "."]
    print("Running:", " ".join(cmd))

    return subprocess.call(cmd, env=env)

if __name__ == "__main__":
    raise SystemExit(main())
