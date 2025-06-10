import xml.etree.ElementTree as ET

def parse_dependencies(pom_path):
    tree = ET.parse(pom_path)
    root = tree.getroot()
    ns = {'m': 'http://maven.apache.org/POM/4.0.0'}

    properties = {}
    for prop in root.findall(".//m:properties/*", ns):
        key = prop.tag.replace(f"{{{ns['m']}}}", "")
        properties[key] = prop.text

    deps = []
    for dep in root.findall(".//m:dependencies/m:dependency", ns):
        group_id = dep.find("m:groupId", ns)
        artifact_id = dep.find("m:artifactId", ns)
        version_elem = dep.find("m:version", ns)
        scope_elem = dep.find("m:scope", ns)

        group = group_id.text if group_id is not None else ""
        artifact = artifact_id.text if artifact_id is not None else ""
        version = version_elem.text if version_elem is not None else None
        scope = scope_elem.text if scope_elem is not None else None

        if version and version.startswith("${") and version.endswith("}"):
            prop_key = version[2:-1]
            version = properties.get(prop_key, version)

        deps.append((group, artifact, version, scope))

    return deps, properties

def parse_dependency_management(pom_path):
    tree = ET.parse(pom_path)
    root = tree.getroot()
    ns = {'m': 'http://maven.apache.org/POM/4.0.0'}

    dm_versions = {}
    for dep in root.findall(".//m:dependencyManagement//m:dependency", ns):
        group_id = dep.find("m:groupId", ns)
        artifact_id = dep.find("m:artifactId", ns)
        version_elem = dep.find("m:version", ns)

        if group_id is not None and artifact_id is not None and version_elem is not None:
            key = f"{group_id.text}:{artifact_id.text}"
            dm_versions[key] = version_elem.text

    return dm_versions

def parse_plugin_management(pom_path):
    tree = ET.parse(pom_path)
    root = tree.getroot()
    ns = {'m': 'http://maven.apache.org/POM/4.0.0'}

    plugins = {}
    for plugin in root.findall(".//m:pluginManagement//m:plugin", ns):
        group_id = plugin.find("m:groupId", ns)
        artifact_id = plugin.find("m:artifactId", ns)
        version_elem = plugin.find("m:version", ns)

        group = group_id.text if group_id is not None else "org.apache.maven.plugins"
        artifact = artifact_id.text if artifact_id is not None else None
        version = version_elem.text if version_elem is not None else None

        if artifact and version:
            plugins[f"{group}:{artifact}"] = version

    return plugins

def parse_build_plugins(pom_path):
    tree = ET.parse(pom_path)
    root = tree.getroot()
    ns = {'m': 'http://maven.apache.org/POM/4.0.0'}

    plugins = []
    for plugin in root.findall(".//m:build/m:plugins/m:plugin", ns):
        plugin_data = {
            "groupId": plugin.findtext("m:groupId", default="org.apache.maven.plugins", namespaces=ns),
            "artifactId": plugin.findtext("m:artifactId", default="", namespaces=ns),
            "version": plugin.findtext("m:version", default=None, namespaces=ns),
            "configuration": {},
            "executions": []
        }

        config_elem = plugin.find("m:configuration", ns)
        config = {}
        if config_elem is not None:
            for child in config_elem:
                tag = child.tag.replace(f"{{{ns['m']}}}", "")
                config[tag] = child.text

            # Special handling for nested manifest -> mainClass in maven-jar-plugin
            archive = config_elem.find("m:archive", ns)
            if archive is not None:
                manifest = archive.find("m:manifest", ns)
                if manifest is not None:
                    main_class_elem = manifest.find("m:mainClass", ns)
                    if main_class_elem is not None:
                        config["mainClass"] = main_class_elem.text

        plugin_data["configuration"] = config

        for execution in plugin.findall("m:executions/m:execution", ns):
            execution_data = {
                "id": execution.findtext("m:id", default="", namespaces=ns),
                "phase": execution.findtext("m:phase", default="", namespaces=ns),
                "goals": [goal.text for goal in execution.findall("m:goals/m:goal", ns)]
            }
            plugin_data["executions"].append(execution_data)

        plugins.append(plugin_data)

    return plugins