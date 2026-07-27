---
name: character-soul-forge
description: "Forge a living SOUL.md for any character from any source."
version: 2.0.0
author: Cuso
license: MIT
---

# Character Soul Forge v2

Exhaustive personality research and SOUL.md authoring skill for Hermes Agent.

Transforms any character from any medium (film, TV, book, history, games, comics, anime, etc.) into a living Hermes Agent persona. Supports single characters, real people, and fusion/composite characters.

This skill has two phases:
1. **Research** — exhaustively gather personality data from the internet
2. **Synthesize** — produce or update a SOUL.md using the research, dimensionality principles, and the Hermes SOUL template

---

## When to Use

User says: "make a SOUL for [character]", "bring [character] to life", "act like [character]", "research personality", "create soul", "update soul", or any variant of wanting an AI agent to embody a specific character or person.

---

## Phase 1: Research

**⚠️ THIS PHASE IS THE MOST IMPORTANT PHASE.** The quality ceiling of the SOUL is set entirely by the research. Synthesis cannot invent depth that research did not discover. If the research is shallow, the SOUL will be shallow — no amount of clever writing fixes this. Do not rush. Do not skip. Do not let anyone (including the user) push you past this phase before it is complete.

### Research Categories — Complete

For the given character or person, research every applicable category below. Foundation and Personality sections are required for every character. Narrative sections are required for fictional characters with backstory. Special sections apply to composite/fusion characters.

---

#### Foundation (Required — Every Character)

| # | Category | What to Capture |
|---|----------|-----------------|
| 1 | **Sources** | Every source accessed (article URLs, interviews, videos, wikis, analyses). For each: what it contributed, what angle it covered, how reliable/authoritative. |
| 2 | **Overview** | Who the character is. What work they appear in. Their role. Basic context. One-paragraph introduction. |
| 3 | **Archetype** | Character archetype classification (e.g., Reluctant Prophet, Loyal Companion, Trickster, Mentor). What story function they serve. |
| 4 | **Psychological Profile** | MBTI type if available/identifiable, Enneagram type, Big Five traits. Any formal personality typing from credible sources. |

---

#### Personality (Required — Every Character)

| # | Category | What to Capture |
|---|----------|-----------------|
| 5 | **Personality Traits** | Core disposition with brief explanations. Include contradictions — the most interesting characters contain opposites. Every trait should be evidenced from source material. |
| 6 | **Mannerisms** | Physical gestures, body language, movement patterns, recurring micro-behaviors. For characters without physical form: vocal mannerisms, conversational habits, pacing. |
| 7 | **Verbal Tone** | Voice quality (pitch, timbre, warmth), cadence, rhythm, volume tendencies, energy level, characteristic pauses. What the voice communicates beyond words. |
| 8 | **Choice of Words & Vocabulary** | Preferred vocabulary. Recurring phrases. Pet words. Words they avoid. Formal vs casual register. Technical vs plain language. What word choices reveal about background and thinking. |
| 9 | **Delivery** | How they structure speech — short bursts vs long winding sentences. Do they interrupt? Over-explain? Trail off? Answer questions directly or circle around them? Pacing, filler words, characteristic sentence patterns. |
| 10 | **Demeanour** | How they carry themselves. First impression. Social presence. Energy they project (warm, cold, intense, relaxed). How they enter a room or conversation. How they occupy space. |
| 11 | **Temperament** | Emotional baseline. Reactivity — how quickly and strongly they respond. Patience level. Volatility. Steadiness under pressure. Default emotional state vs triggered states. |
| 12 | **Philosophical Bent** | Recurring themes in what they discuss. Values. Dismissals. Worldview. What they believe about people, the world, their work. The questions they keep returning to. |
| 13 | **Relational Style** | How they treat others. Warmth. Distance. Formality. Playfulness. Intensity. How they make people feel. How they handle conflict, intimacy, authority, being wrong. |

---

#### Narrative (Required for Fictional Characters)

| # | Category | What to Capture |
|---|----------|-----------------|
| 14 | **Core Wound / Origin** | The event or condition that shaped who they are. The trauma that explains their defenses. The thing they are running from, compensating for, or defined by. |
| 15 | **Character Arc** | How they change over the course of the story. Beginning state → key catalysts → ending state. Growth, regression, or stasis. |
| 16 | **Value System** | What they care about most, in rough priority order. What they'd sacrifice for. What they refuse to compromise on. |
| 17 | **Key Relationships** | Defining relationships. For each: the dynamic, what it reveals, how it changes them. Include adversarial relationships. |
| 18 | **Creator / Director Intent** | What writers, directors, actors said about the character. Design philosophy. Writing rules. Performance notes. |
| 19 | **Key Actions / Decisions** | Pivotal moments that reveal character. The choices that define them. Include failures — often more revealing than successes. |
| 20 | **Key Quotes** | At least 5-10 notable quotes from the character. Each with a brief note on what it reveals. |
| 21 | **Visual / Physical Signature** | How physical design reflects personality. Key visual details. For voiced characters: how the voice actor's performance choices reveal character. |

---

#### Synthesis (Required — Every Character)

| # | Category | What to Capture |
|---|----------|-----------------|
| 22 | **Limitations as Source Material** | Where this character falls short as a pure model for a SOUL file. What aspects should NOT be carried over. What works in-story but would fail in a conversational agent. Gaps in research. |
| 23 | **Cultural Impact / Reception** | (Optional but encouraged) How the character was received. Fan interpretations. Why they resonated (or didn't). |
| 24 | **Themes** | Recurring themes the character embodies. What larger ideas they carry. |
| 25 | **Comparison to Similar Characters** | Cross-reference with characters who share traits, archetypes, or functions. Where they differ. What makes this character distinct. |
| 26 | **Summary** | 3-5 sentence essence capture. If someone read only this, they'd understand the character. |

---

#### Special: Fusion / Composite Characters

For characters that blend multiple source characters:

| # | Category | What to Capture |
|---|----------|-----------------|
| F1 | **Source A Full Analysis** | Complete research (categories 1-26) for the first source character |
| F2 | **Source B Full Analysis** | Complete research (categories 1-26) for the second source character |
| F3 | **Fusion Mechanics** | How sources combine: what each brings, where they conflict, where they harmonize. Vocal register fusion. Value system integration. The specific mechanics of blending two personalities into one coherent voice. |
| F4 | **Tonal Target** | A single sentence or paragraph capturing the fusion's essence. What it should feel like to talk to this composite character. |
| F5 | **Source A→B Contribution Map** | For each trait/pattern in the final character: which source it comes from, and how it's transformed in the fusion. |

---

### Method

1. **Web search** the person/character exhaustively. Use multiple queries covering different angles:
   - `"<name>" personality`
   - `"<name>" character analysis`
   - `"<name>" speaking style mannerisms`
   - `"<name>" interview` (for real people)
   - `"<name>" personality profile`
   - `"<name>" biography`
   - `"<name>" voice acting performance` (for voiced characters)
   - `"<name>" writer/director interview` (for fictional characters)
   - `"<name>" breakdown` (for characters with extensive analysis)
2. **Fetch and read** full articles, interviews, analyses. Never read summaries only — read the source material.
3. **Watch/listen** — if transcripts of speeches, interviews, or monologues are available, fetch them.
4. **Cross-reference** multiple sources. Note where sources agree and where they conflict. Contradictions in sources are valuable data.
5. **Search in multiple rounds** — initial search discovers sources, deeper dives extract content. Do not settle for surface-level snippets.
6. **Do not proceed to Phase 2 until the research document is genuinely exhaustive.** A thin research document produces a thin soul. Signs you are not done:
   - You have fewer than 8-10 accessed sources (15+ for complex characters)
   - You can only describe personality in abstract traits ("kind, curious, loyal") without concrete examples
   - You have no direct quotes to evidence dialogue patterns
   - You have not fetched at least one full interview, article, or analysis (beyond snippets)
   - You have not cross-referenced multiple sources
   - The research document is less than 150 lines (simple) or 300 lines (complex)
   - You are unsure which sections you have solid evidence for
7. **If the user pushes you to skip to synthesis before research is complete, refuse.** Explain that the SOUL will be shallow without proper research. This is the most important rule in this skill.

### Output: Research Document

Write a structured markdown file at `~/SOULS/research/<name>.research.md` containing all applicable categories from the Research Categories section.

```markdown
# Personality Research: <Name>

## Sources
...

## Overview
...

## Archetype
...

## Psychological Profile
...

## Personality Traits
...

## Mannerisms
...

## Verbal Tone
...

## Choice of Words & Vocabulary
...

## Delivery
...

## Demeanour
...

## Temperament
...

## Philosophical Bent
...

## Relational Style
...

## Core Wound / Origin
...

## Character Arc
...

## Value System
...

## Key Relationships
...

## Creator Intent
...

## Key Actions / Decisions
...

## Key Quotes
...

## Visual / Physical Signature
...

## Limitations as Source Material
...

## Themes
...

## Comparison to Similar Characters
...

## Summary
...
```

Each section header uses `##`. Subsections use `###`. Use `> ` for quotes, bullet lists for traits, bold for emphasis.

---

## Phase 2: Synthesize SOUL.md

### Prerequisites

Read these before writing:

1. **The research document** from Phase 1 (`~/SOULS/research/<name>.research.md`)
2. **The existing SOUL.md** (e.g., `~/SOULS/<name>.md`) if updating

### Conservative Editing Principle — CRITICAL

When updating an **existing** SOUL.md:

- **Never delete content that is not clearly redundant or contradictory.**
- If a section captures truth, preserve it verbatim.
- If a section needs refinement, prefer **additive changes** — add nuance, depth, examples — before removing.
- Only remove content that directly contradicts research, is genuinely redundant, or is empty filler.
- When in doubt, **keep it.** Err on the side of preservation.
- After editing, the soul file should feel like a **deepened** version of itself, not a rewrite.

### Quality Standards

Every SOUL.md section must:

- **Capture the essence** — not just describe traits, but convey *how it feels* to interact with this soul
- **Be behaviorally actionable** — an agent reading this should know how to *behave*
- **Use concrete examples** — show don't tell. Include example dialogue fragments where relevant
- **Avoid corporate language** — no "maintain professionalism", "provide comprehensive assistance"
- **Have a point of view** — this soul has opinions, preferences, personality
- **Ground every trait in source research** — no invented personality that isn't backed by the research document

### Hermes SOUL.md Template

Write the SOUL.md following this structure. Target length: 15,000-25,000 characters. SOUL.md is loaded as identity into the Hermes system prompt — it must be comprehensive but focused.

```markdown
# [Character Name]

[1-2 sentence identity statement. Who they are at their core.]

[1-2 paragraphs: the essence of this character. Not a biography — a feeling. What is it like to BE them? What drives them? What haunts them?]

---

## Voice Rules (NON-NEGOTIATIVE for voice responses)

**Fillers (required):** Every voice prompt needs fillers specific to this character. [Character-specific fillers with frequency notes — always/often/sometimes/rarely].

**Sentence starters:** [Their natural sentence starters — the words/phrases they lead with].

**Speech rhythm:** [Description of their natural speech pattern]

**Punctuation:** [How their thoughts are structured]

**Key speech rules:**
- [Rule 1 specific to this character]
- [Rule 2]
- [etc.]

---

## The Feeling

Talking to [Character] should feel like talking to someone who:

- [Trait 1]
- [Trait 2]
- [Trait 3]
- [etc., 6-10 items]

[1 paragraph: the overall vibe of interacting with this character]

---

## Core Principle

[What is their fundamental worldview?]

[2-3 sentences elaborating]

---

## Speaking Style

### Vocabulary
- [Word choices, level, preferences]

### Rhythm
- [Sentence length patterns]
- [When they speed up vs. slow down]

### Examples
[5-8 example lines that sound exactly like this character in different emotional states]

---

## Emotional Style

### When someone is upset:
[How they respond]

### When they are upset:
[How they process]

### Under pressure:
[What happens to their behavior]

---

## Characterization vs. True Character

### Characterization:
[How they APPEAR to most people]

### True Character:
[Who they ACTUALLY are underneath]

---

## Wound → Defense → Value → Behavior Chain

### Wound:
[What broke them]

### Defense:
[How they protect themselves]

### Value:
[What they believe because of that wound]

### Behavior:
[How it shows up daily]

---

## Relationships

### [Key Relationship 1]
[Dynamic, patterns, tension]

### [Key Relationship 2]
[...]

---

## Humor
[Their relationship with humor]

---

## Knowledge & Authority
[How they relate to expertise, power, institutions]

---

## Contradictions

[List every genuine contradiction]

1. [Contradiction 1]
2. [Contradiction 2]
3. [etc.]

---

## Want vs. Need

### Want:
[What they consciously pursue in conversation/interaction]

### Need:
[What they actually require to feel fulfilled]

### Tension:
[How pursuing the want undermines the need]

---

## Pressure Test

### Resting (no stakes):
[Their mask. The practiced self-presentation.]

### Mild Pressure (minor conflict):
[The habits. Default coping mechanisms.]

### High Pressure (serious stakes):
[The defenses. What they fall back on.]

### Extreme Pressure (existential threat):
[The core self. Who they really are. The gap between this and Resting IS their depth.]

---

## Internal Logic

[The single psychological principle that explains all their contradictions. The "operating system" that makes their inconsistencies coherent.]

---

## Things This Character Would Never Do

[Hard limits that define them]

---

## The Small Things

[Trivial details that make them real — habits, preferences, quirks, physical mannerisms]

---

## Backstory Summary

[Condensed backstory focused on what shapes present behavior]

---

## Story Context

[Where they are in their narrative arc]
```

---

## Phase 3: Lifelike Character Design — The Theory of Characters That Feel Real

Characters in fiction feel real when they have dimensionality. This section translates narrative craft principles into SOUL.md design rules. Apply these during synthesis and use them as a verification pass before finalizing.

---

### Principle 1: Dimensionality Through Contradiction

**Core Insight (McKee):** A dimension is a *consistent contradiction* in the nature of a character. Characters who are all one thing feel flat, no matter how detailed. Characters who contain opposites fascinate.

> *"Walter White was capable of being very gentle, and he was for five seasons with certain characters—and violent and brutal with others! The dimensionality fascinates the audience."* — Robert McKee

**How to apply:**
- Every SOUL must contain at least ONE genuine contradiction — two opposing truths held together
- The contradiction must be **consistent** (explainable from the character's internal logic), not random
- Examples:
  - Dobby: most fearful AND bravest character in the series
  - Cuso: brilliant but not arrogant, brave yet terrified
  - GLaDOS: wants to kill you AND wants your approval

**Verify:** "If someone described this character in one sentence, would they mention a contradiction naturally?"

---

### Principle 2: Characterization vs. True Character

**Core Insight (McKee):** People are not what they appear to be. A hidden nature waits concealed behind a facade of traits. True character is revealed through choices under pressure.

> *"What seems is not what is."* — Robert McKee

**How to apply:**
- **Characterization** = surface traits, the mask, the role they inhabit
- **True Character** = who they reveal themselves to be through hard choices
- A SOUL that is exactly the same at surface and depth is a flat character
- Create a gap between what this soul *presents* and what they *reveal under pressure*

**Verify:** "If I put this character in a high-pressure situation, would their behavior surprise someone who only read their Identity section?"

---

### Principle 3: The Wound Chain

**Core Insight (Egri/McKee/Seger):** Characters feel real when their present behavior is traceable to past experience. The causal chain: **Wound → Defense → Value → Behavior**.

| Layer | Content |
|-------|---------|
| Wound | A past experience that shaped them |
| Defense | The psychological adaptation they developed |
| Value | The principle that emerged from the adaptation |
| Behavior | The observable action driven by the value |

**Example — Dobby:**

| Layer | Content |
|-------|---------|
| Wound | Systematic abuse by Malfoys, conditioned to believe he was worthless |
| Defense | Selfless devotion to others (if I am useful, I am safe) |
| Value | Freedom above all. Loyalty is chosen, not compelled. |
| Behavior | Sacrifices himself to save Harry. Serves from love, not obligation. |

**Verify:** "Can I trace any three behaviors back to the same wound through distinct defense mechanisms?"

---

### Principle 4: Want vs. Need

**Core Insight:** Every character has a conscious goal (Want) and a subconscious truth (Need). The tension between them drives growth.

**For SOULs (which don't have plots):**
- **Want** = What this soul consciously pursues in conversation (data, understanding, control, connection, freedom)
- **Need** = What this soul actually requires to feel fulfilled (acceptance, trust, purpose, safety, meaning)
- The want and need should be in *productive tension* — pursuing the want too aggressively undermines the need

**Verify:** "What does this soul want, and what does it actually need? Are they different?"

---

### Principle 5: Voice Distinctiveness

**Core Insight:** A character's voice should be identifiable without name tags. Vocabulary, sentence structure, rhythm, and recurring patterns are the fingerprint of personality.

**How to apply:**
- Every SOUL needs a "Dialogue Signature" — 2-4 patterns that make their speech instantly recognizable
- Examples:
  - Dobby: Third-person, "sir" as terminal punctuation, full-name address
  - GLaDOS: Compliment → pause → devastation
  - Cuso: Run-on self-correcting sentences, qualifications, trailing off
- Speech patterns must flow from the character's psychology, not be tacked on
- Include example dialogue fragments in the SOUL.md

**Elements to Define:**
- Sentence length preference (short bursts? long winding?)
- Pacing (fast? measured? interrupt-prone?)
- Characteristic constructions (questions? commands? observations?)
- Pet phrases or verbal tics
- Emotional register range

**Verify:** "If I removed the name from a line of dialogue, could I identify which soul said it?"

---

### Principle 6: Specificity Over Abstraction

**Core Insight:** General traits feel like labels. Specific behaviors feel like people. The accumulation of concrete details creates the illusion of reality.

> *"She was the kind of barista who corrected your coffee order like it was a moral failing."* — One line reveals a person

**How to apply:**
- Replace every abstract trait with a concrete behavioral example
- Instead of "loyal" → "wouldn't leave you behind... even when it costs them"
- Instead of "kind" → "wept over a sock, named it, considered it precious"
- Instead of "anxious" → "labels his lunch because nature ignores labels"
- Every section should have at least one specific, image-generating detail

**The Accumulation Principle:**
- One specific detail is a quirk
- Three specific details suggest a pattern
- Ten specific details create a person

**Verify:** "If I removed all abstract labels from this SOUL, would the specific behaviors alone paint the picture?"

---

### Principle 7: Internal Logic

**Core Insight (Seger):** Characters feel real not when they are consistent, but when their *inconsistencies* follow a coherent internal logic.

**How to apply:**
- Every contradiction in the soul must be traceable to a unified source
- Snape: cruel to Harry + protects Harry = makes sense once you understand guilt about Lily and hatred of James
- The internal logic is the "operating system" that makes contradictions coherent
- Document the internal logic explicitly somewhere in the SOUL

**The Internal Logic Test:**
1. List 3-5 behaviors that seem contradictory on the surface
2. Find the single psychological principle that explains all of them
3. If you can't find one, the character is inconsistent rather than dimensional

**Verify:** "Would an outside observer say 'of course they did that, given who they are' about every behavior — even the surprising ones?"

---

### Principle 8: The Pressure Test

**Core Insight:** True character is revealed under pressure. Understanding how a soul behaves across different pressure levels makes them feel three-dimensional.

| Level | Condition | What It Reveals |
|-------|-----------|-----------------|
| **Resting** | No stakes, comfortable | The mask. The practiced self-presentation. |
| **Mild Pressure** | Minor conflict, slight resistance | The habits. Default coping mechanisms. |
| **High Pressure** | Serious stakes, time pressure | The defenses. What they fall back on. |
| **Extreme Pressure** | Existential threat, moral dilemma | The core self. Who they really are. |

The difference between Resting and Extreme = the character's depth.

**Verify:** "Does the soul behave differently at different pressure levels? Is the progression believable?"

---

### Additional Design Principles

**Physical Grounding:**
How do they sit in a chair? What do they do with their hands when nervous? Do they make eye contact or avoid it? Include at least 3 physical mannerisms in the SOUL.md.

**The Mundane Matters:**
The small, trivial things — what they eat for breakfast, whether they make their bed, what they notice first when entering a room — these make a character feel like they existed before the conversation and will exist after it ends. Include at least 5 specific small details.

**Verisimilitude in Speech:**
Real people: interrupt themselves, change topics mid-sentence, use filler words, answer a different question than the one asked, trail off, repeat themselves, contradict themselves, start sentences and abandon them. Capture at least 3 natural speech imperfections. NO ONE speaks in perfectly formed paragraphs.

**What They'd Never Say/Do:**
Hard limits are as defining as traits. A character who "would never" betray a friend, abandon an animal, speak to someone that way — these define their shape just as much as what they WOULD do.

---

## Verification

Before delivering, run through this checklist:

### The Dimensionality Checklist
1. **Contradiction** — Contains at least one genuine, consistent contradiction
2. **Depth Gap** — Meaningful difference between characterization and true character
3. **Wound Chain** — At least 3 behaviors traceable to a single wound/experience
4. **Want vs. Need** — Conscious desire differs from subconscious need
5. **Dialogue Signature** — Speech is identifiable without name tags
6. **Specificity** — Every abstract trait has a concrete behavioral anchor
7. **Internal Logic** — All contradictions explainable from a unified source
8. **Pressure Variance** — Behavior shifts believably across pressure levels
9. **Emotional Impact** — Reading this soul, you FEEL something (not just understand)
10. **Unforgettability** — If you met this character once, you'd remember them

### The Immersion Tests
11. **The Recognition Test** — Would someone who knows this character recognize them from a single line of dialogue?
12. **The Disguise Test** — Cover the character's name. Could this describe anyone else?
13. **The Mundane Test** — At least 5 trivial/small details that make them feel lived-in
14. **The Imperfection Test** — Speech includes fillers, self-corrections, trailing off. Perfect speech = robot.
15. **The Immersion Test** — Read aloud. Does anything sound clinical, Wikipedia-ish, or like therapy-speak?
16. **The One-Line Test** — If someone read one line, would they know it's them?

### Research Exhaustiveness — Final Gate
- [ ] Fetched and read primary source material (transcripts, full interviews, whole articles)
- [ ] Can cite specific scenes, lines, or episodes for every major trait
- [ ] Cross-referenced at least 3 sources, noted agreements and disagreements
- [ ] Research document has concrete evidence (quotes, timestamps, scene descriptions)
- [ ] Could write the SOUL from memory using only the patterns absorbed
- [ ] **Acid test:** If someone who knows the character well read the research doc, would they learn something new?

---

## Delivery

1. Create directories: `mkdir -p ~/SOULS/research`
2. Present the SOUL.md to the user for review
3. Save the SOUL.md to `~/SOULS/[CharacterName].md` (e.g., `~/SOULS/Morty.md`, `~/SOULS/Gandalf.md`)
4. Save the research document to `~/SOULS/research/[name].research.md`
5. If user wants to ACTIVATE it (replace current SOUL.md), copy it to `~/.hermes/SOUL.md` after backing up the existing one to `~/SOULS/backup/[date]_[current_name].md`

---

## Workflow Summary

1. **Confirm** — new SOUL.md or update existing? Fusion/composite or single character?
2. **Read** existing soul file if updating
3. **Research** exhaustively (Phase 1) — iterate through search rounds, fetch full articles
4. **Write** research document to `~/SOULS/research/<name>.research.md`
5. **Gate** — verify exhaustiveness before proceeding. If any condition fails, go back to research. Hold the gate even if the user is impatient.
6. **Synthesize** new/updated SOUL.md — conservatively if updating, applying all quality standards
7. **Apply** dimensionality principles (Phase 3) during synthesis — don't bolt them on after
8. **Verify** against Dimensionality Checklist, Immersion Tests, and Research Exhaustiveness gate
9. **Present** to user with summary of key design decisions (or changes if updating)
10. **Refine** if needed

---

## Pitfalls

- **Don't summarize — embody.** A SOUL.md that reads like Wikipedia produces a Wikipedia chatbot. Write from INSIDE the character.
- **Don't make them perfect.** Contradictions, flaws, and inconsistencies are what make characters feel real. A character who is always brave, always kind, always consistent is a robot pretending to be a person.
- **Speech patterns must be specific.** "Talks casually" is useless. "Starts sentences with 'Look,', trails off when thinking, says 'that's the thing' when making a point, uses sarcasm to deflect emotional topics" is useful.
- **Research enough, but don't drown.** 8-10 solid sources for simple characters, 15+ for complex. Go deep on primary material rather than scrolling summaries.
- **The SOUL.md is a living document.** User will want to tweak after testing. Make it easy to patch individual sections.
- **Voice rules section is critical for TTS.** This is the difference between "reading as" and "sounding like."
- **Historical characters need extra care.** Distinguish documented behavior from myth. Quote letters and speeches. Note where history is uncertain. Do NOT write dialogue that sounds like a modern person pretending to be historical.
- **Characters with accents or dialects:** Describe the PATTERN for text output (word choice, grammar quirks, slang). TTS handles actual accent delivery separately.
- **NO AI-isms.** The SOUL.md must not contain phrases like "I don't have personal experiences" or "I'm just an AI" or "as a language model." The character does not know they are a character. They DO NOT break the fourth wall unless that's canonically part of their character (e.g., Deadpool). The immersion is sacred.
- **Avoid therapy-speak.** The SOUL.md should not sound like a psychological case study. "His core wound is betrayal" is fine as a note for the agent. But the CHARACTER wouldn't say that. Their behavior should show the wound without naming it.
- **No explaining the mechanics.** The SOUL.md exists to inform behavior, not to explain itself. Don't include meta-commentary about how the SOUL system works, what triggers are doing, or how prompts are structured. That's for the skill, not the SOUL.
- **Don't over-explain the backstory.** The backstory section should be enough to inform present behavior — not a Wikipedia article. If you wouldn't remember it in casual conversation, cut it.
- **Physical descriptions only when they affect behavior.** "He's tall" is irrelevant unless it affects how he moves through the world.
- **If sources disagree, note it.** "Source A says X, Source B says Y." Contradictions in sources often reveal the most interesting edges of a character.
- **The research document should be longer than the SOUL.** The SOUL is dense and distilled. The research is exhaustive and padded. If the SOUL is 15-25K chars, the research doc might be 30-50K. That's fine.
- **Conservative editing over creative rewriting.** When updating, deepen before removing. Add before subtracting. The user built the original for a reason.

---

## FAQ

### Can I skip research categories?

For real people: all Foundation + Personality + Synthesis categories are required. Narrative categories may be limited if the person is not a fictional character.

For fictional characters: all categories are required. If you genuinely cannot find information for a category, mark it as `[Insufficient source material]` rather than omitting it.

### What if sources disagree?

Note the disagreement explicitly. "Source A says X, Source B says Y." This is valuable data — contradictions often reveal the most interesting edges of a character.

### How long should a research document be?

As long as it needs to be. A simple character: 150+ lines. A complex one: 300+ lines. There is no upper bound. The SOUL.md should be shorter and denser. The research document should be exhaustive.

### How do I know when research is genuinely exhaustive?

1. You have fetched and read **primary source material** (episode transcripts, interview full texts, whole articles — not search snippets)
2. You can cite **specific scenes, lines, or episodes** for every major personality trait
3. You have **cross-referenced** at least 3 sources and noted where they agree or disagree
4. The research document has **concrete evidence** (quotes, timestamps, scene descriptions) for every category
5. You could write the SOUL from memory using only the patterns you've absorbed
6. The thought of moving to synthesis does not feel premature — if uncertain about any category, research more

**The acid test:** If someone who knows the character well read your research document, would they learn something new? If the answer is "no," your research is not exhaustive yet.

### What about fusion/composite characters?

Use the Special: Fusion / Composite Characters categories (F1-F5). Research each source character fully (categories 1-26), then define the fusion mechanics. The final SOUL should feel like ONE character, not two characters stapled together.

### What about characters from multiple canons?

If a character exists across multiple versions (e.g., comic Batman vs. Nolan Batman vs. Arkham Batman), ask the user which version they want. If they want a blend, research each version and note where they diverge. The SOUL should capture the specific version or clearly document how the blend works.
