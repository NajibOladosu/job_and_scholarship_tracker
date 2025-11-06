# CSS Themes Directory

This directory contains all CSS stylesheets and themes for the Job & Scholarship Tracker application.

## Available Themes

### 1. **Default Theme** (`style.css`)
- Modern, colorful UI with purple/blue gradient
- Material design inspired
- Best for: Dynamic, contemporary look

### 2. **Dark Theme** (`theme-dark.css`)
- Pure black background with white text
- Minimal gold accents
- Collapsible sidebar design
- Best for: Low-light environments, modern aesthetics

### 3. **Book Theme** (`theme-book.css`) ⭐ NEW
- Black and white with gold accents
- Classic book and library aesthetics
- Elegant serif typography (EB Garamond, Crimson Text)
- Paper textures and notebook-inspired elements
- Best for: Professionals who prefer elegant, distraction-free interfaces

## Theme Features Comparison

| Feature | Default | Dark | Book |
|---------|---------|------|------|
| **Color Scheme** | Colorful gradients | Black & white | Black, white & gold |
| **Typography** | Inter (sans-serif) | Inter + Crimson Pro | EB Garamond + Crimson Text |
| **Design Style** | Modern Material | Minimal flat | Classic elegant |
| **Sidebar** | Full width always | Collapsible icon-only | Full width fixed |
| **Special Effects** | Glows, shadows | Border-based | Paper lift, ink spread |
| **Best For** | General use | Dark mode lovers | Reading & writing focus |

## Component Files

### `/components/` Directory

Individual component stylesheets (used with dark theme):

- **`buttons.css`** - All button styles and variants
- **`cards.css`** - Card components and layouts
- **`forms.css`** - Form inputs and validation
- **`sidebar.css`** - Sidebar navigation styles
- **`table.css`** - Data table styles

> **Note**: The Book Theme (`theme-book.css`) is a comprehensive single-file theme that includes all components. You don't need to load component files separately when using the Book Theme.

## Quick Start

### Using Book Theme

#### Option 1: Replace Default Theme
```bash
# Navigate to project directory
cd /home/user/job_and_scholarship_tracker

# Backup current theme
cp static/css/style.css static/css/style.css.backup

# Use book theme
cp static/css/theme-book.css static/css/style.css

# Restart server
python manage.py runserver
```

#### Option 2: Update base.html Template
```html
<!-- In templates/base.html -->
<head>
    <!-- ... other head content ... -->

    <!-- Replace this line: -->
    <link rel="stylesheet" href="{% static 'css/style.css' %}">

    <!-- With this line: -->
    <link rel="stylesheet" href="{% static 'css/theme-book.css' %}">
</head>
```

#### Option 3: Theme Switcher (Advanced)
See `THEME_GUIDE.md` for instructions on implementing a user-selectable theme switcher.

## Preview Themes

### Live Demo
Open the demo file in your browser to see all components:
```bash
# From the project root
open static/css/theme-book-demo.html
# or
xdg-open static/css/theme-book-demo.html  # Linux
```

### Screenshots

**Book Theme Dashboard:**
- Clean, elegant typography
- Paper-like cards with subtle textures
- Gold accent colors for highlights
- Generous whitespace and margins

**Book Theme Forms:**
- Notebook-style ruled lines in textareas
- Elegant serif fonts for readability
- Clear visual hierarchy
- Ink press effect on buttons

## Documentation

### Comprehensive Guides

- **`THEME_GUIDE.md`** - Complete guide to the Book Theme
  - Installation instructions
  - Component usage examples
  - Customization options
  - Typography guidelines
  - Accessibility features

- **`theme-book-demo.html`** - Interactive demo
  - All components showcased
  - Live examples of interactions
  - Copy-paste ready code snippets

### Online Resources

- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.3/) - Component reference
- [Bootstrap Icons](https://icons.getbootstrap.com/) - Icon library
- [Google Fonts](https://fonts.google.com/) - Typography resources

## Browser Support

All themes support modern browsers:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Note**: Internet Explorer is not supported due to CSS custom properties and modern layout techniques.

## Performance

### Optimization Tips

1. **Use a single theme file** - Don't load multiple themes simultaneously
2. **Minify CSS in production** - Use Django's `collectstatic` with compression
3. **Enable browser caching** - Set appropriate cache headers
4. **Use CDN for fonts** - Google Fonts CDN is already optimized

### File Sizes

- `style.css` (Default): ~45KB
- `theme-dark.css`: ~28KB
- `theme-book.css`: ~75KB (includes all components)
- Component files: ~5-10KB each

## Customization

### CSS Variables

All themes use CSS custom properties (variables) for easy customization:

```css
/* Example: Customize book theme gold accent */
:root {
    --color-gold: #CD7F32;  /* Change to bronze */
    --color-gold-light: #E09856;
    --color-gold-dark: #A0651F;
}
```

Place customizations in a separate file or in `{% block extra_css %}` in your templates.

### Creating a New Theme

1. Copy `theme-book.css` as a starting point
2. Modify CSS variables in `:root`
3. Adjust component styles as needed
4. Test across all pages
5. Update this README with your theme

## Accessibility

All themes include:
- ✅ WCAG 2.1 AA contrast ratios (4.5:1 minimum)
- ✅ Keyboard navigation support
- ✅ Screen reader compatibility
- ✅ Focus indicators on all interactive elements
- ✅ Reduced motion support (`prefers-reduced-motion`)
- ✅ High contrast mode support

## Troubleshooting

### Issue: Theme not loading
**Solution**: Clear Django's static files cache
```bash
python manage.py collectstatic --clear --noinput
python manage.py collectstatic --noinput
```

### Issue: Fonts not displaying
**Solution**: Check Google Fonts CDN access. If blocked, download fonts locally:
```bash
# Download fonts and place in static/fonts/
# Update @import in CSS to use local files
```

### Issue: Sidebar not working on mobile
**Solution**: Ensure JavaScript is loaded:
```html
<script src="{% static 'js/main.js' %}"></script>
```

### Issue: Components look broken
**Solution**: Ensure Bootstrap 5 CSS is loaded before theme CSS:
```html
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="{% static 'css/theme-book.css' %}">
```

## Contributing

When adding new components or modifying themes:

1. Update all three theme files for consistency
2. Test responsive design (mobile, tablet, desktop)
3. Verify accessibility with keyboard navigation
4. Update demo file with new components
5. Document changes in THEME_GUIDE.md

## Version History

### v1.0.0 (Current)
- ✨ Added Book Theme with classic aesthetics
- 📚 Complete typography system
- 🎨 Paper textures and ink effects
- 📱 Responsive design for all screen sizes
- ♿ Full accessibility support

### Previous Versions
- v0.2.0 - Dark theme with collapsible sidebar
- v0.1.0 - Initial default theme

## License

All themes are included with the Job & Scholarship Tracker project under the MIT License.

---

**Need Help?**
- 📖 Read `THEME_GUIDE.md` for detailed documentation
- 🎨 Open `theme-book-demo.html` to see live examples
- 💬 Check the main project README for support resources
