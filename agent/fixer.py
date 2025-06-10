import os
import time
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def fix_build_gradle(pom_xml: str, build_gradle: str, error_log: str) -> str:
    """
    Use OpenAI to fix a broken build.gradle file based on the pom.xml and error logs.

    Args:
        pom_xml (str): Contents of the pom.xml file.
        build_gradle (str): Current contents of the build.gradle file.
        error_log (str): Output of the failed gradle build.

    Returns:
        str: Updated build.gradle content (or original if retries fail).
    """
    truncated_error_log = "\n".join(error_log.splitlines()[-300:])

    prompt = f"""
You are a Gradle and Java build expert.
Given the following Maven pom.xml:

<pom.xml>
{pom_xml}
</pom.xml>

And the current build.gradle:

<build.gradle>
{build_gradle}
</build.gradle>

The following Gradle build error occurred:

<error>
{truncated_error_log}
</error>

Please return the corrected build.gradle content to resolve the issue.
Only return the fixed build.gradle file content. No explanations or markdown formatting.
"""

    for attempt in range(3):
        try:
            response = openai.chat.completions.create(
                model="gpt-4-0125-preview",
                messages=[
                    {"role": "system", "content": "You are a Gradle and Maven build assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
            )
            content = response.choices[0].message.content.strip()

            if content.startswith("```"):
                lines = content.splitlines()
                lines = lines[1:] if lines[0].startswith("```") else lines
                lines = lines[:-1] if lines and lines[-1].endswith("```") else lines
                content = "\n".join(lines).strip()

            print(f"✅ Gradle fix received (attempt {attempt + 1})")
            return content

        except Exception as e:
            print(f"⚠️ OpenAI API attempt {attempt + 1} failed: {e}")
            time.sleep(2 ** attempt)

    print("❌ All attempts to fix build.gradle failed. Returning original.")
    return build_gradle


def attempt_fix(repo_dir: str):
    """
    Attempts to fix the root build.gradle file using OpenAI if Gradle build fails.
    """
    print("🔍 Attempting fix using OpenAI...")

    pom_path = os.path.join(repo_dir, "pom.xml")
    gradle_path = os.path.join(repo_dir, "build.gradle")
    log_path = os.path.join(repo_dir, "gradle_build.log")

    if not (os.path.exists(pom_path) and os.path.exists(gradle_path) and os.path.exists(log_path)):
        print("⚠️ Required files missing for fix attempt. Skipping.")
        return

    with open(pom_path, "r") as f:
        pom_xml = f.read()

    with open(gradle_path, "r") as f:
        gradle_content = f.read()

    with open(log_path, "r") as f:
        error_log = f.read()

    fixed_content = fix_build_gradle(pom_xml, gradle_content, error_log)

    if fixed_content != gradle_content:
        with open(gradle_path, "w") as f:
            f.write(fixed_content.strip() + "\n")
        print("✅ build.gradle updated with AI fix.")
    else:
        print("ℹ️ No change detected from the fixer.")


def fix_gradle_writer(pom_xml: str, gradle_writer_code: str, error_log: str) -> str:
    """
    Use OpenAI to fix the gradle_writer.py code so it generates correct build.gradle files.

    Args:
        pom_xml (str): Original pom.xml.
        gradle_writer_code (str): Contents of gradle_writer.py.
        error_log (str): Gradle error log caused by the generated build.gradle.

    Returns:
        str: Updated gradle_writer.py content.
    """
    truncated_error_log = "\n".join(error_log.splitlines()[-300:])

    prompt = f"""
You are a Gradle and Python build tooling expert.

The following Python script (`gradle_writer.py`) generates a Gradle build file from Maven pom.xml data.

The current pom.xml is:

<pom.xml>
{pom_xml}
</pom.xml>

The current Python code is:

<gradle_writer.py>
{gradle_writer_code}
</gradle_writer.py>

The generated build.gradle causes the following Gradle build error:

<error>
{truncated_error_log}
</error>

Please modify the Python code to ensure it generates a valid build.gradle.
Only return the full updated gradle_writer.py content, no explanations or markdown.
"""

    for attempt in range(3):
        try:
            response = openai.chat.completions.create(
                model="gpt-4-0125-preview",
                messages=[
                    {"role": "system", "content": "You are a Gradle and Python build assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
            )
            content = response.choices[0].message.content.strip()
            if content.startswith("```"):
                lines = content.splitlines()
                lines = lines[1:] if lines[0].startswith("```") else lines
                lines = lines[:-1] if lines[-1].endswith("```") else lines
                content = "\n".join(lines).strip()
            print(f"✅ gradle_writer.py fix received (attempt {attempt + 1})")
            return content

        except Exception as e:
            print(f"⚠️ OpenAI API attempt {attempt + 1} failed: {e}")
            time.sleep(2 ** attempt)

    print("❌ All attempts to fix gradle_writer.py failed. Returning original.")
    return gradle_writer_code


def attempt_fix_gradle_writer(repo_dir: str, agent_dir: str):
    """
    Attempts to fix gradle_writer.py using OpenAI if Gradle build fails.
    """
    print("🔍 Attempting to fix gradle_writer.py using LLM...")

    pom_path = os.path.join(repo_dir, "pom.xml")
    log_path = os.path.join(repo_dir, "gradle_build.log")
    writer_path = os.path.join(agent_dir, "gradle_writer.py")

    if not (os.path.exists(pom_path) and os.path.exists(log_path) and os.path.exists(writer_path)):
        print("⚠️ Required files missing for source fix attempt.")
        return

    with open(pom_path, "r") as f:
        pom_xml = f.read()

    with open(log_path, "r") as f:
        error_log = f.read()

    with open(writer_path, "r") as f:
        gradle_writer_code = f.read()

    updated_code = fix_gradle_writer(pom_xml, gradle_writer_code, error_log)

    if updated_code != gradle_writer_code:
        backup_path = writer_path + ".bak"
        os.rename(writer_path, backup_path)
        print(f"🛡️ Backup created: {backup_path}")
        with open(writer_path, "w") as f:
            f.write(updated_code.strip() + "\n")
        print("✅ gradle_writer.py updated successfully.")
    else:
        print("ℹ️ No change detected in gradle_writer.py.")