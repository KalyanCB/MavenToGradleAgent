import os
from lxml import etree

def extract_main_class(pom_path, src_dir):
    """
    Tries to infer the fully qualified main class name from pom.xml and source path.
    This is a naive implementation — it looks for a class with a `public static void main`.

    Args:
        pom_path (str): Path to pom.xml (not used yet).
        src_dir (str): Path to src/main/java

    Returns:
        str or None: Fully qualified main class name
    """
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
                            class_name = rel_path.replace("/", ".").replace("\\", ".").replace(".java", "")
                            return class_name
                except Exception:
                    continue
    return None

def detect_modules(pom_path, return_absolute=False):
    """
    Parses a Maven root pom.xml and returns the list of module directories.

    Args:
        pom_path (str): Path to the root pom.xml.
        return_absolute (bool): Whether to return absolute paths for the modules.

    Returns:
        List[str]: List of module names or paths.
    """
    if not os.path.exists(pom_path):
        raise FileNotFoundError(f"Missing pom.xml: {pom_path}")

    tree = etree.parse(pom_path)
    root = tree.getroot()

    # Handle default namespace
    ns = root.nsmap.get(None)
    nsmap = {"m": ns} if ns else {}

    modules = root.xpath("//m:modules/m:module", namespaces=nsmap)
    mod_list = [mod.text.strip() for mod in modules if mod.text]

    if return_absolute:
        base_dir = os.path.dirname(os.path.abspath(pom_path))
        return [os.path.abspath(os.path.join(base_dir, mod)) for mod in mod_list]

    return mod_list

if __name__ == "__main__":
    root_pom = "repo/pom.xml"
    print("📦 Detected modules:")
    try:
        for m in detect_modules(root_pom):
            print(f"- {m}")
    except Exception as e:
        print(f"❌ Error: {e}")