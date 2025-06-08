import os
from lxml import etree

def is_multi_module(pom_path):
    """
    Returns True if the pom.xml includes any <modules>...</modules>
    """
    if not os.path.exists(pom_path):
        return False

    tree = etree.parse(pom_path)
    root = tree.getroot()
    ns = root.nsmap.get(None)
    nsmap = {"m": ns} if ns else {}

    return bool(root.xpath("//m:modules/m:module", namespaces=nsmap))

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