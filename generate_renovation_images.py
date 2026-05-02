#!/usr/bin/env python3
"""
Renovation Image Generator for Peltheide 11, 3150 Haacht, Belgium.

Generates property-specific "after" renovation images by calling the OpenAI
Images API with detailed prompts derived from the actual room photos and the
property data in property_data.json.

Two types of images are produced:
  1. Before/After comparison images  – uses images.edit() so the AI edits the
     actual room photo according to a renovation brief (saved as *_after.jpg).
  2. Inspiration card images          – uses images.generate() with highly
     specific prompts for each design proposal card in index.html
     (saved as *_inspiration_N.jpg).

Usage:
    pip install openai
    export OPENAI_API_KEY=sk-...
    python generate_renovation_images.py

All generated images are saved next to this script so that index.html can
reference them directly.  Re-running the script will overwrite existing files.
"""

import base64
import json
import os
import sys
from pathlib import Path

# ── Configuration ─────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
PROPERTY_FILE = SCRIPT_DIR / "property_data.json"

# Model used for image generation (requires gpt-image-1 access).
# Fall back to "dall-e-3" if you do not have gpt-image-1 enabled on your key.
GENERATE_MODEL = "gpt-image-1"
# Model used for image editing (pass actual room photo + renovation instructions).
# Use "dall-e-2" if you do not have gpt-image-1 editing access.
EDIT_MODEL = "gpt-image-1"

GENERATE_SIZE = "1024x1024"
EDIT_SIZE = "1024x1024"

# ── Property context ───────────────────────────────────────────────────────────
def load_property_data() -> dict:
    with open(PROPERTY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ── OpenAI helpers ─────────────────────────────────────────────────────────────
def get_client():
    try:
        import openai
    except ImportError:
        sys.exit("The 'openai' package is required.  Run:  pip install openai")
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        sys.exit("Please set the OPENAI_API_KEY environment variable.")
    return openai.OpenAI(api_key=api_key)


def generate_image(client, prompt: str, output_path: Path) -> None:
    """Generate an image from scratch and save it as JPEG."""
    print(f"  [generate] {output_path.name} …", end=" ", flush=True)
    try:
        response = client.images.generate(
            model=GENERATE_MODEL,
            prompt=prompt,
            n=1,
            size=GENERATE_SIZE,
        )
        _save_response_image(response, output_path)
        print("✓")
    except Exception as exc:
        print(f"✗  ({exc})")


def edit_image(client, image_path: Path, prompt: str, output_path: Path) -> None:
    """Edit an existing room photo with a renovation instruction and save it."""
    print(f"  [edit]     {output_path.name} …", end=" ", flush=True)
    if not image_path.exists():
        print(f"✗  (source image not found: {image_path})")
        return
    try:
        with open(image_path, "rb") as img_file:
            response = client.images.edit(
                model=EDIT_MODEL,
                image=img_file,
                prompt=prompt,
                n=1,
                size=EDIT_SIZE,
            )
        _save_response_image(response, output_path)
        print("✓")
    except Exception as exc:
        print(f"✗  ({exc})")


def _save_response_image(response, output_path: Path) -> None:
    """Decode base64 image from API response and write as JPEG."""
    item = response.data[0]
    # gpt-image-1 always returns b64_json; dall-e-3 may return a URL instead.
    if hasattr(item, "b64_json") and item.b64_json:
        img_bytes = base64.b64decode(item.b64_json)
    elif hasattr(item, "url") and item.url:
        import urllib.request
        with urllib.request.urlopen(item.url) as resp:
            img_bytes = resp.read()
    else:
        raise ValueError("Response contained neither b64_json nor url.")
    output_path.write_bytes(img_bytes)


# ── Image task definitions ─────────────────────────────────────────────────────
def before_after_tasks(data: dict) -> list[dict]:
    """
    Returns tasks for the 5 Before/After comparison sliders.
    Each task uses the actual room photo as input and produces *_after.jpg.
    """
    prop = data["property"]
    year = prop["year_built"]
    garden = prop["garden_orientation"]

    return [
        {
            "source": SCRIPT_DIR / "living_room.JPG",
            "output": SCRIPT_DIR / "living_room_after.jpg",
            "prompt": (
                f"Renovate this {year} Belgian split-level living room. "
                "Keep the existing chimney breast and fireplace opening. "
                "Replace the laminate floor with wide-plank engineered oak. "
                "Replace wallpaper with smooth plaster walls painted in warm sage green. "
                "Install floor-to-ceiling built-in shelving units flanking the chimney, "
                "painted in deep forest green with brushed brass handles. "
                "Add recessed LED ceiling lights on dimmers and warm reading lamps. "
                "Replace any old terrace doors with slim aluminium sliding doors. "
                "Style with Scandinavian modern furniture: a linen sofa, bouclé armchairs, "
                "and a statement area rug in earthy terracotta tones. "
                "High-quality interior design render, photorealistic."
            ),
        },
        {
            "source": SCRIPT_DIR / "kitchen.JPG",
            "output": SCRIPT_DIR / "kitchen_after.jpg",
            "prompt": (
                f"Renovate this {year} Belgian kitchen that has an exterior door to the "
                f"{garden.lower()}-facing back garden. "
                "Install handleless floor-to-ceiling cabinetry: sage green lower units, "
                "off-white upper units, all with soft-close drawers and pull-out larder units. "
                "Add a large central island with a Calacatta marble waterfall edge worktop "
                "and three bar stools on one side. "
                "Replace the ceramic hob with an induction range cooker and bespoke copper "
                "extractor hood as the focal point above it. "
                "Install two oversized copper pendant lights above the island. "
                "Replace the exterior door with slim aluminium bifold doors opening onto "
                "the south-facing garden. "
                "Add a glass roof lantern above to flood the space with natural light. "
                "High-quality interior design render, photorealistic."
            ),
        },
        {
            "source": SCRIPT_DIR / "bathroom_1.JPG",
            "output": SCRIPT_DIR / "bathroom_after.jpg",
            "prompt": (
                f"Renovate this {year} Belgian first-floor bathroom. "
                "Remove the existing bathtub and convert the shower area into a frameless "
                "glass wet room with large-format porcelain tiles and a linear drain. "
                "Install a sculptural freestanding stone resin bath in matte white beside "
                "the window, with brushed brass floor-standing filler tap. "
                "Clad walls in book-matched marble tiles with a fluted stone accent panel "
                "behind the vanity. "
                "Fit a floating smoked oak double vanity with two under-mount basins and "
                "brushed brass mixer taps. "
                "Add a full-width backlit LED anti-fog smart mirror above the vanity. "
                "Install in-floor electric heating and a programmable heated towel ladder "
                "in brushed brass. "
                "High-quality interior design render, photorealistic."
            ),
        },
        {
            "source": SCRIPT_DIR / "garden.JPG",
            "output": SCRIPT_DIR / "garden_after.jpg",
            "prompt": (
                f"Transform this {garden.lower()}-facing Belgian garden of "
                f"{prop['plot_area_m2']} m² into a luxury outdoor living space. "
                "Add a powder-coated anthracite aluminium pergola with a motorised louvred "
                "roof and warm string lights over a raised composite decking terrace. "
                "Include an outdoor kitchen beneath the pergola with a built-in stainless "
                "steel BBQ, pizza oven, prep sink, and mini fridge. "
                "Install a compact plunge pool edged with composite decking and tall "
                "privacy screening hedges. "
                "Add tiered cedar raised vegetable and herb garden beds along one border. "
                "Create sweeping four-season planting borders with lavender, ornamental "
                "grasses, hellebores, and climbing roses on the fence. "
                "Illuminate with low-level LED path lights and uplighters in the beds. "
                "High-quality landscape design render, photorealistic."
            ),
        },
        {
            "source": SCRIPT_DIR / "bedroom_1.JPG",
            "output": SCRIPT_DIR / "bedroom_after.jpg",
            "prompt": (
                f"Renovate this {year} Belgian first-floor bedroom. "
                "Replace the laminate floor with wide-plank engineered oak. "
                "Install floor-to-ceiling built-in wardrobes with push-to-open doors on "
                "either side of the bed, painted in warm off-white. "
                "Create a deep velvet sage green accent wall behind the bed with an "
                "upholstered bespoke fabric headboard. "
                "Paint the remaining three walls in warm off-white. "
                "Add recessed LED ceiling lights on dimmers, brushed brass bedside wall "
                "sconces, and linen curtains floor to ceiling. "
                "Style with crisp white linen bedding and a textured throw. "
                "High-quality interior design render, photorealistic."
            ),
        },
    ]


def inspiration_tasks() -> list[dict]:
    """
    Returns tasks for the 24 inspiration cards (6 per room section).
    Each task generates a new image from scratch with a property-specific prompt.
    """
    prefix = "High-quality photorealistic interior/exterior design render, no people. "
    suffix = " Architecture visualisation quality, sharp and detailed."
    return [
        # ── Living Room (6 cards) ─────────────────────────────────────────────
        {
            "output": SCRIPT_DIR / "living_room_inspiration_1.jpg",
            "prompt": (
                prefix
                + "Belgian split-level living room, 1968 construction. "
                "Floor-to-ceiling natural stone feature wall behind a linen sofa. "
                "Warm recessed LED strip lighting highlighting the stone texture. "
                "Wide-plank engineered oak floors, sage green plastered walls, "
                "sliding aluminium terrace doors with a south garden view."
                + suffix
            ),
        },
        {
            "output": SCRIPT_DIR / "living_room_inspiration_2.jpg",
            "prompt": (
                prefix
                + "Belgian split-level living room with smart layered lighting. "
                "Recessed ceiling downlights on dimmers, brushed brass floor lamps, "
                "and warm LED strips under a floating TV unit. "
                "Wide-plank oak floors, sage green walls, built-in shelving, "
                "Scandinavian modern furniture in linen and bouclé."
                + suffix
            ),
        },
        {
            "output": SCRIPT_DIR / "living_room_inspiration_3.jpg",
            "prompt": (
                prefix
                + "Belgian living room with floor-to-ceiling bespoke built-in shelving "
                "flanking a chimney breast and wood fire cassette. "
                "Shelves painted forest green with brushed brass fittings, "
                "filled with books, plants, and art. "
                "Wide-plank oak floors, terracotta rug, sliding terrace doors."
                + suffix
            ),
        },
        {
            "output": SCRIPT_DIR / "living_room_inspiration_4.jpg",
            "prompt": (
                prefix
                + "Belgian living room with wide-plank engineered oak hardwood flooring "
                "over underfloor heating. Natural daylight from south-facing sliding "
                "terrace doors. Warm and inviting Scandinavian atmosphere. "
                "Sage green walls, chimney with wood fire, bouclé furniture."
                + suffix
            ),
        },
        {
            "output": SCRIPT_DIR / "living_room_inspiration_5.jpg",
            "prompt": (
                prefix
                + "Belgian living room with bold earthy colour palette. "
                "Deep terracotta accent wall behind the sofa, sage green side walls. "
                "Floor-length linen curtains, bouclé armchairs, statement jute area rug. "
                "Wide-plank oak floors, chimney with cassette fire insert, "
                "south-facing light through terrace doors."
                + suffix
            ),
        },
        {
            "output": SCRIPT_DIR / "living_room_inspiration_6.jpg",
            "prompt": (
                prefix
                + "Belgian living room with concealed home cinema. "
                "4K QLED television inside a custom oak joinery unit with doors that "
                "close over the screen. Dolby Atmos soundbar integrated into shelving. "
                "Dimmable ambient lighting, blackout linen curtains, plush seating."
                + suffix
            ),
        },
        # ── Garden (6 cards) ─────────────────────────────────────────────────
        {
            "output": SCRIPT_DIR / "garden_inspiration_1.jpg",
            "prompt": (
                prefix
                + "South-facing Belgian garden with anthracite aluminium pergola and "
                "motorised louvred roof. Warm string lights, outdoor heaters, "
                "composite decking terrace. Elevated position with garden view. "
                "Evening atmosphere, 626 m² plot."
                + suffix
            ),
        },
        {
            "output": SCRIPT_DIR / "garden_inspiration_2.jpg",
            "prompt": (
                prefix
                + "South-facing Belgian garden with compact plunge pool surrounded by "
                "light composite decking. Tall hornbeam privacy hedging on three sides. "
                "Low-level LED underwater and path lighting, evening mood. "
                "626 m² plot, split-level garden."
                + suffix
            ),
        },
        {
            "output": SCRIPT_DIR / "garden_inspiration_3.jpg",
            "prompt": (
                prefix
                + "South-facing Belgian garden with tiered cedar raised vegetable and "
                "herb garden beds. Composting station and oak rainwater barrel. "
                "Gravel paths between the beds, bee-friendly flowering plants, "
                "south-facing light, productive and sustainable."
                + suffix
            ),
        },
        {
            "output": SCRIPT_DIR / "garden_inspiration_4.jpg",
            "prompt": (
                prefix
                + "South-facing Belgian garden outdoor kitchen and fire pit zone. "
                "Built-in stainless steel BBQ and pizza oven under an anthracite "
                "aluminium pergola. Sunken fire pit lounge with low seating. "
                "Ornamental grasses and lavender borders, composite decking."
                + suffix
            ),
        },
        {
            "output": SCRIPT_DIR / "garden_inspiration_5.jpg",
            "prompt": (
                prefix
                + "South-facing Belgian garden Japanese-style Zen garden zone. "
                "Koi pond with bamboo water feature, moss ground cover, "
                "stepping stone path, a teak meditation bench. "
                "Bamboo privacy screen, Japanese maple, peaceful and minimalist."
                + suffix
            ),
        },
        {
            "output": SCRIPT_DIR / "garden_inspiration_6.jpg",
            "prompt": (
                prefix
                + "South-facing Belgian garden four-season planting scheme. "
                "Sweeping borders with lavender, hellebores, ornamental grasses, "
                "and summer roses. Curved gravel path, outdoor lanterns, "
                "Belgian split-level home facade in background."
                + suffix
            ),
        },
        # ── Bathroom (6 cards) ───────────────────────────────────────────────
        {
            "output": SCRIPT_DIR / "bathroom_inspiration_1.jpg",
            "prompt": (
                prefix
                + "Belgian first-floor bathroom with sculptural matte white freestanding "
                "stone resin bath positioned beside a floor-to-ceiling frosted glass window. "
                "Natural light flooding in. Fluted marble wall behind bath, "
                "brushed brass floor-standing filler tap. Minimal and luxurious."
                + suffix
            ),
        },
        {
            "output": SCRIPT_DIR / "bathroom_inspiration_2.jpg",
            "prompt": (
                prefix
                + "Belgian bathroom converted to frameless glass walk-in wet room. "
                "Large-format matte porcelain floor tiles with linear drain. "
                "Oversized ceiling rainfall shower head and handheld body jets. "
                "Book-matched marble wall tiles, brushed brass fixtures."
                + suffix
            ),
        },
        {
            "output": SCRIPT_DIR / "bathroom_inspiration_3.jpg",
            "prompt": (
                prefix
                + "Belgian bathroom with book-matched Calacatta marble cladding on all walls. "
                "Fluted stone double vanity with two undermount basins. "
                "Brushed brass mixer taps, towel rings, and heated towel rail. "
                "Warm downlighting creating a spa atmosphere."
                + suffix
            ),
        },
        {
            "output": SCRIPT_DIR / "bathroom_inspiration_4.jpg",
            "prompt": (
                prefix
                + "Belgian bathroom steam shower enclosure with frameless glass panels. "
                "Large marble tiles inside the enclosure with in-floor electric heating. "
                "Programmable heated towel ladder in brushed brass on the wall. "
                "Aromatherapy diffuser, Bluetooth ceiling speaker, spa atmosphere."
                + suffix
            ),
        },
        {
            "output": SCRIPT_DIR / "bathroom_inspiration_5.jpg",
            "prompt": (
                prefix
                + "Belgian bathroom with full-width backlit LED anti-fog smart mirror "
                "with touch controls. Below it a floating smoked oak double vanity "
                "with two undermount sinks and brushed brass mixer taps. "
                "Marble tiles, warm ambient glow, minimalist and modern."
                + suffix
            ),
        },
        {
            "output": SCRIPT_DIR / "bathroom_inspiration_6.jpg",
            "prompt": (
                prefix
                + "Belgian bathroom with vertical living moss and fern wall panel "
                "mounted above the freestanding bath. Frosted skylight above for "
                "natural ventilation and daylight. Biophilic design, organic textures, "
                "lush greenery, stone resin bath, brushed brass accents."
                + suffix
            ),
        },
        # ── Kitchen (6 cards) ────────────────────────────────────────────────
        {
            "output": SCRIPT_DIR / "kitchen_inspiration_1.jpg",
            "prompt": (
                prefix
                + "Belgian kitchen-diner with large central island with Calacatta marble "
                "waterfall edge worktop. Three bar stools on one side. "
                "Sage green handleless lower cabinets, off-white upper cabinets. "
                "Two oversized copper pendant lights above island. "
                "Bifold doors open to south-facing garden beyond."
                + suffix
            ),
        },
        {
            "output": SCRIPT_DIR / "kitchen_inspiration_2.jpg",
            "prompt": (
                prefix
                + "Belgian kitchen with floor-to-ceiling handleless cabinetry. "
                "Sage green lower units, off-white upper units reaching the ceiling. "
                "Pull-out larder units and deep pan drawers visible in open drawer. "
                "Marble worktops, integrated appliances behind matching fronts."
                + suffix
            ),
        },
        {
            "output": SCRIPT_DIR / "kitchen_inspiration_3.jpg",
            "prompt": (
                prefix
                + "Belgian kitchen featuring a dual-fuel professional range cooker in "
                "British racing green with a bespoke copper extractor hood above as "
                "the room's focal point. Marble splashback, sage green cabinets, "
                "Calacatta island worktop, copper pendant lights."
                + suffix
            ),
        },
        {
            "output": SCRIPT_DIR / "kitchen_inspiration_4.jpg",
            "prompt": (
                prefix
                + "Belgian kitchen-diner with slim anthracite aluminium bifold doors "
                "fully opened to a south-facing garden. A glass roof lantern above "
                "floods the room with daylight. Sage green handleless cabinets, "
                "marble island, composite decking terrace visible outside."
                + suffix
            ),
        },
        {
            "output": SCRIPT_DIR / "kitchen_inspiration_5.jpg",
            "prompt": (
                prefix
                + "Belgian kitchen with fully integrated smart appliances behind "
                "matching sage green handleless cabinet fronts. "
                "Smart home tablet panel built into the cabinetry. "
                "Calacatta marble worktops and island, copper pendants, "
                "clean minimal design."
                + suffix
            ),
        },
        {
            "output": SCRIPT_DIR / "kitchen_inspiration_6.jpg",
            "prompt": (
                prefix
                + "Belgian kitchen with dramatic bookmatched Calacatta marble slab "
                "splashback behind the range cooker. "
                "Two oversized sculptural copper pendant lights hang above the island. "
                "Sage green handleless cabinetry, marble island worktop, "
                "bifold doors to garden beyond."
                + suffix
            ),
        },
    ]


# ── Main ───────────────────────────────────────────────────────────────────────
def main() -> None:
    prop_data = load_property_data()
    client = get_client()

    ba_tasks = before_after_tasks(prop_data)
    ins_tasks = inspiration_tasks()

    total = len(ba_tasks) + len(ins_tasks)
    print(f"\nPeltheide 11 — Renovation Image Generator")
    print(f"{'─' * 50}")
    print(f"Generating {total} images ({len(ba_tasks)} before/after edits + "
          f"{len(ins_tasks)} inspiration renders).\n")

    # 1. Before/After images (edited from actual room photos)
    print("── Before / After edits ──────────────────────────────")
    for task in ba_tasks:
        edit_image(client, task["source"], task["prompt"], task["output"])

    # 2. Inspiration card images (generated from scratch)
    print("\n── Inspiration card renders ───────────────────────────")
    for task in ins_tasks:
        generate_image(client, task["prompt"], task["output"])

    print(f"\n{'─' * 50}")
    print("Done!  Open index.html in your browser to see the results.")


if __name__ == "__main__":
    main()
