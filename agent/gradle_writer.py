import os
from agent.logger import log_success

def remove_utf8_bom(filepath):
    with open(filepath, 'rb') as f:
        content = f.read()
    if content.startswith(b'\xef\xbb\xbf'):
        print("⚠️ BOM found. Removing from build.gradle.")
        content = content[3:]
        with open(filepath, 'wb') as f:
            f.write(content)

def write_build_gradle(deps, output_path, main_class=None):
    """
    Generates a Groovy DSL-compliant build.gradle file.

    Args:
        deps (List[Tuple[str, str, Optional[str]]]): Maven dependencies as (group, artifact, version).
        output_path (str): File path to write build.gradle.
        main_class (Optional[str]): Fully qualified main class name, if available.
    """

    DEFAULT_VERSIONS = {
        "spring-boot-starter-web": "3.2.5",
        "spring-boot-starter": "3.2.5",
        "spring-boot-starter-test": "3.2.5",
        "spring-boot-starter-data-jpa": "3.2.5",
        "spring-boot-devtools": "3.2.5"
        # Add more default versions as needed
    }

    lines = [
        "plugins {",
        "    id 'java'",
        "    id 'application'",
        "}",
        "",
        "repositories {",
        "    mavenCentral()",
        "}",
        "",
        "dependencies {"
    ]

    for group, artifact, version in deps:
        if not version:
            version = DEFAULT_VERSIONS.get(artifact)
            if version:
                print(f"ℹ️  Using default version '{version}' for {artifact}")
            else:
                print(f"⚠️  No version found for {artifact}. You may need to add it manually.")
        if version:
            lines.append(f"    implementation '{group}:{artifact}:{version}'")
        else:
            lines.append(f"    implementation '{group}:{artifact}'")

    lines.append("}")

    if main_class:
        lines += [
            "",
            "application {",
            f"    mainClass = '{main_class}'",
            "}"
        ]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines).strip() + "\n")

    remove_utf8_bom(output_path)
    log_success("✅ build.gradle written.")

def write_fixed(path, content, backup=True):
    if backup and os.path.exists(path):
        os.rename(path, path + ".bak")
        print(f"📦 Backup created at {path + '.bak'}")

    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content.strip() + "\n")

    log_success("✅ Fixed build.gradle written.")

def write_settings_gradle(output_path, project_name):
    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"rootProject.name = '{project_name}'\n")
    log_success("✅ settings.gradle written.")

def write_gitignore(output_path):
    content = """
    # Gradle
    .gradle/
    build/
    !gradle-wrapper.jar

    # Java
    *.class

    # IntelliJ
    .idea/
    *.iml

    # Logs
    *.log
    """
    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content.strip() + "\n")
    log_success("✅ .gitignore written.")