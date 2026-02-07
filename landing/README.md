# Landing Page

This directory contains the marketing landing page for Code Guro.

## Overview

- **File**: `index.html` - Self-contained landing page with inline CSS and JavaScript
- **Purpose**: Marketing and product showcase page for codeguro.com
- **Design**: Modern, minimal design with light/dark theme toggle
- **Dependencies**: None (all styles and scripts are inline, fonts loaded from Google Fonts CDN)

## Assets

The landing page uses logo assets from the `assets/` subdirectory:
- `assets/logo-light.png` - Logo for light theme
- `assets/logo-dark.png` - Logo for dark theme

These are copies of the optimized logos from the main `assets/` directory.

## Features

- **Responsive Design**: Mobile-first approach with responsive breakpoints
- **Theme Toggle**: Light/dark mode with system preference detection
- **Smooth Animations**: Scroll-based reveal animations (respects `prefers-reduced-motion`)
- **SEO Optimized**: Proper meta tags, semantic HTML, and accessibility features
- **Performance**: Inline critical CSS, minimal external dependencies

## Local Development

To preview the landing page locally:

```bash
# Option 1: Using Python's built-in server
cd landing
python3 -m http.server 8000
# Open http://localhost:8000 in your browser

# Option 2: Open directly in browser
open index.html
```

## Deployment

This landing page is intended for static hosting (GitHub Pages, Netlify, Vercel, etc.). It requires no build step or server-side processing.

### GitHub Pages Deployment

The landing page can be deployed to GitHub Pages by:
1. Configuring GitHub Pages to serve from the `landing/` directory
2. Accessing at: `https://nicoladevera.github.io/code-guro/`

## Content Sections

1. **Hero**: Main headline and installation CTA
2. **Problem**: Why Code Guro exists
3. **Solution**: How Code Guro helps
4. **How It Works**: 3-step process (Configure, Analyze, Explore)
5. **Providers**: LLM provider logos (Anthropic, OpenAI, Google)
6. **Footer**: Links to docs, GitHub, PyPI

## Maintenance

When updating the landing page:
- Keep the file self-contained (inline CSS/JS)
- Test both light and dark themes
- Verify responsive design on mobile devices
- Check accessibility with screen readers
- Validate HTML and ensure SEO meta tags are current

## Related Files

- Main project README: `../README.md`
- Logo assets (source): `../assets/logo-code-guro-*-small.png`
- Documentation screenshots: `../assets/screenshot-*.png`
