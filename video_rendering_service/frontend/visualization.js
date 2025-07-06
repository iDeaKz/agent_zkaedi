/**
 * 3D Visualization for Video Rendering Performance
 * 
 * Creates real-time 3D visualization of processing performance using Three.js
 */

class PerformanceVisualization {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.container = null;
        this.animationId = null;
        
        // Performance objects
        this.cpuCube = null;
        this.memoryBar = null;
        this.gpuSphere = null;
        this.processingCubes = [];
        this.dataFlowLines = [];
        
        // Animation parameters
        this.time = 0;
        this.baseRotationSpeed = 0.005;
        this.performanceData = {
            cpu: 45,
            memory: 32,
            gpu: 78,
            activeJobs: 0,
            throughput: 0
        };
        
        this.init();
    }
    
    init() {
        this.container = document.getElementById('threejs-container');
        if (!this.container) {
            console.error('Three.js container not found');
            return;
        }
        
        this.setupScene();
        this.setupLighting();
        this.createPerformanceObjects();
        this.setupEventListeners();
        this.animate();
    }
    
    setupScene() {
        // Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0f172a);
        
        // Camera
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        this.camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
        this.camera.position.set(0, 5, 10);
        this.camera.lookAt(0, 0, 0);
        
        // Renderer
        this.renderer = new THREE.WebGLRenderer({
            canvas: document.getElementById('performance-canvas'),
            antialias: true,
            alpha: true
        });
        this.renderer.setSize(width, height);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    }
    
    setupLighting() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0x6366f1, 0.4);
        this.scene.add(ambientLight);
        
        // Directional light
        const directionalLight = new THREE.DirectionalLight(0x8b5cf6, 0.8);
        directionalLight.position.set(10, 10, 5);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        this.scene.add(directionalLight);
        
        // Point light for dramatic effect
        const pointLight = new THREE.PointLight(0x10b981, 0.6, 50);
        pointLight.position.set(-10, 5, -10);
        this.scene.add(pointLight);
    }
    
    createPerformanceObjects() {
        // CPU Cube (rotating cube representing CPU usage)
        const cpuGeometry = new THREE.BoxGeometry(2, 2, 2);
        const cpuMaterial = new THREE.MeshLambertMaterial({ 
            color: 0x6366f1,
            transparent: true,
            opacity: 0.8
        });
        this.cpuCube = new THREE.Mesh(cpuGeometry, cpuMaterial);
        this.cpuCube.position.set(-4, 2, 0);
        this.cpuCube.castShadow = true;
        this.scene.add(this.cpuCube);
        
        // Memory Bar (vertical bar representing memory usage)
        const memoryGeometry = new THREE.BoxGeometry(0.5, 4, 0.5);
        const memoryMaterial = new THREE.MeshLambertMaterial({ color: 0x10b981 });
        this.memoryBar = new THREE.Mesh(memoryGeometry, memoryMaterial);
        this.memoryBar.position.set(0, 0, 0);
        this.memoryBar.castShadow = true;
        this.scene.add(this.memoryBar);
        
        // GPU Sphere (pulsating sphere representing GPU usage)
        const gpuGeometry = new THREE.SphereGeometry(1.5, 32, 16);
        const gpuMaterial = new THREE.MeshLambertMaterial({ 
            color: 0xf59e0b,
            transparent: true,
            opacity: 0.9
        });
        this.gpuSphere = new THREE.Mesh(gpuGeometry, gpuMaterial);
        this.gpuSphere.position.set(4, 2, 0);
        this.gpuSphere.castShadow = true;
        this.scene.add(this.gpuSphere);
        
        // Data flow lines
        this.createDataFlowLines();
        
        // Processing visualization cubes
        this.createProcessingCubes();
        
        // Add labels
        this.addLabels();
    }
    
    createDataFlowLines() {
        const lineGeometry = new THREE.BufferGeometry();
        const lineMaterial = new THREE.LineBasicMaterial({ 
            color: 0x8b5cf6,
            transparent: true,
            opacity: 0.6
        });
        
        // Create flowing lines between components
        const points = [
            new THREE.Vector3(-4, 2, 0), // CPU
            new THREE.Vector3(0, 0, 0),  // Memory
            new THREE.Vector3(4, 2, 0)   // GPU
        ];
        
        lineGeometry.setFromPoints(points);
        const dataFlowLine = new THREE.Line(lineGeometry, lineMaterial);
        this.scene.add(dataFlowLine);
        this.dataFlowLines.push(dataFlowLine);
    }
    
    createProcessingCubes() {
        // Create small cubes that represent active processing jobs
        for (let i = 0; i < 10; i++) {
            const cubeGeometry = new THREE.BoxGeometry(0.3, 0.3, 0.3);
            const cubeMaterial = new THREE.MeshLambertMaterial({ 
                color: new THREE.Color().setHSL(i / 10, 0.7, 0.6),
                transparent: true,
                opacity: 0.8
            });
            const cube = new THREE.Mesh(cubeGeometry, cubeMaterial);
            
            // Position cubes in a circle
            const angle = (i / 10) * Math.PI * 2;
            cube.position.set(
                Math.cos(angle) * 6,
                Math.sin(angle * 2) * 2,
                Math.sin(angle) * 6
            );
            
            cube.visible = false; // Hide initially
            this.scene.add(cube);
            this.processingCubes.push(cube);
        }
    }
    
    addLabels() {
        // Add text labels (simplified for this implementation)
        // In a full implementation, you might use THREE.TextGeometry or HTML overlays
        
        // CPU Label
        const cpuLabelGeometry = new THREE.PlaneGeometry(1, 0.3);
        const cpuLabelMaterial = new THREE.MeshBasicMaterial({ 
            color: 0xffffff,
            transparent: true,
            opacity: 0.8
        });
        const cpuLabel = new THREE.Mesh(cpuLabelGeometry, cpuLabelMaterial);
        cpuLabel.position.set(-4, 4, 0);
        this.scene.add(cpuLabel);
        
        // Memory Label
        const memoryLabel = cpuLabel.clone();
        memoryLabel.position.set(0, 4, 0);
        this.scene.add(memoryLabel);
        
        // GPU Label
        const gpuLabel = cpuLabel.clone();
        gpuLabel.position.set(4, 4, 0);
        this.scene.add(gpuLabel);
    }
    
    setupEventListeners() {
        window.addEventListener('resize', () => this.onWindowResize());
        
        // Camera controls (simplified mouse interaction)
        let mouseX = 0, mouseY = 0;
        
        this.container.addEventListener('mousemove', (event) => {
            mouseX = (event.clientX - this.container.offsetLeft) / this.container.clientWidth * 2 - 1;
            mouseY = -(event.clientY - this.container.offsetTop) / this.container.clientHeight * 2 + 1;
            
            // Subtle camera movement based on mouse
            this.camera.position.x = mouseX * 2;
            this.camera.position.y = 5 + mouseY * 2;
            this.camera.lookAt(0, 0, 0);
        });
    }
    
    animate() {
        this.animationId = requestAnimationFrame(() => this.animate());
        
        this.time += 0.016; // Approximate 60fps
        
        // Update performance visualizations
        this.updatePerformanceObjects();
        
        // Render the scene
        this.renderer.render(this.scene, this.camera);
    }
    
    updatePerformanceObjects() {
        if (!this.cpuCube || !this.memoryBar || !this.gpuSphere) return;
        
        // CPU Cube - rotation speed based on usage
        const cpuSpeed = this.baseRotationSpeed * (1 + this.performanceData.cpu / 100);
        this.cpuCube.rotation.x += cpuSpeed;
        this.cpuCube.rotation.y += cpuSpeed * 0.7;
        
        // CPU color intensity based on usage
        const cpuIntensity = 0.3 + (this.performanceData.cpu / 100) * 0.7;
        this.cpuCube.material.color.setHSL(0.7, 0.8, cpuIntensity);
        
        // Memory Bar - height based on usage
        const memoryScale = 0.3 + (this.performanceData.memory / 100) * 0.7;
        this.memoryBar.scale.y = memoryScale;
        this.memoryBar.position.y = (memoryScale * 2) - 2; // Adjust position to keep bottom anchored
        
        // GPU Sphere - pulsing based on usage
        const gpuPulse = 1 + Math.sin(this.time * 3) * 0.2 * (this.performanceData.gpu / 100);
        this.gpuSphere.scale.setScalar(gpuPulse);
        
        // GPU glow effect
        const gpuIntensity = 0.5 + (this.performanceData.gpu / 100) * 0.5;
        this.gpuSphere.material.opacity = gpuIntensity;
        
        // Processing cubes - show active jobs
        this.processingCubes.forEach((cube, index) => {
            if (index < this.performanceData.activeJobs) {
                cube.visible = true;
                cube.rotation.x += 0.02;
                cube.rotation.y += 0.03;
                
                // Floating animation
                cube.position.y += Math.sin(this.time * 2 + index) * 0.01;
            } else {
                cube.visible = false;
            }
        });
        
        // Data flow animation
        this.dataFlowLines.forEach(line => {
            if (line.material) {
                line.material.opacity = 0.3 + Math.sin(this.time * 2) * 0.3;
            }
        });
    }
    
    updatePerformanceData(data) {
        this.performanceData = {
            cpu: data.cpu || 45,
            memory: (data.memory_usage || 32),
            gpu: data.gpu || 78,
            activeJobs: data.active_jobs || 0,
            throughput: data.throughput || 0
        };
    }
    
    onWindowResize() {
        if (!this.container || !this.camera || !this.renderer) return;
        
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        
        this.renderer.setSize(width, height);
    }
    
    reset() {
        // Reset all animations and positions
        this.time = 0;
        
        if (this.cpuCube) {
            this.cpuCube.rotation.set(0, 0, 0);
        }
        
        if (this.memoryBar) {
            this.memoryBar.scale.y = 0.3;
            this.memoryBar.position.y = -1.4;
        }
        
        if (this.gpuSphere) {
            this.gpuSphere.scale.setScalar(1);
        }
        
        this.processingCubes.forEach(cube => {
            cube.visible = false;
        });
        
        // Reset performance data
        this.performanceData = {
            cpu: 45,
            memory: 32,
            gpu: 78,
            activeJobs: 0,
            throughput: 0
        };
    }
    
    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        
        if (this.renderer) {
            this.renderer.dispose();
        }
        
        // Clean up Three.js objects
        this.scene = null;
        this.camera = null;
        this.renderer = null;
    }
}

// Initialize visualization when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Wait a bit for the container to be properly sized
    setTimeout(() => {
        window.visualization = new PerformanceVisualization();
        
        // Update visualization with real performance data
        if (window.app) {
            const originalUpdatePerformanceDisplay = window.app.updatePerformanceDisplay;
            window.app.updatePerformanceDisplay = function(stats) {
                originalUpdatePerformanceDisplay.call(this, stats);
                
                // Update 3D visualization
                if (window.visualization) {
                    window.visualization.updatePerformanceData({
                        memory_usage: stats.total_data_processed_gb,
                        active_jobs: stats.active_jobs_count,
                        cpu: 45 + Math.random() * 20, // Simulated CPU usage
                        gpu: 60 + Math.random() * 30,  // Simulated GPU usage
                    });
                }
            };
        }
    }, 1000);
});

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (window.visualization) {
        window.visualization.destroy();
    }
});