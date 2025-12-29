"""Framework detection for Code Guro.

Detects common frameworks and provides framework-specific context.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class FrameworkInfo:
    """Information about a detected framework."""

    name: str
    version: Optional[str] = None
    description: str = ""
    architecture: str = ""
    conventions: List[str] = field(default_factory=list)
    gotchas: List[str] = field(default_factory=list)
    key_files: List[str] = field(default_factory=list)


# Framework metadata for enhanced documentation
FRAMEWORK_METADATA = {
    "nextjs": FrameworkInfo(
        name="Next.js",
        description="React framework for production with server-side rendering and static generation",
        architecture="Next.js uses file-based routing where files in the app/ or pages/ directory automatically become routes. It supports both Server Components (default) and Client Components.",
        conventions=[
            "Files named page.tsx become route pages",
            "Files named layout.tsx wrap pages with shared UI",
            "Files named loading.tsx show loading states",
            "Files named error.tsx handle errors",
            "The 'use client' directive marks Client Components",
            "API routes go in app/api/ directory",
        ],
        gotchas=[
            "Server Components cannot use hooks or browser APIs",
            "Client Components need 'use client' at the top of the file",
            "Data fetching in Server Components is different from Client Components",
            "Be careful mixing server and client code",
        ],
        key_files=["next.config.js", "next.config.mjs", "app/layout.tsx", "app/page.tsx"],
    ),
    "react": FrameworkInfo(
        name="React",
        description="JavaScript library for building user interfaces with components",
        architecture="React uses a component-based architecture where UI is broken into reusable pieces. Components can manage their own state and receive data through props.",
        conventions=[
            "Components are typically PascalCase (e.g., MyComponent)",
            "Custom hooks start with 'use' (e.g., useMyHook)",
            "State management via useState, useReducer, or external libraries",
            "Side effects handled in useEffect",
        ],
        gotchas=[
            "Hooks must be called at the top level (Rules of Hooks)",
            "State updates are asynchronous",
            "useEffect runs after every render by default",
            "Forgetting dependency arrays can cause infinite loops",
        ],
        key_files=["src/App.jsx", "src/App.tsx", "src/index.jsx", "src/index.tsx"],
    ),
    "vue": FrameworkInfo(
        name="Vue.js",
        description="Progressive JavaScript framework for building user interfaces",
        architecture="Vue uses a component-based architecture with Single File Components (.vue files) that combine template, script, and style in one file.",
        conventions=[
            "Components use .vue extension (Single File Components)",
            "Options API uses data(), methods, computed, etc.",
            "Composition API uses setup() with ref() and reactive()",
            "Props passed with v-bind or : shorthand",
            "Events emitted with v-on or @ shorthand",
        ],
        gotchas=[
            "Reactivity requires using ref() or reactive() in Composition API",
            "Arrays need special handling for reactivity",
            "v-if and v-for shouldn't be on same element",
            "Props should not be mutated directly",
        ],
        key_files=["src/App.vue", "src/main.js", "src/main.ts", "vite.config.js"],
    ),
    "django": FrameworkInfo(
        name="Django",
        description="High-level Python web framework following the MTV pattern",
        architecture="Django follows MTV (Model-Template-View) architecture. Models define database schema, Views handle business logic, and Templates render HTML.",
        conventions=[
            "Models in models.py define database tables",
            "Views in views.py handle HTTP requests",
            "URLs in urls.py map routes to views",
            "Templates in templates/ directory render HTML",
            "Static files go in static/ directory",
            "Apps are self-contained modules with their own models/views/urls",
        ],
        gotchas=[
            "N+1 query problems - use select_related/prefetch_related",
            "Migration conflicts when multiple developers change models",
            "CSRF tokens required for POST forms",
            "Remember to run migrations after model changes",
        ],
        key_files=["manage.py", "settings.py", "urls.py", "wsgi.py", "asgi.py"],
    ),
    "flask": FrameworkInfo(
        name="Flask",
        description="Lightweight Python web framework with minimal dependencies",
        architecture="Flask is a microframework that gives you flexibility in how you structure your app. It uses decorators to define routes and supports extensions for additional functionality.",
        conventions=[
            "Routes defined with @app.route() decorator",
            "Application factory pattern for larger apps",
            "Blueprints for modular applications",
            "Templates use Jinja2 templating",
            "Configuration via app.config",
        ],
        gotchas=[
            "Debug mode should never be on in production",
            "Request context required for request/session access",
            "Application context needed for current_app access",
            "Be careful with circular imports",
        ],
        key_files=["app.py", "wsgi.py", "config.py", "requirements.txt"],
    ),
    "express": FrameworkInfo(
        name="Express.js",
        description="Fast, unopinionated web framework for Node.js",
        architecture="Express uses middleware-based architecture. Requests flow through a chain of middleware functions that can modify request/response or end the cycle.",
        conventions=[
            "Middleware functions have (req, res, next) signature",
            "Routes defined with app.get(), app.post(), etc.",
            "Error handling middleware has 4 parameters",
            "Router for modular route handling",
            "Static files served with express.static()",
        ],
        gotchas=[
            "Middleware order matters - they execute sequentially",
            "Always call next() or send response to avoid hanging",
            "Error handling middleware must have 4 parameters",
            "Async errors need to be caught and passed to next()",
        ],
        key_files=["app.js", "server.js", "index.js", "routes/"],
    ),
    "rails": FrameworkInfo(
        name="Ruby on Rails",
        description="Full-stack Ruby web framework following MVC and convention over configuration",
        architecture="Rails follows MVC (Model-View-Controller) with strong conventions. Models inherit from ApplicationRecord, Controllers from ApplicationController, and Views are ERB templates.",
        conventions=[
            "Models are singular (User), tables are plural (users)",
            "Controllers are plural (UsersController)",
            "RESTful routes by default",
            "Migrations for database schema changes",
            "Helpers for view logic",
            "Concerns for shared behavior",
        ],
        gotchas=[
            "N+1 queries - use includes() or eager_load()",
            "Strong parameters required for mass assignment",
            "Callbacks can make debugging difficult",
            "Asset pipeline behavior differs in development vs production",
        ],
        key_files=[
            "config/routes.rb",
            "app/controllers/application_controller.rb",
            "app/models/application_record.rb",
            "Gemfile",
        ],
    ),
}


def detect_nextjs(root: Path) -> Optional[FrameworkInfo]:
    """Detect Next.js framework."""
    package_json = root / "package.json"
    if not package_json.exists():
        return None

    try:
        with open(package_json, "r") as f:
            pkg = json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

    if "next" in deps:
        info = FRAMEWORK_METADATA["nextjs"]
        info.version = deps.get("next", "").lstrip("^~")

        # Check for App Router vs Pages Router
        if (root / "app").exists():
            info.conventions.insert(0, "Using App Router (app/ directory)")
        elif (root / "pages").exists():
            info.conventions.insert(0, "Using Pages Router (pages/ directory)")

        return info

    return None


def detect_react(root: Path) -> Optional[FrameworkInfo]:
    """Detect React library."""
    package_json = root / "package.json"
    if not package_json.exists():
        return None

    try:
        with open(package_json, "r") as f:
            pkg = json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

    if "react" in deps:
        info = FRAMEWORK_METADATA["react"]
        info.version = deps.get("react", "").lstrip("^~")
        return info

    return None


def detect_vue(root: Path) -> Optional[FrameworkInfo]:
    """Detect Vue.js framework."""
    package_json = root / "package.json"
    if not package_json.exists():
        return None

    try:
        with open(package_json, "r") as f:
            pkg = json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

    if "vue" in deps:
        info = FRAMEWORK_METADATA["vue"]
        info.version = deps.get("vue", "").lstrip("^~")
        return info

    # Check for .vue files
    for path in root.rglob("*.vue"):
        return FRAMEWORK_METADATA["vue"]

    return None


def detect_django(root: Path) -> Optional[FrameworkInfo]:
    """Detect Django framework."""
    # Check for manage.py
    if not (root / "manage.py").exists():
        return None

    # Check requirements.txt
    requirements = root / "requirements.txt"
    if requirements.exists():
        try:
            content = requirements.read_text().lower()
            if "django" in content:
                return FRAMEWORK_METADATA["django"]
        except IOError:
            pass

    # Check for settings.py pattern
    for settings in root.rglob("settings.py"):
        try:
            content = settings.read_text()
            if "INSTALLED_APPS" in content or "Django" in content:
                return FRAMEWORK_METADATA["django"]
        except IOError:
            continue

    return None


def detect_flask(root: Path) -> Optional[FrameworkInfo]:
    """Detect Flask framework."""
    # Check requirements.txt
    requirements = root / "requirements.txt"
    if requirements.exists():
        try:
            content = requirements.read_text().lower()
            if "flask" in content:
                return FRAMEWORK_METADATA["flask"]
        except IOError:
            pass

    # Check for Flask app patterns
    for py_file in ["app.py", "wsgi.py", "main.py"]:
        filepath = root / py_file
        if filepath.exists():
            try:
                content = filepath.read_text()
                if "Flask(" in content or "from flask import" in content:
                    return FRAMEWORK_METADATA["flask"]
            except IOError:
                continue

    return None


def detect_express(root: Path) -> Optional[FrameworkInfo]:
    """Detect Express.js framework."""
    package_json = root / "package.json"
    if not package_json.exists():
        return None

    try:
        with open(package_json, "r") as f:
            pkg = json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

    if "express" in deps:
        info = FRAMEWORK_METADATA["express"]
        info.version = deps.get("express", "").lstrip("^~")
        return info

    return None


def detect_rails(root: Path) -> Optional[FrameworkInfo]:
    """Detect Ruby on Rails framework."""
    gemfile = root / "Gemfile"
    if not gemfile.exists():
        return None

    try:
        content = gemfile.read_text()
        if "rails" in content.lower():
            # Check for routes.rb to confirm
            if (root / "config" / "routes.rb").exists():
                return FRAMEWORK_METADATA["rails"]
    except IOError:
        pass

    return None


def detect_frameworks(root: Path) -> List[FrameworkInfo]:
    """Detect all frameworks used in a codebase.

    Args:
        root: Root directory of the codebase

    Returns:
        List of detected frameworks
    """
    root = Path(root).resolve()
    frameworks = []

    detectors = [
        detect_nextjs,  # Check Next.js before React (more specific)
        detect_react,
        detect_vue,
        detect_django,
        detect_flask,
        detect_express,
        detect_rails,
    ]

    for detector in detectors:
        result = detector(root)
        if result:
            frameworks.append(result)

    return frameworks


def get_framework_context(frameworks: List[FrameworkInfo]) -> str:
    """Generate framework-specific context for documentation.

    Args:
        frameworks: List of detected frameworks

    Returns:
        Markdown string with framework information
    """
    if not frameworks:
        return ""

    sections = []

    for fw in frameworks:
        section = f"## {fw.name}"
        if fw.version:
            section += f" (v{fw.version})"
        section += "\n\n"

        if fw.description:
            section += f"{fw.description}\n\n"

        if fw.architecture:
            section += f"### Architecture\n\n{fw.architecture}\n\n"

        if fw.conventions:
            section += "### Conventions\n\n"
            for conv in fw.conventions:
                section += f"- {conv}\n"
            section += "\n"

        if fw.gotchas:
            section += "### Common Gotchas\n\n"
            for gotcha in fw.gotchas:
                section += f"- {gotcha}\n"
            section += "\n"

        sections.append(section)

    return "\n".join(sections)
