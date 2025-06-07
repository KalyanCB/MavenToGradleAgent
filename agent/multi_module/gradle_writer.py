import os

def write_settings_gradle(modules, output_path):
    lines = ["rootProject.name = 'multi-module-project'"]
    for module in modules:
        lines.append(f"include('{module}')")

    with open(output_path, "w") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    # Example usage
    modules = ["core", "service", "web"]
    write_settings_gradle(modules, "repo/settings.gradle")
    print("✅ settings.gradle written with modules:", modules)