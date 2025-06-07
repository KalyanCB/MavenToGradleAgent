import os
from lxml import etree

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