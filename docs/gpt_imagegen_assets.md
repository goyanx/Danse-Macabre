# GPT Image Generation Assets

These project-bound assets were generated with the built-in GPT image generation flow and copied into `game/images`.

## Active GPT-Generated Backgrounds

- `game/images/bg facade street.png`
- `game/images/bg facade entrance.png`
- `game/images/bg facade map.png`
- `game/images/bg facade salon.png`
- `game/images/bg facade kitchen.png`
- `game/images/bg facade study.png`

All location art uses canonical scene names in `game/facade_story.rpy`. The older placeholder PNGs, imported house renders, and duplicate `gpt`-suffixed room files were removed.

## Prompts

### Street

Use case: cinematic visual-novel background
Asset type: Ren'Py 16:9 exterior for The Glass House
Primary request: photorealistic modern urban townhouse at midnight, with charcoal stone, black glass, aged brass, warm interior light, and rain-dark pavement.
Composition/framing: straight architectural view from across the street, house centered and readable, dark lower area for dialogue UI.
Constraints: no people, obstructing vehicles, text, signage, logos, or watermark.

### Entrance

Use case: cinematic visual-novel background
Asset type: Ren'Py 16:9 interior for The Glass House
Primary request: photorealistic entry foyer matching the salon and kitchen, with black marble, brass, smoked glass, dark walnut, burgundy accents, and a sculptural staircase.
Composition/framing: view from just inside the front door, strong depth and an uncluttered lower third for dialogue UI.
Constraints: no people, body, readable text, logos, watermark, or bright stylized-render appearance.

### Map

Use case: interactive location-map background
Asset type: Ren'Py 16:9 top-down architectural view
Primary request: premium modern townhouse floor plan showing the connected entrance foyer, central hall and staircase, salon, kitchen, and study.
Composition/framing: mostly top-down with slight isometric depth, clear room centers and dark margins for overlaid navigation labels.
Constraints: no people, written labels, icons, UI buttons, logos, or watermark.

### Salon

Use case: stylized-concept
Asset type: Ren'Py 16:9 game background for The Glass House
Primary request: high-fidelity painted background of a modern townhouse salon after midnight, tense domestic mystery atmosphere.
Scene/backdrop: expensive glass-and-brass living room, cracked wedding portrait above a mantel, bar cart with three crystal glasses, city lights through tall windows.
Style/medium: cinematic painterly visual novel background, moody realism, no characters.
Composition/framing: wide 16:9 establishing shot, clear foreground/midground/background, enough open lower area for dialogue textbox.
Lighting/mood: late-night warm lamp light against cool blue city window light, elegant but emotionally claustrophobic.
Color palette: deep charcoal, muted burgundy, brass, cool blue highlights.
Constraints: no text, no watermark, no logos, no people, no readable documents, no speech bubbles.

### Kitchen

Use case: stylized-concept
Asset type: Ren'Py 16:9 game background for The Glass House
Primary request: high-fidelity painted background of a modern townhouse kitchen after midnight, prepared for three people although only two hosts are present.
Scene/backdrop: sleek dark kitchen, marble counter, sink area, one untouched crystal glass beside two used wine glasses, citrus peel, cabinet reflections, doorway toward salon.
Style/medium: cinematic painterly visual novel background, moody realism, no characters.
Composition/framing: wide 16:9 room background with strong readable focal point on the third glass, lower area left open for dialogue textbox.
Lighting/mood: cool appliance light, warm under-cabinet light, quiet suspense, intimate domestic tension.
Color palette: slate, black marble, pale brass, amber wine, cool blue reflections.
Constraints: no text, no watermark, no logos, no people, no readable labels.

### Study

Use case: stylized-concept
Asset type: Ren'Py 16:9 game background for The Glass House
Primary request: high-fidelity painted background of a private modern study after midnight where a hidden letter reveals a family fiction.
Scene/backdrop: dark bookcases, heavy desk, brass lamp, partly open drawer, cream paper letter visible without readable text, closed door in background, rain-dark window.
Style/medium: cinematic painterly visual novel background, moody realism, no characters.
Composition/framing: wide 16:9 visual novel background, desk and letter as focal point, lower area usable for dialogue textbox.
Lighting/mood: warm pool of lamplight, deep shadows, intimate confrontation, psychological suspense.
Color palette: walnut brown, black, smoky violet, brass, cream paper.
Constraints: no readable text, no watermark, no logos, no people, no speech bubbles.

## Active GPT-Generated Character Sprites

These realistic character sprites were generated with the built-in GPT image generation flow, then converted from a flat chroma-key background into transparent Ren'Py sprites.

### Lila Vale

- File: `game/images/lila normal.png`
- Expression files: `game/images/lila angry.png`, `game/images/lila wounded.png`
- Source prompt summary: realistic full-body visual novel sprite of Lila Vale, an elegant late-30s/early-40s townhouse host in a deep burgundy tailored evening dress, poised but emotionally strained, cinematic realism, no text or logos.
- Processing: generated on a flat `#00ff00` chroma-key background for the normal sprite, then expression edits were generated from the normal sprite. Backgrounds were converted to real alpha, cropped, cleaned, and scaled onto `620x1080` transparent canvases.

### Malcolm Vale

- File: `game/images/malcolm normal.png`
- Expression files: `game/images/malcolm amused.png`, `game/images/malcolm wounded.png`
- Source prompt summary: realistic full-body visual novel sprite of Malcolm Vale, a charismatic early/mid-40s townhouse host in a midnight-blue suit and open-collar white shirt, refined but exhausted, cinematic realism, no text or logos.
- Processing: generated on a flat `#00ff00` chroma-key background for the normal sprite, then expression edits were generated from the normal sprite. Backgrounds were converted to real alpha, cropped, cleaned, and scaled onto `620x1080` transparent canvases.

## Notes

The deterministic asset generator in `tools/generate_facade_assets.py` remains useful for reproducible placeholders and menu art. These GPT-generated backgrounds are the higher-fidelity active location art for the current playable build. The generator now skips existing `lila normal.png` and `malcolm normal.png` files so regenerating placeholders does not overwrite the final character sprites.
