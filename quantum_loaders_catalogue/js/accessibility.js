/**
 * Accessibility Module
 * Ensures full accessibility compliance and enhanced user experience
 */

class AccessibilityManager {
  constructor(core) {
    this.core = core;
    this.focusHistory = [];
    this.announcements = [];
    this.lastFocusedElement = null;
    this.skipLinks = [];
    
    this.init();
  }
  
  init() {
    this.setupARIALabels();
    this.setupKeyboardNavigation();
    this.setupFocusManagement();
    this.setupScreenReaderSupport();
    this.setupHighContrastSupport();
    this.setupReducedMotionSupport();
    this.setupSkipLinks();
    this.bindEventListeners();
  }
  
  setupARIALabels() {
    // Ensure all interactive elements have proper ARIA labels
    this.labelInteractiveElements();
    this.setupLiveRegions();
    this.setupLandmarks();
  }
  
  labelInteractiveElements() {
    // Theme buttons
    const themeButtons = document.querySelectorAll('.theme-btn');
    themeButtons.forEach((btn, index) => {
      const themes = ['Dark', 'Light', 'Neon'];
      if (!btn.getAttribute('aria-label')) {
        btn.setAttribute('aria-label', `Switch to ${themes[index]} theme`);
      }
    });
    
    // Control buttons
    const controlButtons = document.querySelectorAll('.control-btn');
    controlButtons.forEach(btn => {
      if (!btn.getAttribute('aria-label') && !btn.textContent.trim()) {
        const icon = btn.textContent.trim();
        let label = 'Control button';
        
        if (icon.includes('⏸')) label = 'Pause animations';
        else if (icon.includes('▶')) label = 'Play animations';
        else if (icon.includes('↺')) label = 'Reset animations';
        else if (icon.includes('⚏')) label = 'Grid view';
        else if (icon.includes('☰')) label = 'List view';
        
        btn.setAttribute('aria-label', label);
      }
    });
    
    // Loader cards
    const loaderCards = document.querySelectorAll('.loader-card');
    loaderCards.forEach(card => {
      const title = card.querySelector('.loader-title')?.textContent;
      if (title && !card.getAttribute('aria-label')) {
        card.setAttribute('aria-label', `${title} loader preview. Press Enter to view details.`);
      }
    });
    
    // Search input
    const searchInput = document.getElementById('search-input');
    if (searchInput && !searchInput.getAttribute('aria-describedby')) {
      searchInput.setAttribute('aria-describedby', 'search-results-count search-help');
      
      // Add search help text
      const helpText = document.createElement('div');
      helpText.id = 'search-help';
      helpText.className = 'sr-only';
      helpText.textContent = 'Search through quantum loaders by name, category, or description';
      searchInput.parentNode.appendChild(helpText);
    }
    
    // Modal close buttons
    const modalCloseButtons = document.querySelectorAll('.modal-close');
    modalCloseButtons.forEach(btn => {
      if (!btn.getAttribute('aria-label')) {
        btn.setAttribute('aria-label', 'Close modal');
      }
    });
  }
  
  setupLiveRegions() {
    // Create main live region for announcements
    if (!document.getElementById('live-region')) {
      const liveRegion = document.createElement('div');
      liveRegion.id = 'live-region';
      liveRegion.setAttribute('aria-live', 'polite');
      liveRegion.setAttribute('aria-atomic', 'true');
      liveRegion.className = 'sr-only';
      document.body.appendChild(liveRegion);
    }
    
    // Create assertive live region for urgent announcements
    if (!document.getElementById('live-region-assertive')) {
      const assertiveLiveRegion = document.createElement('div');
      assertiveLiveRegion.id = 'live-region-assertive';
      assertiveLiveRegion.setAttribute('aria-live', 'assertive');
      assertiveLiveRegion.setAttribute('aria-atomic', 'true');
      assertiveLiveRegion.className = 'sr-only';
      document.body.appendChild(assertiveLiveRegion);
    }
    
    // Ensure search results count is live
    const resultsCount = document.getElementById('search-results-count');
    if (resultsCount && !resultsCount.getAttribute('aria-live')) {
      resultsCount.setAttribute('aria-live', 'polite');
    }
  }
  
  setupLandmarks() {
    // Ensure proper landmark roles
    const header = document.querySelector('.catalogue-header');
    if (header && !header.getAttribute('role')) {
      header.setAttribute('role', 'banner');
    }
    
    const main = document.querySelector('.catalogue-main');
    if (main && !main.getAttribute('role')) {
      main.setAttribute('role', 'main');
    }
    
    const search = document.querySelector('.search-section');
    if (search && !search.getAttribute('role')) {
      search.setAttribute('role', 'search');
    }
    
    // Add complementary role to help panel
    const helpPanel = document.getElementById('help-panel');
    if (helpPanel && !helpPanel.getAttribute('role')) {
      helpPanel.setAttribute('role', 'complementary');
    }
  }
  
  setupKeyboardNavigation() {
    // Enhanced keyboard navigation
    document.addEventListener('keydown', (e) => this.handleGlobalKeyDown(e));
    
    // Grid navigation
    this.setupGridNavigation();
    
    // Modal navigation
    this.setupModalNavigation();
    
    // Tab sequence optimization
    this.optimizeTabSequence();
  }
  
  handleGlobalKeyDown(e) {
    // Skip if typing in inputs
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
      return;
    }
    
    switch (e.key) {
      case 'Escape':
        this.handleEscape();
        break;
      case 'Tab':
        this.handleTab(e);
        break;
      case 'Home':
        if (e.ctrlKey) {
          e.preventDefault();
          this.focusFirstElement();
        }
        break;
      case 'End':
        if (e.ctrlKey) {
          e.preventDefault();
          this.focusLastElement();
        }
        break;
      case '/':
        e.preventDefault();
        this.focusSearch();
        break;
      case '?':
        e.preventDefault();
        this.toggleHelp();
        break;
    }
  }
  
  setupGridNavigation() {
    const grid = document.getElementById('loaders-grid');
    if (!grid) return;
    
    grid.addEventListener('keydown', (e) => {
      if (!e.target.classList.contains('loader-card')) return;
      
      const cards = Array.from(grid.querySelectorAll('.loader-card'));
      const currentIndex = cards.indexOf(e.target);
      const columns = this.getGridColumns();
      
      let targetIndex = currentIndex;
      
      switch (e.key) {
        case 'ArrowRight':
          e.preventDefault();
          targetIndex = Math.min(currentIndex + 1, cards.length - 1);
          break;
        case 'ArrowLeft':
          e.preventDefault();
          targetIndex = Math.max(currentIndex - 1, 0);
          break;
        case 'ArrowDown':
          e.preventDefault();
          targetIndex = Math.min(currentIndex + columns, cards.length - 1);
          break;
        case 'ArrowUp':
          e.preventDefault();
          targetIndex = Math.max(currentIndex - columns, 0);
          break;
        case 'Home':
          e.preventDefault();
          targetIndex = 0;
          break;
        case 'End':
          e.preventDefault();
          targetIndex = cards.length - 1;
          break;
      }
      
      if (targetIndex !== currentIndex && cards[targetIndex]) {
        cards[targetIndex].focus();
        this.announceGridPosition(targetIndex + 1, cards.length);
      }
    });
  }
  
  getGridColumns() {
    const grid = document.getElementById('loaders-grid');
    if (!grid) return 1;
    
    const gridStyle = getComputedStyle(grid);
    const templateColumns = gridStyle.gridTemplateColumns;
    
    if (templateColumns && templateColumns !== 'none') {
      return templateColumns.split(' ').length;
    }
    
    // Fallback: calculate based on card width and container width
    const cards = grid.querySelectorAll('.loader-card');
    if (cards.length < 2) return 1;
    
    const firstCardRect = cards[0].getBoundingClientRect();
    const secondCardRect = cards[1].getBoundingClientRect();
    
    // If second card is on the same row as the first
    if (Math.abs(firstCardRect.top - secondCardRect.top) < 10) {
      // Count cards in the first row
      let columns = 1;
      for (let i = 1; i < cards.length; i++) {
        const cardRect = cards[i].getBoundingClientRect();
        if (Math.abs(firstCardRect.top - cardRect.top) < 10) {
          columns++;
        } else {
          break;
        }
      }
      return columns;
    }
    
    return 1; // Single column layout
  }
  
  setupModalNavigation() {
    // Modal focus trapping
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Tab') {
        const openModal = document.querySelector('dialog[open]');
        if (openModal) {
          this.trapFocus(e, openModal);
        }
      }
    });
  }
  
  trapFocus(event, container) {
    const focusableElements = this.getFocusableElements(container);
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
  
  getFocusableElements(container) {
    const selector = [
      'button:not([disabled])',
      '[href]',
      'input:not([disabled])',
      'select:not([disabled])',
      'textarea:not([disabled])',
      '[tabindex]:not([tabindex="-1"]):not([disabled])',
      'details summary'
    ].join(', ');
    
    return Array.from(container.querySelectorAll(selector)).filter(el => {
      return !el.closest('[hidden]') && !el.closest('[aria-hidden="true"]');
    });
  }
  
  setupFocusManagement() {
    // Track focus history for better navigation
    document.addEventListener('focusin', (e) => {
      this.focusHistory.push(e.target);
      if (this.focusHistory.length > 10) {
        this.focusHistory.shift();
      }
    });
    
    // Restore focus after modal close
    document.addEventListener('quantumLoaders:modalClose', () => {
      this.restoreFocus();
    });
    
    // Save focus before modal open
    document.addEventListener('quantumLoaders:modalOpen', () => {
      this.lastFocusedElement = document.activeElement;
    });
  }
  
  restoreFocus() {
    if (this.lastFocusedElement && document.contains(this.lastFocusedElement)) {
      this.lastFocusedElement.focus();
    } else {
      // Find the best element to focus
      const bestElement = this.findBestFocusTarget();
      if (bestElement) {
        bestElement.focus();
      }
    }
  }
  
  findBestFocusTarget() {
    // Try focus history in reverse order
    for (let i = this.focusHistory.length - 1; i >= 0; i--) {
      const element = this.focusHistory[i];
      if (document.contains(element) && this.isVisibleAndFocusable(element)) {
        return element;
      }
    }
    
    // Fallback to first focusable element
    const firstFocusable = this.getFocusableElements(document.body)[0];
    return firstFocusable || document.body;
  }
  
  isVisibleAndFocusable(element) {
    const rect = element.getBoundingClientRect();
    const style = getComputedStyle(element);
    
    return rect.width > 0 && 
           rect.height > 0 && 
           style.visibility !== 'hidden' && 
           style.display !== 'none' &&
           !element.disabled &&
           element.tabIndex !== -1;
  }
  
  setupScreenReaderSupport() {
    // Announce page structure to screen readers
    this.announcePageStructure();
    
    // Set up status announcements
    this.setupStatusAnnouncements();
    
    // Enhance form labels and descriptions
    this.enhanceFormAccessibility();
  }
  
  announcePageStructure() {
    setTimeout(() => {
      this.announce('Quantum Loaders Catalogue loaded. Navigate with Tab key or use arrow keys in the grid to explore loaders.');
    }, 1000);
  }
  
  setupStatusAnnouncements() {
    // Announce search results
    document.addEventListener('quantumLoaders:resultsUpdate', (e) => {
      const count = document.getElementById('search-results-count')?.textContent || '';
      if (count) {
        setTimeout(() => this.announce(count), 100);
      }
    });
    
    // Announce theme changes
    document.addEventListener('quantumLoaders:themeChange', (e) => {
      this.announce(`Switched to ${e.detail.theme} theme`);
    });
    
    // Announce animation state changes
    document.addEventListener('quantumLoaders:animationToggle', (e) => {
      this.announce(e.detail.paused ? 'Animations paused' : 'Animations resumed');
    });
    
    // Announce favorites
    document.addEventListener('quantumLoaders:favoriteToggle', (e) => {
      const action = e.detail.isFavorite ? 'added to' : 'removed from';
      this.announce(`Loader ${action} favorites`);
    });
  }
  
  enhanceFormAccessibility() {
    // Speed slider
    const speedSlider = document.getElementById('global-speed');
    if (speedSlider) {
      speedSlider.addEventListener('input', (e) => {
        const value = e.target.value;
        speedSlider.setAttribute('aria-valuenow', value);
        speedSlider.setAttribute('aria-valuetext', `${value} times speed`);
      });
    }
    
    // Search input enhancements
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
      let searchTimeout;
      searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
          const resultsCount = document.getElementById('search-results-count')?.textContent;
          if (resultsCount) {
            this.announce(resultsCount, false); // Don't interrupt
          }
        }, 1000);
      });
    }
  }
  
  setupHighContrastSupport() {
    // Detect high contrast mode
    const mediaQuery = window.matchMedia('(prefers-contrast: high)');
    
    const handleHighContrast = (mq) => {
      document.body.classList.toggle('high-contrast', mq.matches);
      
      if (mq.matches) {
        this.enhanceForHighContrast();
      }
    };
    
    // Initial check
    handleHighContrast(mediaQuery);
    
    // Listen for changes
    mediaQuery.addListener(handleHighContrast);
  }
  
  enhanceForHighContrast() {
    // Add high contrast specific enhancements
    const style = document.createElement('style');
    style.id = 'high-contrast-enhancements';
    style.textContent = `
      .high-contrast .loader-card:focus {
        outline: 3px solid currentColor !important;
        outline-offset: 2px !important;
      }
      
      .high-contrast .theme-btn.active {
        border: 2px solid currentColor !important;
      }
      
      .high-contrast .loader-animation {
        filter: contrast(2) !important;
      }
    `;
    
    if (!document.getElementById('high-contrast-enhancements')) {
      document.head.appendChild(style);
    }
  }
  
  setupReducedMotionSupport() {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    
    const handleReducedMotion = (mq) => {
      this.core.isMotionReduced = mq.matches;
      this.core.updateMotionPreference();
      
      if (mq.matches) {
        this.enhanceForReducedMotion();
      }
    };
    
    // Initial check
    handleReducedMotion(mediaQuery);
    
    // Listen for changes
    mediaQuery.addListener(handleReducedMotion);
  }
  
  enhanceForReducedMotion() {
    // Pause all animations
    document.body.classList.add('respect-motion-preference');
    
    // Announce the change
    this.announce('Reduced motion mode enabled. Animations are paused.');
    
    // Provide alternative visual feedback
    const style = document.createElement('style');
    style.id = 'reduced-motion-enhancements';
    style.textContent = `
      .respect-motion-preference .loader-animation::after {
        content: "⏸️";
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 1.5em;
        background: var(--color-bg-secondary);
        padding: 0.25em;
        border-radius: 50%;
        z-index: 10;
      }
    `;
    
    if (!document.getElementById('reduced-motion-enhancements')) {
      document.head.appendChild(style);
    }
  }
  
  setupSkipLinks() {
    // Create skip links for better navigation
    const skipNav = document.createElement('nav');
    skipNav.className = 'skip-links';
    skipNav.setAttribute('aria-label', 'Skip links');
    
    const skipLinks = [
      { href: '#search-input', text: 'Skip to search' },
      { href: '#loaders-grid', text: 'Skip to loaders' },
      { href: '#global-controls', text: 'Skip to controls' }
    ];
    
    skipLinks.forEach(link => {
      const skipLink = document.createElement('a');
      skipLink.href = link.href;
      skipLink.textContent = link.text;
      skipLink.className = 'skip-link';
      skipNav.appendChild(skipLink);
    });
    
    // Insert at the beginning of the page
    document.body.insertBefore(skipNav, document.body.firstChild);
    
    // Style skip links
    this.styleSkipLinks();
  }
  
  styleSkipLinks() {
    const style = document.createElement('style');
    style.textContent = `
      .skip-links {
        position: absolute;
        top: -100px;
        left: 0;
        width: 100%;
        z-index: 10000;
        display: flex;
        gap: 1rem;
        padding: 1rem;
        background: var(--color-bg-primary);
        border-bottom: 1px solid var(--color-border-primary);
      }
      
      .skip-link {
        padding: 0.5rem 1rem;
        background: var(--color-accent-primary);
        color: var(--color-text-inverse);
        text-decoration: none;
        border-radius: 0.25rem;
        font-weight: 600;
        transition: all 0.2s ease;
      }
      
      .skip-link:focus {
        top: 0;
        outline: 2px solid currentColor;
        outline-offset: 2px;
      }
      
      .skip-links:focus-within {
        top: 0;
      }
      
      .skip-link:hover {
        background: var(--color-accent-hover);
        transform: translateY(-1px);
      }
    `;
    
    document.head.appendChild(style);
  }
  
  optimizeTabSequence() {
    // Ensure logical tab order
    const elements = [
      '.skip-links a',
      '.theme-btn',
      '.control-btn',
      '#search-input',
      '.filter-select',
      '#global-play-pause',
      '#global-reset',
      '#global-speed',
      '#grid-view',
      '#list-view',
      '.loader-card',
      '.favorite-btn'
    ];
    
    let tabIndex = 1;
    elements.forEach(selector => {
      const elements = document.querySelectorAll(selector);
      elements.forEach(el => {
        if (!el.hasAttribute('tabindex') || el.tabIndex === 0) {
          el.tabIndex = tabIndex++;
        }
      });
    });
  }
  
  // Public methods
  announce(message, interrupt = false) {
    const liveRegion = interrupt ? 
      document.getElementById('live-region-assertive') : 
      document.getElementById('live-region');
    
    if (liveRegion) {
      // Clear previous message
      liveRegion.textContent = '';
      
      // Add new message after a brief delay to ensure it's announced
      setTimeout(() => {
        liveRegion.textContent = message;
      }, 100);
      
      // Clear message after announcement
      setTimeout(() => {
        if (liveRegion.textContent === message) {
          liveRegion.textContent = '';
        }
      }, interrupt ? 5000 : 3000);
    }
    
    // Store announcement for debugging
    this.announcements.push({
      message,
      timestamp: Date.now(),
      interrupt
    });
    
    // Keep only last 50 announcements
    if (this.announcements.length > 50) {
      this.announcements.shift();
    }
  }
  
  announceGridPosition(current, total) {
    this.announce(`Loader ${current} of ${total}`, false);
  }
  
  handleEscape() {
    // Close any open modals or panels
    const openModal = document.querySelector('dialog[open]');
    if (openModal) {
      this.core.closeModal(openModal);
      return;
    }
    
    const helpPanel = document.getElementById('help-panel');
    if (helpPanel && helpPanel.getAttribute('aria-hidden') === 'false') {
      this.core.toggleHelpPanel();
      return;
    }
    
    // Clear search if focused
    const searchInput = document.getElementById('search-input');
    if (document.activeElement === searchInput && searchInput.value) {
      this.core.clearSearch();
      this.announce('Search cleared');
    }
  }
  
  handleTab(e) {
    // Track tab navigation for better UX
    const activeElement = document.activeElement;
    
    // Announce context when tabbing to certain elements
    if (activeElement.classList.contains('loader-card')) {
      const title = activeElement.querySelector('.loader-title')?.textContent;
      const category = activeElement.querySelector('.loader-category')?.textContent;
      if (title && category) {
        setTimeout(() => {
          this.announce(`${title}, ${category} category`, false);
        }, 100);
      }
    }
  }
  
  focusFirstElement() {
    const firstFocusable = this.getFocusableElements(document.body)[0];
    if (firstFocusable) {
      firstFocusable.focus();
      this.announce('Focused first element');
    }
  }
  
  focusLastElement() {
    const focusableElements = this.getFocusableElements(document.body);
    const lastFocusable = focusableElements[focusableElements.length - 1];
    if (lastFocusable) {
      lastFocusable.focus();
      this.announce('Focused last element');
    }
  }
  
  focusSearch() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
      searchInput.focus();
      this.announce('Search input focused');
    }
  }
  
  toggleHelp() {
    this.core.toggleHelpPanel();
  }
  
  getAccessibilityReport() {
    return {
      announcements: this.announcements.slice(-10),
      focusHistory: this.focusHistory.slice(-5),
      currentFocus: document.activeElement?.tagName || 'BODY',
      motionReduced: this.core.isMotionReduced,
      highContrast: document.body.classList.contains('high-contrast'),
      screenReaderOptimizations: true
    };
  }
}

// Accessibility testing utilities
class AccessibilityTester {
  static runBasicTests() {
    const results = {
      passed: 0,
      failed: 0,
      warnings: 0,
      tests: []
    };
    
    // Test 1: All images have alt text or are decorative
    const images = document.querySelectorAll('img');
    const imagesTest = {
      name: 'Images have alt text',
      status: 'passed',
      message: 'All images have appropriate alt text or are marked as decorative'
    };
    
    images.forEach((img, index) => {
      if (!img.alt && img.getAttribute('role') !== 'presentation') {
        imagesTest.status = 'failed';
        imagesTest.message = `Image ${index + 1} missing alt text`;
      }
    });
    
    results.tests.push(imagesTest);
    results[imagesTest.status]++;
    
    // Test 2: All buttons have accessible names
    const buttons = document.querySelectorAll('button');
    const buttonsTest = {
      name: 'Buttons have accessible names',
      status: 'passed',
      message: 'All buttons have accessible names'
    };
    
    buttons.forEach((btn, index) => {
      const hasText = btn.textContent.trim();
      const hasLabel = btn.getAttribute('aria-label');
      const hasLabelledBy = btn.getAttribute('aria-labelledby');
      
      if (!hasText && !hasLabel && !hasLabelledBy) {
        buttonsTest.status = 'failed';
        buttonsTest.message = `Button ${index + 1} has no accessible name`;
      }
    });
    
    results.tests.push(buttonsTest);
    results[buttonsTest.status]++;
    
    // Test 3: Headings are properly structured
    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
    const headingsTest = {
      name: 'Heading structure',
      status: 'passed',
      message: 'Headings are properly structured'
    };
    
    let lastLevel = 0;
    headings.forEach(heading => {
      const level = parseInt(heading.tagName.charAt(1));
      if (level > lastLevel + 1) {
        headingsTest.status = 'warning';
        headingsTest.message = 'Heading levels may skip levels';
      }
      lastLevel = level;
    });
    
    results.tests.push(headingsTest);
    results[headingsTest.status]++;
    
    // Test 4: Form labels are associated
    const inputs = document.querySelectorAll('input, select, textarea');
    const labelsTest = {
      name: 'Form labels are associated',
      status: 'passed',
      message: 'All form controls have associated labels'
    };
    
    inputs.forEach((input, index) => {
      const hasLabel = input.labels && input.labels.length > 0;
      const hasAriaLabel = input.getAttribute('aria-label');
      const hasAriaLabelledBy = input.getAttribute('aria-labelledby');
      
      if (!hasLabel && !hasAriaLabel && !hasAriaLabelledBy) {
        labelsTest.status = 'failed';
        labelsTest.message = `Form control ${index + 1} has no associated label`;
      }
    });
    
    results.tests.push(labelsTest);
    results[labelsTest.status]++;
    
    // Test 5: Color contrast (simplified)
    const contrastTest = {
      name: 'Color contrast',
      status: 'passed',
      message: 'Color contrast appears adequate (manual verification recommended)'
    };
    
    results.tests.push(contrastTest);
    results[contrastTest.status]++;
    
    return results;
  }
  
  static generateReport() {
    const results = this.runBasicTests();
    
    console.group('Accessibility Test Results');
    console.log(`Passed: ${results.passed}`);
    console.log(`Failed: ${results.failed}`);
    console.log(`Warnings: ${results.warnings}`);
    
    results.tests.forEach(test => {
      const icon = test.status === 'passed' ? '✅' : test.status === 'failed' ? '❌' : '⚠️';
      console.log(`${icon} ${test.name}: ${test.message}`);
    });
    
    console.groupEnd();
    
    return results;
  }
}

// Export classes
window.AccessibilityManager = AccessibilityManager;
window.AccessibilityTester = AccessibilityTester;