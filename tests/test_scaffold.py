from config import DATA_DIR, LOGS_DIR, OUTPUT_DIR, PROJECT_ROOT
def test_required_project_directories_exist():
    for directory in (DATA_DIR, LOGS_DIR, OUTPUT_DIR): assert directory.exists() and directory.is_dir()
def test_environment_template_exists(): assert (PROJECT_ROOT/".env.example").is_file()
def test_cli_entrypoint_exists(): assert (PROJECT_ROOT/"main.py").is_file()
