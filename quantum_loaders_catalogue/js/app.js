/**
 * Main Application File
 * Initializes and coordinates all modules
 */

class QuantumLoadersApp {
  constructor() {
    this.core = null;
    this.loadersData = null;
    this.animationController = null;
    this.exportManager = null;
    this.accessibilityManager = null;
    this.performanceMonitor = null;
    
    this.isInitialized = false;
    this.modules = new Map();
    
    this.init();
  }
  
  async init() {
    try {
      // Wait for DOM to be ready
      if (document.readyState === 'loading') {
        await new Promise(resolve => {
          document.addEventListener('DOMContentLoaded', resolve, { once: true });
        });
      }
      
      // Initialize core first
      this.initializeCore();
      
      // Initialize other modules
      await this.initializeModules();
      
      // Setup global error handling
      this.setupErrorHandling();
      
      // Initialize data and render
      await this.initializeData();
      
      // Setup development tools
      this.setupDevelopmentTools();
      
      // Mark as initialized
      this.isInitialized = true;
      
      console.log('🚀 Quantum Loaders Catalogue initialized successfully');
      
      // Dispatch ready event
      this.dispatchEvent('ready');
      
    } catch (error) {
      console.error('Failed to initialize Quantum Loaders Catalogue:', error);
      this.handleInitializationError(error);
    }
  }
  
  initializeCore() {
    this.core = new QuantumLoadersCore();
    this.modules.set('core', this.core);
    
    console.log('✅ Core module initialized');
  }
  
  async initializeModules() {
    // Initialize modules in dependency order
    const moduleConfigs = [
      {
        name: 'accessibility',
        constructor: AccessibilityManager,
        dependencies: ['core']
      },
      {
        name: 'performance',
        constructor: PerformanceMonitor,
        dependencies: ['core']
      },
      {
        name: 'animation',
        constructor: AnimationController,
        dependencies: ['core']
      },
      {
        name: 'export',
        constructor: ExportManager,
        dependencies: ['core']
      },
      {
        name: 'loaders',
        constructor: QuantumLoadersData,
        dependencies: ['core']
      }
    ];
    
    for (const config of moduleConfigs) {
      try {
        await this.initializeModule(config);
      } catch (error) {
        console.error(`Failed to initialize ${config.name} module:`, error);
        // Continue initialization even if a module fails
      }
    }
  }
  
  async initializeModule(config) {
    // Check dependencies
    for (const dep of config.dependencies) {
      if (!this.modules.has(dep)) {
        throw new Error(`Missing dependency: ${dep}`);
      }
    }
    
    // Initialize module
    const module = new config.constructor(this.core);
    this.modules.set(config.name, module);
    
    // Store reference for easy access
    switch (config.name) {
      case 'accessibility':
        this.accessibilityManager = module;
        break;
      case 'performance':
        this.performanceMonitor = module;
        break;
      case 'animation':
        this.animationController = module;
        break;
      case 'export':
        this.exportManager = module;
        break;
      case 'loaders':
        this.loadersData = module;
        break;
    }
    
    console.log(`✅ ${config.name} module initialized`);
    
    // Allow async initialization
    if (module.asyncInit && typeof module.asyncInit === 'function') {
      await module.asyncInit();
    }
  }
  
  async initializeData() {
    // Data should already be initialized in loadersData module
    // This is a hook for any additional data loading
    console.log('✅ Data initialization complete');
  }
  
  setupErrorHandling() {
    // Global error handler
    window.addEventListener('error', (event) => {
      this.handleError(event.error, 'Global Error');
    });
    
    // Promise rejection handler
    window.addEventListener('unhandledrejection', (event) => {
      this.handleError(event.reason, 'Unhandled Promise Rejection');
    });
    
    // Custom error handler for the app
    document.addEventListener('quantumLoaders:error', (event) => {
      this.handleError(event.detail.error, event.detail.context);
    });
  }
  
  handleError(error, context = 'Unknown') {
    console.error(`[${context}]`, error);
    
    // Try to maintain app functionality
    try {
      // Notify user of non-critical errors
      if (this.accessibilityManager) {
        this.accessibilityManager.announce('An error occurred. The application is attempting to recover.', true);
      }
      
      // Log error for debugging
      this.logError(error, context);
      
      // Attempt recovery
      this.attemptRecovery(error, context);
      
    } catch (recoveryError) {
      console.error('Error during error handling:', recoveryError);
    }
  }
  
  handleInitializationError(error) {
    // Show user-friendly error message
    const errorHTML = `
      <div class="initialization-error">
        <h2>🚫 Initialization Error</h2>
        <p>The Quantum Loaders Catalogue failed to initialize properly.</p>
        <details>
          <summary>Technical Details</summary>
          <pre>${error.message}</pre>
        </details>
        <button onclick="location.reload()">Reload Page</button>
      </div>
    `;
    
    const errorContainer = document.createElement('div');
    errorContainer.innerHTML = errorHTML;
    errorContainer.style.cssText = `
      position: fixed;
      inset: 0;
      background: #0a0e1a;
      color: #e2e8f0;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      z-index: 10000;
      font-family: system-ui, sans-serif;
    `;
    
    document.body.appendChild(errorContainer);
  }
  
  logError(error, context) {
    const errorLog = {
      message: error.message,
      stack: error.stack,
      context,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      modules: Array.from(this.modules.keys())
    };
    
    // In a real application, you might send this to an error reporting service
    console.log('Error Log:', errorLog);
  }
  
  attemptRecovery(error, context) {
    // Basic recovery strategies
    switch (context) {
      case 'Animation Error':
        if (this.animationController) {
          this.animationController.pauseAllAnimations();
        }
        break;
        
      case 'Performance Error':
        if (this.core) {
          this.core.isMotionReduced = true;
          this.core.updateMotionPreference();
        }
        break;
        
      case 'Export Error':
        // Clear any open export modals
        document.querySelectorAll('dialog[open]').forEach(modal => {
          if (this.core) {
            this.core.closeModal(modal);
          }
        });
        break;
        
      default:
        // Generic recovery
        console.log('Attempting generic recovery...');
    }
  }
  
  setupDevelopmentTools() {
    // Only in development mode
    if (this.isDevelopment()) {
      this.setupDevConsole();
      this.setupHotkeys();
      this.setupPerformanceTools();
    }
  }
  
  isDevelopment() {
    return window.location.hostname === 'localhost' || 
           window.location.hostname === '127.0.0.1' ||
           window.location.search.includes('debug=true');
  }
  
  setupDevConsole() {
    // Expose app instance globally for debugging
    window.quantumApp = this;
    
    // Add helpful console methods
    window.quantumDebug = {
      getMetrics: () => this.performanceMonitor?.getMetrics(),
      getRecommendations: () => this.performanceMonitor?.getRecommendations(),
      testAccessibility: () => AccessibilityTester?.runBasicTests(),
      testPerformance: () => PerformanceTester?.runFullSuite(),
      getState: () => ({
        theme: this.core?.currentTheme,
        motionReduced: this.core?.isMotionReduced,
        animationsPaused: this.core?.animationsPaused,
        favorites: Array.from(this.core?.favorites || []),
        modules: Array.from(this.modules.keys())
      }),
      exportReport: () => this.performanceMonitor?.exportReport(),
      resetApp: () => location.reload()
    };
    
    console.log('🛠️ Development tools available: window.quantumDebug');
  }
  
  setupHotkeys() {
    document.addEventListener('keydown', (e) => {
      // Ctrl+Shift combinations for dev tools
      if (e.ctrlKey && e.shiftKey) {
        switch (e.key) {
          case 'D':
            e.preventDefault();
            console.log('Debug info:', window.quantumDebug.getState());
            break;
            
          case 'P':
            e.preventDefault();
            this.performanceMonitor?.togglePerformanceMonitor();
            break;
            
          case 'A':
            e.preventDefault();
            AccessibilityTester?.generateReport();
            break;
            
          case 'T':
            e.preventDefault();
            PerformanceTester?.runFullSuite();
            break;
            
          case 'R':
            e.preventDefault();
            this.performanceMonitor?.exportReport();
            break;
        }
      }
    });
  }
  
  setupPerformanceTools() {
    // Auto-run performance tests periodically in dev mode
    if (this.performanceMonitor) {
      setInterval(() => {
        const score = this.performanceMonitor.getPerformanceScore();
        if (score < 60) {
          console.warn('Performance score dropped to:', score);
        }
      }, 30000); // Check every 30 seconds
    }
  }
  
  // Public API methods
  getModule(name) {
    return this.modules.get(name);
  }
  
  getAllModules() {
    return new Map(this.modules);
  }
  
  isReady() {
    return this.isInitialized;
  }
  
  async waitForReady() {
    if (this.isInitialized) {
      return Promise.resolve();
    }
    
    return new Promise(resolve => {
      document.addEventListener('quantumLoaders:ready', resolve, { once: true });
    });
  }
  
  dispatchEvent(eventName, detail = {}) {
    const event = new CustomEvent(`quantumLoaders:${eventName}`, {
      detail,
      bubbles: true
    });
    document.dispatchEvent(event);
  }
  
  // Lifecycle methods
  destroy() {
    console.log('🗑️ Destroying Quantum Loaders App...');
    
    // Destroy modules in reverse order
    const moduleNames = Array.from(this.modules.keys()).reverse();
    
    moduleNames.forEach(name => {
      const module = this.modules.get(name);
      if (module && typeof module.destroy === 'function') {
        try {
          module.destroy();
          console.log(`✅ ${name} module destroyed`);
        } catch (error) {
          console.error(`❌ Failed to destroy ${name} module:`, error);
        }
      }
    });
    
    this.modules.clear();
    this.isInitialized = false;
    
    // Clean up global references
    if (window.quantumApp === this) {
      delete window.quantumApp;
    }
    
    if (window.quantumDebug) {
      delete window.quantumDebug;
    }
    
    console.log('✅ App destroyed successfully');
  }
  
  restart() {
    this.destroy();
    setTimeout(() => {
      new QuantumLoadersApp();
    }, 100);
  }
  
  // Utility methods
  updateConfiguration(config) {
    // Update app-wide configuration
    if (config.theme && this.core) {
      this.core.setTheme(config.theme);
    }
    
    if (config.motionReduced !== undefined && this.core) {
      this.core.isMotionReduced = config.motionReduced;
      this.core.updateMotionPreference();
    }
    
    if (config.animationSpeed && this.animationController) {
      this.animationController.setGlobalSpeed(config.animationSpeed);
    }
    
    this.dispatchEvent('configurationUpdate', config);
  }
  
  exportConfiguration() {
    if (!this.core) return null;
    
    const config = {
      theme: this.core.currentTheme,
      motionReduced: this.core.isMotionReduced,
      animationSpeed: this.core.currentSpeed,
      favorites: Array.from(this.core.favorites),
      view: this.core.currentView,
      timestamp: Date.now()
    };
    
    return config;
  }
  
  importConfiguration(config) {
    if (!config || typeof config !== 'object') {
      throw new Error('Invalid configuration object');
    }
    
    // Validate configuration
    const validThemes = ['dark', 'light', 'neon'];
    const validViews = ['grid', 'list'];
    
    if (config.theme && !validThemes.includes(config.theme)) {
      console.warn('Invalid theme in configuration:', config.theme);
      delete config.theme;
    }
    
    if (config.view && !validViews.includes(config.view)) {
      console.warn('Invalid view in configuration:', config.view);
      delete config.view;
    }
    
    // Apply configuration
    this.updateConfiguration(config);
    
    // Restore favorites
    if (config.favorites && Array.isArray(config.favorites)) {
      this.core.favorites = new Set(config.favorites);
      localStorage.setItem('quantum-loaders-favorites', JSON.stringify(config.favorites));
    }
    
    console.log('✅ Configuration imported successfully');
  }
}

// Auto-initialize when script loads
document.addEventListener('DOMContentLoaded', () => {
  // Small delay to ensure all scripts are loaded
  setTimeout(() => {
    window.quantumLoadersApp = new QuantumLoadersApp();
  }, 100);
});

// Prevent multiple initialization
if (!window.quantumLoadersAppInitialized) {
  window.quantumLoadersAppInitialized = true;
  
  // Export app class for manual initialization if needed
  window.QuantumLoadersApp = QuantumLoadersApp;
  
  console.log('🌌 Quantum Loaders Catalogue script loaded');
}

// Service Worker registration for PWA capabilities (optional)
if ('serviceWorker' in navigator && window.location.protocol === 'https:') {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then(registration => {
        console.log('SW registered: ', registration);
      })
      .catch(registrationError => {
        console.log('SW registration failed: ', registrationError);
      });
  });
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = QuantumLoadersApp;
}

if (typeof define === 'function' && define.amd) {
  define(() => QuantumLoadersApp);
}