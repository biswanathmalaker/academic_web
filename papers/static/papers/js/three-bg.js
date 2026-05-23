/* ── Three.js background ─────────────────────────────────────────────────── */
function initThreeBackground() {
    const scene    = new THREE.Scene();
    const camera   = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.getElementById('canvas-container').appendChild(renderer.domElement);

    const group = new THREE.Group();
    scene.add(group);

    const geo = new THREE.SphereGeometry(0.02, 8, 8);
    const mat = new THREE.MeshBasicMaterial({ color: 0x38bdf8 });
    for (let i = 0; i < 120; i++) {
        const mesh = new THREE.Mesh(geo, mat);
        mesh.position.set((Math.random()-0.5)*15, (Math.random()-0.5)*15, (Math.random()-0.5)*10);
        mesh.userData.velocity = new THREE.Vector3((Math.random()-0.5)*0.01, (Math.random()-0.5)*0.01, (Math.random()-0.5)*0.01);
        group.add(mesh);
    }
    camera.position.z = 5;

    (function animate() {
        requestAnimationFrame(animate);
        group.children.forEach(p => {
            p.position.add(p.userData.velocity);
            if (Math.abs(p.position.x) > 8) p.userData.velocity.x *= -1;
            if (Math.abs(p.position.y) > 8) p.userData.velocity.y *= -1;
        });
        group.rotation.y += 0.001;
        renderer.render(scene, camera);
    })();

    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
}

// Initialize when document is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initThreeBackground);
} else {
    initThreeBackground();
}
