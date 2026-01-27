import subprocess
import os
import logging
from typing import Optional

class SlicerRunner:
    def __init__(self, slicer_path: str = r"C:\Program Files\Prusa3D\PrusaSlicer\prusa-slicer-console.exe"):
        self.slicer_path = slicer_path

    def _get_preset_args(self, intent: str) -> list[str]:
        """
        Maps a natural language intent to Slicer CLI arguments.
        """
        intent = intent.lower()
        args = []

        # Basic profiles (assuming standard Prusa profiles exist/are loaded)
        # Note: In a real environment, we'd need exact profile names or config bundles.
        # For this prototype, we'll use CLI overrides which are safer than guessing profile names.
        
        if "draft" in intent or "fast" in intent:
            args.extend(["--layer-height", "0.25"])
            args.extend(["--fill-density", "10%"])
            args.extend(["--fill-pattern", "grid"])
        elif "strong" in intent or "strength" in intent or "heavy" in intent:
             args.extend(["--layer-height", "0.2"])
             args.extend(["--fill-density", "40%"])
             args.extend(["--perimeters", "4"])
             args.extend(["--fill-pattern", "gyroid"])
        elif "detail" in intent or "quality" in intent or "pretty" in intent:
             args.extend(["--layer-height", "0.10"])
             args.extend(["--fill-density", "15%"])
        else:
            # Default
            args.extend(["--layer-height", "0.2"])
            args.extend(["--fill-density", "15%"])
            
        return args

    def slice_file(self, input_path: str, output_path: str, intent: str = "default") -> dict:
        """
        Slices the input file using CLI overrides based on intent.
        """
        if not os.path.exists(input_path):
             return {"success": False, "error": f"Input file not found: {input_path}"}

        # Build command
        # prusa-slicer-console -g input.stl --output output.gcode [args]
        cmd = [
            self.slicer_path,
            "-g", # Generate G-code
            input_path,
            "--output", output_path
        ]
        
        cmd.extend(self._get_preset_args(intent))
        
        logging.info(f"Running slicer command: {' '.join(cmd)}")
        
        try:
            # Check if slicer is available first
            # We assume it's in PATH or absolute path provided
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return {
                "success": True,
                "message": "Slicing successful",
                "stdout": result.stdout,
                "output_path": output_path
            }
        except subprocess.CalledProcessError as e:
            logging.error(f"Slicing failed: {e.stderr}")
            return {
                "success": False, 
                "error": f"Slicing failed with code {e.returncode}: {e.stderr}"
            }
        except FileNotFoundError:
             return {
                "success": False, 
                "error": f"Slicer executable not found at '{self.slicer_path}'. Please ensure PrusaSlicer is installed and in PATH."
            }
        except Exception as e:
             return {"success": False, "error": str(e)}
