class WarehouseVisualization {
	constructor() {
		this.scene = null;
		this.camera = null;
		this.renderer = null;
		this.bins = {};
		this.selectedBin = null;
		this.warehouseData = null;
		this.raycaster = new THREE.Raycaster();
		this.mouse = new THREE.Vector2();

		this.init();
		this.setupEventListeners();
	}

	init() {
		// Scene setup
		this.scene = new THREE.Scene();
		this.scene.background = new THREE.Color(0x667eea);
		this.scene.fog = new THREE.Fog(0x667eea, 200, 500);

		// Camera setup
		const canvasElement = document.getElementById('canvas');
		const width = canvasElement.clientWidth;
		const height = canvasElement.clientHeight;
		this.camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
		this.camera.position.set(30, 30, 30);
		this.camera.lookAt(0, 0, 0);

		// Renderer setup
		this.renderer = new THREE.WebGLRenderer({ antialias: true });
		this.renderer.setSize(width, height);
		this.renderer.shadowMap.enabled = true;
		canvasElement.appendChild(this.renderer.domElement);

		// Lighting
		const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
		this.scene.add(ambientLight);

		const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
		directionalLight.position.set(50, 50, 50);
		directionalLight.castShadow = true;
		directionalLight.shadow.camera.left = -100;
		directionalLight.shadow.camera.right = 100;
		directionalLight.shadow.camera.top = 100;
		directionalLight.shadow.camera.bottom = -100;
		directionalLight.shadow.mapSize.width = 2048;
		directionalLight.shadow.mapSize.height = 2048;
		this.scene.add(directionalLight);

		// Add ground
		const groundGeometry = new THREE.PlaneGeometry(200, 200);
		const groundMaterial = new THREE.MeshStandardMaterial({ color: 0x888888 });
		const ground = new THREE.Mesh(groundGeometry, groundMaterial);
		ground.rotation.x = -Math.PI / 2;
		ground.receiveShadow = true;
		this.scene.add(ground);

		// Camera controls
		this.setupControls();

		// Handle window resize
		window.addEventListener('resize', () => this.onWindowResize());

		// Animation loop
		this.animate();

		// Load warehouses
		this.loadWarehouses();
	}

	setupControls() {
		const canvas = this.renderer.domElement;
		let isDragging = false;
		let previousMousePosition = { x: 0, y: 0 };

		canvas.addEventListener('mousedown', (e) => {
			isDragging = true;
			previousMousePosition = { x: e.clientX, y: e.clientY };
		});

		canvas.addEventListener('mousemove', (e) => {
			if (isDragging) {
				const deltaX = e.clientX - previousMousePosition.x;
				const deltaY = e.clientY - previousMousePosition.y;

				this.camera.position.applyAxisAngle(
					new THREE.Vector3(0, 1, 0),
					deltaX * 0.01
				);
				this.camera.position.applyAxisAngle(
					this.camera.position.clone().cross(new THREE.Vector3(0, 1, 0)).normalize(),
					deltaY * 0.01
				);
				this.camera.lookAt(0, 0, 0);

				previousMousePosition = { x: e.clientX, y: e.clientY };
			}

			// Update mouse position for raycasting
			const rect = canvas.getBoundingClientRect();
			this.mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
			this.mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
		});

		canvas.addEventListener('mouseup', () => {
			isDragging = false;
		});

		canvas.addEventListener('mouseleave', () => {
			isDragging = false;
		});

		canvas.addEventListener('click', (e) => {
			this.onCanvasClick();
		});

		canvas.addEventListener('wheel', (e) => {
			e.preventDefault();
			const direction = this.camera.position.clone().normalize();
			const distance = this.camera.position.length();
			const newDistance = distance + (e.deltaY > 0 ? 5 : -5);

			if (newDistance > 10 && newDistance < 150) {
				this.camera.position.copy(direction.multiplyScalar(newDistance));
				this.camera.lookAt(0, 0, 0);
			}
		});
	}

	async loadWarehouses() {
		try {
			const response = await frappe.call({
				method: 'erpnext_wms.doctype.warehouse_layout.warehouse_layout.get_warehouses',
				callback: (r) => {
					if (r.message) {
						this.populateWarehouseSelect(r.message);
					}
				}
			});
		} catch (error) {
			console.error('Error loading warehouses:', error);
			this.showError('Failed to load warehouses');
		}
	}

	populateWarehouseSelect(warehouses) {
		const select = document.getElementById('warehouseSelect');
		warehouses.forEach(w => {
			const option = document.createElement('option');
			option.value = w.warehouse;
			option.textContent = w.warehouse;
			select.appendChild(option);
		});

		if (warehouses.length > 0) {
			select.value = warehouses[0].warehouse;
			this.loadWarehouse(warehouses[0].warehouse);
		}

		select.addEventListener('change', (e) => {
			if (e.target.value) {
				this.loadWarehouse(e.target.value);
			}
		});
	}

	async loadWarehouse(warehouseName) {
		try {
			const response = await frappe.call({
				method: 'erpnext_wms.doctype.warehouse_layout.warehouse_layout.get_warehouse_occupancy',
				args: { warehouse_name: warehouseName },
				callback: (r) => {
					if (r.message) {
						this.warehouseData = r.message;
						this.renderWarehouse();
						this.updateStatistics();
						document.getElementById('statsSection').style.display = 'block';
						document.getElementById('legendSection').style.display = 'block';
					}
				}
			});
		} catch (error) {
			console.error('Error loading warehouse:', error);
			this.showError(`Failed to load warehouse: ${warehouseName}`);
		}
	}

	renderWarehouse() {
		// Clear existing bins
		Object.values(this.bins).forEach(bin => {
			this.scene.remove(bin.mesh);
		});
		this.bins = {};

		if (!this.warehouseData) return;

		const config = this.warehouseData.layout_config;
		const occupancy = this.warehouseData.occupancy;

		const binWidth = config.bin_width;
		const binHeight = config.bin_height;
		const binDepth = config.bin_depth;

		// Center the warehouse in the scene
		const offsetX = -(config.total_bins_x * binWidth) / 2;
		const offsetZ = -(config.total_bins_z * binDepth) / 2;

		// Create bins
		for (let x = 0; x < config.total_bins_x; x++) {
			for (let y = 0; y < config.total_bins_y; y++) {
				for (let z = 0; z < config.total_bins_z; z++) {
					const key = `${x}_${y}_${z}`;
					const occupancyData = occupancy[key];

					const isOccupied = !!occupancyData && occupancyData.status === 'Occupied';
					const fileCreation = occupancyData?.file_creation;

					const geometry = new THREE.BoxGeometry(binWidth * 0.9, binHeight * 0.9, binDepth * 0.9);

					let material;
					if (isOccupied) {
						// Busy - gradient purple/magenta
						material = new THREE.MeshPhongMaterial({
							color: 0xd946ef,
							emissive: 0xa855f7,
							shininess: 100
						});
					} else {
						// Free - gray
						material = new THREE.MeshPhongMaterial({
							color: 0x999999,
							shininess: 30
						});
					}

					const mesh = new THREE.Mesh(geometry, material);
					mesh.position.set(
						offsetX + x * binWidth + binWidth / 2,
						y * binHeight + binHeight / 2,
						offsetZ + z * binDepth + binDepth / 2
					);
					mesh.castShadow = true;
					mesh.receiveShadow = true;

					// Add outline for better visibility
					const edges = new THREE.EdgesGeometry(geometry);
					const wireframe = new THREE.LineSegments(
						edges,
						new THREE.LineBasicMaterial({ color: 0xffffff, linewidth: 0.5 })
					);
					mesh.add(wireframe);

					this.scene.add(mesh);

					this.bins[key] = {
						mesh: mesh,
						x: x,
						y: y,
						z: z,
						occupied: isOccupied,
						fileCreation: fileCreation,
						data: occupancyData
					};
				}
			}
		}

		// Adjust camera to view all bins
		this.fitCameraToScene();
	}

	fitCameraToScene() {
		if (!this.warehouseData) return;

		const config = this.warehouseData.layout_config;
		const maxDim = Math.max(
			config.total_bins_x * config.bin_width,
			config.total_bins_y * config.bin_height,
			config.total_bins_z * config.bin_depth
		);

		const fov = this.camera.fov * (Math.PI / 180);
		let cameraZ = maxDim / (2 * Math.tan(fov / 2));

		cameraZ *= 1.5; // Give some padding

		this.camera.position.set(cameraZ * 0.6, cameraZ * 0.8, cameraZ);
		this.camera.lookAt(0, 0, 0);
	}

	onCanvasClick() {
		this.raycaster.setFromCamera(this.mouse, this.camera);

		const intersects = this.raycaster.intersectObjects(
			Object.values(this.bins).map(b => b.mesh)
		);

		if (intersects.length > 0) {
			const clickedMesh = intersects[0].object;

			// Find which bin was clicked
			for (const [key, binData] of Object.entries(this.bins)) {
				if (binData.mesh === clickedMesh) {
					this.selectBin(key, binData);
					break;
				}
			}
		}
	}

	selectBin(key, binData) {
		// Deselect previous bin
		if (this.selectedBin) {
			const originalColor = this.selectedBin.occupied ? 0xd946ef : 0x999999;
			this.selectedBin.mesh.material.emissive.setHex(this.selectedBin.occupied ? 0xa855f7 : 0x000000);
		}

		// Select new bin
		this.selectedBin = binData;
		binData.mesh.material.emissive.setHex(0xffff00);

		this.displayBinDetails(key, binData);
	}

	displayBinDetails(key, binData) {
		const detailsDiv = document.getElementById('binDetails');
		let html = `
			<div>
				<div class="details-label">Position</div>
				<div>X: ${binData.x}, Y: ${binData.y}, Z: ${binData.z}</div>
			</div>
			<div>
				<div class="details-label">Status</div>
				<div>${binData.occupied ? '✓ Occupied' : '○ Empty'}</div>
			</div>
		`;

		if (binData.fileCreation && this.warehouseData) {
			const fileDetails = this.warehouseData.file_details[binData.fileCreation];
			if (fileDetails) {
				html += `
					<div>
						<div class="details-label">File Number</div>
						<div style="font-weight: 600; color: #d946ef;">${fileDetails.name}</div>
					</div>
					<div>
						<div class="details-label">Type</div>
						<div>${fileDetails.file_type}</div>
					</div>
					<div>
						<div class="details-label">Customer</div>
						<div>${fileDetails.customer}</div>
					</div>
				`;
			}
		}

		detailsDiv.innerHTML = html;
		document.getElementById('detailsSection').style.display = 'block';
	}

	updateStatistics() {
		if (!this.warehouseData) return;

		const occupancy = this.warehouseData.occupancy;
		const totalBins = document.querySelectorAll('.stat-value')[0];
		const occupiedCount = Object.values(occupancy).filter(o => o.status === 'Occupied').length;

		const totalBinsNum = Object.keys(this.bins).length;
		totalBins.textContent = totalBinsNum;
		document.getElementById('occupiedBins').textContent = occupiedCount;
	}

	animate() {
		requestAnimationFrame(() => this.animate());
		this.renderer.render(this.scene, this.camera);
	}

	onWindowResize() {
		const canvasElement = document.getElementById('canvas');
		const width = canvasElement.clientWidth;
		const height = canvasElement.clientHeight;

		this.camera.aspect = width / height;
		this.camera.updateProjectionMatrix();
		this.renderer.setSize(width, height);
	}

	showError(message) {
		const sidebar = document.getElementById('sidebar');
		const errorDiv = document.createElement('div');
		errorDiv.className = 'error';
		errorDiv.textContent = message;
		sidebar.insertBefore(errorDiv, sidebar.firstChild);

		setTimeout(() => errorDiv.remove(), 5000);
	}
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', () => {
	new WarehouseVisualization();
});
