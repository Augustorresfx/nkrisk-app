import * as THREE from "three";
import { OrbitControls } from 'jsm/controls/OrbitControls.js';
import getStarfield from "./src/getStarfield.js";
import { drawThreeGeo } from "./src/threeGeoJSON.js";

const w = window.innerWidth;
const h = window.innerHeight;
const scene = new THREE.Scene();

// Cambiar el color de fondo de la escena (por ejemplo, azul claro)
scene.background = new THREE.Color(0x041324);  // Color de fondo (azul cielo)

// Si deseas mantener la niebla, puedes ajustarla o eliminarla
// scene.fog = new THREE.FogExp2(0x000000, 0.3); // Niebla oscura (comentada aquí si no la necesitas)

const camera = new THREE.PerspectiveCamera(75, w / h, 1, 100);
camera.position.z = 3.4;
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(w, h);
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

const geometry = new THREE.SphereGeometry(2);
const lineMat = new THREE.LineBasicMaterial({ 
  color: 0x0170BA,
  transparent: true,
  opacity: 0.4, 
});
const edges = new THREE.EdgesGeometry(geometry, 1);
const line = new THREE.LineSegments(edges, lineMat);

// Crear un grupo para contener tanto el globo como los países
const globeGroup = new THREE.Group();
globeGroup.add(line);  // Añadir el globo al grupo

const stars = getStarfield({ numStars: 1000, fog: false });
scene.add(stars);

// Check for more datasets
fetch('/static/geojson/ne_110m_land.json')
  .then(response => response.text())
  .then(text => {
    const data = JSON.parse(text);

    // Aquí definimos un color fijo para todos los países
    const countries = drawThreeGeo({
      json: data,
      radius: 2,
      materialOptions: {
        color: 0x0170BA,  // Color fijo para todos los países (verde en este caso)
        fillColor: 0x0170BA, // Color de relleno (dentro del polígono)
        opacity: 1 // Opacidad del relleno
      },
    });

    globeGroup.add(countries);  // Añadir los países al grupo
    scene.add(globeGroup);      // Añadir el grupo a la escena
  });

function animate() {
  requestAnimationFrame(animate);
  
  // Rotar todo el grupo (globo + países) alrededor del eje Y
  globeGroup.rotation.y += 0.001;  // Rota en el eje Y (giro horizontal del globo)

  renderer.render(scene, camera);
  controls.update();
}

animate();

function handleWindowResize () {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}
window.addEventListener('resize', handleWindowResize, false);
