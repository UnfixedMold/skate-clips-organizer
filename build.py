import subprocess
from paths import ICON_ICO

script_name = "app.py"
output_name = "OrganizeClips.exe"

subprocess.run([
    "pyinstaller",
    "--onefile",
    "--noconsole",
    "--name", output_name,
    "--add-data", "sort_config.json;.",
    "--add-data", "icons;icons",
    "--icon", ICON_ICO,
    script_name
], check=True)
