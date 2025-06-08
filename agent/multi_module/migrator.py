import os
from agent import pom_parser, gradle_writer, git_handler, builder, detector
from agent.utils.xml_utils import detect_modules
from agent.multi_module import parser as mm_parser, gradle_writer as mm_writer
import agent.gradle_writer as gw
print("✅ Using gradle_writer from:", gw.__file__)
def migrate_multi_module_project(root_path):
    """
    Converts a multi-module Maven project to Gradle by generating build.gradle and settings.gradle
    """
    print("🔍 Checking for multi-module structure...")

    modules = detect_modules(os.path.join(root_path, "pom.xml"))
    if not modules:
        print("ℹ No submodules found. Skipping multi-module migration.")
        return False

    print(f"📦 Detected submodules: {modules}")

    all_modules = {"root": root_path, **{m: os.path.join(root_path, m) for m in modules}}
    all_deps = {}

    for name, path in all_modules.items():
        pom = os.path.join(path, "pom.xml")
        if not os.path.exists(pom):
            print(f"⚠ Missing pom.xml in {name}. Skipping...")
            continue
        deps = pom_parser.parse_dependencies(pom)
        all_deps[name] = deps

    # Write settings.gradle (list all submodules)
    mm_writer.write_settings_gradle(modules, os.path.join(root_path, "settings.gradle"))
    print("✅ settings.gradle written.")

    # Write build.gradle for each module, with internal project dependency resolution
    for name, deps in all_deps.items():
        target_path = os.path.join(all_modules[name], "build.gradle")

        if name == "root":
            main_class = detector.extract_main_class(
                os.path.join(root_path, "pom.xml"),
                os.path.join(root_path, "src", "main", "java")
            )
            gradle_writer.write_build_gradle(deps, target_path, main_class=main_class, known_modules=modules)
        else:
            gradle_writer.write_build_gradle(deps, target_path, known_modules=modules)

        print(f"✅ build.gradle written for {name}")

    return True

def migrate(repo_dir, branch, base_branch):
    """
    Wrapper for full multi-module migration including Git, build, and PR.
    """
    git_handler.create_branch(repo_dir, branch)

    success = migrate_multi_module_project(repo_dir)
    if not success:
        print("❌ Failed to process multi-module project.")
        return

    builder.ensure_gradle_wrapper(repo_dir)

    # Collect files to commit
    files_to_commit = [
        "settings.gradle",
        "gradlew", "gradlew.bat",
        "gradle/wrapper/gradle-wrapper.jar",
        "gradle/wrapper/gradle-wrapper.properties"
    ]

    # Collect all submodule build.gradle paths
    modules = detect_modules(os.path.join(repo_dir, "pom.xml"))
    all_paths = [repo_dir] + [os.path.join(repo_dir, m) for m in modules]
    for p in all_paths:
        gradle_file = os.path.join(p, "build.gradle")
        if os.path.exists(gradle_file):
            files_to_commit.append(os.path.relpath(gradle_file, start=repo_dir))

    git_handler.commit_and_push(repo_dir, branch, "Initial multi-module Gradle build files", files_to_commit)

    if builder.run_gradle_build(repo_dir):
        if not git_handler.pull_request_exists(branch, base_branch):
            git_handler.create_pull_request(branch, base_branch, "Migrate to Gradle (multi-module)", "Automated migration.")
        print("✅ Multi-module migration completed and PR created.")
    else:
        print("❌ Gradle build failed for multi-module project.")