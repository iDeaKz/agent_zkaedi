/**
 * Animation Controls Module
 * Handles advanced animation manipulation and controls
 */

class AnimationController {
  constructor(core) {
    this.core = core;
    this.animations = new Map();
    this.observers = new Set();
    
    this.init();
  }
  
  init() {
    this.setupIntersectionObserver();
    this.setupMutationObserver();
    this.bindEventListeners();
  }
  
  setupIntersectionObserver() {
    // Optimize performance by pausing animations when out of view
    if ('IntersectionObserver' in window) {
      this.intersectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          const animation = entry.target.querySelector('.loader-animation');
          if (animation) {
            if (entry.isIntersecting) {
              this.resumeAnimation(animation);
            } else {
              this.pauseAnimation(animation);
            }
          }
        });
      }, {
        threshold: 0.1,
        rootMargin: '50px'
      });
      
      // Observe all loader cards
      this.observeLoaderCards();
    }
  }
  
  setupMutationObserver() {
    // Watch for new loader cards being added
    if ('MutationObserver' in window) {
      this.mutationObserver = new MutationObserver((mutations) => {
        mutations.forEach(mutation => {
          mutation.addedNodes.forEach(node => {
            if (node.nodeType === 1 && node.classList.contains('loader-card')) {
              this.intersectionObserver?.observe(node);
              this.initializeAnimation(node.querySelector('.loader-animation'));
            }
          });
        });
      });
      
      const grid = document.getElementById('loaders-grid');
      if (grid) {
        this.mutationObserver.observe(grid, { childList: true });
      }
    }
  }
  
  observeLoaderCards() {
    const cards = document.querySelectorAll('.loader-card');
    cards.forEach(card => {
      this.intersectionObserver?.observe(card);
      this.initializeAnimation(card.querySelector('.loader-animation'));
    });
  }
  
  initializeAnimation(element) {
    if (!element) return;
    
    const id = element.dataset.loaderId || this.generateId();
    element.dataset.animationId = id;
    
    const animationData = {
      element,
      id,
      isPaused: false,
      speed: 1,
      originalDuration: this.getAnimationDuration(element),
      customProperties: new Map()
    };
    
    this.animations.set(id, animationData);
    this.applyPerformanceOptimizations(element);
  }
  
  applyPerformanceOptimizations(element) {
    // Add GPU acceleration hints
    element.style.willChange = 'transform';
    element.style.transform = 'translateZ(0)';
    element.style.backfaceVisibility = 'hidden';
    
    // Add containment for better rendering performance
    element.style.contain = 'layout style paint';
    
    // Optimize for specific animations
    const classList = element.classList;
    if (classList.contains('holographic-cube')) {
      element.style.perspective = '200px';
    }
    
    if (classList.contains('particle-accelerator')) {
      element.style.isolation = 'isolate';
    }
  }
  
  pauseAnimation(element) {
    if (!element) return;
    
    const id = element.dataset.animationId;
    const animationData = this.animations.get(id);
    
    if (animationData && !animationData.isPaused) {
      element.style.animationPlayState = 'paused';
      animationData.isPaused = true;
      
      // Pause child animations
      const children = element.querySelectorAll('*');
      children.forEach(child => {
        child.style.animationPlayState = 'paused';
      });
    }
  }
  
  resumeAnimation(element) {
    if (!element) return;
    
    const id = element.dataset.animationId;
    const animationData = this.animations.get(id);
    
    if (animationData && animationData.isPaused && !this.core.animationsPaused) {
      element.style.animationPlayState = 'running';
      animationData.isPaused = false;
      
      // Resume child animations
      const children = element.querySelectorAll('*');
      children.forEach(child => {
        child.style.animationPlayState = 'running';
      });
    }
  }
  
  setAnimationSpeed(element, speed) {
    if (!element) return;
    
    const id = element.dataset.animationId;
    const animationData = this.animations.get(id);
    
    if (animationData) {
      const newDuration = animationData.originalDuration / speed;
      element.style.animationDuration = `${newDuration}s`;
      animationData.speed = speed;
      
      // Update child animations
      const children = element.querySelectorAll('*');
      children.forEach(child => {
        const childDuration = this.getAnimationDuration(child) / speed;
        if (childDuration > 0) {
          child.style.animationDuration = `${childDuration}s`;
        }
      });
    }
  }
  
  setGlobalSpeed(speed) {
    this.animations.forEach((animationData, id) => {
      this.setAnimationSpeed(animationData.element, speed);
    });
  }
  
  pauseAllAnimations() {
    this.animations.forEach((animationData, id) => {
      this.pauseAnimation(animationData.element);
    });
  }
  
  resumeAllAnimations() {
    this.animations.forEach((animationData, id) => {
      this.resumeAnimation(animationData.element);
    });
  }
  
  resetAnimation(element) {
    if (!element) return;
    
    // Force reflow by cloning and replacing the element
    const parent = element.parentElement;
    const clone = element.cloneNode(true);
    
    parent.removeChild(element);
    parent.offsetHeight; // Force reflow
    parent.appendChild(clone);
    
    // Re-initialize the cloned animation
    this.initializeAnimation(clone);
  }
  
  resetAllAnimations() {
    const animations = [...this.animations.values()];
    animations.forEach(animationData => {
      this.resetAnimation(animationData.element);
    });
  }
  
  setCustomProperty(element, property, value) {
    if (!element) return;
    
    const id = element.dataset.animationId;
    const animationData = this.animations.get(id);
    
    if (animationData) {
      element.style.setProperty(property, value);
      animationData.customProperties.set(property, value);
    }
  }
  
  setColor(element, color) {
    this.setCustomProperty(element, '--color-accent-primary', color);
    this.setCustomProperty(element, '--custom-color', color);
    
    // Calculate secondary color (complementary or lighter/darker variant)
    const secondaryColor = this.calculateSecondaryColor(color);
    this.setCustomProperty(element, '--color-accent-secondary', secondaryColor);
  }
  
  setSize(element, size) {
    if (!element) return;
    
    element.style.width = `${size}px`;
    element.style.height = `${size}px`;
    element.style.fontSize = `${size / 60}em`; // Scale relative elements
  }
  
  getAnimationDuration(element) {
    if (!element) return 2; // Default duration
    
    const computed = getComputedStyle(element);
    const duration = computed.animationDuration;
    
    if (duration && duration !== '0s') {
      return parseFloat(duration);
    }
    
    return 2; // Default fallback
  }
  
  calculateSecondaryColor(color) {
    // Simple secondary color calculation
    // In a real implementation, you might use a color library
    const hex = color.replace('#', '');
    const r = parseInt(hex.substr(0, 2), 16);
    const g = parseInt(hex.substr(2, 2), 16);
    const b = parseInt(hex.substr(4, 2), 16);
    
    // Create a complementary color by inverting hue
    const hsl = this.rgbToHsl(r, g, b);
    hsl[0] = (hsl[0] + 180) % 360; // Shift hue by 180 degrees
    
    const rgb = this.hslToRgb(hsl[0], hsl[1], hsl[2]);
    return `rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`;
  }
  
  rgbToHsl(r, g, b) {
    r /= 255;
    g /= 255;
    b /= 255;
    
    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    let h, s, l = (max + min) / 2;
    
    if (max === min) {
      h = s = 0;
    } else {
      const d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
      
      switch (max) {
        case r: h = (g - b) / d + (g < b ? 6 : 0); break;
        case g: h = (b - r) / d + 2; break;
        case b: h = (r - g) / d + 4; break;
      }
      h /= 6;
    }
    
    return [h * 360, s, l];
  }
  
  hslToRgb(h, s, l) {
    h /= 360;
    
    const hue2rgb = (p, q, t) => {
      if (t < 0) t += 1;
      if (t > 1) t -= 1;
      if (t < 1/6) return p + (q - p) * 6 * t;
      if (t < 1/2) return q;
      if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
      return p;
    };
    
    let r, g, b;
    
    if (s === 0) {
      r = g = b = l;
    } else {
      const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
      const p = 2 * l - q;
      r = hue2rgb(p, q, h + 1/3);
      g = hue2rgb(p, q, h);
      b = hue2rgb(p, q, h - 1/3);
    }
    
    return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
  }
  
  bindEventListeners() {
    // Global animation controls
    document.addEventListener('quantumLoaders:speedChange', (e) => {
      this.setGlobalSpeed(e.detail.speed);
    });
    
    document.addEventListener('quantumLoaders:animationToggle', (e) => {
      if (e.detail.paused) {
        this.pauseAllAnimations();
      } else {
        this.resumeAllAnimations();
      }
    });
    
    document.addEventListener('quantumLoaders:animationReset', () => {
      this.resetAllAnimations();
    });
    
    document.addEventListener('quantumLoaders:motionPreferenceChange', (e) => {
      if (e.detail.reduced) {
        this.pauseAllAnimations();
      } else {
        this.resumeAllAnimations();
      }
    });
    
    // Handle visibility change (tab switching)
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        this.pauseAllAnimations();
      } else if (!this.core.animationsPaused && !this.core.isMotionReduced) {
        this.resumeAllAnimations();
      }
    });
  }
  
  generateId() {
    return 'anim_' + Math.random().toString(36).substr(2, 9);
  }
  
  destroy() {
    // Clean up observers
    if (this.intersectionObserver) {
      this.intersectionObserver.disconnect();
    }
    
    if (this.mutationObserver) {
      this.mutationObserver.disconnect();
    }
    
    // Clear animations
    this.animations.clear();
    this.observers.clear();
  }
}

// Animation presets for different scenarios
class AnimationPresets {
  static getPresets() {
    return {
      performance: {
        name: 'High Performance',
        description: 'Optimized for smooth performance',
        settings: {
          speed: 0.75,
          reducedMotion: false,
          gpuAcceleration: true,
          intersectionObserver: true
        }
      },
      accessibility: {
        name: 'Accessibility Focused',
        description: 'Reduced motion and enhanced accessibility',
        settings: {
          speed: 0.5,
          reducedMotion: true,
          gpuAcceleration: false,
          intersectionObserver: true
        }
      },
      showcase: {
        name: 'Showcase Mode',
        description: 'Maximum visual impact',
        settings: {
          speed: 1.25,
          reducedMotion: false,
          gpuAcceleration: true,
          intersectionObserver: false
        }
      },
      battery: {
        name: 'Battery Saver',
        description: 'Minimal resource usage',
        settings: {
          speed: 0.5,
          reducedMotion: true,
          gpuAcceleration: false,
          intersectionObserver: true
        }
      }
    };
  }
  
  static applyPreset(controller, presetName) {
    const presets = this.getPresets();
    const preset = presets[presetName];
    
    if (!preset) return false;
    
    const settings = preset.settings;
    
    // Apply speed
    controller.setGlobalSpeed(settings.speed);
    
    // Apply motion settings
    if (settings.reducedMotion) {
      controller.core.isMotionReduced = true;
      controller.core.updateMotionPreference();
    }
    
    return true;
  }
}

// Performance metrics for animations
class AnimationMetrics {
  constructor() {
    this.metrics = {
      frameDrops: 0,
      averageFPS: 60,
      animationCount: 0,
      gpuMemoryUsage: 0
    };
    
    this.init();
  }
  
  init() {
    this.startFrameMonitoring();
    this.observeAnimations();
  }
  
  startFrameMonitoring() {
    let lastTime = performance.now();
    let frameCount = 0;
    let droppedFrames = 0;
    
    const monitor = () => {
      const currentTime = performance.now();
      const deltaTime = currentTime - lastTime;
      
      frameCount++;
      
      // Check for dropped frames (assuming 60fps target)
      const expectedFrames = Math.round(deltaTime / 16.67);
      if (expectedFrames > 1) {
        droppedFrames += expectedFrames - 1;
      }
      
      // Update metrics every second
      if (frameCount % 60 === 0) {
        this.metrics.frameDrops = droppedFrames;
        this.metrics.averageFPS = Math.round(1000 / (deltaTime / frameCount));
        frameCount = 0;
        droppedFrames = 0;
      }
      
      lastTime = currentTime;
      requestAnimationFrame(monitor);
    };
    
    requestAnimationFrame(monitor);
  }
  
  observeAnimations() {
    const updateCount = () => {
      const animations = document.querySelectorAll('.loader-animation');
      this.metrics.animationCount = animations.length;
    };
    
    // Update initially and on DOM changes
    updateCount();
    
    if ('MutationObserver' in window) {
      const observer = new MutationObserver(updateCount);
      observer.observe(document.body, { childList: true, subtree: true });
    }
  }
  
  getMetrics() {
    return { ...this.metrics };
  }
  
  getPerformanceScore() {
    const fps = this.metrics.averageFPS;
    const frameDrops = this.metrics.frameDrops;
    const animCount = this.metrics.animationCount;
    
    let score = 100;
    
    // Penalize low FPS
    if (fps < 60) score -= (60 - fps) * 2;
    if (fps < 30) score -= 20;
    if (fps < 15) score -= 30;
    
    // Penalize frame drops
    score -= Math.min(frameDrops * 2, 30);
    
    // Penalize too many animations
    if (animCount > 20) score -= (animCount - 20) * 2;
    
    return Math.max(0, Math.min(100, score));
  }
  
  getRecommendations() {
    const score = this.getPerformanceScore();
    const recommendations = [];
    
    if (score < 70) {
      recommendations.push('Consider reducing animation speed');
      recommendations.push('Enable reduced motion for better performance');
    }
    
    if (this.metrics.frameDrops > 10) {
      recommendations.push('High frame drop rate detected - try closing other tabs');
    }
    
    if (this.metrics.animationCount > 25) {
      recommendations.push('Large number of animations - consider pagination');
    }
    
    if (this.metrics.averageFPS < 30) {
      recommendations.push('Low FPS detected - switch to battery saver mode');
    }
    
    return recommendations;
  }
}

// Export classes
window.AnimationController = AnimationController;
window.AnimationPresets = AnimationPresets;
window.AnimationMetrics = AnimationMetrics;