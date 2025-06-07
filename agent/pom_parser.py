import xml.etree.ElementTree as ET

def parse_dependencies(pom_path):
    tree = ET.parse(pom_path)
    root = tree.getroot()
    ns = {'m': 'http://maven.apache.org/POM/4.0.0'}

    # Extract properties for placeholder resolution
    properties = {}
    for prop in root.findall(".//m:properties/*", ns):
        properties[prop.tag.replace(f"{{{ns['m']}}}", "")] = prop.text

    deps = []
    for dep in root.findall(".//m:dependencies/m:dependency", ns):
        group_id = dep.find("m:groupId", ns)
        artifact_id = dep.find("m:artifactId", ns)
        version_elem = dep.find("m:version", ns)
        scope_elem = dep.find("m:scope", ns)

        # Skip test/provided scope
        if scope_elem is not None and scope_elem.text in ["test", "provided"]:
            continue

        group = group_id.text if group_id is not None else ""
        artifact = artifact_id.text if artifact_id is not None else ""
        version = version_elem.text if version_elem is not None else None

        # Resolve version from properties if placeholder used
        if version and version.startswith("${") and version.endswith("}"):
            prop_key = version[2:-1]
            version = properties.get(prop_key, version)  # fallback to placeholder

        deps.append((group, artifact, version))

    return deps