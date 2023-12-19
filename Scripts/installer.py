import platform
import subprocess
from Config.config import ScriptConfig
from Config.logs_config import setup_logging

logger = setup_logging(ScriptConfig.SCRIPT_FILENAME, ScriptConfig.SCRIPT_LOG_PATH)
class Scripts:
    def run_linux_script(self):
        # Run the linux script
        subprocess.run(['./' + {ScriptConfig.linux_script}])

    def run_windows_script(self):
        # Run the windows script
        subprocess.run(['powershell.exe', '-File', ScriptConfig.windows_script])

    def main(self):
        # Get the operating system
        operating_system = platform.system().lower()
        print(f"Operating system: {operating_system}")
        # Run the appropriate script based on the operating system
        if operating_system == 'linux':
            self.run_linux_script()
        elif operating_system == 'windows':
            self.run_windows_script()
        else:
            print(f"Unsupported operating system: {operating_system}")


