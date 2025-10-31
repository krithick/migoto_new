import { useEffect, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

export default function useModelAnimation(scene, animationClips, play) {
  const mixer = useRef();

  useEffect(() => {

    if(play){
      if (scene && animationClips) {
        mixer.current = new THREE.AnimationMixer(scene);
        const action = mixer.current.clipAction(animationClips);
        action.play();
      }
    }
    return () => {
      mixer.current?.stopAllAction();
    };
  }, [scene, animationClips, play]);

  useFrame((_, delta) => {
    mixer.current?.update(delta);
  });
}
