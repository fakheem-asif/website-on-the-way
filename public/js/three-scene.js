'use strict';

/* ══════════════════════════════════════════════════════════
   LUMIERE — Three.js Minimalist Scene
   Floating orbs · subtle particle field · soft palette
══════════════════════════════════════════════════════════ */

window.LumiereThree = (function () {
  let renderer, scene, camera, particles, ring, knot, clock;
  let mouseX = 0, mouseY = 0;
  let canvas;
  let running = false;
  let resizeBound = null;
  let mouseMoveBound = null;

  function init() {
    canvas = document.getElementById('hero-canvas');
    if (!canvas || typeof THREE === 'undefined') return;
    if (running) return;
    running = true;

    const w = canvas.clientWidth || window.innerWidth;
    const h = canvas.clientHeight || window.innerHeight;

    renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    renderer.setSize(w, h);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    scene = new THREE.Scene();
    scene.fog = new THREE.Fog(0xF5F2EC, 8, 26);

    camera = new THREE.PerspectiveCamera(55, w / h, 0.1, 100);
    camera.position.set(0, 0, 9);

    const ambient = new THREE.AmbientLight(0xffffff, 0.65);
    scene.add(ambient);
    const dir = new THREE.DirectionalLight(0xffffff, 0.7);
    dir.position.set(5, 5, 5);
    scene.add(dir);
    const accent = new THREE.PointLight(0xC77B7A, 1.2, 18);
    accent.position.set(-4, 2, 3);
    scene.add(accent);

    buildParticles();
    buildRing();
    buildKnot();

    clock = new THREE.Clock();

    mouseMoveBound = onMouseMove;
    resizeBound = onResize;
    document.addEventListener('mousemove', mouseMoveBound, { passive: true });
    window.addEventListener('resize', resizeBound);

    animate();
  }

  function buildParticles() {
    const count = 1400;
    const geo = new THREE.BufferGeometry();
    const pos = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const r = 4 + Math.random() * 8;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      pos[i * 3]     = r * Math.sin(phi) * Math.cos(theta);
      pos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      pos[i * 3 + 2] = r * Math.cos(phi);
    }
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const mat = new THREE.PointsMaterial({
      color: 0x14130F,
      size: 0.022,
      transparent: true,
      opacity: 0.55,
      sizeAttenuation: true,
      depthWrite: false
    });
    particles = new THREE.Points(geo, mat);
    scene.add(particles);

    const count2 = 250;
    const geo2 = new THREE.BufferGeometry();
    const pos2 = new Float32Array(count2 * 3);
    for (let i = 0; i < count2; i++) {
      pos2[i * 3]     = (Math.random() - 0.5) * 14;
      pos2[i * 3 + 1] = (Math.random() - 0.5) * 10;
      pos2[i * 3 + 2] = (Math.random() - 0.5) * 6;
    }
    geo2.setAttribute('position', new THREE.BufferAttribute(pos2, 3));
    const mat2 = new THREE.PointsMaterial({
      color: 0xC77B7A,
      size: 0.04,
      transparent: true,
      opacity: 0.45,
      sizeAttenuation: true,
      depthWrite: false
    });
    const roseParticles = new THREE.Points(geo2, mat2);
    scene.add(roseParticles);
    particles.userData.companion = roseParticles;
  }

  function buildRing() {
    const ringGeo = new THREE.TorusGeometry(2.2, 0.012, 16, 200);
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0x14130F,
      transparent: true,
      opacity: 0.4
    });
    ring = new THREE.Mesh(ringGeo, ringMat);
    ring.rotation.x = Math.PI / 2.5;
    scene.add(ring);

    const ring2Geo = new THREE.TorusGeometry(2.8, 0.008, 16, 200);
    const ring2Mat = new THREE.MeshBasicMaterial({
      color: 0xC77B7A,
      transparent: true,
      opacity: 0.5
    });
    const ring2 = new THREE.Mesh(ring2Geo, ring2Mat);
    ring2.rotation.x = Math.PI / 2.5;
    ring2.rotation.y = Math.PI / 6;
    scene.add(ring2);
    ring.userData.outer = ring2;
  }

  function buildKnot() {
    const geo = new THREE.IcosahedronGeometry(1.1, 1);
    const mat = new THREE.MeshPhysicalMaterial({
      color: 0xFBF9F4,
      metalness: 0.15,
      roughness: 0.35,
      transmission: 0.35,
      thickness: 0.6,
      clearcoat: 0.5,
      clearcoatRoughness: 0.3,
      reflectivity: 0.4
    });
    knot = new THREE.Mesh(geo, mat);
    knot.position.set(0, 0, 0);
    scene.add(knot);

    const wireMat = new THREE.MeshBasicMaterial({
      color: 0x14130F,
      wireframe: true,
      transparent: true,
      opacity: 0.18
    });
    const wire = new THREE.Mesh(geo, wireMat);
    knot.add(wire);
  }

  function onMouseMove(e) {
    mouseX = (e.clientX / window.innerWidth  - 0.5) * 2;
    mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
  }

  function onResize() {
    const w = canvas.clientWidth || window.innerWidth;
    const h = canvas.clientHeight || window.innerHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  }

  function animate() {
    const t = clock.getElapsedTime();

    if (particles) {
      particles.rotation.y = t * 0.035;
      particles.rotation.x = Math.sin(t * 0.02) * 0.1;
      if (particles.userData.companion) {
        particles.userData.companion.rotation.y = -t * 0.04;
        particles.userData.companion.rotation.x = Math.cos(t * 0.025) * 0.12;
      }
    }
    if (ring) {
      ring.rotation.z = t * 0.18;
      if (ring.userData.outer) ring.userData.outer.rotation.z = -t * 0.12;
    }
    if (knot) {
      knot.rotation.x = t * 0.18;
      knot.rotation.y = t * 0.24;
      knot.position.y = Math.sin(t * 0.7) * 0.18;
    }

    camera.position.x += (mouseX * 0.7 - camera.position.x) * 0.04;
    camera.position.y += (-mouseY * 0.4 - camera.position.y) * 0.04;
    camera.lookAt(scene.position);

    renderer.render(scene, camera);
    requestAnimationFrame(animate);
  }

  return { init };
})();
