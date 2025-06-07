import os
import subprocess
import platform
from pathlib import Path

_last_error = ""
MAX_ATTEMPTS = 3
LOG_FILE = "gradle_build.log"

def ensure_gradle_wrapper(path):
    gradlew_name = "gradlew.bat" if platform.system() == "Windows" else "gradlew"
    gradlew_path = Path(path) / gradlew_name

    if not gradlew_path.exists():
        print("📦 Gradle wrapper not found. Generating...")
        try:
            result = subprocess.run(["gradle", "wrapper"], cwd=path, check=True, capture_output=True, text=True)
            print(result.stdout)
            if not gradlew_path.exists():
                raise RuntimeError("Gradle wrapper generation failed: gradlew not found.")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to generate Gradle wrapper:\n{e.stderr.strip()}")

    if platform.system() != "Windows":
        subprocess.run(["chmod", "+x", str(gradlew_path)], check=True)

    return gradlew_path


def run_gradle_tasks(path="repo", tasks=None):
    global _last_error
    tasks = tasks or ["clean", "build", "test"]
    gradlew = ensure_gradle_wrapper(path)

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"🔧 Attempt {attempt}: Running `{gradlew} {' '.join(tasks)}`...")
        try:
            result = subprocess.run(
                ["./gradlew"] + tasks + ["--stacktrace", "--debug"],
                cwd=path,
                capture_output=True,
                text=True
            )

            log_file = Path(path) / LOG_FILE
            print(f"📄 Writing log to: {log_file}")
            with open(log_file, "w") as log:
                log.write(result.stdout)
                log.write("\n--- STDERR ---\n")
                log.write(result.stderr)

            # PRINT THE ERROR TO CONSOLE
            print("🔍 Short STDERR:")
            print(result.stderr[:500])  # print only first 500 chars

            if result.returncode == 0:
                print("✅ Gradle tasks completed successfully.")
                return True

            else:
                print(f"❌ Task failed. Retrying... ({attempt}/{MAX_ATTEMPTS})")
                _last_error = result.stderr + "\n" + result.stdout

        except Exception as e:
            _last_error = f"Exception during build: {str(e)}"
            print("❌ Exception during subprocess:", _last_error)
            return False

    print(f"📄 Check detailed logs at {log_file}")
    return False


def run_gradle_build(path="repo"):
    return run_gradle_tasks(path, ["clean", "build", "test"])


def get_last_error():
    return _last_error