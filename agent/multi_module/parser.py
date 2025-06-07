import os
from agent.pom_parser import parse_dependencies


def parse_all_modules(repo_root, module_names):
    module_deps = {}
    for module in module_names:
        pom_path = os.path.join(repo_root, module, "pom.xml")
        if os.path.exists(pom_path):
            try:
                deps = parse_dependencies(pom_path)
                module_deps[module] = deps
            except Exception as e:
                print(f"❌ Failed to parse {module}/pom.xml: {e}")
        else:
            print(f"⚠ No pom.xml found for module: {module}")
    return module_deps


if __name__ == "__main__":
    repo_root = "repo"
    modules = ["core", "service", "web"]  # Example
    all_deps = parse_all_modules(repo_root, modules)
    for mod, deps in all_deps.items():
        print(f"\n📦 Module: {mod}")
        for group, artifact, version in deps:
            print(f"  - {group}:{artifact}:{version or ''}")