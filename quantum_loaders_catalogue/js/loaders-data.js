/**
 * Quantum Loaders Data Module
 * Contains all loader definitions and rendering logic
 */

class QuantumLoadersData {
  constructor(core) {
    this.core = core;
    this.loaders = this.initializeLoaders();
    this.filteredLoaders = [...this.loaders];
    
    this.init();
  }
  
  init() {
    this.renderLoaders();
    this.setupEventListeners();
    this.updateResultsCount();
  }
  
  initializeLoaders() {
    return [
      {
        id: 'quantum-tunnel',
        title: 'Quantum Tunnel',
        category: 'quantum',
        complexity: 'medium',
        description: 'A mesmerizing tunnel effect with expanding quantum rings',
        tags: ['tunnel', 'rings', 'expansion', 'portal'],
        size: '2.1KB',
        browserSupport: 'IE10+',
        cssClass: 'quantum-tunnel',
        customizable: {
          color: true,
          speed: true,
          size: true
        },
        html: this.generateTunnelHTML(),
        css: this.generateTunnelCSS()
      },
      {
        id: 'dna-sequencer',
        title: 'DNA Sequencer',
        category: 'bio',
        complexity: 'complex',
        description: 'Double helix DNA structure with sequencing base pairs',
        tags: ['dna', 'helix', 'biology', 'genetic'],
        size: '3.2KB',
        browserSupport: 'Chrome 60+',
        cssClass: 'dna-sequencer',
        customizable: {
          color: true,
          speed: true,
          size: true
        },
        html: this.generateDNAHTML(),
        css: this.generateDNACSS()
      },
      {
        id: 'holographic-cube',
        title: 'Holographic Cube',
        category: 'tech',
        complexity: 'complex',
        description: '3D rotating cube with holographic transparency effects',
        tags: ['3d', 'cube', 'hologram', 'rotation'],
        size: '4.1KB',
        browserSupport: 'Chrome 45+',
        cssClass: 'holographic-cube',
        customizable: {
          color: true,
          speed: true,
          size: true
        },
        html: this.generateCubeHTML(),
        css: this.generateCubeCSS()
      },
      {
        id: 'energy-sphere',
        title: 'Energy Sphere',
        category: 'energy',
        complexity: 'medium',
        description: 'Pulsating energy sphere with orbital rings',
        tags: ['sphere', 'energy', 'pulse', 'orbital'],
        size: '2.8KB',
        browserSupport: 'IE11+',
        cssClass: 'energy-sphere',
        customizable: {
          color: true,
          speed: true,
          size: true
        },
        html: this.generateSphereHTML(),
        css: this.generateSphereCSS()
      },
      {
        id: 'particle-accelerator',
        title: 'Particle Accelerator',
        category: 'quantum',
        complexity: 'medium',
        description: 'Particles orbiting in a circular accelerator chamber',
        tags: ['particles', 'orbit', 'physics', 'acceleration'],
        size: '2.5KB',
        browserSupport: 'Chrome 50+',
        cssClass: 'particle-accelerator',
        customizable: {
          color: true,
          speed: true,
          size: true
        },
        html: this.generateAcceleratorHTML(),
        css: this.generateAcceleratorCSS()
      },
      {
        id: 'quantum-gate',
        title: 'Quantum Gate Circuit',
        category: 'quantum',
        complexity: 'complex',
        description: 'Quantum computing gate with traveling qubits',
        tags: ['quantum', 'gate', 'circuit', 'qubits'],
        size: '3.5KB',
        browserSupport: 'Chrome 55+',
        cssClass: 'quantum-gate',
        customizable: {
          color: true,
          speed: true,
          size: true
        },
        html: this.generateGateHTML(),
        css: this.generateGateCSS()
      },
      {
        id: 'electromagnetic-field',
        title: 'Electromagnetic Field',
        category: 'energy',
        complexity: 'medium',
        description: 'Expanding electromagnetic field waves',
        tags: ['electromagnetic', 'waves', 'field', 'physics'],
        size: '2.3KB',
        browserSupport: 'IE10+',
        cssClass: 'electromagnetic-field',
        customizable: {
          color: true,
          speed: true,
          size: true
        },
        html: this.generateFieldHTML(),
        css: this.generateFieldCSS()
      },
      {
        id: 'plasma-storm',
        title: 'Plasma Storm',
        category: 'energy',
        complexity: 'complex',
        description: 'Chaotic plasma lightning with storm effects',
        tags: ['plasma', 'lightning', 'storm', 'chaos'],
        size: '3.8KB',
        browserSupport: 'Chrome 60+',
        cssClass: 'plasma-storm',
        customizable: {
          color: true,
          speed: true,
          size: true
        },
        html: this.generateStormHTML(),
        css: this.generateStormCSS()
      },
      {
        id: 'dark-matter-vortex',
        title: 'Dark Matter Vortex',
        category: 'space',
        complexity: 'complex',
        description: 'Swirling dark matter vortex with gravitational effects',
        tags: ['dark matter', 'vortex', 'gravity', 'space'],
        size: '3.6KB',
        browserSupport: 'Chrome 55+',
        cssClass: 'dark-matter-vortex',
        customizable: {
          color: true,
          speed: true,
          size: true
        },
        html: this.generateVortexHTML(),
        css: this.generateVortexCSS()
      },
      {
        id: 'singularity-collapse',
        title: 'Singularity Collapse',
        category: 'space',
        complexity: 'complex',
        description: 'Matter collapsing into a gravitational singularity',
        tags: ['singularity', 'collapse', 'gravity', 'black hole'],
        size: '4.2KB',
        browserSupport: 'Chrome 60+',
        cssClass: 'singularity-collapse',
        customizable: {
          color: true,
          speed: true,
          size: true
        },
        html: this.generateSingularityHTML(),
        css: this.generateSingularityCSS()
      }
    ];
  }
  
  setupEventListeners() {
    // Listen to core events
    document.addEventListener('quantumLoaders:resultsUpdate', (e) => {
      this.filterLoaders(e.detail.searchTerm, e.detail.filters);
    });
    
    document.addEventListener('quantumLoaders:favoriteToggle', (e) => {
      this.updateFavoriteButton(e.detail.loaderId, e.detail.isFavorite);
    });
  }
  
  filterLoaders(searchTerm = '', filters = {}) {
    this.filteredLoaders = this.loaders.filter(loader => {
      // Search filter
      if (searchTerm) {
        const searchableText = `${loader.title} ${loader.description} ${loader.tags.join(' ')}`.toLowerCase();
        if (!searchableText.includes(searchTerm)) {
          return false;
        }
      }
      
      // Category filter
      if (filters.category && loader.category !== filters.category) {
        return false;
      }
      
      // Complexity filter
      if (filters.complexity && loader.complexity !== filters.complexity) {
        return false;
      }
      
      return true;
    });
    
    this.renderLoaders();
    this.updateResultsCount();
  }
  
  renderLoaders() {
    const grid = document.getElementById('loaders-grid');
    if (!grid) return;
    
    // Clear existing content
    grid.innerHTML = '';
    
    // Render filtered loaders
    this.filteredLoaders.forEach(loader => {
      const card = this.createLoaderCard(loader);
      grid.appendChild(card);
    });
    
    // Render favorites
    this.renderFavorites();
  }
  
  renderFavorites() {
    const favoritesGrid = document.getElementById('favorites-grid');
    if (!favoritesGrid) return;
    
    favoritesGrid.innerHTML = '';
    
    const favoriteLoaders = this.loaders.filter(loader => 
      this.core.favorites.has(loader.id)
    );
    
    favoriteLoaders.forEach(loader => {
      const card = this.createLoaderCard(loader, true);
      favoritesGrid.appendChild(card);
    });
    
    // Show/hide favorites section
    const favoritesSection = document.getElementById('favorites-section');
    if (favoritesSection) {
      favoritesSection.style.display = favoriteLoaders.length > 0 ? 'block' : 'none';
    }
  }
  
  createLoaderCard(loader, isFavorite = false) {
    const card = document.createElement('div');
    card.className = 'loader-card';
    card.setAttribute('role', 'gridcell');
    card.setAttribute('tabindex', '0');
    card.setAttribute('data-loader-id', loader.id);
    
    const isFav = this.core.favorites.has(loader.id);
    
    card.innerHTML = `
      <div class="loader-preview">
        <div class="loader-animation ${loader.cssClass}" data-loader-id="${loader.id}">
          ${loader.html}
        </div>
      </div>
      <div class="loader-info">
        <h3 class="loader-title">${loader.title}</h3>
        <div class="loader-category">${this.formatCategory(loader.category)}</div>
        <p class="loader-description">${loader.description}</p>
      </div>
      <div class="loader-actions">
        <button type="button" class="favorite-btn ${isFav ? 'active' : ''}" 
                data-loader-id="${loader.id}" 
                aria-label="${isFav ? 'Remove from' : 'Add to'} favorites">
          ${isFav ? '♥' : '♡'}
        </button>
        <div class="loader-stats">
          <span class="complexity">${this.formatComplexity(loader.complexity)}</span>
          <span class="size">${loader.size}</span>
        </div>
      </div>
    `;
    
    // Add event listeners
    card.addEventListener('click', (e) => {
      if (!e.target.classList.contains('favorite-btn')) {
        this.openLoaderModal(loader);
      }
    });
    
    card.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        this.openLoaderModal(loader);
      }
    });
    
    const favoriteBtn = card.querySelector('.favorite-btn');
    favoriteBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      this.core.toggleFavorite(loader.id);
    });
    
    return card;
  }
  
  openLoaderModal(loader) {
    const modal = document.getElementById('loader-modal');
    if (!modal) return;
    
    // Populate modal with loader data
    this.populateLoaderModal(loader);
    
    // Open modal
    this.core.openModal('loader-modal');
  }
  
  populateLoaderModal(loader) {
    const modal = document.getElementById('loader-modal');
    
    // Update title
    const title = modal.querySelector('#modal-title');
    if (title) title.textContent = loader.title;
    
    // Update preview
    const previewContainer = modal.querySelector('#modal-preview-container');
    if (previewContainer) {
      previewContainer.innerHTML = `
        <div class="loader-animation ${loader.cssClass}" style="width: 100px; height: 100px;">
          ${loader.html}
        </div>
      `;
    }
    
    // Update properties
    const categoryEl = modal.querySelector('#modal-category');
    const complexityEl = modal.querySelector('#modal-complexity');
    const sizeEl = modal.querySelector('#modal-size');
    const supportEl = modal.querySelector('#modal-support');
    
    if (categoryEl) categoryEl.textContent = this.formatCategory(loader.category);
    if (complexityEl) complexityEl.textContent = this.formatComplexity(loader.complexity);
    if (sizeEl) sizeEl.textContent = loader.size;
    if (supportEl) supportEl.textContent = loader.browserSupport;
    
    // Update favorite button
    const favoriteBtn = modal.querySelector('#favorite-toggle');
    if (favoriteBtn) {
      const isFav = this.core.favorites.has(loader.id);
      favoriteBtn.innerHTML = `
        <span class="btn-icon">${isFav ? '♥' : '♡'}</span>
        <span class="btn-text">${isFav ? 'Remove from' : 'Add to'} Favorites</span>
      `;
      favoriteBtn.onclick = () => this.core.toggleFavorite(loader.id);
    }
    
    // Store current loader for export
    modal.dataset.currentLoader = loader.id;
    
    // Setup customization controls
    this.setupCustomizationControls(loader);
    
    // Setup export handlers
    this.setupExportHandlers(loader);
  }
  
  setupCustomizationControls(loader) {
    const modal = document.getElementById('loader-modal');
    const preview = modal.querySelector('.loader-animation');
    
    // Size control
    const sizeControl = modal.querySelector('#custom-size');
    const sizeValue = modal.querySelector('#custom-size-value');
    if (sizeControl && sizeValue && preview) {
      sizeControl.addEventListener('input', (e) => {
        const size = e.target.value + 'px';
        sizeValue.textContent = size;
        preview.style.width = size;
        preview.style.height = size;
      });
    }
    
    // Speed control
    const speedControl = modal.querySelector('#custom-speed');
    const speedValue = modal.querySelector('#custom-speed-value');
    if (speedControl && speedValue && preview) {
      speedControl.addEventListener('input', (e) => {
        const speed = e.target.value;
        speedValue.textContent = speed + 'x';
        preview.style.animationDuration = `${2 / speed}s`;
      });
    }
    
    // Color control
    const colorControl = modal.querySelector('#custom-color');
    if (colorControl && preview) {
      colorControl.addEventListener('input', (e) => {
        const color = e.target.value;
        preview.style.setProperty('--color-accent-primary', color);
        preview.style.setProperty('--custom-color', color);
      });
    }
    
    // Background control
    const backgroundControl = modal.querySelector('#preview-background');
    const previewContainer = modal.querySelector('#modal-preview-container');
    if (backgroundControl && previewContainer) {
      backgroundControl.addEventListener('change', (e) => {
        const bg = e.target.value;
        previewContainer.className = 'preview-container';
        if (bg !== 'transparent') {
          previewContainer.classList.add(`bg-${bg}`);
        }
      });
    }
  }
  
  setupExportHandlers(loader) {
    const modal = document.getElementById('loader-modal');
    
    // Copy CSS handler
    const copyCssBtn = modal.querySelector('#copy-css');
    if (copyCssBtn) {
      copyCssBtn.onclick = () => this.copyToClipboard(loader.css, 'CSS');
    }
    
    // Copy SVG handler (placeholder - would need SVG conversion)
    const copySvgBtn = modal.querySelector('#copy-svg');
    if (copySvgBtn) {
      copySvgBtn.onclick = () => this.copyToClipboard(this.generateSVG(loader), 'SVG');
    }
    
    // Export handler
    const exportBtn = modal.querySelector('#export-loader');
    if (exportBtn) {
      exportBtn.onclick = () => this.openExportModal(loader);
    }
  }
  
  openExportModal(loader) {
    this.core.closeModal(document.getElementById('loader-modal'));
    
    const exportModal = document.getElementById('code-modal');
    if (!exportModal) return;
    
    // Populate export modal
    this.populateExportModal(loader);
    this.core.openModal('code-modal');
  }
  
  populateExportModal(loader) {
    const modal = document.getElementById('code-modal');
    const codeContent = modal.querySelector('#export-code-content');
    const formatRadios = modal.querySelectorAll('input[name="export-format"]');
    
    const updateCode = () => {
      const selectedFormat = modal.querySelector('input[name="export-format"]:checked')?.value || 'html';
      const code = this.generateExportCode(loader, selectedFormat);
      if (codeContent) {
        codeContent.textContent = code;
        codeContent.className = `language-${this.getLanguageClass(selectedFormat)}`;
      }
    };
    
    // Setup format change listeners
    formatRadios.forEach(radio => {
      radio.addEventListener('change', updateCode);
    });
    
    // Initial code generation
    updateCode();
    
    // Setup copy and download handlers
    const copyBtn = modal.querySelector('#copy-export-code');
    const downloadBtn = modal.querySelector('#download-export');
    
    if (copyBtn) {
      copyBtn.onclick = () => {
        const code = codeContent?.textContent || '';
        this.copyToClipboard(code, 'Export code');
      };
    }
    
    if (downloadBtn) {
      downloadBtn.onclick = () => {
        const selectedFormat = modal.querySelector('input[name="export-format"]:checked')?.value || 'html';
        const code = codeContent?.textContent || '';
        this.downloadFile(code, `${loader.id}.${this.getFileExtension(selectedFormat)}`, this.getMimeType(selectedFormat));
      };
    }
  }
  
  generateExportCode(loader, format) {
    switch (format) {
      case 'html':
        return this.generateStandaloneHTML(loader);
      case 'css':
        return loader.css;
      case 'react':
        return this.generateReactComponent(loader);
      case 'vue':
        return this.generateVueComponent(loader);
      case 'angular':
        return this.generateAngularComponent(loader);
      case 'svg':
        return this.generateSVG(loader);
      default:
        return loader.css;
    }
  }
  
  generateStandaloneHTML(loader) {
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${loader.title} - Quantum Loader</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            background: #0a0e1a;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            font-family: system-ui, sans-serif;
        }
        
        .container {
            text-align: center;
            color: #e2e8f0;
        }
        
        .loader-title {
            margin-bottom: 20px;
            font-size: 1.5rem;
            color: #00ff88;
        }
        
        ${loader.css}
    </style>
</head>
<body>
    <div class="container">
        <h1 class="loader-title">${loader.title}</h1>
        <div class="loader-animation ${loader.cssClass}">
            ${loader.html}
        </div>
    </div>
</body>
</html>`;
  }
  
  generateReactComponent(loader) {
    const componentName = loader.title.replace(/\s+/g, '') + 'Loader';
    return `import React from 'react';
import './styles.css'; // Import the CSS

const ${componentName} = ({ size = 60, speed = 1, color = '#00ff88' }) => {
  const loaderStyle = {
    width: size,
    height: size,
    '--color-accent-primary': color,
    '--custom-color': color,
    animationDuration: \`\${2 / speed}s\`
  };

  return (
    <div 
      className="loader-animation ${loader.cssClass}" 
      style={loaderStyle}
      role="img"
      aria-label="${loader.title} loading animation"
    >
      ${loader.html.replace(/\n\s*/g, '\n      ')}
    </div>
  );
};

export default ${componentName};`;
  }
  
  generateVueComponent(loader) {
    const componentName = loader.title.replace(/\s+/g, '') + 'Loader';
    return `<template>
  <div 
    class="loader-animation ${loader.cssClass}"
    :style="loaderStyle"
    role="img"
    :aria-label="'${loader.title} loading animation'"
  >
    ${loader.html.replace(/\n\s*/g, '\n    ')}
  </div>
</template>

<script>
export default {
  name: '${componentName}',
  props: {
    size: {
      type: Number,
      default: 60
    },
    speed: {
      type: Number,
      default: 1
    },
    color: {
      type: String,
      default: '#00ff88'
    }
  },
  computed: {
    loaderStyle() {
      return {
        width: this.size + 'px',
        height: this.size + 'px',
        '--color-accent-primary': this.color,
        '--custom-color': this.color,
        animationDuration: (2 / this.speed) + 's'
      };
    }
  }
};
</script>

<style scoped>
${loader.css}
</style>`;
  }
  
  generateAngularComponent(loader) {
    const componentName = loader.title.replace(/\s+/g, '') + 'LoaderComponent';
    const selector = loader.id.replace(/_/g, '-');
    
    return `import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-${selector}',
  template: \`
    <div 
      class="loader-animation ${loader.cssClass}"
      [style.width.px]="size"
      [style.height.px]="size"
      [style.--color-accent-primary]="color"
      [style.--custom-color]="color"
      [style.animation-duration]="(2 / speed) + 's'"
      role="img"
      [attr.aria-label]="'${loader.title} loading animation'"
    >
      ${loader.html.replace(/\n\s*/g, '\n      ')}
    </div>
  \`,
  styles: [\`
    ${loader.css.replace(/\n/g, '\n    ')}
  \`]
})
export class ${componentName} {
  @Input() size: number = 60;
  @Input() speed: number = 1;
  @Input() color: string = '#00ff88';
}`;
  }
  
  generateSVG(loader) {
    // This is a simplified SVG version - would need more complex conversion for full animations
    return `<svg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .loader-svg {
        animation: spin 2s linear infinite;
      }
      @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
      }
    </style>
  </defs>
  <g class="loader-svg">
    <circle cx="30" cy="30" r="25" fill="none" stroke="#00ff88" stroke-width="2" opacity="0.3"/>
    <circle cx="30" cy="30" r="25" fill="none" stroke="#00ff88" stroke-width="2" 
            stroke-dasharray="50,100" stroke-linecap="round"/>
  </g>
  <text x="30" y="70" text-anchor="middle" fill="#00ff88" font-size="8">${loader.title}</text>
</svg>`;
  }
  
  updateResultsCount() {
    const countElement = document.getElementById('search-results-count');
    if (countElement) {
      const count = this.filteredLoaders.length;
      const text = count === 1 ? '1 loader found' : `${count} loaders found`;
      countElement.textContent = text;
    }
  }
  
  updateFavoriteButton(loaderId, isFavorite) {
    const buttons = document.querySelectorAll(`[data-loader-id="${loaderId}"] .favorite-btn`);
    buttons.forEach(btn => {
      btn.textContent = isFavorite ? '♥' : '♡';
      btn.classList.toggle('active', isFavorite);
      btn.setAttribute('aria-label', `${isFavorite ? 'Remove from' : 'Add to'} favorites`);
    });
    
    // Update modal favorite button if open
    const modal = document.getElementById('loader-modal');
    if (modal?.dataset.currentLoader === loaderId) {
      const modalBtn = modal.querySelector('#favorite-toggle');
      if (modalBtn) {
        modalBtn.innerHTML = `
          <span class="btn-icon">${isFavorite ? '♥' : '♡'}</span>
          <span class="btn-text">${isFavorite ? 'Remove from' : 'Add to'} Favorites</span>
        `;
      }
    }
    
    // Re-render favorites
    this.renderFavorites();
  }
  
  copyToClipboard(text, type = 'Content') {
    navigator.clipboard.writeText(text).then(() => {
      this.core.announceToScreenReader(`${type} copied to clipboard`);
      
      // Show temporary success message
      this.showToast(`${type} copied!`, 'success');
    }).catch(err => {
      console.error('Failed to copy:', err);
      this.showToast('Failed to copy', 'error');
    });
  }
  
  downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    this.showToast(`${filename} downloaded!`, 'success');
  }
  
  showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: var(--color-bg-modal);
      color: var(--color-text-primary);
      padding: 12px 20px;
      border-radius: 8px;
      border: 1px solid var(--color-border-primary);
      z-index: 10000;
      animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.style.animation = 'slideOut 0.3s ease-in forwards';
      setTimeout(() => {
        document.body.removeChild(toast);
      }, 300);
    }, 3000);
  }
  
  formatCategory(category) {
    const categories = {
      quantum: 'Quantum Physics',
      bio: 'Biological',
      tech: 'Technology',
      space: 'Space & Cosmic',
      energy: 'Energy & Particles'
    };
    return categories[category] || category;
  }
  
  formatComplexity(complexity) {
    return complexity.charAt(0).toUpperCase() + complexity.slice(1);
  }
  
  getLanguageClass(format) {
    const languages = {
      html: 'html',
      css: 'css',
      react: 'jsx',
      vue: 'vue',
      angular: 'typescript',
      svg: 'xml'
    };
    return languages[format] || 'text';
  }
  
  getFileExtension(format) {
    const extensions = {
      html: 'html',
      css: 'css',
      react: 'jsx',
      vue: 'vue',
      angular: 'ts',
      svg: 'svg'
    };
    return extensions[format] || 'txt';
  }
  
  getMimeType(format) {
    const mimeTypes = {
      html: 'text/html',
      css: 'text/css',
      react: 'text/javascript',
      vue: 'text/javascript',
      angular: 'text/typescript',
      svg: 'image/svg+xml'
    };
    return mimeTypes[format] || 'text/plain';
  }
  
  // HTML generators for each loader type
  generateTunnelHTML() { return ''; }
  generateDNAHTML() { return '<div class="dna-base"></div><div class="dna-base"></div><div class="dna-base"></div>'; }
  generateCubeHTML() { 
    return `<div class="face front"></div><div class="face back"></div><div class="face right"></div><div class="face left"></div><div class="face top"></div><div class="face bottom"></div>`;
  }
  generateSphereHTML() { return ''; }
  generateAcceleratorHTML() { return '<div class="particle"></div><div class="particle"></div><div class="particle"></div>'; }
  generateGateHTML() { 
    return `<div class="gate-line"></div><div class="gate-line"></div><div class="gate-line"></div><div class="quantum-bit"></div><div class="quantum-bit"></div><div class="quantum-bit"></div>`;
  }
  generateFieldHTML() { 
    return '<div class="field-line"></div><div class="field-line"></div><div class="field-line"></div><div class="field-line"></div>';
  }
  generateStormHTML() { return '<div class="lightning"></div><div class="lightning"></div><div class="lightning"></div>'; }
  generateVortexHTML() { return ''; }
  generateSingularityHTML() { 
    return '<div class="matter-particle"></div><div class="matter-particle"></div><div class="matter-particle"></div><div class="matter-particle"></div><div class="matter-particle"></div><div class="matter-particle"></div>';
  }
  
  // CSS generators (simplified - in real implementation would be more detailed)
  generateTunnelCSS() { return `/* Quantum Tunnel CSS - see loaders.css for full implementation */`; }
  generateDNACSS() { return `/* DNA Sequencer CSS - see loaders.css for full implementation */`; }
  generateCubeCSS() { return `/* Holographic Cube CSS - see loaders.css for full implementation */`; }
  generateSphereCSS() { return `/* Energy Sphere CSS - see loaders.css for full implementation */`; }
  generateAcceleratorCSS() { return `/* Particle Accelerator CSS - see loaders.css for full implementation */`; }
  generateGateCSS() { return `/* Quantum Gate CSS - see loaders.css for full implementation */`; }
  generateFieldCSS() { return `/* Electromagnetic Field CSS - see loaders.css for full implementation */`; }
  generateStormCSS() { return `/* Plasma Storm CSS - see loaders.css for full implementation */`; }
  generateVortexCSS() { return `/* Dark Matter Vortex CSS - see loaders.css for full implementation */`; }
  generateSingularityCSS() { return `/* Singularity Collapse CSS - see loaders.css for full implementation */`; }
}

// Export for use in app.js
window.QuantumLoadersData = QuantumLoadersData;