import os
from agent import git_handler, pom_parser, gradle_writer, builder, fixer
from agent.multi_module import detector, migrator  # <-- Add this
from agent.utils import xml_utils  # for parsing modules from pom.xml


def run_migration():
    print("🚀 Starting Maven to Gradle AI agent...")

    repo_dir = "repo"
    branch = os.getenv("FEATURE_BRANCH_NAME", "gradle-migration")
    base_branch = os.getenv("BASE_BRANCH_NAME", "main")

    # 1. Clone the GitHub repository
    git_handler.clone_repo(repo_dir)

    # 2. Check for multi-module project
    pom_path = os.path.join(repo_dir, "pom.xml")
    if detector.is_multi_module(pom_path):
        print("📦 Detected multi-module Maven project.")
        migrator.migrate(repo_dir, branch, base_branch)
        return

    # ---- Single-module logic continues here ----

    src_path = os.path.join(repo_dir, "src", "main", "java")
    deps = pom_parser.parse_dependencies(pom_path)

    # 3. Attempt to extract main class
    main_class = detector.extract_main_class(pom_path, src_path)

    # 4. Create feature branch
    git_handler.create_branch(repo_dir, branch)

    # 5. Generate Gradle files
    gradle_path = os.path.join(repo_dir, "build.gradle")
    settings_path = os.path.join(repo_dir, "settings.gradle")
    gitignore_path = os.path.join(repo_dir, ".gitignore")

    project_name = os.path.basename(os.path.abspath(repo_dir))
    gradle_writer.write_build_gradle(deps, gradle_path, main_class)
    gradle_writer.write_settings_gradle(settings_path, project_name)
    gradle_writer.write_gitignore(gitignore_path)

    # 6. Generate Gradle wrapper (fail fast if build.gradle is broken)
    builder.ensure_gradle_wrapper(repo_dir)

    # 7. Commit all Gradle-related files including wrapper
    files_to_commit = [
        "build.gradle", "settings.gradle", ".gitignore",
        "gradlew", "gradlew.bat", "gradle/wrapper/gradle-wrapper.jar", "gradle/wrapper/gradle-wrapper.properties"
    ]
    git_handler.commit_and_push(repo_dir, branch, "Initial Gradle build files", files_to_commit)

    # 8. Run Gradle build and retry if needed
    success = builder.run_gradle_build(repo_dir)
    attempts = 0

    while not success and attempts < 3:
        print(f"🔁 Build failed. Attempt {attempts + 1}/3. Asking OpenAI...")
        error = builder.get_last_error()

        with open(pom_path) as f:
            pom_xml = f.read()
        with open(gradle_path) as f:
            build_gradle = f.read()

        fixed = fixer.fix_build_gradle(pom_xml, build_gradle, error)
        gradle_writer.write_fixed(gradle_path, fixed)
        git_handler.commit_and_push(repo_dir, branch, "Fix build.gradle using AI", ["build.gradle"])

        success = builder.run_gradle_build(repo_dir)
        attempts += 1

    # 9. Create pull request if build was successful
    if success:
        if not git_handler.pull_request_exists(branch, base_branch):
            git_handler.create_pull_request(branch, base_branch, "Migrate to Gradle", "Automated migration.")
        print("✅ Migration completed and PR created.")
    else:
        print("❌ Migration failed after retries.")