/* 暖阳庄园 · Sunnyfield Manor —— 原创英式红砖乡村别墅 (Three.js r128) */
'use strict';
/* ========== 基础 ========== */
const container = document.getElementById('app');
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, innerWidth/innerHeight, 0.1, 500);
camera.position.set(30, 18, 38);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputEncoding = THREE.sRGBEncoding;
container.appendChild(renderer.domElement);
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true; controls.dampingFactor = 0.06;
controls.maxPolarAngle = Math.PI * 0.495; controls.minDistance = 6; controls.maxDistance = 120;
controls.target.set(0, 4, 2);

/* ========== 灯光 ========== */
const hemi = new THREE.HemisphereLight(0xd8ecff, 0x6b6a4a, 0.7); scene.add(hemi);
const sun = new THREE.DirectionalLight(0xffe8c4, 1.3);
sun.position.set(35, 48, 24); sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left=-55; sun.shadow.camera.right=55; sun.shadow.camera.top=55; sun.shadow.camera.bottom=-55;
sun.shadow.camera.far = 150; sun.shadow.bias = -0.0004;
scene.add(sun);
const moon = new THREE.DirectionalLight(0x8fa8ff, 0.0); moon.position.set(-28, 38, -18); scene.add(moon);

/* ========== 材质 ========== */
function M(color, opts){ return new THREE.MeshStandardMaterial(Object.assign({ color: color, roughness: 0.9, metalness: 0.0 }, opts||{})); }
const MAT = {
  brick:  M(0xA8522C), brickDark: M(0x93421F), brickTrim: M(0xB8643C),
  plaster: M(0xF2E8D4), timber: M(0x4A3422, {roughness:0.7}),
  roof:   M(0x3C4147, {roughness:0.75}), roofTrim: M(0x33383D),
  trim:   M(0xF6F2E8), door: M(0x5A4028, {roughness:0.6}),
  stone:  M(0xB7AC96), plinth: M(0x9E927C),
  glassDay: M(0x9FBFD8, {roughness:0.15, metalness:0.35}),
  lawn:   M(0x6B9950), gravel: M(0xC9BFA8), path: M(0xBFAe94),
  hedge:  M(0x3F6B34), trunk: M(0x6B4A32),
  leaf1:  M(0x4C7A3A), leaf2: M(0x5B8C45), leaf3: M(0x437036),
  flower1: M(0xD86A6A), flower2: M(0xE8C84A), flower3: M(0xE8E4DA), flower4: M(0xD87AB0),
  wood:   M(0x8A6844), fabric: M(0x8C4A4A), fabric2: M(0x4A6A8C), white: M(0xEFEFEA),
  gold:   M(0xC8A85A, {roughness:0.35, metalness:0.8}),
  lampGlow: M(0xFFE3A1, {emissive:0xFFC964, emissiveIntensity:0})
};
const glassMats = [];
function glassMat(){ const g = MAT.glassDay.clone(); glassMats.push(g); return g; }
const lampLights = [];

/* ========== 几何助手 ========== */
const manor = new THREE.Group(); scene.add(manor);
function box(parent, w,h,d, mat, x,y,z, ry){
  const m = new THREE.Mesh(new THREE.BoxGeometry(w,h,d), mat);
  m.position.set(x,y,z); if(ry) m.rotation.y = ry;
  m.castShadow = true; m.receiveShadow = true; parent.add(m); return m;
}
function cyl(parent, rt,rb,h, mat, x,y,z, seg){
  const m = new THREE.Mesh(new THREE.CylinderGeometry(rt,rb,h,seg||16), mat);
  m.position.set(x,y,z); m.castShadow = true; m.receiveShadow = true; parent.add(m); return m;
}
function sph(parent, r, mat, x,y,z){
  const m = new THREE.Mesh(new THREE.SphereGeometry(r, 16, 12), mat);
  m.position.set(x,y,z); m.castShadow = true; parent.add(m); return m;
}
function wallsBox(parent, w, h, d, y, mat, t){
  t = t || 0.35;
  box(parent, w, h, t, mat, 0, y+h/2, d/2-t/2);
  box(parent, w, h, t, mat, 0, y+h/2, -d/2+t/2);
  box(parent, t, h, d-2*t, mat, w/2-t/2, y+h/2, 0);
  box(parent, t, h, d-2*t, mat, -w/2+t/2, y+h/2, 0);
}
/* 山墙屋顶: 两坡 + 屋脊 */
function gableRoof(parent, w, d, y0, h, overhang, mat){
  const g = new THREE.Group();
  const span = d/2 + overhang;
  const L = Math.sqrt(span*span + h*h);
  const a = Math.atan2(h, span);
  for(const s of [1,-1]){
    const p = new THREE.Mesh(new THREE.BoxGeometry(w+overhang*2, 0.22, L), mat);
    p.position.set(0, y0 + h/2, s*span/2);
    p.rotation.x = s*a;
    p.castShadow = true; p.receiveShadow = true; g.add(p);
  }
  box(g, w+overhang*2, 0.26, 0.3, mat, 0, y0+h+0.1, 0);
  parent.add(g); return g;
}
/* 山墙三角(用 ExtrudeGeometry) */
function gableWall(parent, w, y0, h, z, mat, depth, xoff){
  const s = new THREE.Shape();
  s.moveTo(-w/2, y0); s.lineTo(w/2, y0); s.lineTo(0, y0+h); s.closePath();
  const geo = new THREE.ExtrudeGeometry(s, { depth: depth||0.3, bevelEnabled: false });
  geo.translate(0, 0, -(depth||0.3)/2);
  const m = new THREE.Mesh(geo, mat);
  m.position.set(xoff||0, 0, z); m.castShadow = true; m.receiveShadow = true; parent.add(m); return m;
}
function windowAt(parent, x, y, z, ry, w, h, arched){
  const g = new THREE.Group();
  box(g, w+0.14, h+0.14, 0.12, MAT.trim, 0, 0, 0);
  box(g, w, h, 0.14, glassMat(), 0, 0, 0);
  // 分格: 竖挺 + 横挺
  box(g, 0.06, h, 0.16, MAT.trim, -w/4, 0, 0);
  box(g, 0.06, h, 0.16, MAT.trim, w/4, 0, 0);
  box(g, w, 0.06, 0.16, MAT.trim, 0, 0, 0);
  if(arched){ const arc = new THREE.Mesh(new THREE.CylinderGeometry(w/2,w/2,0.14,12,1,false,0,Math.PI), glassMat()); arc.rotation.z=Math.PI; arc.position.y=h/2; g.add(arc); }
  box(g, w+0.5, 0.13, 0.32, MAT.trim, 0, -h/2-0.1, 0);   // 窗台
  g.position.set(x,y,z); g.rotation.y = ry||0; parent.add(g); return g;
}

/* ===== 分组 ===== */
const gRoof = new THREE.Group(), gF1 = new THREE.Group(), gF2 = new THREE.Group(), gF3 = new THREE.Group(), gF4 = new THREE.Group(), gSite = new THREE.Group();
manor.add(gRoof, gF1, gF2, gF3, gF4, gSite);

const Y1=0.5, H1=3.4, H2=3.1, H3=3.0, H4=2.8;
const Y2=Y1+H1, Y3=Y2+H2, Y4=Y3+H3, YT=Y4+H4, EAVE=YT+0.05;   // 四层

/* ===== 一层 ===== */
box(gF1, 24, 0.5, 12, MAT.plinth, 0, 0.25, 0);
wallsBox(gF1, 22, H1, 9, Y1, MAT.brick);
/* 东翼(前凸) */
(function(){ const ww=6, dd=4.5, cx=8, cz=4.5+2.25;
  box(gF1, ww, 0.5, dd, MAT.plinth, cx, 0.25, cz);
  box(gF1, ww, H1, 0.35, MAT.brick, cx, Y1+H1/2, cz+dd/2-0.175);
  box(gF1, ww, H1, 0.35, MAT.brick, cx, Y1+H1/2, cz-dd/2+0.175);
  box(gF1, 0.35, H1, dd-0.7, MAT.brick, cx+ww/2-0.175, Y1+H1/2, cz);
  box(gF1, 0.35, H1, dd-0.7, MAT.brick, cx-ww/2+0.175, Y1+H1/2, cz);
  box(gF1, 0.4, H1, 0.4, MAT.brickDark, cx-ww/2+0.2, Y1+H1/2, cz-dd/2+0.2);
  box(gF1, 0.4, H1, 0.4, MAT.brickDark, cx+ww/2-0.2, Y1+H1/2, cz-dd/2+0.2);
})();
/* 西侧凸窗 */
box(gF1, 3.2, H1*0.8, 1.4, MAT.brick, -6.5, Y1+H1*0.4, 4.5+0.7);
/* 层间线 */
(function(){ const t=0.4, w=22.6, d=9.6, y=Y2-0.08;
  box(gF1, w, 0.16, t, MAT.brickTrim, 0, y, d/2-t/2);
  box(gF1, w, 0.16, t, MAT.brickTrim, 0, y, -d/2+t/2);
  box(gF1, t, 0.16, d-2*t, MAT.brickTrim, w/2-t/2, y, 0);
  box(gF1, t, 0.16, d-2*t, MAT.brickTrim, -w/2+t/2, y, 0);
})();
/* 窗户(一层) */
for(const x of [-9,-5.5,-2]){ windowAt(gF1, x, Y1+1.9, 4.5+0.06, 0, 1.4, 2.0, false); }
windowAt(gF1, 8, Y1+1.9, 4.5+4.5+0.06, 0, 1.4, 2.0, false);   // 翼前窗
windowAt(gF1, -6.5, Y1+1.9, 4.5+1.4+0.06, 0, 2.2, 1.8, false); // 凸窗
for(const z of [-2, 2]){ windowAt(gF1, 11+0.06, Y1+1.9, z, Math.PI/2, 1.2, 1.8, false); windowAt(gF1, -11-0.06, Y1+1.9, z, -Math.PI/2, 1.2, 1.8, false); }
/* 门廊 */
(function(){
  box(gF1, 2.4, 2.6, 0.25, MAT.door, 0, Y1+1.3, 4.5+0.1);
  cyl(gF1, 0.14, 0.16, 3.0, MAT.white, -1.5, Y1+1.5, 4.5+1.1, 10);
  cyl(gF1, 0.14, 0.16, 3.0, MAT.white, 1.5, Y1+1.5, 4.5+1.1, 10);
  box(gF1, 4.6, 0.18, 1.9, MAT.white, 0, Y1+3.05, 4.5+0.95);
  [[-1.9],[1.9]].forEach(function(p){ const gl=sph(gF1, 0.12, MAT.lampGlow.clone(), p[0], Y1+2.6, 4.5+1.15); glassMats.push(gl.material); const l=new THREE.PointLight(0xFFC964,0,9); l.position.set(p[0],Y1+2.6,4.5+1.3); gF1.add(l); lampLights.push(l); });
})();

/* ===== 二层 ===== */
wallsBox(gF2, 22, H2, 9, Y2, MAT.brick);
(function(){ const ww=6, dd=4.5, cx=8, cz=4.5+2.25;
  box(gF2, ww, H2, 0.3, MAT.brick, cx, Y2+H2/2, cz+dd/2-0.15);
  box(gF2, ww, H2, 0.3, MAT.brick, cx, Y2+H2/2, cz-dd/2+0.15);
  box(gF2, 0.3, H2, dd, MAT.brick, cx+ww/2-0.15, Y2+H2/2, cz);
  box(gF2, 0.3, H2, dd, MAT.brick, cx-ww/2+0.15, Y2+H2/2, cz);
})();   // 翼二层(空心)
for(const x of [-9,-5.5,-2]){ windowAt(gF2, x, Y2+1.6, 4.5+0.06, 0, 1.3, 1.7, false); }
windowAt(gF2, -6.5, Y2+1.6, 4.5+1.4+0.06, 0, 2.0, 1.5, false);
for(const z of [-2, 2]){ windowAt(gF2, 11+0.06, Y2+1.6, z, Math.PI/2, 1.15, 1.6, false); windowAt(gF2, -11-0.06, Y2+1.6, z, -Math.PI/2, 1.15, 1.6, false); }

/* ===== 三层 ===== */
wallsBox(gF3, 22, H3, 9, Y3, MAT.brick);
for(const x of [-9,-5.5,-2]){ windowAt(gF3, x, Y3+1.5, 4.5+0.06, 0, 1.3, 1.6, false); }
for(const x of [-8.2,-4.5]){ windowAt(gF3, x, Y3+1.5, -4.5-0.06, Math.PI, 1.2, 1.5, false); }
for(const z of [-2, 2]){ windowAt(gF3, 11+0.06, Y3+1.5, z, Math.PI/2, 1.15, 1.5, false); windowAt(gF3, -11-0.06, Y3+1.5, z, -Math.PI/2, 1.15, 1.5, false); }
/* 四层 */
wallsBox(gF4, 22, H4, 9, Y4, MAT.brick);
for(const x of [-9,-5.5,-2, 0.5]){ windowAt(gF4, x, Y4+1.35, 4.5+0.06, 0, 1.2, 1.4, false); }
for(const z of [-2, 2]){ windowAt(gF4, 11+0.06, Y4+1.35, z, Math.PI/2, 1.1, 1.4, false); windowAt(gF4, -11-0.06, Y4+1.35, z, -Math.PI/2, 1.1, 1.4, false); }
/* 层间线(三/四层) */
(function(){ const t=0.4, w=22.6, d=9.6, y=Y3-0.08;
  box(gF2, w, 0.16, t, MAT.brickTrim, 0, y, d/2-t/2);
  box(gF2, w, 0.16, t, MAT.brickTrim, 0, y, -d/2+t/2);
  box(gF2, t, 0.16, d-2*t, MAT.brickTrim, w/2-t/2, y, 0);
  box(gF2, t, 0.16, d-2*t, MAT.brickTrim, -w/2+t/2, y, 0);
})();
(function(){ const t=0.4, w=22.6, d=9.6, y=Y4-0.08;
  box(gF3, w, 0.16, t, MAT.brickTrim, 0, y, d/2-t/2);
  box(gF3, w, 0.16, t, MAT.brickTrim, 0, y, -d/2+t/2);
  box(gF3, t, 0.16, d-2*t, MAT.brickTrim, w/2-t/2, y, 0);
  box(gF3, t, 0.16, d-2*t, MAT.brickTrim, -w/2+t/2, y, 0);
})();
/* ===== 屋顶 ===== */
/* ===== 屋顶 ===== */
gableRoof(gRoof, 22, 9, EAVE, 3.2, 0.6, MAT.roof);          // 主体
gableWall(gRoof, 22, EAVE, 3.2, 4.5, MAT.plaster, 0.3);     // 前山墙
gableWall(gRoof, 22, EAVE, 3.2, -4.5, MAT.plaster, 0.3);    // 后山墙
/* 翼屋顶(横向山墙, 前凸) */
(function(){ const ww=6, dd=4.5, cx=8, cz=4.5+2.25, y0=Y3+0.1, hh=2.0;
  const r = gableRoof(gRoof, dd+1.2, ww, y0, hh, 0.5, MAT.roof);
  r.rotation.y = Math.PI/2;
  r.position.set(cx, 0, cz);
  const s=new THREE.Shape(); s.moveTo(-(ww/2+0.5), y0); s.lineTo(ww/2+0.5, y0); s.lineTo(0, y0+hh); s.closePath();
  const geo=new THREE.ExtrudeGeometry(s,{depth:0.3,bevelEnabled:false}); geo.translate(0,0,-0.15);
  const m=new THREE.Mesh(geo, MAT.plaster); m.position.set(cx,0, cz+dd/2+0.5); m.castShadow=true; gRoof.add(m);
})();
/* 门廊顶(见一层 canopy 盒) */
/* 凸窗小顶 */
(function(){ const r=gableRoof(gRoof, 3.4, 1.8, Y1+H1*0.8+0.9, 0.9, 0.15, MAT.roof); r.position.set(-6.5, 0, 4.5+0.7); })();
/* 半木结构装饰(前山墙) */
(function(){
  const pts=[[-3,0.6,0.5],[3,0.6,-0.5],[-3,0.6,-0.5],[3,0.6,0.5]];
  pts.forEach(function(p){ const l=new THREE.Mesh(new THREE.BoxGeometry(0.18, 3.0, 0.18), MAT.timber); l.position.set(p[0], EAVE+1.6, 4.5+0.3); l.rotation.z = p[2]; l.castShadow=true; gRoof.add(l); });
  box(gRoof, 22, 0.2, 0.2, MAT.timber, 0, EAVE+0.1, 4.5+0.3);
})();
/* 烟囱 */
function chimney(x, z, hh){
  box(gRoof, 1.0, hh, 1.0, MAT.brickDark, x, EAVE-1.5+hh/2, z);
  box(gRoof, 1.25, 0.25, 1.25, MAT.roofTrim, x, EAVE-1.5+hh+0.12, z);
  [[-0.3],[0.3]].forEach(function(px){ cyl(gRoof, 0.16, 0.16, 0.5, MAT.roofTrim, x+px[0], EAVE-1.5+hh+0.45, z, 8); });
}
chimney(-7, -2, 4.2); chimney(7, 0, 4.6);

/* ===== 花园(英式乡村) ===== */
const LAWN_X=90, LAWN_Z=70;
(function(){ const l=new THREE.Mesh(new THREE.PlaneGeometry(LAWN_X, LAWN_Z), MAT.lawn); l.rotation.x=-Math.PI/2; l.receiveShadow=true; gSite.add(l); })();
/* 蜿蜒砾石小径 */
(function(){
  const pts=[[0, 30],[0, 20],[2, 12],[0, 8]];
  for(let i=0;i<pts.length-1;i++){
    const x1=pts[i][0],z1=pts[i][1],x2=pts[i+1][0],z2=pts[i+1][1];
    const len=Math.sqrt((x2-x1)**2+(z2-z1)**2), ang=Math.atan2(x2-x1, z2-z1);
    const p=new THREE.Mesh(new THREE.BoxGeometry(1.8,0.08,len), MAT.gravel);
    p.position.set((x1+x2)/2,0.04,(z1+z2)/2); p.rotation.y=-ang; p.receiveShadow=true; gSite.add(p);
  }
})();
/* 石墙(矮) + 木门 */
(function(){
  const sx=60, sz=50;
  function wallSeg(cx,cz,ww,dd){ box(gSite, ww, 1.1, 0.3, MAT.stone, cx, 0.55, cz); box(gSite, ww, 1.1, 0.3, MAT.stone, cx, 0.55, cz+dd); }
  box(gSite, sx, 1.1, 0.3, MAT.stone, 0, 0.55, -sz/2);
  box(gSite, 0.3, 1.1, sz, MAT.stone, -sx/2, 0.55, 0); box(gSite, 0.3, 1.1, sz, MAT.stone, sx/2, 0.55, 0);
  // 前墙留门洞
  const gap=2.6;
  box(gSite, sx/2-gap, 1.1, 0.3, MAT.stone, -(sx/4+gap/2), 0.55, sz/2); box(gSite, sx/2-gap, 1.1, 0.3, MAT.stone, (sx/4+gap/2), 0.55, sz/2);
  // 门柱 + 木门
  box(gSite, 0.5, 1.8, 0.5, MAT.stone, -gap/2-0.3, 0.9, sz/2); box(gSite, 0.5, 1.8, 0.5, MAT.stone, gap/2+0.3, 0.9, sz/2);
  box(gSite, gap/2-0.2, 1.5, 0.12, MAT.wood, -gap/4, 0.8, sz/2+0.08); box(gSite, gap/2-0.2, 1.5, 0.12, MAT.wood, gap/4, 0.8, sz/2+0.08);
})();
/* 花境(玫瑰/月季) */
(function(){
  const cols=[MAT.flower1, MAT.flower2, MAT.flower3, MAT.flower4];
  box(gSite, 16, 0.15, 1.6, M(0x4A3A28), 6, 0.08, 7.5);
  box(gSite, 10, 0.15, 1.4, M(0x4A3A28), -7, 0.08, 6.2);
  let seed=13; function rnd(){ seed=(seed*16807)%2147483647; return seed/2147483647; }
  for(let i=0;i<60;i++){ sph(gSite, 0.09+rnd()*0.08, cols[Math.floor(rnd()*4)], -2+rnd()*16, 0.26+rnd()*0.1, 6.8+rnd()*1.4); }
  for(let i=0;i<40;i++){ sph(gSite, 0.09+rnd()*0.08, cols[Math.floor(rnd()*4)], -12+rnd()*10, 0.26+rnd()*0.1, 5.6+rnd()*1.2); }
})();
/* 树 */
function tree(x, z, s){
  const g = new THREE.Group();
  cyl(g, 0.26*s, 0.38*s, 2.6*s, MAT.trunk, 0, 1.3*s, 0, 10);
  sph(g, 1.8*s, MAT.leaf1, 0, 3.4*s, 0);
  sph(g, 1.3*s, MAT.leaf2, 1.0*s, 4.1*s, 0.5*s);
  sph(g, 1.15*s, MAT.leaf3, -0.9*s, 4.2*s, -0.5*s);
  g.position.set(x, 0, z); gSite.add(g);
}
[[-26,18],[-24,-6],[-30,6],[26,16],[24,-8],[16,22],[-14,-22],[14,-24],[-8,26],[8,26],[-30,-20],[30,-20]].forEach(function(p){ tree(p[0], p[1], 0.85+Math.random()*0.5); });
/* 灌木球 + 路灯 */
[[-12,10],[12,10],[-15,14],[15,14],[-4,20],[4,20]].forEach(function(p){ sph(gSite, 0.5+((p[0]*p[1])%3)*0.12, MAT.hedge, p[0], 0.55, p[1]); });
function lamp(x, z){
  cyl(gSite, 0.08, 0.12, 2.8, MAT.timber, x, 1.4, z, 8);
  const gl=sph(gSite, 0.26, MAT.lampGlow.clone(), x, 2.9, z); glassMats.push(gl.material);
  const l=new THREE.PointLight(0xFFC964, 0, 15); l.position.set(x, 2.9, z); gSite.add(l); lampLights.push(l);
}
lamp(-2.4, 14); lamp(2.4, 14);

/* ===== 内部(精装版) ===== */
const inWall = M(0xF2E9D8), inFloor = M(0xC9A876);
const rugRed = M(0x9E4A44), rugBlue = M(0x4A6A8C), rugGreen = M(0x5A7A4A);
const woodD = M(0x7A5A3A), appl = M(0xE8E4DC), darkM = M(0x2E3236), tile = M(0xBFD0D8), sofaC = M(0x6A7B8C);
function slab(parent, y, th){ box(parent, 21, th, 8.5, inFloor, 0, y, 0); }
function partSeg(parent, x, z0, z1, h){ box(parent, 0.16, h, z1-z0, inWall, x, h/2, (z0+z1)/2); }
function partWall(parent, z, x0, x1, h){ box(parent, x1-x0, h, 0.16, inWall, (x0+x1)/2, h/2, z); }
function rug(parent, w, d, x, z, y, mat){ box(parent, w, 0.03, d, mat, x, y, z); }
function chair(parent, x, z, y0, ry){
  const g=new THREE.Group();
  box(g, 0.45, 0.08, 0.45, woodD, 0, 0.5, 0);
  box(g, 0.45, 0.55, 0.09, woodD, 0, 0.82, -0.2);
  [[-0.18,-0.18],[0.18,-0.18],[-0.18,0.18],[0.18,0.18]].forEach(function(p){ box(g, 0.06, 0.5, 0.06, woodD, p[0], 0.25, p[1]); });
  g.position.set(x, y0, z); g.rotation.y=ry||0; parent.add(g); return g;
}
function sofa(parent, x, z, ry, Y){
  const g=new THREE.Group();
  box(g, 3.2, 0.5, 1.15, sofaC, 0, 0.4, 0);
  box(g, 3.2, 0.65, 0.28, sofaC, 0, 0.85, -0.44);
  box(g, 0.28, 0.62, 1.15, sofaC, -1.46, 0.83, 0);
  box(g, 0.28, 0.62, 1.15, sofaC, 1.46, 0.83, 0);
  box(g, 0.55, 0.2, 0.5, M(0xD8C8A8), -0.8, 0.78, -0.25);
  box(g, 0.55, 0.2, 0.5, M(0xD8C8A8), 0.8, 0.78, -0.25);
  g.position.set(x, (Y||Y1)+0.03, z); g.rotation.y=ry||0; parent.add(g);
}
function bed(parent, x, z, ry, Y){
  const g=new THREE.Group();
  box(g, 1.6, 0.42, 2.2, woodD, 0, 0.26, 0);
  box(g, 1.5, 0.2, 2.0, MAT.white, 0, 0.57, 0);
  box(g, 1.4, 0.16, 0.5, MAT.fabric, 0, 0.68, -0.65);
  box(g, 1.6, 0.85, 0.12, woodD, 0, 0.7, -1.12);
  g.position.set(x, (Y||Y2)+0.03, z); g.rotation.y=ry||0; parent.add(g);
}
function wardrobe(parent, x, z, ry, Y){
  const g=new THREE.Group();
  box(g, 1.6, 2.1, 0.55, woodD, 0, 1.05, 0);
  box(g, 0.05, 1.9, 0.03, darkM, 0, 1.05, 0.29);
  g.position.set(x, (Y||Y2)+0.03, z); g.rotation.y=ry||0; parent.add(g);
}
function nightstand(parent, x, z, Y){
  const YY = Y||Y2;
  box(parent, 0.5, 0.5, 0.5, woodD, x, YY+0.28, z);
  cyl(parent, 0.03, 0.03, 0.25, darkM, x, YY+0.65, z, 6);
  const gl=sph(parent, 0.1, MAT.lampGlow.clone(), x, YY+0.82, z); glassMats.push(gl.material);
}
function pendant(parent, x, z, y){
  cyl(parent, 0.02, 0.02, 0.5, darkM, x, y+0.25, z, 6);
  const gl=sph(parent, 0.14, MAT.lampGlow.clone(), x, y, z); glassMats.push(gl.material);
}
/* --- 一层: 客厅 | 餐厅 | 厨房 --- */
slab(gF1, Y1+0.03, 0.06);
partSeg(gF1, -4.2, -4.25, -0.9, H1-0.35); partSeg(gF1, -4.2, 0.9, 4.25, H1-0.35);
partSeg(gF1, 4.2, -4.25, -0.9, H1-0.35); partSeg(gF1, 4.2, 0.9, 4.25, H1-0.35);
/* 客厅(左) */
rug(gF1, 4.6, 3.4, -7.4, 0.6, Y1+0.06, rugRed);
sofa(gF1, -7.4, 2.3, Math.PI);
box(gF1, 2.0, 0.35, 0.9, woodD, -7.4, Y1+0.22, 0.2);
box(gF1, 0.5, 0.35, 0.5, woodD, -8.6, Y1+0.2, 0.2);
box(gF1, 2.4, 0.5, 0.42, woodD, -7.4, Y1+0.28, -3.95);
box(gF1, 1.8, 1.05, 0.09, darkM, -7.4, Y1+1.15, -4.15);
box(gF1, 1.7, 2.2, 0.38, woodD, -10.4, Y1+1.1, -1.5);
chair(gF1, -9.6, 1.2, Y1+0.03, Math.PI/2);
pendant(gF1, -7.4, 0.4, Y1+2.9);
/* 餐厅(中) */
rug(gF1, 3.6, 3.0, 0, 1.2, Y1+0.06, rugBlue);
box(gF1, 2.4, 0.09, 1.2, woodD, 0, Y1+0.75, 1.0);
[[-0.95,0.55],[0.95,0.55],[-0.95,1.45],[0.95,1.45]].forEach(function(p){ box(gF1, 0.1, 0.72, 0.1, woodD, p[0], Y1+0.38, p[1]); });
chair(gF1, -0.85, 0.15, Y1+0.03, 0); chair(gF1, 0.85, 0.15, Y1+0.03, 0);
chair(gF1, -0.85, 1.9, Y1+0.03, Math.PI); chair(gF1, 0.85, 1.9, Y1+0.03, Math.PI);
box(gF1, 1.6, 1.0, 0.4, woodD, 0, Y1+0.5, -3.95);
pendant(gF1, 0, 1.0, Y1+2.9);
/* 楼梯(中右) */
for(let i=0;i<10;i++){ box(gF1, 1.7, 0.16, 0.34, MAT.wood, 3.3, Y1+0.08+i*0.3, 0.7+i*0.34); }
/* 厨房(右后) */
box(gF1, 6.0, 0.85, 0.6, appl, 7.6, Y1+0.45, -3.85);
box(gF1, 0.6, 0.85, 2.6, appl, 10.35, Y1+0.45, -2.4);
box(gF1, 1.9, 0.88, 0.95, appl, 7.4, Y1+0.47, -1.6);
box(gF1, 0.9, 2.0, 0.75, M(0x9FB6C4), 4.75, Y1+1.0, -3.8);
pendant(gF1, 7.0, -1.6, Y1+2.2); pendant(gF1, 7.8, -1.6, Y1+2.2);
/* --- 二层: 主卧 | 家庭房 | 次卧 | 卫浴 --- */
slab(gF2, Y2+0.03, 0.06);
partSeg(gF2, -4.2, -4.25, -0.9, H2-0.35); partSeg(gF2, -4.2, 0.9, 4.25, H2-0.35);
partSeg(gF2, 4.2, -4.25, -0.9, H2-0.35); partSeg(gF2, 4.2, 0.9, 4.25, H2-0.35);
partWall(gF2, 0, 4.2, 10.8, H2-0.35);
/* 主卧(左) */
rug(gF2, 4.4, 3.2, -7.4, 0.6, Y2+0.06, rugRed);
bed(gF2, -8.0, 0.4, 0);
nightstand(gF2, -9.2, 0.4); nightstand(gF2, -6.8, 0.4);
wardrobe(gF2, -6.2, -3.85, 0);
box(gF2, 1.6, 0.09, 0.7, woodD, -9.7, Y2+0.76, 3.3);
chair(gF2, -9.7, 2.5, Y2+0.03, Math.PI);
pendant(gF2, -8.0, 0.4, Y2+2.6);
/* 家庭房(中) */
rug(gF2, 5.0, 3.2, 0, 0.8, Y2+0.06, rugGreen);
bed(gF2, -0.5, 1.0, 0);
wardrobe(gF2, 2.8, -3.85, 0);
box(gF2, 1.5, 0.75, 0.5, woodD, -2.5, Y2+0.4, -3.9);
pendant(gF2, 0, 1.0, Y2+2.6);
/* 次卧(右前) */
rug(gF2, 4.0, 2.6, 7.4, 2.4, Y2+0.06, rugBlue);
bed(gF2, 7.4, 2.4, 0);
nightstand(gF2, 5.9, 2.4);
wardrobe(gF2, 10.3, 3.6, 0);
pendant(gF2, 7.4, 2.4, Y2+2.6);
/* 卫浴(右后) */
box(gF2, 1.9, 0.6, 0.95, MAT.white, 6.3, Y2+0.32, -3.55);
box(gF2, 1.6, 0.12, 0.65, M(0x7FA8C4), 6.3, Y2+0.56, -3.55);
cyl(gF2, 0.34, 0.28, 0.42, MAT.white, 9.9, Y2+0.21, -1.7, 14);
box(gF2, 0.55, 0.75, 0.2, MAT.white, 9.9, Y2+0.65, -1.35);
box(gF2, 0.95, 0.85, 0.5, MAT.white, 8.4, Y2+0.43, -3.85);
cyl(gF2, 0.25, 0.3, 0.12, tile, 8.4, Y2+0.9, -3.85, 12);
/* 书房(翼楼二层) */
(function(){ const cx=8, cz=4.5+2.25;
  box(gF2, 6, 0.06, 4.5, inFloor, cx, Y2+0.03, cz);
  rug(gF2, 3.6, 2.8, cx, cz, Y2+0.06, rugGreen);
  box(gF2, 1.7, 0.09, 0.75, woodD, cx, Y2+0.76, cz-1.2);
  chair(gF2, cx, cz-0.4, Y2+0.03, 0);
  box(gF2, 1.6, 2.0, 0.4, woodD, cx+2.2, Y2+1.0, cz+1.5);
})();

/* --- 三层: 主卧套房 | 书房 | 卫浴 | 客房 --- */
slab(gF3, Y3+0.03, 0.06);
partSeg(gF3, -4.2, -4.25, -0.9, H3-0.35); partSeg(gF3, -4.2, 0.9, 4.25, H3-0.35);
partSeg(gF3, 4.2, -4.25, -0.9, H3-0.35); partSeg(gF3, 4.2, 0.9, 4.25, H3-0.35);
partWall(gF3, 0, 4.2, 10.8, H3-0.35);
/* 主卧套房(左) */
rug(gF3, 4.6, 3.4, -7.4, 0.6, Y3+0.06, rugRed);
bed(gF3, -7.8, 0.6, 0, Y3);
nightstand(gF3, -9.1, 0.6, Y3); nightstand(gF3, -6.5, 0.6, Y3);
wardrobe(gF3, -5.9, -3.85, 0, Y3);
box(gF3, 1.4, 0.75, 0.5, woodD, -10.3, Y3+0.4, -3.8);
sph(gF3, 0.16, M(0xC8A85A), -10.3, Y3+0.95, -3.8);
box(gF3, 2.0, 1.1, 0.12, darkM, -7.8, Y3+1.0, -3.9);
chair(gF3, -9.3, 1.6, Y3+0.03, Math.PI/2);
pendant(gF3, -7.8, 0.6, Y3+2.5);
/* 书房(中) */
rug(gF3, 5.0, 3.2, 0, 1.0, Y3+0.06, rugGreen);
box(gF3, 2.0, 0.09, 0.9, woodD, 0, Y3+0.76, 1.0);
chair(gF3, 0, 0.3, Y3+0.03, 0);
box(gF3, 2.2, 2.2, 0.4, woodD, 2.5, Y3+1.1, -3.85);
box(gF3, 2.2, 2.2, 0.4, woodD, -2.5, Y3+1.1, -3.85);
pendant(gF3, 0, 1.0, Y3+2.5);
/* 卫浴(右后) */
box(gF3, 2.0, 0.6, 1.0, MAT.white, 6.3, Y3+0.32, -3.5);
box(gF3, 1.7, 0.12, 0.7, M(0x7FA8C4), 6.3, Y3+0.56, -3.5);
cyl(gF3, 0.34, 0.28, 0.42, MAT.white, 9.9, Y3+0.21, -1.7, 14);
box(gF3, 0.55, 0.75, 0.2, MAT.white, 9.9, Y3+0.65, -1.35);
box(gF3, 1.0, 0.85, 0.5, MAT.white, 8.4, Y3+0.43, -3.85);
cyl(gF3, 0.25, 0.3, 0.12, tile, 8.4, Y3+0.9, -3.85, 12);
/* 客房(右前) */
rug(gF3, 4.0, 2.6, 7.4, 2.4, Y3+0.06, rugBlue);
bed(gF3, 7.4, 2.4, 0, Y3);
nightstand(gF3, 5.9, 2.4, Y3);
wardrobe(gF3, 10.3, 3.6, 0, Y3);
pendant(gF3, 7.4, 2.4, Y3+2.5);

/* --- 四层: 影音游戏室 | 阅读储藏 --- */
slab(gF4, Y4+0.03, 0.06);
partWall(gF4, 0, -11, 11, H4-0.35);
/* 影音室(前) */
rug(gF4, 7.0, 3.0, -3, 2.0, Y4+0.06, rugBlue);
sofa(gF4, -4.0, 3.0, Math.PI, Y4);
box(gF4, 3.4, 1.8, 0.12, darkM, -3, Y4+1.3, -3.9);
box(gF4, 2.4, 0.35, 0.5, woodD, -3, Y4+0.2, -3.9);
box(gF4, 1.8, 0.75, 1.1, M(0x4A6A8C), 7.5, Y4+0.4, 1.5);
box(gF4, 1.8, 0.1, 1.1, M(0x2E6B3A), 7.5, Y4+0.82, 1.5);
pendant(gF4, 7.5, 1.5, Y4+2.3);
box(gF4, 0.8, 1.8, 0.7, M(0x4A4A5A), -9.5, Y4+0.9, 1.8);
box(gF4, 0.7, 0.5, 0.15, M(0xE8C84A), -9.5, Y4+1.7, 1.95);
chair(gF4, -8.0, 1.5, Y4+0.03, -Math.PI/2);
/* 阅读储藏(后) */
rug(gF4, 5.0, 3.0, 4, -1.8, Y4+0.06, rugGreen);
sofa(gF4, 4.5, -3.2, 0, Y4);
box(gF4, 1.2, 1.2, 0.4, woodD, 8.5, Y4+0.6, -2.5);
for(let i=0;i<3;i++){ box(gF4, 1.5, 0.4, 0.5, woodD, 7.0, Y4+0.2+i*0.45, -1.0); }
pendant(gF4, 4.5, -1.8, Y4+2.3);


/* ===== 外景升级: 阳台/百叶窗/花箱/假山池塘/亭/停车场车/长椅 ===== */
const rockMat = M(0x8A8878, {roughness:1.0});

/* 阳台 */
function balcony(parent, x, y, z, w, depth){
  box(parent, w, 0.12, depth, MAT.stone, x, y+0.06, z+depth/2);
  box(parent, w, 0.06, 0.06, MAT.iron, x, y+0.85, z+depth-0.05);
  box(parent, w, 0.06, 0.06, MAT.iron, x, y+0.06, z+depth-0.05);
  const n = Math.max(3, Math.floor(w/0.42));
  for(let i=0;i<=n;i++){
    box(parent, 0.05, 0.8, 0.05, MAT.iron, x-w/2+i*(w/n), y+0.45, z+depth-0.05);
  }
}
balcony(gF2, 0, Y2, 4.5, 3.2, 0.9);
balcony(gF3, -7.4, Y3, 4.5, 2.4, 0.85);
balcony(gF4, -2, Y4, 4.5, 2.2, 0.8);

/* 窗下花箱(一层前窗) */
(function(){
  const cols=[M(0xC94A4A), M(0xE8C84A), M(0xD87AB0), M(0xE8E4DA)];
  [-9,-5.5,-2].forEach(function(x){
    box(gF1, 1.2, 0.26, 0.32, M(0x9B5A3C), x, Y1+1.15, 4.5+0.28);
    for(let i=0;i<4;i++) sph(gF1, 0.08, cols[(i+Math.round(Math.abs(x)*7))%4], x-0.45+i*0.3, Y1+1.34, 4.5+0.3+((i%2)?0.06:-0.06));
  });
})();

/* 百叶窗(一二层前窗) */
(function(){
  [-9,-5.5,-2].forEach(function(x){
    [[gF1, Y1+1.9, 2.0],[gF2, Y2+1.6, 1.7]].forEach(function(fl){
      box(fl[0], 0.16, fl[2], 0.06, M(0x3E5A3A), x-0.85, fl[1], 4.5+0.14);
      box(fl[0], 0.16, fl[2], 0.06, M(0x3E5A3A), x+0.85, fl[1], 4.5+0.14);
    });
  });
})();

/* 假山 + 池塘 */
(function(){
  const pond = new THREE.Mesh(new THREE.CylinderGeometry(2.6, 2.4, 0.25, 24), M(0x6FA8C8, {roughness:0.15}));
  pond.position.set(-21, 0.05, -14); pond.receiveShadow = true; gSite.add(pond);
  const wtr = new THREE.Mesh(new THREE.CylinderGeometry(2.35, 2.35, 0.02, 24), M(0x7FB4D8, {roughness:0.1, metalness:0.1}));
  wtr.position.set(-21, 0.18, -14); gSite.add(wtr);
  [[-19,-16,1.2],[-20,-16.5,0.8],[-21,-16.3,1.0],[-22,-15.8,0.7],[-19.5,-15.2,0.9],[-20.5,-15.5,1.3]].forEach(function(r){
    const m = new THREE.Mesh(new THREE.DodecahedronGeometry(r[2], 0), rockMat);
    m.position.set(r[0], r[2]*0.5, r[1]);
    m.scale.set(1, 0.6+Math.random()*0.5, 1);
    m.rotation.set(Math.random()*0.4, Math.random()*Math.PI, Math.random()*0.4);
    m.castShadow = true; m.receiveShadow = true; gSite.add(m);
  });
  for(let i=0;i<6;i++) sph(gSite, 0.22+Math.random()*0.15, MAT.hedge, -20+(Math.random()-0.5)*3, 0.7+Math.random()*0.4, -15.5+(Math.random()-0.5)*1.5);
})();

/* 亭子 */
(function(){
  const g = new THREE.Group();
  cyl(g, 2.3, 2.4, 0.35, MAT.stone, 0, 0.18, 0, 6);
  for(let i=0;i<6;i++){
    const a = i/6*Math.PI*2;
    cyl(g, 0.09, 0.11, 2.7, M(0x7A4A28), Math.cos(a)*1.75, 1.55, Math.sin(a)*1.75, 10);
  }
  const cone = new THREE.Mesh(new THREE.ConeGeometry(2.9, 1.5, 6), M(0x8A5A30));
  cone.position.y = 3.45; cone.castShadow = true; g.add(cone);
  sph(g, 0.16, MAT.gold, 0, 4.3, 0);
  for(let i=0;i<6;i++){
    const a = i/6*Math.PI*2;
    box(g, 0.06, 0.45, 0.06, M(0x7A4A28), Math.cos(a)*1.75, 0.45, Math.sin(a)*1.75);
  }
  box(g, 0.5, 0.12, 2.6, M(0x8A6844), 0, 0.55, 0);
  box(g, 2.6, 0.12, 0.5, M(0x8A6844), 0, 0.55, 0);
  g.position.set(22, 0, -13); gSite.add(g);
})();

/* 停车场 + 车 */
(function(){
  box(gSite, 9, 0.06, 6.5, M(0x8E9296), 16, 0.03, 13);
  box(gSite, 0.1, 0.02, 4.2, M(0xE8E8E0), 12.5, 0.07, 13);
  box(gSite, 0.1, 0.02, 4.2, M(0xE8E8E0), 16, 0.07, 13);
  box(gSite, 0.1, 0.02, 4.2, M(0xE8E8E0), 19.5, 0.07, 13);
  const c = new THREE.Group();
  box(c, 4.3, 0.7, 1.9, M(0xB03A3A), 0, 0.75, 0);
  box(c, 2.1, 0.55, 1.7, M(0xB03A3A), -0.2, 1.32, 0);
  box(c, 1.95, 0.42, 1.55, M(0x2E3A45, {roughness:0.15, metalness:0.3}), -0.2, 1.34, 0);
  box(c, 0.16, 0.14, 0.3, M(0xFFE8A1), -2.18, 0.72, -0.5);
  box(c, 0.16, 0.14, 0.3, M(0xFFE8A1), -2.18, 0.72, 0.5);
  box(c, 0.14, 0.12, 0.25, M(0xC94A4A), 2.18, 0.72, -0.5);
  box(c, 0.14, 0.12, 0.25, M(0xC94A4A), 2.18, 0.72, 0.5);
  [[-1.45,-0.95],[1.45,-0.95],[-1.45,0.95],[1.45,0.95]].forEach(function(p){
    const w = new THREE.Mesh(new THREE.CylinderGeometry(0.42,0.42,0.32,18), M(0x1E1E1E));
    w.rotation.z = Math.PI/2; w.position.set(p[0], 0.42, p[1]); w.castShadow=true; c.add(w);
    const h = new THREE.Mesh(new THREE.CylinderGeometry(0.16,0.16,0.34,12), M(0xC8C8C8));
    h.rotation.z = Math.PI/2; h.position.set(p[0], 0.42, p[1]); c.add(h);
  });
  c.position.set(17.7, 0, 12.4); c.rotation.y = -Math.PI/2; gSite.add(c);
})();

/* 长椅 */
(function(){
  [[-24, 6],[20, -8]].forEach(function(p){
    box(gSite, 1.8, 0.1, 0.5, M(0x8A6844), p[0], 0.5, p[1]);
    box(gSite, 1.8, 0.1, 0.18, M(0x8A6844), p[0], 0.82, p[1]-0.2);
    box(gSite, 0.08, 0.45, 0.45, M(0x4A3422), p[0]-0.75, 0.28, p[1]);
    box(gSite, 0.08, 0.45, 0.45, M(0x4A3422), p[0]+0.75, 0.28, p[1]);
  });
})();


/* ===== 日夜切换 ===== */
let night = false;
function setNight(v){
  night = v;
  sun.intensity = v?0.0:1.3; hemi.intensity = v?0.16:0.7; moon.intensity = v?0.35:0.0;
  scene.background = new THREE.Color(v?0x0A1224:0xBFD8EE);
  scene.fog = new THREE.Fog(v?0x0A1224:0xBFD8EE, 120, 320);
  glassMats.forEach(function(m){
    m.emissive = new THREE.Color(v?0xFFC964:0x000000);
    m.emissiveIntensity = v?0.9:0.0;
    m.color = new THREE.Color(v?0xE8D8A8:0x9FBFD8);
  });
  lampLights.forEach(function(l){ l.intensity = v?1.4:0; });
}
scene.background = new THREE.Color(0xBFD8EE);
scene.fog = new THREE.Fog(0xBFD8EE, 120, 320);

/* ===== 平滑过渡系统 ===== */
const tweens = [];
function easeInOut(k){ return k<0.5 ? 4*k*k*k : 1-Math.pow(-2*k+2,3)/2; }
function addTween(key, fn, dur){
  for(let i=tweens.length-1;i>=0;i--){ if(tweens[i].key===key) tweens.splice(i,1); }
  tweens.push({ key:key, t0:performance.now(), dur:dur, fn:fn });
}
function tweenVec(key, v, to, dur){
  const from = v.clone();
  const toV = new THREE.Vector3(to.x||0, to.y||0, to.z||0);
  addTween(key, function(k){ v.lerpVectors(from, toV, k); }, dur);
}
function tweenCam(pos, target){
  tweenVec('camPos', camera.position, {x:pos[0], y:pos[1], z:pos[2]}, 1300);
  tweenVec('camTgt', controls.target, {x:target[0], y:target[1], z:target[2]}, 1300);
}

/* ===== 视角模式 ===== */
const views = {
  ext: { pos: [30, 18, 38], target: [0, 5, 2] },
  f1:  { pos: [0, 42, 8],   target: [0, 1.5, 0] },
  f2:  { pos: [0, 46, 8],   target: [0, 5.4, 0] },
  f3:  { pos: [0, 50, 8],   target: [0, 8.5, 0] },
  f4:  { pos: [0, 54, 8],   target: [0, 11.3, 0] }
};
let mode = 'ext';
const FLOOR_GROUPS = { f2:gF2, f3:gF3, f4:gF4, roof:gRoof };
const MODE_SLIDES = {
  ext: {},
  f1:  { f2:1, f3:2, f4:3, roof:4 },
  f2:  { f3:1, f4:2, roof:3 },
  f3:  { f4:1, roof:2 },
  f4:  { roof:1 }
};
function setMode(v){
  mode = v;
  for(const gname in FLOOR_GROUPS){
    const order = MODE_SLIDES[v][gname];
    const to = order ? {x:42, y:order*2.5, z:0} : {x:0, y:0, z:0};
    tweenVec(gname, FLOOR_GROUPS[gname].position, to, 1300);
  }
  const t = views[v];
  tweenCam(t.pos, t.target);
  const lbl = {ext:'外观环视', f1:'一层平面', f2:'二层平面', f3:'三层平面', f4:'四层平面'};
  document.getElementById('label').textContent = lbl[v];
  Array.prototype.forEach.call(document.querySelectorAll('[data-view]'), function(b){ b.classList.toggle('on', b.getAttribute('data-view')===v); });
}

/* ===== 导出 GLB ===== */
document.getElementById('exportBtn').addEventListener('click', function(){
  const exporter = new THREE.GLTFExporter();
  const saves = {};
  for(const gname in FLOOR_GROUPS){ saves[gname] = FLOOR_GROUPS[gname].position.clone(); FLOOR_GROUPS[gname].position.set(0,0,0); }
  setNight(false);
  exporter.parse(manor, function(result){
    const blob = new Blob([result], { type: 'model/gltf-binary' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = 'sunnyfield_manor.glb'; a.click();
    URL.revokeObjectURL(a.href);
    for(const gname in FLOOR_GROUPS){ FLOOR_GROUPS[gname].position.copy(saves[gname]); }
    setNight(night);
  }, { binary: true });
});

/* ===== UI 绑定 ===== */
document.getElementById('nightBtn').addEventListener('click', function(){
  setNight(!night); this.textContent = night ? '☀ 白天' : '☾ 夜晚';
});
document.getElementById('rotBtn').addEventListener('click', function(){
  controls.autoRotate = !controls.autoRotate; controls.autoRotateSpeed = 0.8;
  this.classList.toggle('on', controls.autoRotate);
});
Array.prototype.forEach.call(document.querySelectorAll('[data-view]'), function(b){
  b.addEventListener('click', function(){ setMode(b.getAttribute('data-view')); });
});
addEventListener('resize', function(){
  camera.aspect = innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

/* ===== 可编辑系统 + 填充物 ===== */
function makeTree(s){ s = s||1; const g=new THREE.Group(); cyl(g,0.26*s,0.38*s,2.6*s,MAT.trunk,0,1.3*s,0,10); sph(g,1.8*s,MAT.leaf1,0,3.4*s,0); sph(g,1.3*s,MAT.leaf2,1.0*s,4.1*s,0.5*s); sph(g,1.15*s,MAT.leaf3,-0.9*s,4.2*s,-0.5*s); return g; }
function makeBush(){ const g=new THREE.Group(); sph(g,0.5,MAT.hedge,0,0.45,0); sph(g,0.38,MAT.leaf2,0.28,0.72,0.14); return g; }
function makeFlower(){ const g=new THREE.Group(); const cols=[M(0xC94A4A),M(0xE8C84A),M(0xD87AB0),M(0xE8E4DA)]; for(let i=0;i<5;i++){ sph(g,0.12,cols[i%4],(i-2)*0.22,0.14,(i%2?0.12:-0.12)); } return g; }
function makeRock(s){ const g=new THREE.Group(); const m=new THREE.Mesh(new THREE.DodecahedronGeometry(s||0.8,0), rockMat); m.scale.set(1,0.7,1); m.castShadow=m.receiveShadow=true; g.add(m); return g; }
function makeBench(){ const g=new THREE.Group(); box(g,1.8,0.1,0.5,M(0x8A6844),0,0.5,0); box(g,1.8,0.1,0.18,M(0x8A6844),0,0.82,-0.2); box(g,0.08,0.45,0.45,M(0x4A3422),-0.75,0.28,0); box(g,0.08,0.45,0.45,M(0x4A3422),0.75,0.28,0); return g; }
function makeLamp(){ const g=new THREE.Group(); cyl(g,0.08,0.12,2.8,MAT.timber,0,1.4,0,8); const gl=sph(g,0.26,MAT.lampGlow.clone(),0,2.9,0); glassMats.push(gl.material); const l=new THREE.PointLight(0xFFC964,0,15); l.position.set(0,2.9,0); g.add(l); lampLights.push(l); return g; }
function makeCar(){ const c=new THREE.Group();
  box(c,4.3,0.7,1.9,M(0xB03A3A),0,0.75,0); box(c,2.1,0.55,1.7,M(0xB03A3A),-0.2,1.32,0);
  box(c,1.95,0.42,1.55,M(0x2E3A45,{roughness:0.15,metalness:0.3}),-0.2,1.34,0);
  box(c,0.16,0.14,0.3,M(0xFFE8A1),-2.18,0.72,-0.5); box(c,0.16,0.14,0.3,M(0xFFE8A1),-2.18,0.72,0.5);
  box(c,0.14,0.12,0.25,M(0xC94A4A),2.18,0.72,-0.5); box(c,0.14,0.12,0.25,M(0xC94A4A),2.18,0.72,0.5);
  [[-1.45,-0.95],[1.45,-0.95],[-1.45,0.95],[1.45,0.95]].forEach(function(p){
    const w=new THREE.Mesh(new THREE.CylinderGeometry(0.42,0.42,0.32,18),M(0x1E1E1E)); w.rotation.z=Math.PI/2; w.position.set(p[0],0.42,p[1]); w.castShadow=true; c.add(w);
    const h=new THREE.Mesh(new THREE.CylinderGeometry(0.16,0.16,0.34,12),M(0xC8C8C8)); h.rotation.z=Math.PI/2; h.position.set(p[0],0.42,p[1]); c.add(h);
  });
  return c; }
function makePavilion(){ const g=new THREE.Group();
  cyl(g,2.3,2.4,0.35,MAT.stone,0,0.18,0,6);
  for(let i=0;i<6;i++){ const a=i/6*Math.PI*2; cyl(g,0.09,0.11,2.7,M(0x7A4A28),Math.cos(a)*1.75,1.55,Math.sin(a)*1.75,10); }
  const cone=new THREE.Mesh(new THREE.ConeGeometry(2.9,1.5,6),M(0x8A5A30)); cone.position.y=3.45; cone.castShadow=true; g.add(cone);
  sph(g,0.16,MAT.gold,0,4.3,0);
  for(let i=0;i<6;i++){ const a=i/6*Math.PI*2; box(g,0.06,0.45,0.06,M(0x7A4A28),Math.cos(a)*1.75,0.45,Math.sin(a)*1.75); }
  box(g,0.5,0.12,2.6,M(0x8A6844),0,0.55,0); box(g,2.6,0.12,0.5,M(0x8A6844),0,0.55,0);
  return g; }
function makeFountain(){ const g=new THREE.Group();
  cyl(g,1.6,1.75,0.5,MAT.stone,0,0.25,0,20); cyl(g,1.3,1.3,0.1,M(0x7FB4D8,{roughness:0.1}),0,0.5,0,20);
  cyl(g,0.3,0.4,1.0,MAT.stone,0,1.0,0,12); cyl(g,0.6,0.7,0.2,MAT.stone,0,1.5,0,12);
  cyl(g,0.5,0.5,0.08,M(0x7FB4D8,{roughness:0.1}),0,1.66,0,12); sph(g,0.18,M(0x7FB4D8),0,2.0,0);
  return g; }
const FACTORIES = { tree:makeTree, bush:makeBush, flower:makeFlower, rock:makeRock, bench:makeBench, lamp:makeLamp, car:makeCar, pavilion:makePavilion, fountain:makeFountain };

/* 填充空地(默认内容) */
(function(){
  const f=makeFountain(); f.position.set(0,0,16); gSite.add(f);
  for(let r=0;r<2;r++) for(let c=0;c<3;c++){ const t=makeTree(0.8); t.position.set(18+r*3.5,0,-18+c*3.5); gSite.add(t); }
  for(let r=0;r<4;r++){ box(gSite,6,0.1,1.4,M(0x6B4A2E),-18,0.05,-16+r*2.4); for(let i=0;i<8;i++){ sph(gSite,0.1,[M(0xC94A4A),M(0xE8C84A),M(0xD87AB0)][i%3],-20+i*0.6,0.2,-16+r*2.4); } }
  const c2=makeCar(); c2.position.set(13.3,0,11.5); c2.rotation.y=-Math.PI/2; gSite.add(c2);
  (function(){ const sw=new THREE.Group();
    box(sw,0.12,2.6,0.12,MAT.wood,-1.2,1.3,0); box(sw,0.12,2.6,0.12,MAT.wood,1.2,1.3,0);
    box(sw,2.6,0.15,0.15,MAT.wood,0,2.6,0);
    box(sw,0.6,0.1,0.35,MAT.wood,-0.35,0.6,-0.15); box(sw,0.6,0.1,0.35,MAT.wood,0.35,0.6,-0.15);
    [[-0.35],[0.35]].forEach(function(p){ box(sw,0.04,1.7,0.04,MAT.iron,p[0],1.5,-0.2); });
    sw.position.set(-14,0,8); gSite.add(sw); })();
  [[-34,-24],[34,-24],[-34,24],[34,24],[-26,-26],[26,-26]].forEach(function(p){ const t=makeTree(1.1); t.position.set(p[0],0,p[1]); gSite.add(t); });
})();

/* 编辑模式交互 */
let editMode = false, selected = null, dragging = false, selRing = null;
const groundPlane = new THREE.Plane(new THREE.Vector3(0,1,0), 0);
const editRay = new THREE.Raycaster();
function initSelRing(){
  selRing = new THREE.Mesh(new THREE.RingGeometry(0.5,0.62,32), new THREE.MeshBasicMaterial({color:0xFFD24A, side:THREE.DoubleSide, transparent:true, opacity:0.9}));
  selRing.rotation.x = -Math.PI/2; selRing.visible = false; scene.add(selRing);
}
function updateRing(){ if(selected){ const wp=new THREE.Vector3(); selected.getWorldPosition(wp); selRing.position.set(wp.x, 0.08, wp.z); } }
function select(o){ selected = o; selRing.visible = true; updateRing(); document.getElementById('seltools').style.display='flex'; }
function deselect(){ selected = null; if(selRing) selRing.visible=false; document.getElementById('seltools').style.display='none'; }
function isLawn(o){ return o.geometry && o.geometry.type === 'PlaneGeometry'; }
function toSiteRoot(o){ let p=o; while(p && p.parent && p.parent !== gSite){ p=p.parent; } return (p && p.parent===gSite) ? p : o; }
function pickObj(e){
  const ndc = new THREE.Vector2((e.clientX/innerWidth)*2-1, -(e.clientY/innerHeight)*2+1);
  editRay.setFromCamera(ndc, camera);
  const hits = editRay.intersectObjects(gSite.children, true);
  for(const h of hits){ if(!isLawn(h.object)) return toSiteRoot(h.object); }
  return null;
}
renderer.domElement.addEventListener('pointerdown', function(e){
  if(!editMode || e.button !== 0) return;
  const o = pickObj(e);
  if(o){ select(o); dragging = true; controls.enabled = false; }
  else { deselect(); }
});
renderer.domElement.addEventListener('pointermove', function(e){
  if(!editMode || !dragging || !selected) return;
  const ndc = new THREE.Vector2((e.clientX/innerWidth)*2-1, -(e.clientY/innerHeight)*2+1);
  editRay.setFromCamera(ndc, camera);
  const pt = new THREE.Vector3();
  if(editRay.ray.intersectPlane(groundPlane, pt)){
    selected.position.x = pt.x; selected.position.z = pt.z;
    updateRing();
  }
});
addEventListener('pointerup', function(){ dragging = false; controls.enabled = true; });
addEventListener('keydown', function(e){
  if(!editMode || !selected) return;
  if(e.key==='Delete' || e.key==='Backspace'){ gSite.remove(selected); deselect(); }
  if(e.key==='Escape'){ deselect(); }
});

document.getElementById('editBtn').addEventListener('click', function(){
  editMode = !editMode;
  this.classList.toggle('on', editMode);
  document.getElementById('editbar').style.display = editMode ? 'flex' : 'none';
  controls.mouseButtons = editMode
    ? { LEFT: null, MIDDLE: THREE.MOUSE.DOLLY, RIGHT: THREE.MOUSE.ROTATE }
    : { LEFT: THREE.MOUSE.ROTATE, MIDDLE: THREE.MOUSE.DOLLY, RIGHT: THREE.MOUSE.PAN };
  document.getElementById('hint').textContent = editMode ? '点击选中并拖动 · 右键旋转 · 滚轮缩放 · Delete删除' : '左键旋转 · 滚轮缩放 · 右键平移';
  if(!editMode) deselect();
});
Array.prototype.forEach.call(document.querySelectorAll('[data-add]'), function(b){
  b.addEventListener('click', function(){
    const f = FACTORIES[b.getAttribute('data-add')];
    if(!f) return;
    const obj = f();
    gSite.add(obj);
    obj.position.set((Math.random()-0.5)*10, 0, 5 + Math.random()*6);
    select(obj);
  });
});
document.getElementById('rotL').addEventListener('click', function(){ if(selected){ selected.rotation.y -= Math.PI/8; } });
document.getElementById('rotR').addEventListener('click', function(){ if(selected){ selected.rotation.y += Math.PI/8; } });
document.getElementById('scUp').addEventListener('click', function(){ if(selected){ selected.scale.multiplyScalar(1.15); } });
document.getElementById('scDn').addEventListener('click', function(){ if(selected){ selected.scale.multiplyScalar(0.87); } });
document.getElementById('del').addEventListener('click', function(){ if(selected){ gSite.remove(selected); deselect(); } });

initSelRing();


/* ===== 渲染循环 ===== */
(function animate(){
  requestAnimationFrame(animate);
  const now = performance.now();
  for(let i=tweens.length-1;i>=0;i--){
    const tw = tweens[i];
    const k = easeInOut(Math.min(1, (now-tw.t0)/tw.dur));
    tw.fn(k);
    if(k>=1) tweens.splice(i,1);
  }
  controls.update(); renderer.render(scene, camera);
})();
setMode('ext');
document.getElementById('loading').style.display = 'none';
