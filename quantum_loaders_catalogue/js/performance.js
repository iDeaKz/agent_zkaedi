/**
 * Performance Monitoring Module
 * Tracks and optimizes performance metrics
 */

class PerformanceMonitor {
  constructor(core) {
    this.core = core;
    this.metrics = {
      fps: 60,
      frameDrops: 0,
      memoryUsage: 0,
      cpuUsage: 0,
      animationCount: 0,
      renderTime: 0,
      loadTime: 0,
      interactionLatency: 0
    };
    
    this.observers = new Map();
    this.measurements = [];
    this.recommendations = [];
    this.isMonitoring = false;
    this.performanceEntries = [];
    
    this.init();
  }
  
  init() {
    this.setupPerformanceObserver();
    this.startMetricsCollection();
    this.setupMemoryMonitoring();
    this.setupInteractionTracking();
    this.bindEventListeners();
  }
  
  setupPerformanceObserver() {
    if ('PerformanceObserver' in window) {
      // Observe paint timing
      try {
        const paintObserver = new PerformanceObserver((list) => {
          list.getEntries().forEach(entry => {
            if (entry.name === 'first-contentful-paint') {
              this.metrics.loadTime = entry.startTime;
              this.analyzeLoadPerformance();
            }
          });
        });
        paintObserver.observe({ entryTypes: ['paint'] });
        this.observers.set('paint', paintObserver);
      } catch (e) {
        console.warn('Paint timing not supported');
      }
      
      // Observe layout shifts
      try {
        const layoutObserver = new PerformanceObserver((list) => {
          list.getEntries().forEach(entry => {
            if (entry.hadRecentInput) return;
            this.trackLayoutShift(entry.value);
          });
        });
        layoutObserver.observe({ entryTypes: ['layout-shift'] });
        this.observers.set('layout', layoutObserver);
      } catch (e) {
        console.warn('Layout shift tracking not supported');
      }
      
      // Observe largest contentful paint
      try {
        const lcpObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          this.trackLCP(lastEntry.startTime);
        });
        lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
        this.observers.set('lcp', lcpObserver);
      } catch (e) {
        console.warn('LCP tracking not supported');
      }
      
      // Observe long tasks
      try {
        const longTaskObserver = new PerformanceObserver((list) => {
          list.getEntries().forEach(entry => {
            this.trackLongTask(entry.duration);
          });
        });
        longTaskObserver.observe({ entryTypes: ['longtask'] });
        this.observers.set('longtask', longTaskObserver);
      } catch (e) {
        console.warn('Long task tracking not supported');
      }
    }
  }
  
  startMetricsCollection() {
    this.isMonitoring = true;
    this.startFPSMonitoring();
    this.startMemoryMonitoring();
    this.startAnimationCounting();
  }
  
  startFPSMonitoring() {
    let lastTime = performance.now();
    let frameCount = 0;
    let frames = [];
    
    const measureFPS = (currentTime) => {
      if (!this.isMonitoring) return;
      
      frameCount++;
      const deltaTime = currentTime - lastTime;
      
      if (deltaTime >= 1000) {
        const fps = Math.round((frameCount * 1000) / deltaTime);
        this.metrics.fps = fps;
        
        // Track frame drops
        const expectedFrames = Math.round(deltaTime / 16.67);
        const droppedFrames = Math.max(0, expectedFrames - frameCount);
        this.metrics.frameDrops += droppedFrames;
        
        // Store FPS history
        frames.push(fps);
        if (frames.length > 60) frames.shift(); // Keep last 60 seconds
        
        // Update display
        this.updateFPSDisplay(fps);
        this.analyzeFPSPerformance(fps, frames);
        
        frameCount = 0;
        lastTime = currentTime;
      }
      
      requestAnimationFrame(measureFPS);
    };
    
    requestAnimationFrame(measureFPS);
  }
  
  startMemoryMonitoring() {
    if (!performance.memory) return;
    
    setInterval(() => {
      if (!this.isMonitoring) return;
      
      const memory = performance.memory;
      this.metrics.memoryUsage = Math.round(memory.usedJSHeapSize / 1048576); // MB
      
      this.updateMemoryDisplay(this.metrics.memoryUsage);
      this.analyzeMemoryUsage(memory);
    }, 2000);
  }
  
  startAnimationCounting() {
    const countAnimations = () => {
      if (!this.isMonitoring) return;
      
      const activeAnimations = document.querySelectorAll('.loader-animation');
      this.metrics.animationCount = activeAnimations.length;
      
      // Count running animations
      let runningCount = 0;
      activeAnimations.forEach(anim => {
        const computedStyle = getComputedStyle(anim);
        if (computedStyle.animationPlayState === 'running') {
          runningCount++;
        }
      });
      
      this.metrics.runningAnimations = runningCount;
      this.analyzeAnimationLoad(runningCount);
      
      setTimeout(countAnimations, 1000);
    };
    
    countAnimations();
  }
  
  setupMemoryMonitoring() {
    // Monitor memory leaks
    if ('PerformanceObserver' in window) {
      try {
        const memoryObserver = new PerformanceObserver((list) => {
          list.getEntries().forEach(entry => {
            if (entry.entryType === 'measure') {
              this.trackCustomMetric(entry.name, entry.duration);
            }
          });
        });
        memoryObserver.observe({ entryTypes: ['measure'] });
        this.observers.set('memory', memoryObserver);
      } catch (e) {
        console.warn('Memory monitoring not fully supported');
      }
    }
  }
  
  setupInteractionTracking() {
    // Track interaction latency
    const interactionTypes = ['click', 'keydown', 'touchstart'];
    
    interactionTypes.forEach(type => {
      document.addEventListener(type, (e) => {
        const startTime = performance.now();
        
        requestAnimationFrame(() => {
          const endTime = performance.now();
          const latency = endTime - startTime;
          this.trackInteractionLatency(latency);
        });
      }, { passive: true });
    });
  }
  
  trackInteractionLatency(latency) {
    this.metrics.interactionLatency = latency;
    
    if (latency > 100) {
      this.addRecommendation('High interaction latency detected', 'warning');
    }
  }
  
  trackLayoutShift(value) {
    if (value > 0.1) {
      this.addRecommendation('Layout shift detected', 'warning');
    }
  }
  
  trackLCP(time) {
    if (time > 2500) {
      this.addRecommendation('Slow Largest Contentful Paint', 'warning');
    }
  }
  
  trackLongTask(duration) {
    if (duration > 50) {
      this.addRecommendation(`Long task detected: ${duration.toFixed(2)}ms`, 'warning');
    }
  }
  
  trackCustomMetric(name, value) {
    this.performanceEntries.push({
      name,
      value,
      timestamp: Date.now()
    });
    
    // Keep only last 100 entries
    if (this.performanceEntries.length > 100) {
      this.performanceEntries.shift();
    }
  }
  
  updateFPSDisplay(fps) {
    const fpsElement = document.getElementById('fps-value');
    if (fpsElement) {
      fpsElement.textContent = fps;
      
      // Color coding
      if (fps >= 55) {
        fpsElement.style.color = 'var(--color-accent-primary)';
      } else if (fps >= 30) {
        fpsElement.style.color = 'orange';
      } else {
        fpsElement.style.color = 'red';
      }
    }
  }
  
  updateMemoryDisplay(memory) {
    const memoryElement = document.getElementById('memory-value');
    if (memoryElement) {
      memoryElement.textContent = `${memory}MB`;
      
      // Color coding based on usage
      if (memory > 100) {
        memoryElement.style.color = 'red';
      } else if (memory > 50) {
        memoryElement.style.color = 'orange';
      } else {
        memoryElement.style.color = 'var(--color-accent-primary)';
      }
    }
  }
  
  updateGPUDisplay(status) {
    const gpuElement = document.getElementById('gpu-value');
    if (gpuElement) {
      gpuElement.textContent = status;
    }
  }
  
  analyzeFPSPerformance(currentFPS, fpsHistory) {
    const averageFPS = fpsHistory.reduce((a, b) => a + b, 0) / fpsHistory.length;
    const lowFPSCount = fpsHistory.filter(fps => fps < 30).length;
    
    if (averageFPS < 45) {
      this.addRecommendation('Low average FPS detected', 'error');
    } else if (lowFPSCount > fpsHistory.length * 0.1) {
      this.addRecommendation('Frequent FPS drops detected', 'warning');
    }
    
    // Update GPU status based on performance
    if (currentFPS >= 55) {
      this.updateGPUDisplay('Optimal');
    } else if (currentFPS >= 30) {
      this.updateGPUDisplay('Moderate');
    } else {
      this.updateGPUDisplay('Poor');
    }
  }
  
  analyzeMemoryUsage(memory) {
    const usedRatio = memory.usedJSHeapSize / memory.totalJSHeapSize;
    
    if (usedRatio > 0.9) {
      this.addRecommendation('High memory usage detected', 'error');
    } else if (usedRatio > 0.7) {
      this.addRecommendation('Moderate memory usage', 'warning');
    }
    
    // Check for memory leaks
    const growthRate = this.calculateMemoryGrowthRate();
    if (growthRate > 1) { // 1MB per minute
      this.addRecommendation('Potential memory leak detected', 'error');
    }
  }
  
  analyzeAnimationLoad(runningAnimations) {
    if (runningAnimations > 20) {
      this.addRecommendation('Too many concurrent animations', 'warning');
    } else if (runningAnimations > 30) {
      this.addRecommendation('Excessive animation load', 'error');
    }
  }
  
  analyzeLoadPerformance() {
    if (this.metrics.loadTime > 3000) {
      this.addRecommendation('Slow initial load time', 'warning');
    }
  }
  
  calculateMemoryGrowthRate() {
    // Simplified memory growth calculation
    // In a real implementation, you'd track memory over time
    return 0; // Placeholder
  }
  
  getPerformanceScore() {
    let score = 100;
    
    // FPS scoring
    if (this.metrics.fps < 60) score -= (60 - this.metrics.fps) * 2;
    if (this.metrics.fps < 30) score -= 30;
    
    // Memory scoring
    if (this.metrics.memoryUsage > 100) score -= 20;
    if (this.metrics.memoryUsage > 200) score -= 30;
    
    // Animation count scoring
    if (this.metrics.animationCount > 25) score -= 15;
    if (this.metrics.animationCount > 50) score -= 25;
    
    // Frame drops scoring
    if (this.metrics.frameDrops > 10) score -= 10;
    if (this.metrics.frameDrops > 30) score -= 20;
    
    // Interaction latency scoring
    if (this.metrics.interactionLatency > 100) score -= 15;
    if (this.metrics.interactionLatency > 200) score -= 25;
    
    return Math.max(0, Math.min(100, score));
  }
  
  getOptimizationRecommendations() {
    const recommendations = [];
    const score = this.getPerformanceScore();
    
    if (score < 70) {
      recommendations.push({
        type: 'critical',
        message: 'Performance is below acceptable levels',
        actions: [
          'Reduce number of active animations',
          'Enable reduced motion mode',
          'Consider using lighter themes'
        ]
      });
    }
    
    if (this.metrics.fps < 45) {
      recommendations.push({
        type: 'warning',
        message: 'Low frame rate detected',
        actions: [
          'Close unnecessary browser tabs',
          'Reduce animation speed',
          'Use battery saver mode'
        ]
      });
    }
    
    if (this.metrics.memoryUsage > 100) {
      recommendations.push({
        type: 'warning',
        message: 'High memory usage',
        actions: [
          'Refresh the page periodically',
          'Limit number of visible loaders',
          'Use list view instead of grid'
        ]
      });
    }
    
    if (this.metrics.animationCount > 25) {
      recommendations.push({
        type: 'info',
        message: 'Many animations active',
        actions: [
          'Use pagination for loaders',
          'Implement virtual scrolling',
          'Pause off-screen animations'
        ]
      });
    }
    
    return recommendations;
  }
  
  addRecommendation(message, type = 'info') {
    const recommendation = {
      message,
      type,
      timestamp: Date.now()
    };
    
    this.recommendations.push(recommendation);
    
    // Keep only last 20 recommendations
    if (this.recommendations.length > 20) {
      this.recommendations.shift();
    }
    
    // Notify if critical
    if (type === 'error') {
      this.core.announceToScreenReader(`Performance warning: ${message}`);
    }
  }
  
  startProfiling(name) {
    performance.mark(`${name}-start`);
  }
  
  endProfiling(name) {
    performance.mark(`${name}-end`);
    performance.measure(name, `${name}-start`, `${name}-end`);
    
    const entries = performance.getEntriesByName(name);
    const latestEntry = entries[entries.length - 1];
    
    if (latestEntry) {
      this.trackCustomMetric(name, latestEntry.duration);
      
      // Clean up marks
      performance.clearMarks(`${name}-start`);
      performance.clearMarks(`${name}-end`);
      performance.clearMeasures(name);
    }
  }
  
  profileFunction(fn, name) {
    return (...args) => {
      this.startProfiling(name);
      const result = fn.apply(this, args);
      this.endProfiling(name);
      return result;
    };
  }
  
  profileAsync(promise, name) {
    this.startProfiling(name);
    return promise.finally(() => {
      this.endProfiling(name);
    });
  }
  
  getBandwidthInfo() {
    if ('connection' in navigator) {
      const connection = navigator.connection;
      return {
        effectiveType: connection.effectiveType,
        downlink: connection.downlink,
        rtt: connection.rtt,
        saveData: connection.saveData
      };
    }
    return null;
  }
  
  adaptToConnection() {
    const connection = this.getBandwidthInfo();
    
    if (connection) {
      if (connection.saveData || connection.effectiveType === 'slow-2g') {
        this.enableDataSavingMode();
      }
      
      if (connection.effectiveType === '2g' || connection.effectiveType === 'slow-2g') {
        this.enableLowBandwidthMode();
      }
    }
  }
  
  enableDataSavingMode() {
    // Reduce animation quality
    this.core.setAnimationSpeed(0.5);
    
    // Enable reduced motion
    this.core.isMotionReduced = true;
    this.core.updateMotionPreference();
    
    this.addRecommendation('Data saving mode enabled', 'info');
  }
  
  enableLowBandwidthMode() {
    // Further reduce animation complexity
    document.body.classList.add('low-bandwidth');
    
    this.addRecommendation('Low bandwidth mode enabled', 'info');
  }
  
  bindEventListeners() {
    // Performance mode toggle
    document.addEventListener('keydown', (e) => {
      if (e.ctrlKey && e.shiftKey && e.key === 'P') {
        this.togglePerformanceMonitor();
      }
    });
    
    // Battery status
    if ('getBattery' in navigator) {
      navigator.getBattery().then(battery => {
        const updateBatteryMode = () => {
          if (battery.level < 0.2 || battery.charging === false) {
            this.enableBatterySavingMode();
          }
        };
        
        battery.addEventListener('levelchange', updateBatteryMode);
        battery.addEventListener('chargingchange', updateBatteryMode);
        updateBatteryMode();
      });
    }
    
    // Visibility change optimization
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        this.pauseMonitoring();
      } else {
        this.resumeMonitoring();
      }
    });
  }
  
  enableBatterySavingMode() {
    // Reduce frame rate target
    this.core.setAnimationSpeed(0.25);
    
    // Enable reduced motion
    this.core.isMotionReduced = true;
    this.core.updateMotionPreference();
    
    this.addRecommendation('Battery saving mode enabled', 'info');
  }
  
  togglePerformanceMonitor() {
    const monitor = document.getElementById('performance-monitor');
    if (monitor) {
      const isVisible = monitor.style.display !== 'none';
      monitor.style.display = isVisible ? 'none' : 'block';
      
      if (!isVisible) {
        this.generatePerformanceReport();
      }
    }
  }
  
  pauseMonitoring() {
    this.isMonitoring = false;
  }
  
  resumeMonitoring() {
    this.isMonitoring = true;
  }
  
  generatePerformanceReport() {
    const report = {
      timestamp: new Date().toISOString(),
      metrics: { ...this.metrics },
      score: this.getPerformanceScore(),
      recommendations: this.getOptimizationRecommendations(),
      systemInfo: this.getSystemInfo(),
      connectionInfo: this.getBandwidthInfo(),
      performanceEntries: this.performanceEntries.slice(-10)
    };
    
    console.group('Performance Report');
    console.log('Score:', report.score);
    console.log('Metrics:', report.metrics);
    console.log('Recommendations:', report.recommendations);
    console.log('System Info:', report.systemInfo);
    console.groupEnd();
    
    return report;
  }
  
  getSystemInfo() {
    return {
      userAgent: navigator.userAgent,
      hardwareConcurrency: navigator.hardwareConcurrency,
      deviceMemory: navigator.deviceMemory,
      platform: navigator.platform,
      language: navigator.language,
      cookieEnabled: navigator.cookieEnabled,
      onLine: navigator.onLine,
      screen: {
        width: screen.width,
        height: screen.height,
        colorDepth: screen.colorDepth,
        pixelDepth: screen.pixelDepth
      },
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight
      }
    };
  }
  
  exportReport() {
    const report = this.generatePerformanceReport();
    const blob = new Blob([JSON.stringify(report, null, 2)], { 
      type: 'application/json' 
    });
    
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `performance-report-${Date.now()}.json`;
    link.click();
    
    URL.revokeObjectURL(url);
  }
  
  destroy() {
    this.isMonitoring = false;
    
    // Disconnect observers
    this.observers.forEach(observer => {
      observer.disconnect();
    });
    this.observers.clear();
    
    // Clear intervals and timeouts
    // (In a real implementation, you'd track these)
  }
  
  // Public API methods
  getMetrics() {
    return { ...this.metrics };
  }
  
  getRecommendations() {
    return [...this.recommendations];
  }
  
  clearRecommendations() {
    this.recommendations = [];
  }
  
  // Benchmark utilities
  static benchmark(fn, iterations = 1000) {
    const times = [];
    
    for (let i = 0; i < iterations; i++) {
      const start = performance.now();
      fn();
      const end = performance.now();
      times.push(end - start);
    }
    
    times.sort((a, b) => a - b);
    
    return {
      min: times[0],
      max: times[times.length - 1],
      median: times[Math.floor(times.length / 2)],
      mean: times.reduce((a, b) => a + b) / times.length,
      p95: times[Math.floor(times.length * 0.95)],
      p99: times[Math.floor(times.length * 0.99)]
    };
  }
  
  static measureMemoryLeaks(fn, duration = 10000) {
    const initial = performance.memory?.usedJSHeapSize || 0;
    const samples = [];
    
    const sampleMemory = () => {
      const current = performance.memory?.usedJSHeapSize || 0;
      samples.push(current);
    };
    
    const interval = setInterval(() => {
      fn();
      sampleMemory();
    }, 100);
    
    return new Promise(resolve => {
      setTimeout(() => {
        clearInterval(interval);
        const final = performance.memory?.usedJSHeapSize || 0;
        
        resolve({
          initial,
          final,
          growth: final - initial,
          samples,
          hasLeak: (final - initial) > 1048576 // 1MB threshold
        });
      }, duration);
    });
  }
}

// Performance testing utilities
class PerformanceTester {
  static testAnimationPerformance() {
    return new Promise(resolve => {
      const results = {
        averageFPS: 0,
        frameDrops: 0,
        memoryIncrease: 0,
        duration: 10000
      };
      
      const startMemory = performance.memory?.usedJSHeapSize || 0;
      const startTime = performance.now();
      let frameCount = 0;
      let lastFrameTime = startTime;
      
      const measureFrame = () => {
        const currentTime = performance.now();
        const deltaTime = currentTime - lastFrameTime;
        
        if (deltaTime > 16.67 * 1.5) { // Dropped frame threshold
          results.frameDrops++;
        }
        
        frameCount++;
        lastFrameTime = currentTime;
        
        if (currentTime - startTime < results.duration) {
          requestAnimationFrame(measureFrame);
        } else {
          const endMemory = performance.memory?.usedJSHeapSize || 0;
          results.averageFPS = (frameCount * 1000) / (currentTime - startTime);
          results.memoryIncrease = endMemory - startMemory;
          resolve(results);
        }
      };
      
      requestAnimationFrame(measureFrame);
    });
  }
  
  static async runFullSuite() {
    console.group('Performance Test Suite');
    
    // Test 1: Animation performance
    console.log('Testing animation performance...');
    const animationResults = await this.testAnimationPerformance();
    console.log('Animation test results:', animationResults);
    
    // Test 2: Memory usage
    console.log('Testing memory usage...');
    const memoryResults = await PerformanceMonitor.measureMemoryLeaks(() => {
      // Simulate typical usage
      document.dispatchEvent(new CustomEvent('quantumLoaders:resultsUpdate', {
        detail: { searchTerm: 'test', filters: {} }
      }));
    });
    console.log('Memory test results:', memoryResults);
    
    // Test 3: Rendering performance
    console.log('Testing rendering performance...');
    const renderResults = PerformanceMonitor.benchmark(() => {
      // Force reflow
      document.body.offsetHeight;
    });
    console.log('Render test results:', renderResults);
    
    console.groupEnd();
    
    return {
      animation: animationResults,
      memory: memoryResults,
      rendering: renderResults,
      timestamp: Date.now()
    };
  }
}

// Export classes
window.PerformanceMonitor = PerformanceMonitor;
window.PerformanceTester = PerformanceTester;