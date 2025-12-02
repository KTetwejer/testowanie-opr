import subprocess
import sys


def main():
    result = subprocess.run(
        [sys.executable, "-m", "pytest"],
        capture_output=False,
        text=True,
    )
    if result.returncode == 0:
        print("All tests passed")
    else:
        print("Tests failed")
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()

