import subprocess

script_name = "app.py"
output_name = "OrganizeClips.exe"

subprocess.run([
    "pyinstaller",
    "--onefile",
    "--noconsole",
    "--name", output_name,
    "--add-data", "sort_config.json;.",
    script_name
], check=True)
