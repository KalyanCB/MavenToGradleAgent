import os
from lxml import etree


def extract_main_class(pom_path, src_dir):
    """Attempts to extract the fully qualified main class name."""
    if not os.path.isdir(src_dir):
        return None

    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".java"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r") as f:
                        content = f.read()
                        if "public static void main" in content:
                            rel_path = os.path.relpath(path, src_dir)
                            class_name = rel_path.replace(os.sep, ".").replace(".java", "")
                            return class_name
                except Exception:
                    continue
    return None


def detect_modules(pom_path, return_absolute=False):
    """Returns the list of module directories from a Maven root pom.xml."""
    if not os.path.exists(pom_path):
        raise FileNotFoundError(f"Missing pom.xml: {pom_path}")

    tree = etree.parse(pom_path)
    root = tree.getroot()

    ns = root.nsmap.get(None)
    nsmap = {"m": ns} if ns else {}

    modules = root.xpath("//m:modules/m:module", namespaces=nsmap)
    mod_list = [mod.text.strip() for mod in modules if mod.text]

    if return_absolute:
        base_dir = os.path.dirname(os.path.abspath(pom_path))
        abs_modules = [
            os.path.abspath(os.path.join(base_dir, mod))
            for mod in mod_list
        ]
        return [mod for mod in abs_modules if os.path.isdir(mod)]

    return mod_list


def is_multi_module(pom_path):
    """Returns True if the project has <modules> defined."""
    return len(detect_modules(pom_path)) > 0


if __name__ == "__main__":
    root_pom = "repo/pom.xml"
    print("📦 Detected modules:")
    try:
        for m in detect_modules(root_pom):
            print(f"- {m}")
    except Exception as e:
        print(f"❌ Error: {e}")