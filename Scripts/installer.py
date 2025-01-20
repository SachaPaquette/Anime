import platform
import subprocess
import os
import ctypes  # Used for admin privilege checks on Windows
from Config.config import ScriptConfig
from Config.logs_config import setup_logging

# Configure the logger
logger = setup_logging(ScriptConfig.SCRIPT_FILENAME, ScriptConfig.SCRIPT_LOG_PATH)


class Scripts:
    def check_admin_privileges(self):
        """Check if the script is running with administrative privileges."""
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            is_admin = False
        if not is_admin:
            message = "This script must be run as an administrator."
            raise PermissionError(message)

    def ensure_chocolatey(self):
        """Ensure Chocolatey is installed and accessible."""
        try:
            subprocess.run(['choco', '--version'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            self.check_admin_privileges()
            
            self.install_chocolatey()

    def install_chocolatey(self):
        """Install Chocolatey on the system."""
        try:
            # Command to download and install Chocolatey
            install_command = (
                'Set-ExecutionPolicy Bypass -Scope Process -Force; '
                '[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; '
                'iex ((New-Object System.Net.WebClient).DownloadString(\'https://community.chocolatey.org/install.ps1\'))'
            )

            # Run the installation command using PowerShell
            subprocess.run(
                ['powershell.exe', '-Command', install_command],
                check=True
            )

            logger.info("Chocolatey has been installed successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install Chocolatey: {e}")
            raise Exception("Failed to install Chocolatey. Please try installing it manually.")

    def run_script(self):
        """Run the appropriate script based on the operating system."""
        if platform.system().lower() == 'linux':
            # Run the create environment script
            self.create_environment()
            # Run the Linux installation script
            subprocess.run(['bash', ScriptConfig.linux_script], check=True)
        elif platform.system().lower() == 'windows':
            # Ensure Chocolatey is installed
            self.ensure_chocolatey()

            # Run the create environment script
            self.create_environment()

            # Run the Windows installation script
            subprocess.run(['powershell.exe', '-File', ScriptConfig.windows_script], check=True)

            # Install curses for Windows
            self.install_python_package(ScriptConfig.windows_curse)
        else:
            raise Exception(f"Unsupported operating system: {platform.system().lower()}")

    def create_environment(self):
        """Create the virtual environment."""
        subprocess.run(['python', '-m', 'venv', ScriptConfig.venv_name], check=True)

    def install_python_package(self, package=None):
        """Install a Python package or all packages from requirements."""
        python_executable = (
            os.path.join(ScriptConfig.venv_name, 'Scripts', 'python.exe')
            if platform.system().lower() == 'windows'
            else os.path.join(ScriptConfig.venv_name, 'bin', 'python')
        )

        if package:
            subprocess.run([python_executable, '-m', 'pip', 'install', package], check=True)
        else:
            # Install all the required packages
            subprocess.run([python_executable, '-m', 'pip', 'install', '-r', ScriptConfig.requirements_file], check=True)

    def main(self):
        try:
            self.run_script()
        except PermissionError as e:
            print(f"Error: {e}")
        except subprocess.CalledProcessError as e:
            logger.error(f"A subprocess error occurred: {e}")
            print("Error: A critical step in the installation failed. Check the logs for details.")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            print(f"Error: {e}")


# Execute the script
if __name__ == "__main__":
    Scripts().main()
