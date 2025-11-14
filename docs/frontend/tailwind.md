# Tailwind CSS Setup

## Installation

### package.json

```json
{
  "name": "retail-branch-demo",
  "version": "1.0.0",
  "scripts": {
    "dev": "npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch",
    "build": "npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify"
  },
  "devDependencies": {
    "tailwindcss": "^3.4.0"
  }
}
```

### tailwind.config.js

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html",
    "./static/js/**/*.js"
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

### static/css/input.css

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

## Build Commands

```bash
# Development mode (watch for changes)
npm run dev

# Production build (minified)
npm run build
```

## Usage in Templates

```html
<!DOCTYPE html>
<html>
<head>
    <link href="/static/css/output.css" rel="stylesheet">
</head>
<body class="bg-gray-50">
    <div class="container mx-auto px-4">
        <button class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
            Click me
        </button>
    </div>
</body>
</html>
```

## Related Documentation

- [../DESIGN.md](../DESIGN.md) - Design guidelines and color palette
- [../development/setup.md](../development/setup.md) - Development setup
