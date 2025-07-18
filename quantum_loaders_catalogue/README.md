# Enhanced Quantum Loaders & Spinners Catalogue

A professional-grade collection of quantum-themed CSS animations with advanced controls, accessibility features, and framework integrations.

## 🌟 Features

### ✨ 10 Unique Quantum Loaders
- **Quantum Tunnel Loader** - Expanding quantum rings portal effect
- **DNA Sequencer** - Double helix structure with base pairs
- **Holographic Cube** - 3D rotating cube with transparency
- **Energy Sphere** - Pulsating energy with orbital rings
- **Particle Accelerator** - Orbiting particles in circular chamber
- **Quantum Gate Circuit** - Computing gate with traveling qubits
- **Electromagnetic Field** - Expanding field wave animation
- **Plasma Storm** - Chaotic lightning with storm effects
- **Dark Matter Vortex** - Swirling gravitational effects
- **Singularity Collapse** - Matter collapsing into black hole

### 🎨 Theme System
- **Dark Theme** - Professional dark interface
- **Light Theme** - Clean light interface  
- **Neon Theme** - Cyberpunk neon aesthetics
- Auto theme detection based on system preference
- Smooth theme transitions

### 🎮 Animation Controls
- **Global Controls** - Play/pause, speed adjustment, reset
- **Individual Customization** - Size, speed, color per loader
- **Speed Range** - 0.25x to 3x animation speed
- **Real-time Preview** - Instant visual feedback

### 🔍 Search & Filter
- **Real-time Search** - Filter by name, category, tags
- **Category Filters** - Quantum, Bio, Tech, Space, Energy
- **Complexity Filters** - Simple, Medium, Complex
- **Results Counter** - Live search results count

### ⭐ Favorites System
- **Local Storage** - Persistent favorites across sessions
- **Quick Access** - Dedicated favorites section
- **Visual Indicators** - Heart icons for favorite status
- **Bulk Operations** - Easy favorites management

### 📱 Responsive Design
- **Mobile First** - Optimized for all screen sizes
- **Touch Friendly** - Enhanced touch interactions
- **Flexible Grid** - Auto-adapting layout
- **Container Queries** - Modern responsive techniques

### ♿ Accessibility Features
- **ARIA Labels** - Complete screen reader support
- **Keyboard Navigation** - Full keyboard accessibility
- **Reduced Motion** - Respects motion preferences
- **High Contrast** - Enhanced visibility modes
- **Focus Management** - Logical tab sequences
- **Skip Links** - Quick navigation shortcuts

### 🚀 Performance Optimizations
- **CSS Containment** - Optimized rendering performance
- **GPU Acceleration** - Hardware-accelerated animations
- **Intersection Observer** - Pause off-screen animations
- **Memory Management** - Efficient resource usage
- **FPS Monitoring** - Real-time performance tracking

### 📦 Export Functionality
- **Multiple Formats** - HTML, CSS, React, Vue, Angular, Svelte
- **Framework Components** - Ready-to-use code
- **Standalone Files** - Self-contained exports
- **SVG Conversion** - Scalable vector graphics
- **Web Components** - Modern web standards

### 🔧 Advanced Features
- **Performance Monitor** - FPS, memory, optimization tips
- **Accessibility Tester** - Built-in compliance checking
- **Custom Properties** - CSS variable integration
- **Error Boundaries** - Graceful failure handling
- **Development Tools** - Debug console and hotkeys

## 🚀 Quick Start

### Basic Usage

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quantum Loaders</title>
    <link rel="stylesheet" href="css/core.css">
    <link rel="stylesheet" href="css/themes.css">
    <link rel="stylesheet" href="css/loaders.css">
    <link rel="stylesheet" href="css/responsive.css">
</head>
<body class="theme-dark">
    <!-- Your loader here -->
    <div class="loader-animation quantum-tunnel">
        <!-- Loader HTML content -->
    </div>
    
    <script src="js/core.js"></script>
    <script src="js/app.js"></script>
</body>
</html>
```

### Individual Loader Usage

```html
<!-- Quantum Tunnel Loader -->
<div class="loader-animation quantum-tunnel" style="width: 60px; height: 60px;"></div>

<!-- DNA Sequencer -->
<div class="loader-animation dna-sequencer">
    <div class="dna-base"></div>
    <div class="dna-base"></div>
    <div class="dna-base"></div>
</div>

<!-- Energy Sphere -->
<div class="loader-animation energy-sphere"></div>
```

### CSS Customization

```css
:root {
    --color-accent-primary: #00ff88;
    --color-accent-secondary: #00d4ff;
    --loader-size: 60px;
    --animation-speed: 1;
}

.custom-loader {
    width: var(--loader-size);
    height: var(--loader-size);
    --color-accent-primary: #ff6b6b;
    animation-duration: calc(2s / var(--animation-speed));
}
```

## 🎯 Framework Integration

### React Component

```jsx
import React from 'react';

const QuantumTunnelLoader = ({ 
  size = 60, 
  speed = 1, 
  color = '#00ff88' 
}) => {
  const loaderStyle = {
    width: size,
    height: size,
    '--color-accent-primary': color,
    animationDuration: `${2 / speed}s`
  };

  return (
    <div 
      className="loader-animation quantum-tunnel"
      style={loaderStyle}
      role="img"
      aria-label="Quantum tunnel loading animation"
    />
  );
};

export default QuantumTunnelLoader;
```

### Vue Component

```vue
<template>
  <div 
    class="loader-animation quantum-tunnel"
    :style="loaderStyle"
    role="img"
    aria-label="Quantum tunnel loading animation"
  />
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  size: { type: Number, default: 60 },
  speed: { type: Number, default: 1 },
  color: { type: String, default: '#00ff88' }
});

const loaderStyle = computed(() => ({
  width: props.size + 'px',
  height: props.size + 'px',
  '--color-accent-primary': props.color,
  animationDuration: (2 / props.speed) + 's'
}));
</script>
```

### Angular Component

```typescript
import { Component, Input } from '@angular/core';

@Component({
  selector: 'quantum-tunnel-loader',
  template: `
    <div 
      class="loader-animation quantum-tunnel"
      [style.width.px]="size"
      [style.height.px]="size"
      [style.--color-accent-primary]="color"
      [style.animation-duration]="animationDuration"
      role="img"
      aria-label="Quantum tunnel loading animation"
    ></div>
  `
})
export class QuantumTunnelLoaderComponent {
  @Input() size: number = 60;
  @Input() speed: number = 1;
  @Input() color: string = '#00ff88';
  
  get animationDuration(): string {
    return `${2 / this.speed}s`;
  }
}
```

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Toggle animations play/pause |
| `F` | Focus search input |
| `Escape` | Close modals/panels |
| `1-3` | Switch themes (Dark/Light/Neon) |
| `Home` | Focus first element |
| `End` | Focus last element |
| `Tab` | Navigate through interface |
| `Arrow Keys` | Navigate grid (when focused) |

### Development Shortcuts

| Key Combination | Action |
|-----------------|--------|
| `Ctrl+Shift+D` | Show debug info |
| `Ctrl+Shift+P` | Toggle performance monitor |
| `Ctrl+Shift+A` | Run accessibility tests |
| `Ctrl+Shift+T` | Run performance tests |
| `Ctrl+Shift+R` | Export performance report |

## 🎨 Themes

### Theme Classes

- `.theme-dark` - Dark theme (default)
- `.theme-light` - Light theme
- `.theme-neon` - Neon theme

### Custom Theme Creation

```css
.theme-custom {
    --color-bg-primary: #your-bg-color;
    --color-text-primary: #your-text-color;
    --color-accent-primary: #your-accent-color;
    --color-accent-secondary: #your-secondary-color;
    --color-border-primary: #your-border-color;
}
```

## 📱 Responsive Breakpoints

| Breakpoint | Screen Size | Grid Columns |
|------------|-------------|--------------|
| Mobile | < 480px | 2 columns |
| Small | 480px - 767px | 2 columns |
| Medium | 768px - 991px | 3 columns |
| Large | 992px - 1199px | 4 columns |
| XL | 1200px - 1399px | 5 columns |
| XXL | ≥ 1400px | 6 columns |

## ♿ Accessibility

### Screen Reader Support
- Complete ARIA labeling
- Live regions for announcements
- Semantic HTML structure
- Descriptive text alternatives

### Keyboard Navigation
- Logical tab order
- Focus indicators
- Keyboard shortcuts
- Grid navigation with arrow keys

### Motion Preferences
- Respects `prefers-reduced-motion`
- Manual motion toggle
- Animation pause controls
- Alternative static states

### Visual Accessibility
- High contrast mode support
- Scalable text and interface
- Color-blind friendly palette
- Focus indicators

## 🚀 Performance

### Optimization Techniques
- CSS containment properties
- GPU-accelerated transforms
- Intersection Observer API
- Efficient animation loops
- Memory leak prevention

### Performance Monitoring
```javascript
// Access performance metrics
const metrics = window.quantumDebug.getMetrics();
console.log('FPS:', metrics.fps);
console.log('Memory:', metrics.memoryUsage);

// Run performance tests
const results = await window.quantumDebug.testPerformance();
console.log('Performance score:', results.score);
```

### Browser Support

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| Basic animations | 60+ | 55+ | 13+ | 79+ |
| CSS containment | 65+ | 69+ | 15.4+ | 79+ |
| Intersection Observer | 58+ | 55+ | 12.1+ | 16+ |
| CSS custom properties | 49+ | 31+ | 9.1+ | 16+ |

## 🔧 Development

### Project Structure
```
quantum_loaders_catalogue/
├── css/
│   ├── core.css          # Base styles and utilities
│   ├── themes.css        # Theme system
│   ├── loaders.css       # Loader animations
│   └── responsive.css    # Responsive design
├── js/
│   ├── core.js           # Core functionality
│   ├── loaders-data.js   # Loader definitions
│   ├── animations.js     # Animation controls
│   ├── export.js         # Export functionality
│   ├── accessibility.js  # Accessibility features
│   ├── performance.js    # Performance monitoring
│   └── app.js            # Main application
├── components/           # Framework components
├── examples/             # Usage examples
├── docs/                 # Documentation
└── index.html            # Main application
```

### Local Development

1. Clone the repository
2. Open `index.html` in your browser
3. Or serve with a local server:
   ```bash
   python -m http.server 8000
   # Navigate to http://localhost:8000
   ```

### Building Components

The catalogue includes build scripts for generating framework-specific components:

```bash
# Generate React components
npm run build:react

# Generate Vue components  
npm run build:vue

# Generate Angular components
npm run build:angular

# Build all formats
npm run build:all
```

## 📚 API Reference

### Core API

```javascript
// Initialize manually
const app = new QuantumLoadersApp();

// Wait for initialization
await app.waitForReady();

// Get modules
const core = app.getModule('core');
const loaders = app.getModule('loaders');

// Configuration
app.updateConfiguration({
    theme: 'neon',
    motionReduced: false,
    animationSpeed: 1.5
});

// Export configuration
const config = app.exportConfiguration();
```

### Animation Control

```javascript
// Get animation controller
const animationController = app.getModule('animation');

// Control individual animations
const loader = document.querySelector('.quantum-tunnel');
animationController.setAnimationSpeed(loader, 2);
animationController.setColor(loader, '#ff6b6b');
animationController.setSize(loader, 80);

// Global controls
animationController.pauseAllAnimations();
animationController.resumeAllAnimations();
animationController.resetAllAnimations();
```

### Performance Monitoring

```javascript
// Get performance monitor
const performanceMonitor = app.getModule('performance');

// Get current metrics
const metrics = performanceMonitor.getMetrics();

// Get performance score
const score = performanceMonitor.getPerformanceScore();

// Get recommendations
const recommendations = performanceMonitor.getOptimizationRecommendations();

// Export performance report
performanceMonitor.exportReport();
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Guidelines

1. Follow existing code style
2. Add tests for new features
3. Update documentation
4. Ensure accessibility compliance
5. Test across browsers
6. Optimize for performance

### Adding New Loaders

1. Create CSS animation in `css/loaders.css`
2. Add loader definition in `js/loaders-data.js`
3. Include HTML structure if needed
4. Add to category filters
5. Test accessibility
6. Document usage

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by quantum physics and modern web technologies
- Built with accessibility and performance in mind
- Designed for production use in professional applications

## 📞 Support

- 📧 Email: support@quantumloaders.dev
- 🐛 Issues: [GitHub Issues](https://github.com/ideakz/agent_zkaedi/issues)
- 📖 Docs: [Documentation](https://quantumloaders.dev/docs)
- 💬 Community: [Discussions](https://github.com/ideakz/agent_zkaedi/discussions)

---

**Made with ❤️ for the quantum computing and web development communities**