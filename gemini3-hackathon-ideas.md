# Gemini 3 Hackathon: 3D Printing AI Copilot

## Hackathon Overview

- **Event:** Gemini 3 Hackathon on Devpost
- **Prize Pool:** $100,000 ($50K grand prize)
- **Judging Criteria:**
  - Technical Execution (40%)
  - Innovation/Wow Factor (30%)
  - Potential Impact (20%)
  - Presentation/Demo (10%)

**Key Quote from Organizers:** "Build a game, a productivity tool, a scientific analyzer, or a **robotic controller**."

---

## Core Concept: PrintForge

**An AI-powered copilot for additive manufacturing that turns Gemini 3 into a 3D printing powerhouse.**

Target Hardware: Prusa 3D Printer (MK4 or similar) with webcam

---

## Project Ideas (Tiered by Impact)

### Tier 1: High Impact, High Wow Factor

#### 1. PrintForge: AI Copilot for Additive Manufacturing (RECOMMENDED)

A comprehensive assistant combining multiple Gemini 3 strengths:

| Feature | Description |
|---------|-------------|
| Vision-Based Failure Detection | Webcam monitors prints in real-time, detects spaghetti, layer shifts, warping, stringing → auto-pauses printer |
| Natural Language Control | "Start the Benchy with 20% infill in PETG", "Pause when you reach layer 50" |
| Photo Diagnosis | Upload failed print photos → Gemini diagnoses root cause + recommends fixes |
| G-Code Intelligence | Explain, optimize, or inject custom modifications into G-code |

**Why it wins:** Demonstrates multimodal (vision + text), reasoning, and real-world physical impact. Extremely demo-able.

#### 2. "Just Describe It" → Print Pipeline

End-to-end natural language to physical object:

```
User: "I need a wall-mounted holder for 3 toothbrushes"
Gemini: [generates OpenSCAD code or parametric model]
        [slices with optimal settings]
        [sends to printer]
```

Could also work from rough sketches (photo → interpreted design → STL).

**Why it wins:** The "wow" of describing something and having it materialize is visceral.

#### 3. Print Archaeologist

Point camera at any 3D printed object → Gemini reverse-engineers:
- Likely print settings (layer height, infill, orientation)
- Material identification
- Attempts to recreate a printable STL
- Identifies potential model source (Thingiverse, Printables match)

**Why it wins:** Novel problem space, showcases vision reasoning.

---

### Tier 2: Solid & Practical

#### 4. Conversational Slicer

Instead of navigating 200+ PrusaSlicer settings:

```
"Make this as strong as possible"
"I'm printing in a cold garage"
"Optimize for speed, strength doesn't matter"
```

Gemini translates intent → slicer profile modifications with explanations.

#### 5. Print Queue Optimizer (for print farms)

Multi-printer orchestration:
- Assigns jobs based on printer calibration quality, loaded material, current state
- Predicts failures based on printer history
- Optimizes batch scheduling for energy/time

#### 6. Voice-First Accessibility Mode

Fully voice-controlled printing for visually impaired makers:
- AI describes printer state, progress, issues
- Guides through bed leveling, filament loading
- Alerts on completion/failure

---

### Tier 3: Creative Moonshots

#### 7. Predictive Maintenance via Sound/Vibration

Microphone captures printer sounds → Gemini detects:
- Bearing wear patterns
- Belt tension issues
- Stepper motor problems
- "Your X-axis bearings will need replacement in ~200 print hours"

#### 8. AI Design Critic

Upload STL → Gemini analyzes for:
- Printability issues (overhangs, supports needed)
- Structural weaknesses
- Orientation optimization
- "This will fail at layer 47 due to unsupported overhang at 62°"

---

## Gemini 3-Specific Features & Integration

### Key Gemini 3 Capabilities

| Feature | Description |
|---------|-------------|
| Dynamic Thinking | `thinking_level` parameter: low/medium/high controls reasoning depth |
| Thought Signatures | Encrypted reasoning persists across multi-turn conversations |
| Media Resolution Control | `media_resolution`: low (70 tokens) to ultra_high (1120 tokens) per image |
| Tool Integration | Google Search, Code Execution, URL Context built-in |
| Structured Outputs + Tools | Combine JSON schemas with tool use |
| 1M Token Context | Massive context window for long print sessions |

---

## How Each Feature Maps to PrintForge

### 1. Dynamic Thinking System (`thinking_level`)

Different tasks need different reasoning depths:

```python
# Quick status check - minimal thinking, low latency
response = model.generate_content(
    [frame, "Is this print still running normally? Yes/No + brief reason"],
    generation_config={"thinking_level": "low"}
)

# Complex failure diagnosis - deep reasoning
response = model.generate_content(
    [frame, "Analyze this print failure. What went wrong and why?"],
    generation_config={"thinking_level": "high"}
)
```

| Task | Thinking Level | Why |
|------|----------------|-----|
| Real-time monitoring (every 30s) | `low` | Speed matters, simple binary check |
| Failure root cause analysis | `high` | Complex multi-factor reasoning |
| G-code optimization | `high` | Needs to understand geometry + physics |
| "What's my ETA?" | `minimal` | Trivial lookup |

**Demo idea:** Show the same print failure image with `low` vs `high` thinking - demonstrate the depth difference.

### 2. Media Resolution Control (`media_resolution`)

Balance token costs vs detection accuracy:

```python
# Real-time monitoring - lower resolution, faster, cheaper
response = model.generate_content(
    [frame, "Detect failures"],
    generation_config={"media_resolution": "low"}  # 70 tokens/frame
)

# Detailed post-failure analysis - max resolution
response = model.generate_content(
    [detailed_photo, "Analyze layer adhesion issues in detail"],
    generation_config={"media_resolution": "ultra_high"}  # 1120 tokens
)
```

**Demo idea:** Show dynamic resolution adjustment - fast monitoring during prints, ultra-high when investigating failures.

### 3. Thought Signatures (Multi-turn Context)

Maintains printer state awareness across long sessions:

```
Turn 1: "My prints keep failing at layer 20"
Turn 2: Gemini asks for photo, analyzes → "I see Z-banding. Let's check your Z-axis."
Turn 3: "I tightened the Z screw"
Turn 4: Gemini remembers full context → "Good. Start a test print - I'll monitor
        specifically for Z-banding at layer 15-25 given your previous failures."
```

**Demo idea:** Multi-turn troubleshooting session where Gemini remembers printer history.

### 4. Tool Integration

#### Code Execution - Generate/modify G-code:

```python
response = model.generate_content(
    "Generate OpenSCAD code for a 50mm calibration cube with chamfered edges",
    tools=["code_execution"]
)
# Gemini writes AND executes OpenSCAD code, returns STL
```

#### Google Search Grounding - Real-time troubleshooting:

```python
response = model.generate_content(
    [failed_print_image, "What's causing this? Search for solutions."],
    tools=["google_search"]
)
# Returns diagnosis grounded in real forum posts, documentation
```

#### URL Context - Pull printer-specific documentation:

```python
response = model.generate_content(
    "How do I calibrate the first layer on my Prusa MK4?",
    tools=[{"url_context": {"urls": ["https://help.prusa3d.com/"]}}]
)
```

### 5. Structured Outputs + Tools Combined

Return structured printer commands while also searching:

```python
response = model.generate_content(
    [image, "Diagnose this and give me the fix"],
    tools=["google_search"],
    generation_config={
        "response_mime_type": "application/json",
        "response_schema": {
            "diagnosis": "string",
            "confidence": "number",
            "printer_commands": ["string"],
            "sources": ["string"]
        }
    }
)
```

Returns:

```json
{
  "diagnosis": "Heat creep causing clogs",
  "confidence": 0.85,
  "printer_commands": ["M104 S190", "G28", "G1 Z50 F300"],
  "sources": ["https://help.prusa3d.com/article/..."]
}
```

---

## API Integration Examples

### Vision-Based Failure Detection

```python
import google.generativeai as genai
from PIL import Image
import io

genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel("gemini-3-pro")

def analyze_print_frame(image_bytes: bytes) -> dict:
    image = Image.open(io.BytesIO(image_bytes))

    response = model.generate_content(
        [
            image,
            """Analyze this 3D printer webcam frame. Detect any print failures:

            Look for:
            - Spaghetti (filament not adhering, creating tangled mess)
            - Layer shifts (horizontal displacement between layers)
            - Warping (corners lifting from bed)
            - Stringing (thin wisps between parts)
            - Bed adhesion failure (part detached from bed)
            - Nozzle blob (material stuck to nozzle)

            Respond in JSON:
            {
              "status": "ok" | "warning" | "failure",
              "issues": [{"type": "...", "confidence": 0.0-1.0, "description": "..."}],
              "recommendation": "continue" | "pause" | "stop"
            }"""
        ],
        generation_config={
            "thinking_level": "low",
            "media_resolution": "medium"
        }
    )

    return parse_json(response.text)
```

### Monitoring Loop

```python
async def monitor_print():
    while print_active:
        frame = capture_webcam_frame()
        analysis = analyze_print_frame(frame)

        if analysis["recommendation"] == "pause":
            octoprint.pause_print()
            notify_user(analysis["issues"])

            # Switch to high thinking for diagnosis
            detailed = await deep_diagnosis(frame)
            notify_user(detailed)

        await asyncio.sleep(30)  # check every 30 seconds
```

### Natural Language Control with Function Calling

```python
tools = [
    {
        "name": "start_print",
        "description": "Start printing a file",
        "parameters": {
            "filename": {"type": "string"},
            "settings_overrides": {"type": "object"}
        }
    },
    {
        "name": "pause_print",
        "description": "Pause the current print"
    },
    {
        "name": "set_temperature",
        "description": "Set hotend or bed temperature",
        "parameters": {
            "target": {"type": "string", "enum": ["hotend", "bed"]},
            "temperature": {"type": "integer"}
        }
    },
    {
        "name": "home_axes",
        "description": "Home printer axes",
        "parameters": {
            "axes": {"type": "array", "items": {"type": "string", "enum": ["X", "Y", "Z"]}}
        }
    }
]

def process_command(user_input: str):
    response = model.generate_content(
        user_input,
        tools=tools,
        system_instruction="""You control a Prusa MK4 3D printer.
        The user will give natural language commands.
        Call the appropriate function(s) to execute their request.
        Available files: benchy.gcode, phone_stand.gcode, bracket_v2.gcode"""
    )

    for call in response.function_calls:
        execute_printer_command(call.name, call.args)
```

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        PrintForge Web UI                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Chat      │  │   Live      │  │   Print Queue &         │  │
│  │   Interface │  │   Preview   │  │   History               │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PrintForge Backend                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  Gemini 3 API   │  │  OctoPrint/     │  │  Webcam         │  │
│  │  Integration    │  │  PrusaLink API  │  │  Manager        │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
         │                      │                     │
         ▼                      ▼                     ▼
┌─────────────────┐  ┌─────────────────────┐  ┌─────────────────┐
│   Gemini 3      │  │   Prusa Printer     │  │   USB/IP        │
│   Pro API       │  │   (via network)     │  │   Webcam        │
└─────────────────┘  └─────────────────────┘  └─────────────────┘
```

### Tech Stack Options

| Component | Options |
|-----------|---------|
| Frontend | React, Next.js, or simple HTML/JS |
| Backend | Python (FastAPI), Node.js |
| Printer API | OctoPrint API, PrusaLink API |
| Webcam | USB webcam, Prusa Cam, IP camera |
| Gemini SDK | `google-generativeai` Python package |

---

## Hackathon Pitch (200 words)

> **PrintForge** transforms Gemini 3 into an intelligent manufacturing copilot for 3D printing. By leveraging Gemini 3's dynamic thinking system, we provide instant real-time monitoring (`thinking_level: low`) during prints while enabling deep root-cause analysis (`thinking_level: high`) when failures occur.
>
> The system uses variable `media_resolution` to balance real-time failure detection speed against detailed forensic analysis of print defects. Thought signatures maintain full printer state context across multi-hour print sessions, remembering calibration history, previous failures, and ongoing troubleshooting.
>
> Key features include:
> - **Vision-based failure detection** that auto-pauses prints before wasting hours of filament
> - **Natural language printer control** via function calling
> - **Photo diagnosis** of failed prints with actionable fixes
> - **G-code intelligence** for optimization and modification
>
> Built-in code execution generates parametric models on-demand from text descriptions, while Google Search grounding provides real-time troubleshooting sourced from community knowledge.
>
> This isn't a generic chatbot connected to a printer—it's specifically architected around Gemini 3's unique capabilities to solve real problems in additive manufacturing, preventing failed prints and democratizing access to expert-level 3D printing knowledge.

---

## Demo Script (3 minutes)

1. **0:00-0:30** - Introduction
   - Show the Prusa printer with webcam
   - "PrintForge is your AI copilot for 3D printing"

2. **0:30-1:15** - Live Failure Detection
   - Start a print that will fail (simulate spaghetti)
   - Show PrintForge detecting the failure in real-time
   - Auto-pause triggers, notification appears
   - Show the `thinking_level: low` → `high` transition for diagnosis

3. **1:15-1:45** - Natural Language Control
   - "Start the calibration cube with 15% infill"
   - Show function calls being made
   - Printer responds

4. **1:45-2:30** - Photo Diagnosis
   - Upload a photo of a failed print
   - Gemini analyzes with `media_resolution: ultra_high`
   - Returns root cause + specific settings to change
   - Show Google Search grounding pulling real solutions

5. **2:30-3:00** - Wrap-up
   - Show multi-turn context (thought signatures)
   - "PrintForge remembers your printer's history"
   - Call to action

---

## Next Steps

1. [ ] Set up development environment
2. [ ] Get Gemini 3 API access
3. [ ] Connect to Prusa printer via OctoPrint/PrusaLink
4. [ ] Set up webcam integration
5. [ ] Build core failure detection loop
6. [ ] Add natural language control
7. [ ] Build simple web UI
8. [ ] Record demo video
9. [ ] Write submission materials
