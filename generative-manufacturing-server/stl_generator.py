import os
import base64
import subprocess
import re
import tempfile
import logging
import shutil
from google import genai
from google.genai import types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
def get_openscad_path():
    env_path = os.getenv("OPENSCAD_PATH")
    if env_path:
        return env_path
    
    which_path = shutil.which("openscad")
    if which_path:
        return which_path
        
    return r"C:\Program Files\OpenSCAD\openscad.exe"

OPENSCAD_PATH = get_openscad_path()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def format_prompt(prompt: str) -> str:
    return f"""
    Write a valid OpenSCAD script to create a 3D model of: {prompt}.
    
    Requirements:
    1. The model must be centered at [0,0,0].
    2. The model size should be reasonable (approx 20mm to 100mm bounding box) unless specified otherwise.
    3. Use standard OpenSCAD primitives (cube, cylinder, sphere) and transformations (translate, rotate, union, difference).
    4. Ensure the code is syntax-error free.
    5. CRITICAL: The model MUST be "3D Print Ready". This means:
       - It must be Manifold (watertight).
       - It must have NO self-intersections.
       - Walls must be thick enough for FDM printing (> 1-2mm).
       - Avoid floating parts; everything must be connected.
    6. Output ONLY the OpenSCAD code. Do not include markdown formatting or explanations.
    """

def clean_code(code: str) -> str:
    """Removes markdown code fences and whitespace."""
    code = re.sub(r"```openscad", "", code, flags=re.IGNORECASE)
    code = re.sub(r"```", "", code)
    return code.strip()

def generate_scad_code(prompt: str, client: genai.Client = None) -> str:
    """Generates OpenSCAD code using Gemini."""
    if not client:
        if not GEMINI_API_KEY:
             raise ValueError("GEMINI_API_KEY not set and no client provided.")
        client = genai.Client(api_key=GEMINI_API_KEY)

    full_prompt = format_prompt(prompt)
    
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents=full_prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(include_thoughts=True)
            )
        )
        return clean_code(response.text)
    except Exception as e:
        logger.error(f"Error generating SCAD code: {e}")
        raise


def compile_scad_to_stl(scad_code: str, output_path: str) -> bool:
    """Compiles SCAD code to STL using OpenSCAD CLI. Also generates a PNG preview."""
    if not os.path.exists(OPENSCAD_PATH):
        logger.error(f"OpenSCAD executable not found at {OPENSCAD_PATH}")
        return False

    with tempfile.NamedTemporaryFile(mode='w', suffix='.scad', delete=False) as temp_scad:
        temp_scad.write(scad_code)
        temp_scad_path = temp_scad.name

    try:
        # Run OpenSCAD in headless mode for STL
        # openscad.exe -o output.stl input.scad
        cmd_stl = [OPENSCAD_PATH, "-o", output_path, temp_scad_path]
        logger.info(f"Running OpenSCAD STL: {' '.join(cmd_stl)}")
        
        result_stl = subprocess.run(cmd_stl, capture_output=True, text=True, check=True)
        
        if result_stl.returncode != 0 or not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            logger.error(f"OpenSCAD STL failed. Output: {result_stl.stderr}")
            return False

        # Generate PNG Preview
        png_path = output_path.replace(".stl", ".png")
        cmd_png = [OPENSCAD_PATH, "-o", png_path, "--imgsize=800,600", "--colorscheme=DeepOcean", temp_scad_path]
        logger.info(f"Running OpenSCAD PNG: {' '.join(cmd_png)}")
        
        subprocess.run(cmd_png, capture_output=True, text=True, check=False) # Don't fail if PNG fails
        
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"OpenSCAD execution error: {e.stderr}")
        return False
    finally:
        if os.path.exists(temp_scad_path):
            os.remove(temp_scad_path)

def generate_model(prompt: str, output_filename: str, client: genai.Client = None) -> dict:
    """
    Orchestrates the generation of an STL component from a prompt.
    
    Args:
        prompt: User description of the object.
        output_filename: Name of the file to save (e.g. "gear.stl")
        client: Optional Gemini client.
    
    Returns:
        Dictionary with status, path, and image_base64.
    """
    
    # Ensure assets/models directory exists
    models_dir = os.path.join(os.path.dirname(__file__), "assets", "models")
    os.makedirs(models_dir, exist_ok=True)
    
    full_output_path = os.path.join(models_dir, output_filename)
    if not full_output_path.endswith(".stl"):
        full_output_path += ".stl"
        
    try:
        logger.info(f"Generating SCAD code for: {prompt}")
        scad_code = generate_scad_code(prompt, client)
        
        logger.info("Compiling to STL...")
        success = compile_scad_to_stl(scad_code, full_output_path)
        
        if success:
            png_path = full_output_path.replace(".stl", ".png")
            image_base64 = None
            if os.path.exists(png_path):
                 with open(png_path, "rb") as image_file:
                    image_base64 = base64.b64encode(image_file.read()).decode('utf-8')

            return {
                "status": "success",
                "path": full_output_path,
                "filename": os.path.basename(full_output_path),
                "image_base64": image_base64,
                "message": f"Successfully generated {output_filename}"
            }
        else:
             return {
                "status": "error",
                "message": "Failed to compile OpenSCAD code to STL."
            }

    except Exception as e:
        logger.error(f"Generation failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

