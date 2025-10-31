/*
 *  Document    : character.jsx
 *  Author      : Novac - Ganapathy
 *  Description : This page user for Load 3D character and call its animation.
 */

// import { useLoader } from "@react-three/fiber";
// import { GLTFLoader } from "three/addons/loaders/GLTFLoader";
import CharacterLoader from "./CharacterLoader";
import { useGLTF } from "@react-three/drei";

const ModelAnimationLoader = ({
  recording,
  avatarAction,
  audioReload,
  animationGLB,
  glbfiles,
}) => {
  // Load 3D character
  //   let gltf = useLoader(GLTFLoader, `/Character/Joh_Armature.glb`);
  const { animations } = useGLTF(animationGLB);

  return (
    <>
      {glbfiles &&
        glbfiles.map((value, index) => (
          <CharacterLoader
            key={index}
            // url={value}
            url={value.file}
            avatarAction={avatarAction}
            audioReload={audioReload}
            recording={recording}
            animation={animations}
          />
        ))}
    </>
  );
};

export default ModelAnimationLoader;
