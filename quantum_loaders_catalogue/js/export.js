/**
 * Export Module
 * Handles exporting loaders in various formats and frameworks
 */

class ExportManager {
  constructor(core) {
    this.core = core;
    this.templates = this.initializeTemplates();
    
    this.init();
  }
  
  init() {
    this.setupEventListeners();
  }
  
  setupEventListeners() {
    // Export modal format changes
    document.addEventListener('change', (e) => {
      if (e.target.name === 'export-format') {
        this.updateExportPreview();
      }
    });
  }
  
  initializeTemplates() {
    return {
      html: {
        name: 'Standalone HTML',
        extension: 'html',
        mimeType: 'text/html',
        language: 'html'
      },
      css: {
        name: 'CSS Only',
        extension: 'css',
        mimeType: 'text/css',
        language: 'css'
      },
      react: {
        name: 'React Component',
        extension: 'jsx',
        mimeType: 'text/javascript',
        language: 'jsx'
      },
      vue: {
        name: 'Vue Component',
        extension: 'vue',
        mimeType: 'text/javascript',
        language: 'vue'
      },
      angular: {
        name: 'Angular Component',
        extension: 'ts',
        mimeType: 'text/typescript',
        language: 'typescript'
      },
      svelte: {
        name: 'Svelte Component',
        extension: 'svelte',
        mimeType: 'text/javascript',
        language: 'svelte'
      },
      svg: {
        name: 'SVG Animation',
        extension: 'svg',
        mimeType: 'image/svg+xml',
        language: 'xml'
      },
      webcomponent: {
        name: 'Web Component',
        extension: 'js',
        mimeType: 'text/javascript',
        language: 'javascript'
      }
    };
  }
  
  generateCode(loader, format, customizations = {}) {
    switch (format) {
      case 'html':
        return this.generateStandaloneHTML(loader, customizations);
      case 'css':
        return this.generateCSSOnly(loader, customizations);
      case 'react':
        return this.generateReactComponent(loader, customizations);
      case 'vue':
        return this.generateVueComponent(loader, customizations);
      case 'angular':
        return this.generateAngularComponent(loader, customizations);
      case 'svelte':
        return this.generateSvelteComponent(loader, customizations);
      case 'svg':
        return this.generateSVGAnimation(loader, customizations);
      case 'webcomponent':
        return this.generateWebComponent(loader, customizations);
      default:
        return this.generateCSSOnly(loader, customizations);
    }
  }
  
  generateStandaloneHTML(loader, customizations = {}) {
    const {
      title = loader.title,
      size = 60,
      speed = 1,
      color = '#00ff88',
      backgroundColor = '#0a0e1a',
      includeControls = false
    } = customizations;
    
    const controlsHTML = includeControls ? this.generateControlsHTML() : '';
    
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${title} - Quantum Loader</title>
    <style>
        :root {
            --color-accent-primary: ${color};
            --color-accent-secondary: ${this.calculateSecondaryColor(color)};
            --loader-size: ${size}px;
            --animation-speed: ${speed};
        }
        
        * {
            box-sizing: border-box;
        }
        
        body {
            margin: 0;
            padding: 20px;
            background: ${backgroundColor};
            color: #e2e8f0;
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }
        
        .container {
            text-align: center;
            max-width: 500px;
            width: 100%;
        }
        
        .loader-title {
            margin-bottom: 30px;
            font-size: 2rem;
            font-weight: 700;
            color: var(--color-accent-primary);
            text-shadow: 0 0 20px currentColor;
        }
        
        .loader-container {
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 30px 0;
            min-height: 120px;
        }
        
        .loader-animation {
            width: var(--loader-size);
            height: var(--loader-size);
            animation-duration: calc(2s / var(--animation-speed));
        }
        
        .description {
            margin-top: 20px;
            font-size: 1rem;
            color: #94a3b8;
            line-height: 1.6;
        }
        
        ${this.getLoaderCSS(loader)}
        
        /* Responsive design */
        @media (max-width: 600px) {
            body {
                padding: 15px;
            }
            .loader-title {
                font-size: 1.5rem;
            }
            .loader-animation {
                transform: scale(0.8);
            }
        }
        
        /* Reduced motion support */
        @media (prefers-reduced-motion: reduce) {
            .loader-animation * {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="loader-title">${title}</h1>
        
        <div class="loader-container">
            <div class="loader-animation ${loader.cssClass}">
                ${loader.html}
            </div>
        </div>
        
        <p class="description">${loader.description}</p>
        
        ${controlsHTML}
    </div>
    
    ${includeControls ? this.generateControlsScript() : ''}
</body>
</html>`;
  }
  
  generateCSSOnly(loader, customizations = {}) {
    const {
      includeVariables = true,
      includeComments = true,
      minify = false
    } = customizations;
    
    let css = '';
    
    if (includeComments) {
      css += `/*\n * ${loader.title} - Quantum Loader\n * ${loader.description}\n * Generated from Quantum Loaders Catalogue\n */\n\n`;
    }
    
    if (includeVariables) {
      css += `:root {\n`;
      css += `  --color-accent-primary: #00ff88;\n`;
      css += `  --color-accent-secondary: #00d4ff;\n`;
      css += `  --loader-size: 60px;\n`;
      css += `  --animation-speed: 1;\n`;
      css += `}\n\n`;
    }
    
    css += this.getLoaderCSS(loader);
    
    if (minify) {
      css = this.minifyCSS(css);
    }
    
    return css;
  }
  
  generateReactComponent(loader, customizations = {}) {
    const {
      typescript = false,
      includeProps = true,
      includePropTypes = false
    } = customizations;
    
    const componentName = this.pascalCase(loader.title) + 'Loader';
    const ext = typescript ? 'tsx' : 'jsx';
    const propTypes = typescript ? this.generateTypeScriptProps() : this.generatePropTypes();
    
    return `import React${includeProps ? ', { CSSProperties }' : ''} from 'react';
${includePropTypes && !typescript ? "import PropTypes from 'prop-types';" : ''}

${typescript ? propTypes : ''}

${includeProps ? this.generateReactPropsInterface(typescript) : ''}

const ${componentName}${typescript ? ': React.FC<LoaderProps>' : ''} = (${includeProps ? '{\n  size = 60,\n  speed = 1,\n  color = "#00ff88",\n  className = "",\n  ...props\n}' : ''}) => {
  ${includeProps ? `const loaderStyle${typescript ? ': CSSProperties' : ''} = {
    width: size,
    height: size,
    '--color-accent-primary': color,
    '--color-accent-secondary': calculateSecondaryColor(color),
    animationDuration: \`\${2 / speed}s\`,
  }${typescript ? ' as CSSProperties' : ''};` : ''}

  return (
    <div 
      className={\`loader-animation ${loader.cssClass} \${className}\`}
      ${includeProps ? 'style={loaderStyle}' : ''}
      role="img"
      aria-label="${loader.title} loading animation"
      ${includeProps ? '{...props}' : ''}
    >
      ${loader.html.replace(/\n\s*/g, '\n      ')}
    </div>
  );
};

${includeProps && !typescript ? `
const calculateSecondaryColor = (color) => {
  // Simple complementary color calculation
  const hex = color.replace('#', '');
  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);
  
  // Return a lighter/darker variant for simplicity
  const factor = (r + g + b) / 3 > 128 ? 0.7 : 1.3;
  return \`rgb(\${Math.round(r * factor)}, \${Math.round(g * factor)}, \${Math.round(b * factor)})\`;
};` : ''}

${includePropTypes && !typescript ? `
${componentName}.propTypes = {
  size: PropTypes.number,
  speed: PropTypes.number,
  color: PropTypes.string,
  className: PropTypes.string,
};` : ''}

export default ${componentName};

/* CSS - Add this to your stylesheet or CSS-in-JS solution */
/*
${this.getLoaderCSS(loader).replace(/\n/g, '\n')}
*/`;
  }
  
  generateVueComponent(loader, customizations = {}) {
    const {
      composition = true,
      typescript = false
    } = customizations;
    
    const componentName = this.kebabCase(loader.title) + '-loader';
    const script = composition ? this.generateVueCompositionScript(loader, typescript) : this.generateVueOptionsScript(loader, typescript);
    
    return `<template>
  <div 
    :class="[\`loader-animation ${loader.cssClass}\`, className]"
    :style="loaderStyle"
    role="img"
    :aria-label="\`${loader.title} loading animation\`"
  >
    ${loader.html.replace(/\n\s*/g, '\n    ')}
  </div>
</template>

${script}

<style scoped>
${this.getLoaderCSS(loader)}
</style>`;
  }
  
  generateAngularComponent(loader, customizations = {}) {
    const componentName = this.pascalCase(loader.title) + 'LoaderComponent';
    const selector = this.kebabCase(loader.title) + '-loader';
    
    return `import { Component, Input, HostBinding } from '@angular/core';

@Component({
  selector: 'app-${selector}',
  template: \`
    <div 
      class="loader-animation ${loader.cssClass}"
      [style.width.px]="size"
      [style.height.px]="size"
      [style.--color-accent-primary]="color"
      [style.--color-accent-secondary]="secondaryColor"
      [style.animation-duration]="animationDuration"
      role="img"
      [attr.aria-label]="'${loader.title} loading animation'"
    >
      ${loader.html.replace(/\n\s*/g, '\n      ')}
    </div>
  \`,
  styles: [\`
    :host {
      display: inline-block;
    }
    
    ${this.getLoaderCSS(loader).replace(/\n/g, '\n    ')}
  \`]
})
export class ${componentName} {
  @Input() size: number = 60;
  @Input() speed: number = 1;
  @Input() color: string = '#00ff88';
  
  get secondaryColor(): string {
    return this.calculateSecondaryColor(this.color);
  }
  
  get animationDuration(): string {
    return \`\${2 / this.speed}s\`;
  }
  
  private calculateSecondaryColor(color: string): string {
    // Simple complementary color calculation
    const hex = color.replace('#', '');
    const r = parseInt(hex.substr(0, 2), 16);
    const g = parseInt(hex.substr(2, 2), 16);
    const b = parseInt(hex.substr(4, 2), 16);
    
    const factor = (r + g + b) / 3 > 128 ? 0.7 : 1.3;
    return \`rgb(\${Math.round(r * factor)}, \${Math.round(g * factor)}, \${Math.round(b * factor)})\`;
  }
}`;
  }
  
  generateSvelteComponent(loader, customizations = {}) {
    const componentName = this.pascalCase(loader.title) + 'Loader';
    
    return `<script>
  export let size = 60;
  export let speed = 1;
  export let color = '#00ff88';
  export let className = '';
  
  $: secondaryColor = calculateSecondaryColor(color);
  $: animationDuration = \`\${2 / speed}s\`;
  
  function calculateSecondaryColor(color) {
    const hex = color.replace('#', '');
    const r = parseInt(hex.substr(0, 2), 16);
    const g = parseInt(hex.substr(2, 2), 16);
    const b = parseInt(hex.substr(4, 2), 16);
    
    const factor = (r + g + b) / 3 > 128 ? 0.7 : 1.3;
    return \`rgb(\${Math.round(r * factor)}, \${Math.round(g * factor)}, \${Math.round(b * factor)})\`;
  }
</script>

<div 
  class="loader-animation ${loader.cssClass} {className}"
  style="
    width: {size}px;
    height: {size}px;
    --color-accent-primary: {color};
    --color-accent-secondary: {secondaryColor};
    animation-duration: {animationDuration};
  "
  role="img"
  aria-label="${loader.title} loading animation"
>
  ${loader.html.replace(/\n\s*/g, '\n  ')}
</div>

<style>
  ${this.getLoaderCSS(loader)}
</style>`;
  }
  
  generateSVGAnimation(loader, customizations = {}) {
    const {
      width = 60,
      height = 60,
      includeAnimation = true
    } = customizations;
    
    // This is a simplified SVG conversion
    // In a real implementation, you'd need more sophisticated CSS-to-SVG conversion
    return `<svg 
  width="${width}" 
  height="${height}" 
  viewBox="0 0 ${width} ${height}" 
  xmlns="http://www.w3.org/2000/svg"
  aria-label="${loader.title} loading animation"
>
  <defs>
    <style>
      .loader-svg {
        ${includeAnimation ? 'animation: spin 2s linear infinite;' : ''}
        transform-origin: center;
      }
      ${includeAnimation ? '@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }' : ''}
    </style>
  </defs>
  
  <!-- Simplified SVG representation of ${loader.title} -->
  <g class="loader-svg">
    ${this.generateSVGElements(loader, width, height)}
  </g>
  
  <title>${loader.title}</title>
  <desc>${loader.description}</desc>
</svg>`;
  }
  
  generateWebComponent(loader, customizations = {}) {
    const componentName = this.kebabCase(loader.title) + '-loader';
    const className = this.pascalCase(loader.title) + 'Loader';
    
    return `class ${className} extends HTMLElement {
  static get observedAttributes() {
    return ['size', 'speed', 'color'];
  }
  
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.render();
  }
  
  connectedCallback() {
    this.render();
  }
  
  attributeChangedCallback(name, oldValue, newValue) {
    if (oldValue !== newValue) {
      this.render();
    }
  }
  
  get size() {
    return this.getAttribute('size') || '60';
  }
  
  get speed() {
    return this.getAttribute('speed') || '1';
  }
  
  get color() {
    return this.getAttribute('color') || '#00ff88';
  }
  
  calculateSecondaryColor(color) {
    const hex = color.replace('#', '');
    const r = parseInt(hex.substr(0, 2), 16);
    const g = parseInt(hex.substr(2, 2), 16);
    const b = parseInt(hex.substr(4, 2), 16);
    
    const factor = (r + g + b) / 3 > 128 ? 0.7 : 1.3;
    return \`rgb(\${Math.round(r * factor)}, \${Math.round(g * factor)}, \${Math.round(b * factor)})\`;
  }
  
  render() {
    const secondaryColor = this.calculateSecondaryColor(this.color);
    const animationDuration = \`\${2 / parseFloat(this.speed)}s\`;
    
    this.shadowRoot.innerHTML = \`
      <style>
        :host {
          display: inline-block;
          width: \${this.size}px;
          height: \${this.size}px;
        }
        
        .loader-animation {
          width: 100%;
          height: 100%;
          --color-accent-primary: \${this.color};
          --color-accent-secondary: \${secondaryColor};
          animation-duration: \${animationDuration};
        }
        
        ${this.getLoaderCSS(loader)}
      </style>
      
      <div 
        class="loader-animation ${loader.cssClass}"
        role="img"
        aria-label="${loader.title} loading animation"
      >
        ${loader.html}
      </div>
    \`;
  }
}

// Register the custom element
customElements.define('${componentName}', ${className});

// Usage:
// <${componentName} size="80" speed="1.5" color="#ff6b6b"></${componentName}>`;
  }
  
  exportAsFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
    
    return true;
  }
  
  copyToClipboard(content) {
    return navigator.clipboard.writeText(content).then(() => {
      return true;
    }).catch(err => {
      console.error('Failed to copy to clipboard:', err);
      return false;
    });
  }
  
  generateExportBundle(loader, formats = ['html', 'css', 'react'], customizations = {}) {
    const bundle = {};
    
    formats.forEach(format => {
      const template = this.templates[format];
      if (template) {
        const content = this.generateCode(loader, format, customizations);
        const filename = `${loader.id}.${template.extension}`;
        bundle[filename] = content;
      }
    });
    
    return bundle;
  }
  
  exportAsZip(loader, formats, customizations = {}) {
    // This would require a ZIP library like JSZip
    // For now, we'll export individual files
    const bundle = this.generateExportBundle(loader, formats, customizations);
    
    Object.entries(bundle).forEach(([filename, content]) => {
      const template = this.templates[formats.find(f => filename.endsWith(this.templates[f].extension))];
      this.exportAsFile(content, filename, template.mimeType);
    });
    
    return true;
  }
  
  // Utility methods
  getLoaderCSS(loader) {
    // This would contain the actual CSS for the loader
    // For now, return a placeholder
    return `/* ${loader.title} CSS */\n.${loader.cssClass} {\n  /* Animation styles would go here */\n}`;
  }
  
  generateSVGElements(loader, width, height) {
    // Simplified SVG generation based on loader type
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) / 3;
    
    return `<circle cx="${centerX}" cy="${centerY}" r="${radius}" 
            fill="none" stroke="#00ff88" stroke-width="2" opacity="0.3"/>
            <circle cx="${centerX}" cy="${centerY}" r="${radius}" 
            fill="none" stroke="#00ff88" stroke-width="2" 
            stroke-dasharray="50,100" stroke-linecap="round"/>`;
  }
  
  calculateSecondaryColor(color) {
    const hex = color.replace('#', '');
    const r = parseInt(hex.substr(0, 2), 16);
    const g = parseInt(hex.substr(2, 2), 16);
    const b = parseInt(hex.substr(4, 2), 16);
    
    const factor = (r + g + b) / 3 > 128 ? 0.7 : 1.3;
    return `rgb(${Math.round(r * factor)}, ${Math.round(g * factor)}, ${Math.round(b * factor)})`;
  }
  
  pascalCase(str) {
    return str.replace(/(?:^\w|[A-Z]|\b\w)/g, (word, index) => {
      return word.toUpperCase();
    }).replace(/\s+/g, '');
  }
  
  kebabCase(str) {
    return str.replace(/([a-z])([A-Z])/g, '$1-$2')
              .replace(/\s+/g, '-')
              .toLowerCase();
  }
  
  minifyCSS(css) {
    return css.replace(/\s+/g, ' ')
              .replace(/;\s*}/g, '}')
              .replace(/,\s*/g, ',')
              .replace(/:\s*/g, ':')
              .replace(/;\s*/g, ';')
              .trim();
  }
  
  generateControlsHTML() {
    return `
        <div class="controls" style="margin-top: 30px;">
            <div class="control-group">
                <label for="speed-control">Speed: <span id="speed-display">1x</span></label>
                <input type="range" id="speed-control" min="0.25" max="3" step="0.25" value="1">
            </div>
            
            <div class="control-group">
                <label for="color-control">Color:</label>
                <input type="color" id="color-control" value="#00ff88">
            </div>
            
            <button id="play-pause" style="margin-top: 15px;">Pause</button>
        </div>`;
  }
  
  generateControlsScript() {
    return `
    <script>
        const loader = document.querySelector('.loader-animation');
        const speedControl = document.getElementById('speed-control');
        const speedDisplay = document.getElementById('speed-display');
        const colorControl = document.getElementById('color-control');
        const playPauseBtn = document.getElementById('play-pause');
        
        let isPaused = false;
        
        speedControl.addEventListener('input', (e) => {
            const speed = parseFloat(e.target.value);
            speedDisplay.textContent = speed + 'x';
            loader.style.animationDuration = (2 / speed) + 's';
        });
        
        colorControl.addEventListener('input', (e) => {
            const color = e.target.value;
            loader.style.setProperty('--color-accent-primary', color);
        });
        
        playPauseBtn.addEventListener('click', () => {
            isPaused = !isPaused;
            loader.style.animationPlayState = isPaused ? 'paused' : 'running';
            playPauseBtn.textContent = isPaused ? 'Play' : 'Pause';
        });
    </script>`;
  }
  
  generateReactPropsInterface(typescript) {
    if (!typescript) return '';
    
    return `interface LoaderProps {
  size?: number;
  speed?: number;
  color?: string;
  className?: string;
  [key: string]: any;
}`;
  }
  
  generateTypeScriptProps() {
    return `interface LoaderProps {
  size?: number;
  speed?: number;
  color?: string;
  className?: string;
}`;
  }
  
  generatePropTypes() {
    return `const LoaderProps = {
  size: PropTypes.number,
  speed: PropTypes.number,
  color: PropTypes.string,
  className: PropTypes.string,
};`;
  }
  
  generateVueCompositionScript(loader, typescript) {
    const lang = typescript ? ' lang="ts"' : '';
    
    return `<script setup${lang}>
import { computed } from 'vue';

interface Props {
  size?: number;
  speed?: number;
  color?: string;
  className?: string;
}

const props = withDefaults(defineProps<Props>(), {
  size: 60,
  speed: 1,
  color: '#00ff88',
  className: '',
});

const secondaryColor = computed(() => calculateSecondaryColor(props.color));
const loaderStyle = computed(() => ({
  width: props.size + 'px',
  height: props.size + 'px',
  '--color-accent-primary': props.color,
  '--color-accent-secondary': secondaryColor.value,
  animationDuration: (2 / props.speed) + 's',
}));

function calculateSecondaryColor(color: string): string {
  const hex = color.replace('#', '');
  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);
  
  const factor = (r + g + b) / 3 > 128 ? 0.7 : 1.3;
  return \`rgb(\${Math.round(r * factor)}, \${Math.round(g * factor)}, \${Math.round(b * factor)})\`;
}
</script>`;
  }
  
  generateVueOptionsScript(loader, typescript) {
    const lang = typescript ? ' lang="ts"' : '';
    
    return `<script${lang}>
export default {
  name: '${this.pascalCase(loader.title)}Loader',
  props: {
    size: {
      type: Number,
      default: 60,
    },
    speed: {
      type: Number,
      default: 1,
    },
    color: {
      type: String,
      default: '#00ff88',
    },
    className: {
      type: String,
      default: '',
    },
  },
  computed: {
    secondaryColor() {
      return this.calculateSecondaryColor(this.color);
    },
    loaderStyle() {
      return {
        width: this.size + 'px',
        height: this.size + 'px',
        '--color-accent-primary': this.color,
        '--color-accent-secondary': this.secondaryColor,
        animationDuration: (2 / this.speed) + 's',
      };
    },
  },
  methods: {
    calculateSecondaryColor(color) {
      const hex = color.replace('#', '');
      const r = parseInt(hex.substr(0, 2), 16);
      const g = parseInt(hex.substr(2, 2), 16);
      const b = parseInt(hex.substr(4, 2), 16);
      
      const factor = (r + g + b) / 3 > 128 ? 0.7 : 1.3;
      return \`rgb(\${Math.round(r * factor)}, \${Math.round(g * factor)}, \${Math.round(b * factor)})\`;
    },
  },
};
</script>`;
  }
}

// Export for use in app.js
window.ExportManager = ExportManager;