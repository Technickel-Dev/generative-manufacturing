import subprocess
import os
import sys
from typing import Optional

class SlicerRunner:
    def __init__(self, slicer_path: Optional[str] = None):
        if slicer_path:
            self.slicer_path = slicer_path
        else:
            # Priority: Env Var -> System Path -> Windows Default
            env_path = os.getenv("PRUSA_SLICER_PATH")
            if env_path:
                self.slicer_path = env_path
            else:
                # Check for prusa-slicer in PATH (common on Linux)
                import shutil
                which_path = shutil.which("prusa-slicer")
                if which_path:
                    self.slicer_path = which_path
                else:
                    # Fallback to Windows default
                    self.slicer_path = r"C:\Program Files\Prusa3D\PrusaSlicer\prusa-slicer-console.exe"

    def _get_preset_args(self, intent: str) -> list[str]:
        """
        Maps a natural language intent to Slicer CLI arguments.
        Uses the official Vendor bundle and specific profile selection flags.
        """
        intent = intent.lower()
        args = []
        
        # Point to the official Vendor bundle
        # Check standard locations on both Windows and Linux/Mac to be robust
        potential_paths = []
        
        # Windows AppData
        if sys.platform == "win32" or os.getenv("APPDATA"):
            app_data = os.getenv("APPDATA")
            if app_data:
                potential_paths.append(os.path.join(app_data, "PrusaSlicer", "vendor", "PrusaResearch.ini"))
        
        # Linux/Mac XDG Config or Home
        config_home = os.getenv("XDG_CONFIG_HOME", os.path.join(os.path.expanduser("~"), ".config"))
        potential_paths.append(os.path.join(config_home, "PrusaSlicer", "vendor", "PrusaResearch.ini"))
        
        vendor_path = ""
        for path in potential_paths:
            if os.path.exists(path):
                vendor_path = path
                break
        
        if os.path.exists(vendor_path):
             args.extend(["--load", vendor_path])
             args.extend(["--printer-profile", "Prusa CORE One HF0.4 nozzle"])
             # Note: The official Core One profile includes M862.6 P"Input shaper" in start G-code.
             args.extend(["--material-profile", "Generic PLA @COREONE HF0.4"])
             
             # Default print profile
             print_profile = "0.20mm BALANCED @COREONE HF0.4"
             
             if "draft" in intent or "fast" in intent:
                  print_profile = "0.25mm DRAFT @COREONE HF0.4"
             elif "detail" in intent or "quality" in intent:
                  print_profile = "0.10mm DETAIL @COREONE HF0.4"
             
             args.extend(["--print-profile", print_profile])
             
        else:
             print(f"Warning: Vendor config not found at {vendor_path}. Slicing may fail or use defaults.")

        return args

    async def slice_file(self, stl_path: str, intent: str = "balanced", output_path: Optional[str] = None) -> str:
        """
        Slices the given STL file using PrusaSlicer CLI.
        Returns the path to the generated G-code file.
        """
        if not self.slicer_path:
            raise RuntimeError("PrusaSlicer executable not found")

        if not output_path:
            output_path = stl_path.replace(".stl", ".gcode")
        
        # Build command matches user verified structure:
        # & "executable" -g "file.stl" --output "output.gcode" --load "vendor.ini" ... --no-binary-gcode
        cmd = [
            self.slicer_path,
            "-g", stl_path,
            "--output", output_path
        ]
        
        preset_args = self._get_preset_args(intent)
        cmd.extend(preset_args)
        
        # Crucial flag identified by user to fix compatibility issues
        cmd.append("--no-binary-gcode")
        
        print(f"Executing: {' '.join(cmd)}")
        
        try:
            # Run the slicer
            process = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            print("Slicing output:", process.stdout)
            
            if os.path.exists(output_path):
                return output_path
            else:
                # Sometimes output filename differs based on format settings
                # Find the most recently created gcode file in the same directory
                directory = os.path.dirname(stl_path)
                files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".gcode")]
                if files:
                    latest_file = max(files, key=os.path.getctime)
                    return latest_file
                
                # Check for bgcode if binary wasn't suppressed (shouldn't happen now)
                files_bg = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".bgcode")]
                if files_bg:
                     latest_file = max(files_bg, key=os.path.getctime)
                     return latest_file

                raise RuntimeError("G-code file was not generated")
                
        except subprocess.CalledProcessError as e:
            print(f"Slicing failed: {e.stderr}")
            raise RuntimeError(f"Slicing failed: {e.stderr}")
