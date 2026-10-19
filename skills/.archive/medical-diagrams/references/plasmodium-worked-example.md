# Worked Example: Plasmodium Life Cycle Diagram

## Request
"Show me the life cycle of plasmodium" — user wanted both Excalidraw and HTML/CSS versions.

## What was produced

### Excalidraw (74 elements, 63KB)
- Two color-coded host zones: Human (left) and Mosquito (right)
- Sub-zones: Liver Stage (purple), Blood Stage (blue), Mosquito Gut (orange), Salivary Glands (green)
- 15 labeled arrows + 3 dashed cross-host arrows
- Container-bound text on all shapes (verified both `containerId` and `boundElements`)
- Hand-drawn roughness: 1

### HTML/CSS (489 lines, 27KB)
- Dark background (#020617) with grid, JetBrains Mono font
- 13 numbered stages across both hosts
- Color-coded boxes: cyan=blood, violet=liver, amber=mosquito gut, rose=salivary glands, orange=gametocytes, slate=external
- SVG arrow markers, dashed cross-host arrows
- Legend + 3 summary cards (Human Phase, Mosquito Phase, Clinical Significance)
- Pulsing dot animation in header

## Lessons learned

1. **Architecture-diagram skill can be repurposed** for medical content by reassigning color categories:
   - Frontend (cyan) → Blood/circulatory stages
   - Backend (emerald) → Intracellular stages
   - Database (violet) → Liver/tissue stages
   - AWS/Cloud (amber) → Vector (mosquito) stages
   - Security (rose) → Specialized structures
   - Message Bus (orange) → Transitional forms
   - External (slate) → Cross-host transitions

2. **Dual-format approach works well.** Excalidraw for studying/editing, HTML for polished reference. User can choose what fits their workflow.

3. **Parallel delegation** — two subagents can build both formats simultaneously, saving time.

4. **Screenshot pipeline** — playwright in a temp venv works for generating PNGs of HTML diagrams. Excalidraw screenshots need the React fiber API approach on excalidraw.com.
