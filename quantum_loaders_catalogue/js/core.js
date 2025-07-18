/**
 * Core JavaScript for Quantum Loaders Catalogue
 * Handles theme switching, accessibility, and core functionality
 */

class QuantumLoadersCore {
  constructor() {
    this.currentTheme = 'dark';
    this.isMotionReduced = false;
    this.animationsPaused = false;
    this.currentSpeed = 1;
    this.currentView = 'grid';
    this.searchTerm = '';
    this.filters = {
      category: '',
      complexity: ''
    };
    this.favorites = new Set();
    this.performanceMonitor = null;
    
    this.init();
  }
  
  init() {
    this.loadPreferences();
    this.setupEventListeners();
    this.initializeAccessibility();
    this.initializePerformanceMonitor();
    this.setupKeyboardShortcuts();
    
    // Initialize with a small delay to ensure DOM is ready
    setTimeout(() => {
      this.hideInitialLoader();
    }, 1000);
  }
  
  loadPreferences() {
    // Load theme preference
    const savedTheme = localStorage.getItem('quantum-loaders-theme');
    if (savedTheme && ['dark', 'light', 'neon'].includes(savedTheme)) {
      this.setTheme(savedTheme);
    } else {
      // Auto-detect based on system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      this.setTheme(prefersDark ? 'dark' : 'light');
    }
    
    // Load motion preference
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const savedMotion = localStorage.getItem('quantum-loaders-motion');
    this.isMotionReduced = savedMotion ? savedMotion === 'reduced' : prefersReduced;
    this.updateMotionPreference();
    
    // Load favorites
    const savedFavorites = localStorage.getItem('quantum-loaders-favorites');
    if (savedFavorites) {
      this.favorites = new Set(JSON.parse(savedFavorites));
    }
    
    // Load view preference
    const savedView = localStorage.getItem('quantum-loaders-view');
    if (savedView && ['grid', 'list'].includes(savedView)) {
      this.currentView = savedView;
    }
  }
  
  setupEventListeners() {
    // Theme switcher
    document.querySelectorAll('.theme-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const theme = e.target.dataset.theme;
        this.setTheme(theme);
      });
    });
    
    // Motion toggle
    const motionToggle = document.getElementById('motion-toggle');
    if (motionToggle) {
      motionToggle.addEventListener('click', () => {
        this.toggleMotionPreference();
      });
    }
    
    // Help toggle
    const helpToggle = document.getElementById('help-toggle');
    const helpPanel = document.getElementById('help-panel');
    if (helpToggle && helpPanel) {
      helpToggle.addEventListener('click', () => {
        this.toggleHelpPanel();
      });
    }
    
    // Global animation controls
    const playPauseBtn = document.getElementById('global-play-pause');
    if (playPauseBtn) {
      playPauseBtn.addEventListener('click', () => {
        this.toggleAnimations();
      });
    }
    
    const resetBtn = document.getElementById('global-reset');
    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        this.resetAnimations();
      });
    }
    
    // Speed control
    const speedSlider = document.getElementById('global-speed');
    const speedValue = document.getElementById('speed-value');
    if (speedSlider && speedValue) {
      speedSlider.addEventListener('input', (e) => {
        this.setAnimationSpeed(parseFloat(e.target.value));
      });
    }
    
    // View controls
    const gridViewBtn = document.getElementById('grid-view');
    const listViewBtn = document.getElementById('list-view');
    if (gridViewBtn && listViewBtn) {
      gridViewBtn.addEventListener('click', () => this.setView('grid'));
      listViewBtn.addEventListener('click', () => this.setView('list'));
    }
    
    // Search functionality
    const searchInput = document.getElementById('search-input');
    const searchClear = document.querySelector('.search-clear');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.handleSearch(e.target.value);
      });
    }
    if (searchClear) {
      searchClear.addEventListener('click', () => {
        this.clearSearch();
      });
    }
    
    // Filters
    const categoryFilter = document.getElementById('category-filter');
    const complexityFilter = document.getElementById('complexity-filter');
    if (categoryFilter) {
      categoryFilter.addEventListener('change', (e) => {
        this.setFilter('category', e.target.value);
      });
    }
    if (complexityFilter) {
      complexityFilter.addEventListener('change', (e) => {
        this.setFilter('complexity', e.target.value);
      });
    }
    
    // Modal close handlers
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('modal-close')) {
        this.closeModal(e.target.closest('dialog'));
      }
    });
    
    // Close modals on backdrop click
    document.addEventListener('click', (e) => {
      if (e.target.tagName === 'DIALOG') {
        this.closeModal(e.target);
      }
    });
    
    // System theme change detection
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (!localStorage.getItem('quantum-loaders-theme')) {
        this.setTheme(e.matches ? 'dark' : 'light');
      }
    });
    
    // System motion preference change
    window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', (e) => {
      if (!localStorage.getItem('quantum-loaders-motion')) {
        this.isMotionReduced = e.matches;
        this.updateMotionPreference();
      }
    });
  }
  
  setTheme(theme) {
    if (!['dark', 'light', 'neon'].includes(theme)) return;
    
    // Remove existing theme classes
    document.body.classList.remove('theme-dark', 'theme-light', 'theme-neon');
    
    // Add new theme class
    document.body.classList.add(`theme-${theme}`);
    
    // Update theme buttons
    document.querySelectorAll('.theme-btn').forEach(btn => {
      const isActive = btn.dataset.theme === theme;
      btn.classList.toggle('active', isActive);
      btn.setAttribute('aria-pressed', isActive);
    });
    
    this.currentTheme = theme;
    localStorage.setItem('quantum-loaders-theme', theme);
    
    // Dispatch theme change event
    this.dispatchEvent('themeChange', { theme });
  }
  
  toggleMotionPreference() {
    this.isMotionReduced = !this.isMotionReduced;
    this.updateMotionPreference();
    localStorage.setItem('quantum-loaders-motion', this.isMotionReduced ? 'reduced' : 'normal');
  }
  
  updateMotionPreference() {
    const motionToggle = document.getElementById('motion-toggle');
    if (motionToggle) {
      motionToggle.setAttribute('aria-pressed', this.isMotionReduced);
      motionToggle.textContent = this.isMotionReduced ? '🎭' : '🎬';
    }
    
    if (this.isMotionReduced) {
      document.body.classList.add('respect-motion-preference');
    } else {
      document.body.classList.remove('respect-motion-preference');
    }
    
    this.dispatchEvent('motionPreferenceChange', { reduced: this.isMotionReduced });
  }
  
  toggleHelpPanel() {
    const helpPanel = document.getElementById('help-panel');
    const helpToggle = document.getElementById('help-toggle');
    
    if (!helpPanel || !helpToggle) return;
    
    const isVisible = helpPanel.getAttribute('aria-hidden') === 'false';
    helpPanel.setAttribute('aria-hidden', isVisible);
    helpToggle.setAttribute('aria-expanded', !isVisible);
    
    if (!isVisible) {
      // Focus first element in panel when opening
      const firstFocusable = helpPanel.querySelector('h2');
      if (firstFocusable) firstFocusable.focus();
    }
  }
  
  toggleAnimations() {
    this.animationsPaused = !this.animationsPaused;
    
    const playPauseBtn = document.getElementById('global-play-pause');
    const btnIcon = playPauseBtn?.querySelector('.btn-icon');
    const btnText = playPauseBtn?.querySelector('.btn-text');
    
    if (this.animationsPaused) {
      document.body.classList.add('animation-paused');
      if (btnIcon) btnIcon.textContent = '▶️';
      if (btnText) btnText.textContent = 'Play All';
      if (playPauseBtn) playPauseBtn.setAttribute('aria-pressed', 'true');
    } else {
      document.body.classList.remove('animation-paused');
      if (btnIcon) btnIcon.textContent = '⏸️';
      if (btnText) btnText.textContent = 'Pause All';
      if (playPauseBtn) playPauseBtn.setAttribute('aria-pressed', 'false');
    }
    
    this.dispatchEvent('animationToggle', { paused: this.animationsPaused });
  }
  
  resetAnimations() {
    // Remove and re-add animation classes to restart animations
    const loaders = document.querySelectorAll('.loader-animation');
    loaders.forEach(loader => {
      const parent = loader.parentElement;
      const clone = loader.cloneNode(true);
      parent.removeChild(loader);
      // Force reflow
      parent.offsetHeight;
      parent.appendChild(clone);
    });
    
    this.dispatchEvent('animationReset');
  }
  
  setAnimationSpeed(speed) {
    this.currentSpeed = speed;
    const speedValue = document.getElementById('speed-value');
    if (speedValue) {
      speedValue.textContent = `${speed}x`;
    }
    
    // Apply speed class to body
    document.body.className = document.body.className.replace(/speed-[\d-]+/g, '');
    const speedClass = `speed-${speed.toString().replace('.', '-')}`;
    document.body.classList.add(speedClass);
    
    this.dispatchEvent('speedChange', { speed });
  }
  
  setView(view) {
    if (!['grid', 'list'].includes(view)) return;
    
    this.currentView = view;
    
    // Update view buttons
    const gridBtn = document.getElementById('grid-view');
    const listBtn = document.getElementById('list-view');
    
    if (gridBtn && listBtn) {
      gridBtn.classList.toggle('active', view === 'grid');
      listBtn.classList.toggle('active', view === 'list');
      gridBtn.setAttribute('aria-pressed', view === 'grid');
      listBtn.setAttribute('aria-pressed', view === 'list');
    }
    
    // Update grid classes
    const grid = document.getElementById('loaders-grid');
    if (grid) {
      grid.classList.toggle('list-view', view === 'list');
    }
    
    localStorage.setItem('quantum-loaders-view', view);
    this.dispatchEvent('viewChange', { view });
  }
  
  handleSearch(term) {
    this.searchTerm = term.toLowerCase().trim();
    this.updateResults();
    
    // Update clear button visibility
    const searchClear = document.querySelector('.search-clear');
    if (searchClear) {
      searchClear.style.opacity = term ? '1' : '0';
    }
  }
  
  clearSearch() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
      searchInput.value = '';
      this.handleSearch('');
      searchInput.focus();
    }
  }
  
  setFilter(type, value) {
    this.filters[type] = value;
    this.updateResults();
    this.dispatchEvent('filterChange', { type, value });
  }
  
  updateResults() {
    // This will be called by the loaders data module
    this.dispatchEvent('resultsUpdate', {
      searchTerm: this.searchTerm,
      filters: this.filters
    });
  }
  
  toggleFavorite(loaderId) {
    if (this.favorites.has(loaderId)) {
      this.favorites.delete(loaderId);
    } else {
      this.favorites.add(loaderId);
    }
    
    localStorage.setItem('quantum-loaders-favorites', JSON.stringify([...this.favorites]));
    this.dispatchEvent('favoriteToggle', { loaderId, isFavorite: this.favorites.has(loaderId) });
    
    // Update favorites section visibility
    this.updateFavoritesSection();
  }
  
  updateFavoritesSection() {
    const favoritesSection = document.getElementById('favorites-section');
    if (favoritesSection) {
      favoritesSection.style.display = this.favorites.size > 0 ? 'block' : 'none';
    }
  }
  
  openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal && modal.tagName === 'DIALOG') {
      modal.showModal();
      
      // Focus first focusable element
      const firstFocusable = modal.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
      if (firstFocusable) {
        firstFocusable.focus();
      }
      
      this.dispatchEvent('modalOpen', { modalId });
    }
  }
  
  closeModal(modal) {
    if (modal && modal.tagName === 'DIALOG') {
      modal.close();
      this.dispatchEvent('modalClose', { modalId: modal.id });
    }
  }
  
  initializeAccessibility() {
    // Announce page load to screen readers
    this.announceToScreenReader('Quantum Loaders Catalogue loaded. Use tab to navigate through loaders.');
    
    // Set up focus management
    this.setupFocusManagement();
    
    // Set up ARIA live regions
    this.setupLiveRegions();
  }
  
  setupFocusManagement() {
    // Ensure modals trap focus
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Tab') {
        const modal = document.querySelector('dialog[open]');
        if (modal) {
          this.trapFocus(e, modal);
        }
      }
    });
  }
  
  trapFocus(event, container) {
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];
    
    if (event.shiftKey && document.activeElement === firstElement) {
      event.preventDefault();
      lastElement.focus();
    } else if (!event.shiftKey && document.activeElement === lastElement) {
      event.preventDefault();
      firstElement.focus();
    }
  }
  
  setupLiveRegions() {
    // Create live region for announcements
    const liveRegion = document.createElement('div');
    liveRegion.setAttribute('aria-live', 'polite');
    liveRegion.setAttribute('aria-atomic', 'true');
    liveRegion.className = 'sr-only';
    liveRegion.id = 'live-region';
    document.body.appendChild(liveRegion);
  }
  
  announceToScreenReader(message) {
    const liveRegion = document.getElementById('live-region');
    if (liveRegion) {
      liveRegion.textContent = message;
      
      // Clear after announcement
      setTimeout(() => {
        liveRegion.textContent = '';
      }, 1000);
    }
  }
  
  setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      // Don't trigger shortcuts when typing in inputs
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        return;
      }
      
      switch (e.key) {
        case ' ':
          e.preventDefault();
          this.toggleAnimations();
          break;
        case 'f':
        case 'F':
          e.preventDefault();
          // Focus search input
          const searchInput = document.getElementById('search-input');
          if (searchInput) searchInput.focus();
          break;
        case 'Escape':
          // Close open modals or panels
          const openModal = document.querySelector('dialog[open]');
          if (openModal) {
            this.closeModal(openModal);
          } else {
            const helpPanel = document.getElementById('help-panel');
            if (helpPanel && helpPanel.getAttribute('aria-hidden') === 'false') {
              this.toggleHelpPanel();
            }
          }
          break;
        case '1':
          e.preventDefault();
          this.setTheme('dark');
          break;
        case '2':
          e.preventDefault();
          this.setTheme('light');
          break;
        case '3':
          e.preventDefault();
          this.setTheme('neon');
          break;
      }
    });
  }
  
  initializePerformanceMonitor() {
    if (typeof PerformanceObserver !== 'undefined') {
      this.performanceMonitor = new PerformanceMonitor();
    }
  }
  
  hideInitialLoader() {
    const initialLoader = document.getElementById('initial-loader');
    if (initialLoader) {
      initialLoader.classList.add('hidden');
      setTimeout(() => {
        initialLoader.style.display = 'none';
      }, 350);
    }
  }
  
  dispatchEvent(eventName, detail = {}) {
    const event = new CustomEvent(`quantumLoaders:${eventName}`, {
      detail,
      bubbles: true
    });
    document.dispatchEvent(event);
  }
  
  // Utility methods
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
  
  throttle(func, limit) {
    let inThrottle;
    return function executedFunction(...args) {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    }
  }
}

// Performance Monitor Class
class PerformanceMonitor {
  constructor() {
    this.fps = 60;
    this.frameCount = 0;
    this.lastTime = performance.now();
    this.isMonitoring = false;
    
    this.init();
  }
  
  init() {
    this.createMonitorElement();
    this.startMonitoring();
    this.observePerformance();
  }
  
  createMonitorElement() {
    const monitor = document.getElementById('performance-monitor');
    if (monitor) {
      const fpsValue = monitor.querySelector('#fps-value');
      const memoryValue = monitor.querySelector('#memory-value');
      const gpuValue = monitor.querySelector('#gpu-value');
      
      this.elements = { monitor, fpsValue, memoryValue, gpuValue };
    }
  }
  
  startMonitoring() {
    this.isMonitoring = true;
    this.measureFPS();
    
    // Update memory usage every 2 seconds
    setInterval(() => {
      this.updateMemoryUsage();
    }, 2000);
  }
  
  measureFPS() {
    if (!this.isMonitoring) return;
    
    const currentTime = performance.now();
    this.frameCount++;
    
    if (currentTime >= this.lastTime + 1000) {
      this.fps = Math.round((this.frameCount * 1000) / (currentTime - this.lastTime));
      this.frameCount = 0;
      this.lastTime = currentTime;
      
      this.updateFPSDisplay();
    }
    
    requestAnimationFrame(() => this.measureFPS());
  }
  
  updateFPSDisplay() {
    if (this.elements?.fpsValue) {
      this.elements.fpsValue.textContent = this.fps;
      
      // Color code FPS
      if (this.fps >= 55) {
        this.elements.fpsValue.style.color = 'var(--color-accent-primary)';
      } else if (this.fps >= 30) {
        this.elements.fpsValue.style.color = 'orange';
      } else {
        this.elements.fpsValue.style.color = 'red';
      }
    }
  }
  
  updateMemoryUsage() {
    if (performance.memory && this.elements?.memoryValue) {
      const used = Math.round(performance.memory.usedJSHeapSize / 1048576);
      this.elements.memoryValue.textContent = `${used}MB`;
    }
  }
  
  observePerformance() {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          if (entry.entryType === 'measure') {
            console.log(`Performance: ${entry.name} took ${entry.duration.toFixed(2)}ms`);
          }
        });
      });
      
      observer.observe({ entryTypes: ['measure'] });
    }
  }
  
  toggleVisibility() {
    if (this.elements?.monitor) {
      const isVisible = this.elements.monitor.style.display !== 'none';
      this.elements.monitor.style.display = isVisible ? 'none' : 'block';
    }
  }
}

// Export for use in other modules
window.QuantumLoadersCore = QuantumLoadersCore;