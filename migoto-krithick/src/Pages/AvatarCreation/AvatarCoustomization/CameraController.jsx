import React, { useEffect, useRef } from 'react';
import { useThree, useFrame } from '@react-three/fiber';
import * as THREE from 'three';

export default function CameraController({ filter }) {
  const { camera, controls } = useThree();

  const targetPosition = useRef(new THREE.Vector3());
  const targetLookAt = useRef(new THREE.Vector3());
  const speed = 0.1;

  useEffect(() => {
    switch (filter) {
      case "Body":
        targetPosition.current.set(0, 0.14, 2.5);
        targetLookAt.current.set(0, -0.1, 0);
        break;
      case "Pant":
        targetPosition.current.set(1, -0.2, 1);
        targetLookAt.current.set(0, -0.8, 0);
        break;
      case "Hair":
        targetPosition.current.set(0.21, 0.2, 0.15);
        targetLookAt.current.set(0.1, 0.16, -0.1);
        break;
      case "Shoes":
        targetPosition.current.set(0.3, -0.4, 1);
        targetLookAt.current.set(-0.1, -1.6, -0.4);
        break;
      case "Shirt":
        targetPosition.current.set(0, 0, 1);
        targetLookAt.current.set(0, 0, 0);
        break;
      case "Glass":
        targetPosition.current.set(0.4, 0.15, 0.55);
        targetLookAt.current.set(0, 0.1, -0.2);
        break;
      case "Beard":
        targetPosition.current.set(-0.1, 0.15, -0.05);
        targetLookAt.current.set(-0.07, 0.14, -0.2);
        break;
      case "Watch":
        targetPosition.current.set(0.6, 0, 0.2);
        targetLookAt.current.set(0.2, 0.4, 0);
        break;
      case "Ama":
        targetPosition.current.set(0, 0.08, 0.2);
        targetLookAt.current.set(0, 0.09, 0);
        break;
      case "Da":
        targetPosition.current.set(0, 0.07, 0.2);
        targetLookAt.current.set(0, 0.09, 0);
        break;
      case "Joh":
        targetPosition.current.set(0, 0.01, 0.18);
        targetLookAt.current.set(0, 0.03, 0);
        break;
      case "Moh":
        targetPosition.current.set(0, 0.12, 0.15);
        targetLookAt.current.set(0, 0.10, -0.2);
        break;
      default:
        targetPosition.current.set(0, 0, 2);
        targetLookAt.current.set(0, 0, 0);
        break;
    }
  }, [filter]);

  useFrame(() => {
    if (!controls) return;


    controls.object.position.lerp(targetPosition.current, speed);
    controls.target.lerp(targetLookAt.current, speed);
  
    controls.update();
  });
  

  return null;
}

// import React, { useEffect, useRef } from "react";
// import { useThree, useFrame } from "@react-three/fiber";
// import * as THREE from "three";

// export default function CameraController({ filter }) {
//   const { camera, controls } = useThree();
//   const targetPosition = useRef(new THREE.Vector3());
//   const targetFocus = useRef(new THREE.Vector3(0, 1, 0));
//   const currentPosition = useRef(new THREE.Vector3());
//   const currentFocus = useRef(new THREE.Vector3(0, 1, 0));
//   const speed = 0.1;

//   useEffect(() => {
//     switch (filter) {
//       case "Body":
//         targetPosition.current.set(0, 0.2, 1.3);
//         targetFocus.current.set(0, 0.8, 0);
//         break;
//       case "Pant":
//         targetPosition.current.set(0.8, 0, 1.6);
//         targetFocus.current.set(0.2, -0.8, 0);
//         break;
//       case "Hair":
//         targetPosition.current.set(0, 0, 0.45);
//         camera.zoom = 2;
//         camera.updateProjectionMatrix();
//         targetFocus.current.set(0, 0.6, 0.1);
//         break;
//       case "Shoes":
//         targetPosition.current.set(0.4, -0.6, 1.6);
//         targetFocus.current.set(0, -1.8, 0.7);
//         break;
//       case "Shirt":
//         targetPosition.current.set(-0.1, 0.1, 0.4);
//         targetFocus.current.set(0.1, 0.2, 0);
//         break;
//       case "Glass":
//         targetPosition.current.set(0.1, 0, 0.2);
//         targetFocus.current.set(0, 0.6, 0.1);
//         break;
//       case "Beard":
//         targetPosition.current.set(0, 0, 0.01);
//         targetFocus.current.set(0, 0.6, 0);
//         break;
//       case "Watch":
//         targetPosition.current.set(0.6, 0, 0.2);
//         targetFocus.current.set(0.2, 0.4, 0);
//         break;
//       case "Save":
//         targetPosition.current.set(0, 0, 0.4);
//         targetFocus.current.set(0, 0.6, 0.2);
//         break;
//       default:
//         targetPosition.current.set(0, 0, 2);
//         targetFocus.current.set(0, 0, 0);
//         break;
//     }
//   }, [filter]);

//   useFrame(() => {
//     currentPosition.current.lerp(targetPosition.current, speed);
//     currentFocus.current.lerp(targetFocus.current, speed);

//     camera.position.copy(currentPosition.current);
//     if (controls) {
//       controls.target.copy(currentFocus.current);
//       controls.update();
//     }
//   });

//   return null;
// }
