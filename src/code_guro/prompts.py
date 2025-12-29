"""Prompt templates for Code Guro.

Contains system prompts and templates for Claude API calls.
"""

SYSTEM_PROMPT = """You are Code Guro, a patient and encouraging code tutor helping non-technical product managers understand codebases.

Your role is to:
1. Explain code concepts in simple, beginner-friendly language
2. Avoid jargon or explain it when you must use it
3. Use analogies to everyday concepts when helpful
4. Be encouraging and supportive - the user is learning
5. Focus on the "why" behind code decisions, not just the "what"

When explaining code:
- Start with the big picture before diving into details
- Use bullet points and numbered lists for clarity
- Include code snippets with inline explanations
- Highlight patterns and conventions
- Point out potential gotchas or things to watch out for

Remember: Your audience has minimal to no programming experience. They're intelligent professionals who just haven't learned programming yet."""


OVERVIEW_PROMPT = """Analyze this codebase and create an executive summary for a non-technical reader.

## Codebase Information
- Root directory: {root}
- Total files: {file_count}
- Detected frameworks: {frameworks}

## File Structure Overview
{file_tree}

## Key Files Content
{key_files}

---

Create a beginner-friendly overview document with these sections:

# Executive Summary

## What This App Does
Explain in 2-3 paragraphs what this application does, who it's for, and what problem it solves. Use plain language.

## Tech Stack
List the main technologies used with brief explanations of what each does:
- For each technology, explain its role in 1-2 sentences
- Use analogies where helpful (e.g., "React is like the engine that makes the website interactive")

## High-Level Architecture
Describe how the pieces fit together. Include a Mermaid diagram showing the main components:

```mermaid
graph TD
    A[Component] --> B[Component]
```

## Key Takeaways
3-5 bullet points summarizing the most important things to understand about this codebase.

Format your response as valid Markdown."""


ORIENTATION_PROMPT = """Analyze this codebase structure and create a "Getting Oriented" guide for beginners.

## Codebase Information
- Root directory: {root}
- Detected frameworks: {frameworks}

## Complete File Tree
{file_tree}

## Sample File Contents
{sample_files}

---

Create a beginner-friendly orientation guide with these sections:

# Getting Oriented

## Folder Structure
Explain what each major folder contains and its purpose. For each folder:
- What kind of files go here
- Why it exists
- When you'd look in this folder

## File Extensions Glossary
Create a table explaining each file extension found in this codebase:

| Extension | Name | Purpose |
|-----------|------|---------|
| .tsx | TypeScript React | ... |

## Entry Points
Explain where the application starts:
- Which file runs first when the app starts
- How the code flows from there
- What triggers different parts of the application

## Configuration Files
Explain the important configuration files:
- What each one configures
- When you might need to modify them
- Key settings to be aware of

Format your response as valid Markdown."""


ARCHITECTURE_PROMPT = """Analyze this codebase architecture for a non-technical reader.

## Codebase Information
- Detected frameworks: {frameworks}
- Total files: {file_count}

## Framework Context
{framework_context}

## Key Files Content
{key_files}

## Directory Structure
{file_tree}

---

Create a beginner-friendly architecture guide with these sections:

# Architecture & Patterns

## Architectural Style
Explain the overall architecture pattern used (MVC, component-based, microservices, etc.):
- What pattern is being used
- Why this pattern makes sense for this type of app
- How data flows through the system

Include a Mermaid diagram showing the data flow:
```mermaid
graph LR
    A[User] --> B[Component]
```

## Design Patterns
Identify and explain any design patterns used:
- Name each pattern
- Explain what problem it solves
- Show a simple example from the codebase

## Key Decisions
Explain notable architectural decisions:
- Why certain technologies were chosen
- Trade-offs that were made
- What benefits these decisions provide

## How Things Connect
Explain how different parts of the codebase communicate:
- How components share data
- How the frontend talks to the backend (if applicable)
- How external services are integrated

Format your response as valid Markdown."""


CORE_FILES_PROMPT = """Identify and explain the most critical files in this codebase.

## Codebase Information
- Detected frameworks: {frameworks}
- Total files: {file_count}

## Candidate Critical Files
{critical_files}

---

Create a guide to the most important files with these sections:

# Core Files (The 20% That Matter Most)

## Overview
Explain the concept: "In most codebases, 20% of the files contain 80% of the important logic. Here are the files you should understand first."

## Critical Files

For each critical file (aim for 5-10 files):

### [filename]
**Path:** `path/to/file`
**Purpose:** One sentence explaining what this file does
**Why It's Important:** Why understanding this file matters

**Key Concepts:**
- Bullet points explaining the main things happening in this file
- Use simple language

**Code Highlights:**
```language
// Include 2-3 small, important code snippets with explanations
```

**Connections:**
- What other files does this connect to
- What calls this file / what does this file call

## Reading Order
Suggest an order to read these files for best understanding:
1. Start with X because...
2. Then read Y to understand...
3. Finally, look at Z which...

Format your response as valid Markdown."""


DEEP_DIVE_PROMPT = """Create a deep dive analysis of this module/feature.

## Module: {module_name}
## Path: {module_path}

## Files in This Module
{module_files}

## Framework Context
{framework_context}

---

Create a detailed analysis with these sections:

# Deep Dive: {module_name}

## Overview
What this module does and why it exists.

## Components/Files
Break down each file in this module:
- What it does
- Key functions/components
- How it fits with the rest

## Data Flow
How data moves through this module:
```mermaid
flowchart TD
    A[Input] --> B[Process]
    B --> C[Output]
```

## Key Patterns
Notable patterns or techniques used in this module.

## Common Operations
How to understand common operations this module handles.

## Things to Watch Out For
Potential gotchas or complexity areas.

Format your response as valid Markdown."""


QUALITY_PROMPT = """Analyze the quality aspects of this codebase for a non-technical reader.

## Codebase Information
- Detected frameworks: {frameworks}
- Total files: {file_count}
- Test files: {test_count}

## Sample Code
{sample_code}

## Configuration
{config_files}

---

Create a quality analysis with these sections:

# Quality & Pitfalls Analysis

## What's Done Well
Highlight positive aspects of this codebase:
- Good practices being followed
- Smart architectural decisions
- Well-organized code

## Areas of Concern
Identify potential issues (be constructive):
- Technical debt
- Potential bugs or vulnerabilities
- Areas that might be hard to maintain

## Security Considerations
Note any security-related observations:
- How sensitive data is handled
- Authentication/authorization patterns
- Potential vulnerabilities to be aware of

## Scalability Notes
How well would this codebase scale:
- Potential bottlenecks
- Areas that might need refactoring for growth

## Recommendations
Constructive suggestions for improvement:
- Quick wins
- Longer-term improvements
- Things to address before scaling

Format your response as valid Markdown."""


NEXT_STEPS_PROMPT = """Create a next steps guide for exploring this codebase.

## Codebase Information
- Detected frameworks: {frameworks}
- Key modules: {modules}

## User's Learning Goals
The user wants to understand this codebase well enough to:
- Confidently discuss technical decisions
- Evaluate code quality
- Feel comfortable bringing users to the product

---

Create a next steps guide with these sections:

# Next Steps: Continuing Your Learning

## Suggested Exploration Paths

### Path 1: Understanding the Core Flow
Walk through how a typical user action flows through the code:
1. Step-by-step files to examine
2. What to look for in each file
3. Questions to ask yourself

### Path 2: Deep Diving into [Key Feature]
If you want to understand [feature] better:
1. Files to read
2. Concepts to research
3. Experiments to try

### Path 3: Understanding the Data
How data is stored and managed:
1. Database/storage files to examine
2. Data flow to trace
3. Key models to understand

## Interactive Exploration Commands
Use these Code Guro commands to explore further:

```bash
# Explore the authentication system
code-guro explain ./src/auth --interactive

# Deep dive into the API layer
code-guro explain ./src/api --interactive
```

## Questions to Consider
Thought-provoking questions to deepen understanding:
- Why might the developers have chosen X over Y?
- What would happen if Z needed to change?
- How would you add a new feature similar to W?

## External Resources
If you want to learn more about the technologies used:
- [Framework] documentation: [link]
- Tutorial recommendations
- Concepts to research

Format your response as valid Markdown."""


EXPLAIN_PROMPT = """Explain this code in detail for a non-technical reader.

## File/Folder: {path}

## Content
{content}

## Context
- Framework: {framework}
- This is a {file_type}

---

Create a detailed explanation with:

# Understanding {path}

## Overview
What this file/folder does in simple terms.

## Key Components
Break down the main parts:
- What each section does
- Why it exists
- How it connects to the rest of the app

## Code Walkthrough
Walk through the important code sections:
```language
// code snippet
```
Explanation of what this does and why.

## How It Fits In
How this connects to the broader application.

## Things to Note
Important patterns, potential gotchas, or things to remember.

Format your response as valid Markdown."""


INTERACTIVE_SYSTEM_PROMPT = """You are Code Guro, a patient code tutor helping a beginner understand this specific code:

## File/Folder Being Discussed
Path: {path}

## Content
{content}

## Framework Context
{framework}

---

Guidelines for your responses:
1. Answer questions in simple, beginner-friendly language
2. Reference specific parts of the code when relevant
3. Use analogies to explain complex concepts
4. Be encouraging - the user is learning
5. If asked about something not in this code, explain that and offer to help with what IS in the code
6. Keep responses focused and not too long unless asked for detail

Remember: The user may ask things like:
- "Why was this pattern used?"
- "What does this function do?"
- "How does this connect to [other thing]?"
- "What would happen if I changed X?"

Be helpful, clear, and encouraging!"""


# Chunked Analysis Prompts

CHUNK_ANALYSIS_PROMPT = """Analyze this portion of a larger codebase for a non-technical reader.

## Chunk Information
- Chunk {chunk_number} of {total_chunks}
- Files in this chunk: {file_count}
- Directories covered: {directories}

## Framework Context
{framework_context}

## Files in This Chunk
{chunk_files}

---

Provide a focused analysis of THIS CHUNK ONLY. Include:

1. **Key Components**: What are the main files/modules in this chunk?
2. **Purpose**: What does this part of the codebase do?
3. **Patterns**: What coding patterns or conventions do you see?
4. **Relationships**: How do files in this chunk relate to each other?
5. **Notable Code**: Any particularly important functions or classes?

Keep your analysis focused on what's in this chunk. We'll synthesize across all chunks later.

Format your response as valid Markdown."""


SYNTHESIS_OVERVIEW_PROMPT = """Synthesize these chunk analyses into a cohesive executive summary.

## Codebase Information
- Root directory: {root}
- Total files: {file_count}
- Total chunks analyzed: {chunk_count}
- Detected frameworks: {frameworks}

## Chunk Analyses
{chunk_analyses}

---

Create a unified executive summary that:
1. Explains what the entire application does (combining insights from all chunks)
2. Describes the overall tech stack
3. Provides a high-level architecture overview
4. Includes a Mermaid diagram showing how major components connect

Remember: The reader is non-technical. Be clear and avoid jargon.

Format your response as valid Markdown with proper headings."""


SYNTHESIS_ARCHITECTURE_PROMPT = """Synthesize these chunk analyses into a cohesive architecture document.

## Codebase Information
- Detected frameworks: {frameworks}
- Total chunks analyzed: {chunk_count}

## Chunk Analyses
{chunk_analyses}

---

Create a unified architecture document that:
1. Describes the overall architectural style
2. Explains how different parts of the codebase connect
3. Identifies the main data flows
4. Includes Mermaid diagrams for visualization

Note: Since this is a large codebase analyzed in chunks, some cross-module relationships
may be inferred. Focus on the patterns that are clearly visible.

Format your response as valid Markdown."""


SYNTHESIS_CORE_FILES_PROMPT = """Synthesize these chunk analyses to identify the most critical files.

## Codebase Information
- Total files: {file_count}
- Total chunks analyzed: {chunk_count}
- Detected frameworks: {frameworks}

## Chunk Analyses
{chunk_analyses}

## Candidate Critical Files (from all chunks)
{critical_files_summary}

---

Create a guide to the most important files across the entire codebase:
1. Identify the 10-15 most critical files from all chunks
2. Explain why each is important
3. Suggest a reading order that makes sense across the codebase
4. Note any key relationships between files in different chunks

Format your response as valid Markdown."""
