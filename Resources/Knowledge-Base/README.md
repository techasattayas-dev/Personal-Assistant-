# Knowledge Base

## Overview

This Knowledge Base uses the **Zettelkasten method** for building interconnected, atomic notes that grow into a personal knowledge network over time.

## Structure

### Fleeting-Notes/
**Purpose**: Quick captures and temporary thoughts

- Capture ideas immediately as they come
- Don't worry about structure or connections
- Process within 7 days into permanent notes or discard
- Use these as an inbox for thoughts

**When to use**: During meetings, reading, brainstorming, or when inspiration strikes

### Literature-Notes/
**Purpose**: Summaries and insights from external sources

- Books you've read
- Articles and blog posts
- Videos and podcasts
- Research papers
- Courses and lectures

**Format**: Source citation + key takeaways + your thoughts

### Permanent-Notes/
**Purpose**: Atomic, well-developed concepts

- One idea per note
- Written in your own words
- Highly interconnected via wiki-links
- Standalone and evergreen
- Forms the core of your knowledge system

## Zettelkasten Principles

### 1. Atomicity
Each note contains ONE idea. If a note covers multiple concepts, split it into multiple notes.

### 2. Autonomy
Each note should be understandable on its own, without needing to read other notes first.

### 3. Connectivity
Notes gain value through connections. Link liberally using `[[note-name]]` syntax.

### 4. Evergreen
Write notes to last. Use timeless language. Update rather than create duplicates.

## Naming Convention

Use descriptive names that capture the core concept:
- `habit-formation-requires-environmental-design.md`
- `compound-interest-in-learning.md`
- `feedback-loops-in-systems-thinking.md`

**Avoid**:
- Generic names like `note1.md` or `thoughts.md`
- Dates in filenames (use YAML frontmatter instead)
- Overly long names (keep under 50 characters)

## Linking Notes

Use wiki-style links to connect ideas:

```markdown
This concept relates to [[compound-interest-in-learning]] and is
supported by research in [[habit-formation-requires-environmental-design]].
```

## YAML Frontmatter Template

```yaml
---
title: Note Title
created: 2026-03-11
tags: [tag1, tag2, tag3]
type: permanent | literature | fleeting
source: (for literature notes - book/article/url)
---
```

## Workflow

### 1. Capture (Fleeting Notes)
When you encounter an idea:
- Create a fleeting note immediately
- Keep it brief, just enough to remember the thought
- Don't worry about formatting or connections

### 2. Process (Literature Notes)
When consuming content:
- Take literature notes with key insights
- Include source information
- Add your own thoughts and reactions
- Identify concepts worth developing into permanent notes

### 3. Develop (Permanent Notes)
Regularly (daily or weekly):
- Review fleeting and literature notes
- Extract concepts worth remembering
- Create permanent notes in your own words
- Add connections to existing notes
- Delete or archive processed fleeting notes

### 4. Connect
As your knowledge base grows:
- Look for unexpected connections
- Create index notes for major topics
- Build concept maps
- Follow link trails to discover insights

## Index Notes

Create index notes for major topics to serve as entry points:
- `_index-productivity.md` - Collects all productivity-related notes
- `_index-learning.md` - Learning and education concepts
- `_index-technology.md` - Tech notes and resources

(Use `_` prefix to sort index notes to the top)

## Tags

Use tags sparingly for broad categorization:
- `#concept` - Theoretical ideas
- `#practice` - Actionable techniques
- `#resource` - Tools and references
- `#question` - Open questions to explore

## Best Practices

### Do:
- ✅ Write in your own words (aids understanding)
- ✅ Link notes liberally (builds connections)
- ✅ Keep notes atomic (one idea per note)
- ✅ Update notes as understanding evolves
- ✅ Review and process regularly

### Don't:
- ❌ Copy/paste without understanding
- ❌ Create isolated notes without links
- ❌ Let fleeting notes pile up unprocessed
- ❌ Worry about perfect organization upfront
- ❌ Create complex folder hierarchies

## Examples

### Fleeting Note Example
```markdown
---
title: Idea about habit streaks
created: 2026-03-11
type: fleeting
---

Don't break the chain method - visual streak tracking helps maintain habits.
Jerry Seinfeld's method. Could apply to my writing goal.
```

### Literature Note Example
```markdown
---
title: Atomic Habits - James Clear
created: 2026-03-11
type: literature
source: "Clear, James. Atomic Habits. 2018."
tags: [habits, productivity, book]
---

## Key Insights

- Habits are the compound interest of self-improvement
- Focus on systems, not goals
- Four laws: Make it obvious, attractive, easy, satisfying
- Identity-based habits are more powerful than outcome-based

## My Thoughts

This connects to [[habit-formation-requires-environmental-design]].
The idea of identity-based habits is particularly powerful - "I am a writer"
vs "I want to write a book".

Could apply the four laws to [[my-morning-routine]].
```

### Permanent Note Example
```markdown
---
title: Systems thinking beats goal thinking
created: 2026-03-11
type: permanent
tags: [productivity, systems, mental-models]
---

# Systems Thinking Beats Goal Thinking

Goals are about the destination; systems are about the journey.

Problem with goals:
- Winners and losers have the same goals
- Goals are momentary; what happens after achievement?
- Goals create happiness dependency
- Goals conflict with long-term progress

Systems are better:
- Focus on process, not outcome
- Sustainable and continuous
- Provide direction without constrictive endpoints
- Build identity and lasting change

Related: [[atomic-habits-summary]] [[feedback-loops-in-systems-thinking]]

## Application

Rather than "goal: lose 20 pounds", create a system:
"I am someone who moves 30 minutes daily and eats home-cooked meals"

## Sources

- [[atomic-habits-james-clear]]
- Personal experience with goal failure
```

## Getting Started

1. **Start with fleeting notes** - Just begin capturing ideas
2. **Process weekly** - Convert fleeting → permanent regularly
3. **Don't over-organize** - Let connections emerge organically
4. **Link as you write** - Create connections while writing new notes
5. **Review monthly** - Read random notes, discover connections

## Tools

This knowledge base works with:
- **Any text editor** (VS Code, Vim, Sublime)
- **Obsidian** (specialized PKM tool with graph view)
- **Notion** (can sync via integration)
- **Plain markdown** (future-proof, never locked in)

---

**Last Updated**: 2026-03-11
**Total Notes**: 0
**Next Review**: 2026-03-18
