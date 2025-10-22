import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { FBXLoader } from 'three/addons/loaders/FBXLoader.js';

function waitForContainer() {
    const container = document.getElementById('three-container');
    if (!container) {
        // 继续等待 100ms
        setTimeout(waitForContainer, 100);
        return;
    }

    // container 存在，可以安全执行 Three.js 初始化
    initThree(container);
}

// ✅ 提前定义一个全局对象
let bonesByName = {};
let actor;

function initThree(container) {
    console.log("========begin=====V001=====");
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    // 加光源
    scene.add(new THREE.AmbientLight(0x404040));
    const light = new THREE.DirectionalLight(0xcccccc, 1);
    light.position.set(100, 100, 100);
    scene.add(light);

    const light2 = new THREE.DirectionalLight(0xcccccc, 1);
    light2.position.set(-100, 0, -100);
    scene.add(light2);


    scene.background = new THREE.Color(0xeeeeee);  // 灰白背景

    const gridHelper = new THREE.GridHelper(1500, 50);
    scene.add(gridHelper);

    // OrbitControls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;  // 开启阻尼（惯性）
    controls.dampingFactor = 0.05;

    camera.position.set(0, 150, -400);

    // 加载 FBX 模型
    const loader = new FBXLoader();
    loader.load('/res/fbx/PNSRobot_Skin_NR.fbx', function (object) {
        //object.scale.set(0.1, 0.1, 0.1);
        object.position.set(0, 0, 0);
        console.log('FBX 加载成功', object);
        scene.add(object);
        actor = object;

        object.traverse((child) =>
        {
            //console.log("child:", child);
            if (child.isBone){
    //            {
    //                // 创建一个可视化的小球
    //                const sphereGeometry = new THREE.SphereGeometry(0.5);
    //                const sphereMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 }); // 红色
    //                const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
    //
    //                // 把小球加到骨骼上，这样它会随着骨骼移动
    //                child.add(sphere);
    //
    //            }

                bonesByName[child.name] = child;

            }
            // if (child.isMesh) {
            //     child.geometry = new THREE.BufferGeometry().fromGeometry(child.geometry);
            //     child.geometry.computeVertexNormals();
            // }
        });

        }, undefined, function (error) {
        console.error('Error loading FBX:', error);
    });

    function animate() {
        requestAnimationFrame(animate);
        //applyExternalPose();
        controls.update();  // 更新控制器
        renderer.render(scene, camera);
    }
    animate();
}

function applyExternalPose() {
  for (const name in bonesByName) {
    const bone = bonesByName[name];

    // 创建一个随机欧拉角（可以调节旋转范围）
    const euler = new THREE.Euler(
      (Math.random() - 0.5) * Math.PI * 0.2, // x: [-~18°, ~18°]
      (Math.random() - 0.5) * Math.PI * 0.2, // y
      (Math.random() - 0.5) * Math.PI * 0.2, // z
      'XYZ'
    );

    // 使用四元数设置骨骼旋转
    bone.quaternion.setFromEuler(euler);
  }
}

function updateBoneRotations(bvh_data) {
//    console.log("====bvh_data", bvh_data);
    for (const node of bvh_data.bones) {
        const bone = bonesByName[node.bone];
        const rot = node.rotation;
        const pos = node.offset;
        if (bone) {
            bone.quaternion.set(rot.x, rot.y, rot.z, rot.w).normalize();
            if (node.bone == "Hips"){
                bone.position.set(pos.x, pos.y , pos.z );
            }
        } else {
//            console.warn(`骨骼未找到: ${node.bone}`);
        }
    }
}

window.updateBoneRotations = updateBoneRotations;
window.waitForContainer = waitForContainer;

//waitForContainer();