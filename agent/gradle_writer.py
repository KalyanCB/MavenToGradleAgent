import os
from agent.logger import log_success

def remove_utf8_bom(filepath):
    with open(filepath, 'rb') as f:
        content = f.read()
    if content.startswith(b'\xef\xbb\xbf'):
        print("\u26a0\ufe0f BOM found. Removing from build.gradle.")
        content = content[3:]
        with open(filepath, 'wb') as f:
            f.write(content)

def write_build_gradle(
    deps,
    output_path,
    main_class=None,
    known_modules=None,
    properties=None,
    plugin_versions=None,
    build_plugins=None
):
    known_modules = known_modules or []
    properties = properties or {}
    plugin_versions = plugin_versions or {}
    build_plugins = build_plugins or []

    DEFAULT_VERSIONS = {
        "spring-boot-starter-web": "3.2.5",
        "spring-boot-starter": "3.2.5",
        "spring-boot-starter-test": "3.2.5",
        "spring-boot-starter-data-jpa": "3.2.5",
        "spring-boot-devtools": "3.2.5"
    }

    SCOPE_MAP = {
        "compile": "implementation",
        "runtime": "runtimeOnly",
        "test": "testImplementation",
        "provided": "compileOnly"
    }

    if not main_class:
        for plugin in build_plugins:
            if plugin.get("artifactId") == "maven-jar-plugin":
                jar_config = plugin.get("configuration", {})
                try:
                    archive = jar_config.get("archive", {})
                    manifest = archive.get("manifest", {})
                    main_class = manifest.get("mainClass")
                    if main_class:
                        print(f"\u2139\ufe0f  Extracted mainClass from maven-jar-plugin: {main_class}")
                except Exception as e:
                    print(f"\u26a0\ufe0f Failed to extract mainClass from jar plugin config: {e}")
                break

    lines = ["plugins {"]
    lines.append("    id 'java'")
    if main_class:
        lines.append("    id 'application'")

    if "org.springframework.boot:spring-boot-gradle-plugin" in plugin_versions:
        spring_boot_version = plugin_versions["org.springframework.boot:spring-boot-gradle-plugin"]
        lines.append(f"    id 'org.springframework.boot' version '{spring_boot_version}'")
    elif any(p.get("artifactId") == "spring-boot-maven-plugin" for p in build_plugins):
        lines.append("    id 'org.springframework.boot'")
        print("\u2139\ufe0f Detected spring-boot-maven-plugin, applying Gradle equivalent")

    lines.append("}")

    filtered_properties = {k: v for k, v in properties.items() if k not in {"version", "group", "name"}}
    if filtered_properties:
        lines += ["", "ext {"]
        for k, v in filtered_properties.items():
            safe_key = k.replace(".", "_").replace("-", "_")
            if k != safe_key:
                print(f"\u2139\ufe0f  Renamed property key: {k} → {safe_key}")
            lines.append(f"    {safe_key} = '{v}'")
        lines.append("}")

    lines += [
        "",
        "repositories {",
        "    mavenCentral()",
        "}",
        "",
        "dependencies {"
    ]

    for group, artifact, version, scope in deps:
        if artifact in known_modules:
            lines.append(f"    implementation project(':{artifact}')")
            continue

        config = SCOPE_MAP.get(scope or "compile", "implementation")

        if version and version.startswith("${") and version.endswith("}"):
            prop_key = version[2:-1]
            version = properties.get(prop_key, DEFAULT_VERSIONS.get(artifact))
            if not version:
                print(f"\u26a0\ufe0f  Unresolved version for property {prop_key} used in {group}:{artifact}")

        if not version:
            version = DEFAULT_VERSIONS.get(artifact)
            if version:
                print(f"\u2139\ufe0f  Using default version '{version}' for {artifact}")
            else:
                version = "3.2.5"
                print(f"\u26a0\ufe0f  No specific version for {artifact}, using fallback version: {version}")

        lines.append(f"    {config} '{group}:{artifact}:{version}'")

    lines.append("}")

    if main_class:
        lines += [
            "",
            "application {",
            f"    mainClass = '{main_class}'",
            "}",
            "",
            "springBoot {",
            f"    mainClass = '{main_class}'",
            "}"
        ]

    lines += ["", "// Plugin-specific Gradle configuration"]
    for plugin in build_plugins:
        ga = f"{plugin.get('groupId')}:{plugin.get('artifactId')}"
        version = plugin.get("version")
        config = plugin.get("configuration", {})
        if isinstance(config, str):
            config = {}

        if plugin["artifactId"] == "maven-compiler-plugin":
            source = config.get("source", properties.get("java.version", "11"))
            target = config.get("target", properties.get("java.version", "11"))
            lines += [
                "tasks.withType(JavaCompile) {",
                f"    sourceCompatibility = '{source}'",
                f"    targetCompatibility = '{target}'",
                "}"
            ]

        elif plugin["artifactId"] == "maven-surefire-plugin":
            lines += [
                "test {",
                "    useJUnitPlatform()",
                "    // Additional test options can go here",
                "}"
            ]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines).strip() + "\n")

    remove_utf8_bom(output_path)
    log_success(f"\u2705 build.gradle written at {output_path}")

def write_settings_gradle(modules, output_path):
    """
    Writes a settings.gradle file including root project name and submodules.
    """
    root_project_name = os.path.basename(os.path.abspath(os.path.dirname(output_path)))
    lines = ["// Auto-generated by MavenToGradleAgent"]
    lines.append(f"rootProject.name = '{root_project_name}'")

    for module in modules:
        lines.append(f"include('{module}')")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines).strip() + "\n")

    log_success(f"\u2705 settings.gradle written at {output_path} with modules: {modules}")

def write_fixed(path, content, backup=True):
    if backup and os.path.exists(path):
        os.rename(path, path + ".bak")
        print(f"\ud83d\uddd6\ufe0f Backup created at {path + '.bak'}")

    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content.strip() + "\n")

    log_success("\u2705 Fixed build.gradle written.")

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
    log_success("\u2705 .gitignore written.")
