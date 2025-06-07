# agent/multi_module/migrator.py

import os
from agent import detector, pom_parser, gradle_writer
from agent.multi_module import parser as mm_parser, gradle_writer as mm_writer

def migrate_multi_module_project(root_path):
    print("🔍 Checking for multi-module structure...")

    modules = detector.detect_modules(os.path.join(root_path, "pom.xml"))
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

    # Write settings.gradle
    mm_writer.write_settings_gradle(modules, os.path.join(root_path, "settings.gradle"))
    print("✅ settings.gradle written.")

    # Write build.gradle for each module
    for name, deps in all_deps.items():
        target_path = os.path.join(all_modules[name], "build.gradle")
        gradle_writer.write_build_gradle(deps, target_path)
        print(f"✅ build.gradle written for {name}")

    return True
