# - - - - - - - - IN-BUILT IMPORTS
import os, platform, json
import subprocess
from traceback import format_exc
from distutils.dir_util import copy_tree
from shutil import rmtree, copy2
from datetime import datetime

# - - - - - - - - CLASS LIBRARY
class Compiler:

    @staticmethod
    def collect_files(folder_path):
        """Collects relevant python script files.

        Args:
            folder_path (str): Root directory to collect_files.

        Returns:
            list(str): List of absolute file paths.

        """
        files = []
        # Ignore the current file, and files named '__init__.py'. Add other names if required.
        ignore_list = (os.path.basename(__file__), "__init__.py", "local", "bin")

        if os.path.isdir(folder_path):
            for file in os.listdir(folder_path):
                abs_path = os.path.join(folder_path, file)
                # ignore from ignore_list.
                if not file in ignore_list and file.endswith(".py"):
                    files.append(abs_path)
                # Recursiion for sub-folders
                elif os.path.isdir(abs_path) and file.lower() not in ignore_list:
                    files += Compiler.collect_files(abs_path)
        
        return files
    
    @staticmethod
    def Build(filename, source_folder = "", copy_target = "", export_folder = "bin"):
        """Collects and compiles project files into a dll.

        Args:
            filename (str): Name of final output (.dll) file.
            source_folder (str): (optional) Folder to collect files from.
            copy_target (str) : (optional) File path to where the output needs to be copied.
            export_folder (str): Subfolder for output file.

        Returns:
            (bool) True if successful, False otherwise.

        """
        folder_name = os.path.dirname(os.path.abspath(__file__))
        source_folder = os.path.join(folder_name, source_folder)
        target_folder = os.path.join(folder_name, export_folder)
        target_file = os.path.join(target_folder, filename)

        # Create export folder.
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        
        # Collect necessary files from project folder.
        program_files = Compiler.collect_files(source_folder)
        print("\nCollected {} files".format(len(program_files)))

        try:
            from clr import CompileModules
            CompileModules(target_file, *program_files)
            print("BUILD SUCCESSFUL\nTarget: {}\n".format(target_file))
            
            # Copy output file to user specified location.
            if copy_target:
                if not os.path.exists(copy_target):
                    os.makedirs(copy_target)
                copy2(target_file, copy_target)
                print("COPY SUCCESSFUL\n")
            
            return True

        except ImportError:
            print("\nBUILD FAILED\n\nPlease run the script using IronPython.\nRefer docstrings for more information.\n")

        except Exception as ex:
            print("\nBUILD FAILED\n")
            print(format_exc())
            print(str(ex))
            return False


class Application:

    SETTINGS_FILE = "maghpy_settings.json"
    SETTINGS_DATA = {
                        "IRONPYTHONPATH": r"C:\Program Files\Python\IronPython27\ipy.exe",
                        "RHINOPATH"    : r"C:\Program Files\Rhino 7\System\Rhino.exe",
                        "PLUGINPATH"   : os.path.join(os.environ["APPDATA"], "Grasshopper", "Libraries"),
                        "BUILDPATH"    : os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin"),
                    }

    @staticmethod
    def show(color="RED", tag="INFO", message="This is a console message."):
        ansi_colors =   {  
                            "RED"    : u"\u001b[31m" ,
                            "GREEN"  : u"\u001b[32m" ,
                            "YELLOW" : u"\u001b[33m" ,
                            "BLUE"   : u"\u001b[34m" ,
                            "MAGENTA": u"\u001b[35m" ,
                            "CYAN"   : u"\u001b[36m" ,
                            "DEFAULT": u"\u001b[0m"  ,
                        }
        status_message = u'{}<{}> {}{}'.format(ansi_colors[color], tag, ansi_colors["DEFAULT"], message);
        print(status_message)

    @staticmethod
    def find_config():
        config_data = {}
        current_directory = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_directory, Application.SETTINGS_FILE)

        # Create settings file if not found.
        found = Application.SETTINGS_FILE in os.listdir(current_directory) 
        if not found:
            Application.show("GREEN", "LOG", "'{}' created successfully. Relaunch application to continue.".format(Application.SETTINGS_FILE))
            with open(file_path, 'w') as file:
                json.dump(Application.SETTINGS_DATA, file, indent=2, ensure_ascii=False)

        else:
            with open(file_path, 'r') as file:
                config_data = json.load(file)

        return found, config_data

    def __init__(self):
        self.OS = platform.system()
        # Clean Screen
        self.clear()

        # Application will not run if the settings file was freshly created.
        self.is_ready, self.config_data = Application.find_config()

    def clear(self):
        if self.OS == "Darwin":
            os.system("clear")
        elif self.OS == "Windows":
            os.system("cls")
        else:
            self.show("RED", "ERROR", "Unrecognised Operating System.")

    def launch_rhino(self, launch_grasshopper = False):

        if self.is_ready:
            Application.show("GREEN", "LOG", "Launching Rhino...")
            cmd = '"{}" /nosplash'.format(self.config_data["RHINOPATH"])
            if launch_grasshopper:
                Application.show("GREEN", "LOG", "Launching Grasshopper...")
                cmd +=  '/runscript="_-Grasshopper Banner Disable Window Load Window Show _Enter"'
            result = subprocess.call(cmd)
            Application.show("GREEN", "LOG", "Exiting Rhino...")
            return result
        else:
            Application.show("RED", "ERROR", "Application is not ready. Relaunch and continue.")

    def kill_rhino(self):
        if self.OS == "Windows":
            command = r"taskkill /im Rhino.exe /t /f"
            
        Application.show("GREEN", "LOG", "Terminating Rhino.exe")
        os.system(command)
        return

    def compile_plugin(self):
        # Copy python-package pre-build.
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        package_source = os.path.join(root, 'python-package', 'src', 'tapir_py')
        package_target = os.path.join(root, 'grasshopper-plugin', 'src', 'tapir_py')
        if os.path.exists(package_source):
            copy_tree(package_source, package_target)
            # TODO: Refactor
            # Generate Unique Name 
            package_name = datetime.now().strftime("tapir_gh_%Y_%b_%d-%H_%M_%S.ghpy")
                        
            # Build grasshopper-plugin.
            copy_target = self.config_data["BUILDPATH"]
            Compiler.Build(package_name, source_folder='src', copy_target=copy_target)
            # Clean up post-build
            rmtree(package_target)
        else:
            Application.show("RED", "ERROR", "Build Failed. 'tapir_py' package not found.")
            #print("\nBUILD FAILED\n'tapir_py' package not found.\n")

            return
    
    def build(self):
        command = "{} {} {}".format(self.config_data["IRONPYTHONPATH"], os.path.abspath(__file__), self.config_data["BUILDPATH"])

        subprocess.call(command)
        

if __name__ == "__main__":

    app = Application()
    app.build()
    print("")