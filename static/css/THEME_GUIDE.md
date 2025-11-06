# Book Theme Guide

## Overview

The **Book Theme** is an elegant, sophisticated design system inspired by classic literature, beautiful notebooks, and timeless libraries. It features a pure black and white aesthetic with minimal gold accents, creating a distraction-free environment perfect for managing your job and scholarship applications.

## Design Philosophy

### Inspiration Sources
- **Classic Books**: EB Garamond typography, generous margins, elegant spacing
- **Notebooks**: Moleskine-inspired layouts with subtle ruled lines
- **Libraries**: Card catalog navigation, index card aesthetics
- **Manuscripts**: Paper textures, ink effects, serif typography
- **Writing Desks**: Clean, organized, professional appearance

### Color Palette

#### Primary Colors
- **Ink Black**: `#000000` - Main text and important elements
- **Paper White**: `#FFFFFF` - Backgrounds and cards
- **Cream**: `#F8F7F4` - Page background with subtle texture

#### Accent Colors
- **Gold**: `#D4AF37` - Primary accent (borders, hover states, active links)
- **Sepia**: `#8B7355` - Secondary accent (links, muted highlights)

#### Grayscale
- Sophisticated 9-step grayscale from white to black
- Used for borders, shadows, and secondary text

## Installation & Usage

### Method 1: Replace Default Theme (Recommended)

1. **Backup current style.css**:
   ```bash
   cp static/css/style.css static/css/style.css.backup
   ```

2. **Replace with book theme**:
   ```bash
   cp static/css/theme-book.css static/css/style.css
   ```

3. **Restart Django server**:
   ```bash
   python manage.py runserver
   ```

### Method 2: Add as Alternative Theme

1. **Update base.html** to include theme switcher:
   ```html
   <head>
       <!-- ... existing head content ... -->

       <!-- Default Theme -->
       <link rel="stylesheet" href="{% static 'css/style.css' %}" id="theme-default">

       <!-- Book Theme (optional) -->
       <!-- <link rel="stylesheet" href="{% static 'css/theme-book.css' %}" id="theme-book"> -->
   </head>
   ```

2. **Add theme toggle button** in topbar:
   ```html
   <button id="theme-toggle" class="topbar-action-btn" title="Toggle Theme">
       <i class="bi bi-book"></i>
   </button>
   ```

3. **Add theme switcher JavaScript**:
   ```javascript
   // In static/js/main.js or new file
   document.getElementById('theme-toggle')?.addEventListener('click', function() {
       const defaultTheme = document.getElementById('theme-default');
       const bookTheme = document.getElementById('theme-book');

       if (defaultTheme.disabled) {
           defaultTheme.disabled = false;
           bookTheme.disabled = true;
           localStorage.setItem('theme', 'default');
       } else {
           defaultTheme.disabled = true;
           bookTheme.disabled = false;
           localStorage.setItem('theme', 'book');
       }
   });

   // Load saved theme preference
   window.addEventListener('DOMContentLoaded', function() {
       const savedTheme = localStorage.getItem('theme');
       if (savedTheme === 'book') {
           document.getElementById('theme-default').disabled = true;
           document.getElementById('theme-book').disabled = false;
       }
   });
   ```

### Method 3: Django Template Setting

Create a user preference in your Django models:

```python
# accounts/models.py
class User(AbstractUser):
    # ... existing fields ...
    theme_preference = models.CharField(
        max_length=20,
        choices=[
            ('default', 'Modern'),
            ('dark', 'Dark'),
            ('book', 'Book'),
        ],
        default='default'
    )
```

Then in `base.html`:
```html
<link rel="stylesheet" href="{% static 'css/theme-' %}{{ user.theme_preference|default:'default' }}.css">
```

## Typography

### Font Families

#### Display & Headings
```css
font-family: 'EB Garamond', 'Crimson Text', Georgia, serif;
```
- Used for: H1-H6, brand name, large titles
- Characteristics: Elegant, classic, highly readable
- Perfect for: Chapter headings, page titles

#### Body Text
```css
font-family: 'Crimson Text', 'Libre Baskerville', Georgia, serif;
```
- Used for: Paragraphs, card content, descriptions
- Characteristics: Comfortable for extended reading
- Perfect for: Application descriptions, notes, content

#### UI Elements
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```
- Used for: Navigation, labels, form fields
- Characteristics: Clean, modern, functional
- Perfect for: Buttons, labels, system UI

#### Code & Dates
```css
font-family: 'IBM Plex Mono', 'SF Mono', Monaco, Consolas, monospace;
```
- Used for: Dates, deadlines, technical info
- Characteristics: Tabular, precise, typewriter-like
- Perfect for: Timestamps, IDs, code snippets

### Type Scale

```
--text-xs:    0.75rem  (12px) - Labels, captions
--text-sm:    0.875rem (14px) - UI elements, secondary text
--text-base:  1rem     (16px) - Body text
--text-lg:    1.125rem (18px) - Emphasized text
--text-xl:    1.25rem  (20px) - Small headings
--text-2xl:   1.5rem   (24px) - Section headings
--text-3xl:   1.875rem (30px) - Page headings
--text-4xl:   2.25rem  (36px) - Major headings
--text-5xl:   3rem     (48px) - Hero headings
--text-6xl:   3.75rem  (60px) - Display text
```

## Components

### Cards

#### Standard Card
```html
<div class="card">
    <div class="card-header">
        <h3>Card Title</h3>
    </div>
    <div class="card-body">
        <p>Card content with paper-like texture and subtle shadows.</p>
    </div>
    <div class="card-footer">
        <button class="btn btn-primary">Action</button>
    </div>
</div>
```

#### Card with Folded Corner
```html
<div class="card card-folded">
    <div class="card-body">
        <p>This card has a folded corner effect that appears on hover.</p>
    </div>
</div>
```

#### Stats Card (Dashboard Metrics)
```html
<div class="stats-card">
    <div class="stats-icon">
        <i class="bi bi-briefcase"></i>
    </div>
    <div class="stats-value">12</div>
    <div class="stats-label">Applications</div>
</div>
```

#### Application Card
```html
<div class="application-card">
    <h5><a href="#">Senior Software Engineer</a></h5>
    <p class="text-muted">Tech Company Inc. • San Francisco, CA</p>
    <div class="d-flex gap-2">
        <span class="badge badge-primary">Job</span>
        <span class="badge badge-warning">In Progress</span>
    </div>
</div>
```

### Buttons

#### Button Variants
```html
<!-- Primary (Gold accent) -->
<button class="btn btn-primary">Apply Now</button>

<!-- Secondary (Black/White) -->
<button class="btn btn-secondary">Cancel</button>

<!-- Success (Green) -->
<button class="btn btn-success">Save</button>

<!-- Danger (Red) -->
<button class="btn btn-danger">Delete</button>

<!-- Outline variants -->
<button class="btn btn-outline-primary">View Details</button>
<button class="btn btn-outline-secondary">Edit</button>

<!-- Ghost button (minimal) -->
<button class="btn btn-ghost">Skip</button>

<!-- Link style -->
<button class="btn btn-link">Learn More</button>

<!-- With icon -->
<button class="btn btn-primary">
    <i class="bi bi-plus-circle"></i>
    New Application
</button>

<!-- Icon only -->
<button class="btn btn-icon btn-primary">
    <i class="bi bi-heart"></i>
</button>

<!-- Sizes -->
<button class="btn btn-primary btn-sm">Small</button>
<button class="btn btn-primary">Default</button>
<button class="btn btn-primary btn-lg">Large</button>

<!-- Floating Action Button -->
<button class="btn-fab">
    <i class="bi bi-pen"></i>
</button>
```

### Forms

#### Text Input
```html
<div class="form-group">
    <label class="form-label required">Company Name</label>
    <input type="text" class="form-control" placeholder="Enter company name...">
    <small class="form-text">The organization you're applying to</small>
</div>
```

#### Textarea (with notebook lines)
```html
<div class="form-group">
    <label class="form-label">Cover Letter</label>
    <textarea class="form-control" rows="8" placeholder="Write your cover letter..."></textarea>
</div>
```

#### Select Dropdown
```html
<div class="form-group">
    <label class="form-label">Application Type</label>
    <select class="form-select">
        <option>Job</option>
        <option>Scholarship</option>
        <option>Internship</option>
    </select>
</div>
```

#### Checkboxes & Radio Buttons
```html
<div class="form-check">
    <input type="checkbox" class="form-check-input" id="terms">
    <label class="form-check-label" for="terms">
        I agree to the terms and conditions
    </label>
</div>

<div class="form-check">
    <input type="radio" class="form-check-input" name="priority" id="high">
    <label class="form-check-label" for="high">High Priority</label>
</div>
```

#### Search Input
```html
<input type="search" class="form-control search-input" placeholder="Search applications...">
```

#### File Upload
```html
<input type="file" class="form-file-input">
```

### Tables

#### Ledger-Style Table
```html
<div class="table-wrapper">
    <table class="table">
        <thead>
            <tr>
                <th>Position</th>
                <th>Company</th>
                <th>Deadline</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><a href="#">Software Engineer</a></td>
                <td>Tech Corp</td>
                <td>Dec 31, 2024</td>
                <td><span class="badge badge-success">Applied</span></td>
                <td>
                    <button class="btn btn-sm btn-ghost"><i class="bi bi-eye"></i></button>
                    <button class="btn btn-sm btn-ghost"><i class="bi bi-pencil"></i></button>
                </td>
            </tr>
        </tbody>
    </table>
</div>
```

For mobile-responsive card view, add `data-label` attributes:
```html
<td data-label="Position"><a href="#">Software Engineer</a></td>
<td data-label="Company">Tech Corp</td>
```

### Badges (Wax Seals)

```html
<span class="badge badge-primary">Featured</span>
<span class="badge badge-success">Applied</span>
<span class="badge badge-danger">Overdue</span>
<span class="badge badge-warning">In Progress</span>
<span class="badge badge-info">Interview</span>
<span class="badge badge-secondary">Draft</span>
```

### Modals

```html
<div class="modal fade" id="exampleModal">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Confirm Action</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <p>Are you sure you want to proceed with this action?</p>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary">Confirm</button>
            </div>
        </div>
    </div>
</div>
```

## Special Effects

### Animations

#### Page Turn In
```html
<div class="card page-in">
    <!-- Content with page turn animation -->
</div>
```

#### Fade In
```html
<div class="fade-in">
    <!-- Content with fade in animation -->
</div>
```

#### Write In (underline effect)
```html
<h1 class="write-in">My Applications</h1>
```

#### Quill Float (for icons)
```html
<i class="bi bi-pen quill-float"></i>
```

### Interactive Effects

#### Hover Lift
```html
<div class="card hover-lift">
    <!-- Card lifts on hover -->
</div>
```

#### Ink Effect (button press)
```html
<button class="btn btn-primary ink-effect">Click Me</button>
```

#### Quill Icon Rotation
```html
<i class="bi bi-pen quill-icon"></i>
```

## Customization

### CSS Variables

All theme values are defined as CSS custom properties in `:root`. You can override them:

```css
/* In your custom CSS file */
:root {
    /* Change gold accent to bronze */
    --color-gold: #CD7F32;
    --color-gold-light: #E09856;
    --color-gold-dark: #A0651F;

    /* Adjust spacing */
    --spacing-xl: 2.5rem;

    /* Change font */
    --font-display: 'Playfair Display', serif;
}
```

### Dark Mode Variation

To create a dark book theme (ink on cream to cream on black):

```css
@media (prefers-color-scheme: dark) {
    :root {
        --color-ink-black: #FFFFFF;
        --color-paper-white: #1A1A1A;
        --color-cream: #0F0F0F;
        /* ... adjust other colors ... */
    }
}
```

## Accessibility

### Features Included

- **High Contrast**: 4.5:1 minimum contrast ratios
- **Focus Indicators**: Clear 2px gold outlines on all interactive elements
- **Screen Reader Support**: `sr-only` utility class for hidden labels
- **Keyboard Navigation**: All interactive elements are keyboard accessible
- **Reduced Motion**: Respects `prefers-reduced-motion` media query
- **Semantic HTML**: Proper heading hierarchy and ARIA labels

### Usage

```html
<!-- Screen reader only text -->
<span class="sr-only">Additional context for screen readers</span>

<!-- Proper heading hierarchy -->
<h1>Main Page Title</h1>
<h2>Section Title</h2>
<h3>Subsection Title</h3>

<!-- ARIA labels -->
<button aria-label="Delete application">
    <i class="bi bi-trash"></i>
</button>
```

## Browser Support

- **Modern Browsers**: Full support (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- **Fallbacks**: Graceful degradation for older browsers
- **CSS Grid & Flexbox**: Used throughout (IE11 not supported)
- **Custom Properties**: Required (no IE11 support)

## Performance

### Optimizations Included

- **Single CSS file**: No component imports needed
- **Minimal shadows**: Subtle effects for better performance
- **Hardware acceleration**: `transform` and `opacity` for animations
- **Selective effects**: Animations only on user interaction
- **Reduced motion**: Disabled for users who prefer it

## Tips & Best Practices

### 1. **Use Serif Fonts for Content**
   - Headings and body text use elegant serif fonts
   - Navigation and UI use clean sans-serif fonts

### 2. **Embrace White Space**
   - Generous padding and margins
   - Don't overcrowd cards and containers

### 3. **Minimal Color Usage**
   - Primary: Gold (#D4AF37) for accents only
   - Keep most UI black, white, and gray
   - Use color to highlight important actions

### 4. **Paper-like Texture**
   - Subtle background patterns simulate paper
   - Ruled lines in textareas mimic notebooks
   - Avoid heavy shadows, prefer borders

### 5. **Typography Hierarchy**
   - Clear distinction between heading levels
   - Use uppercase for labels and categories
   - Proper line height for readability (1.8 for body)

### 6. **Interactive Feedback**
   - Smooth transitions on hover
   - Ink press effect on buttons
   - Page lift effect on cards
   - Gold accents appear on interaction

### 7. **Mobile Considerations**
   - Simplified layout on small screens
   - No notebook lines on mobile
   - Card-based table view
   - Collapsible sidebar

## Troubleshooting

### Issue: Fonts not loading
**Solution**: Google Fonts are imported via `@import` at the top of the CSS file. Ensure your server can access Google Fonts CDN.

### Issue: Animations too slow/fast
**Solution**: Adjust transition variables:
```css
:root {
    --transition-fast: 100ms;
    --transition-base: 200ms;
    --transition-smooth: 300ms;
}
```

### Issue: Colors too muted
**Solution**: Increase contrast by darkening text or lightening backgrounds:
```css
:root {
    --color-gray-700: #303030; /* Darker text */
}
```

### Issue: Sidebar doesn't collapse on mobile
**Solution**: Ensure JavaScript for sidebar toggle is included:
```javascript
document.querySelector('.menu-toggle')?.addEventListener('click', function() {
    document.querySelector('.sidebar')?.classList.toggle('show');
});
```

## Examples Gallery

Check out these example pages to see the theme in action:

1. **Dashboard**: Stats cards, application list, quick actions
2. **Application Detail**: Full application view with documents and notes
3. **Form Pages**: Create/edit applications with all form elements
4. **Tables**: Application listing in ledger format
5. **Profile**: User information with elegant typography

## Credits

**Design Inspiration**:
- Classic literature and typography
- Moleskine notebooks
- Library card catalogs
- Vintage typewriters
- Manuscript aesthetics

**Fonts**:
- EB Garamond by Georg Duffner
- Crimson Text by Sebastian Kosch
- Libre Baskerville by Impallari Type
- Inter by Rasmus Andersson
- IBM Plex Mono by IBM

**Icons**: Bootstrap Icons

---

**Version**: 1.0.0
**Last Updated**: 2024
**License**: MIT (included with project)

For questions or issues, refer to the main project documentation or create an issue on GitHub.
