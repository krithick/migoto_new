/*
 *  Document    : character.jsx
 *  Author      : Novac - Ganapathy
 *  Description : This page user for Load 3D character and call its animation.
 */

import { useAnimations, useGLTF } from "@react-three/drei";
import { useEffect } from "react";
import * as THREE from "three";

const CharacterLoader = ({
  url,
  animation,
  recording,
  avatarAction,
  audioReload,
}) => {
  const { scene } = useGLTF(url);

  // Write a function to filter /Character/Joh_Beard_Br1.glb to Joh_Beard_Br1
  const fileName = url.split("/").pop().split(".")[0];

  const { actions, names } = useAnimations(animation, scene); // Load animations

  useEffect(() => {
    if (actions) {
      Object.values(actions).forEach((action) => action.stop()); // Stop all animations
      for (let i = 0; i < names.length; i++) {
        if (names[i].toLowerCase().includes("talk") && audioReload) {
          actions[names[i]]?.reset().fadeIn(0.5).play();
        }
        if (names[i].toLowerCase().includes("idle") && !audioReload) {
          actions[names[i]]?.reset().fadeIn(0.5).play();
        }
      }
    }
  }, [audioReload, actions]);

  useEffect(() => {
    scene.traverse((child) => {
      if (child.isMesh) {
        if (child.name.toLowerCase().includes("hair")) {
          if (!child.material.name.toLowerCase().includes("scalp")) {
            child.renderOrder = 1;
            // child.material.roughness = 1;
            // child.material.side = THREE.FrontSide;
            // child.material.side = THREE.BackSide;
            // child.material.side = THREE.FrontSide;
          }

          // console.log("child: ", child);
        }
      }
    });
  }, []);

  return (
    <primitive
      name={fileName}
      object={scene}
      scale={[30, 30, 30]}
      position={[0, -20, 0]}
      rotation={[0, 0, 0]}
    />
  );
};

export default CharacterLoader;
