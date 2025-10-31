// export default function Lights() {
//     return (
//       <>
//         <ambientLight intensity={1} />
//         <directionalLight position={[3, 6, 3]} intensity={9} />
//         <spotLight
//           position={[0, 65, 0]}
//           angle={0.2}
//           penumbra={0.5}
//           intensity={300}
//           castShadow
//         />
//       </>
//     );
//   }
import { useHelper } from "@react-three/drei";
import { useRef } from "react";
import { DirectionalLightHelper } from "three";

export default function Lights() {
  const keyLightRef = useRef();
  const fillLightRef = useRef();
  const backLightRef = useRef();

  // useHelper(keyLightRef, DirectionalLightHelper, 1, 'red');    // Key light
  // useHelper(fillLightRef, DirectionalLightHelper, 1, 'green'); // Fill light
  // useHelper(backLightRef, DirectionalLightHelper, 1, 'blue');  // Back light

  return (
    <>
      <ambientLight intensity={1} /> 
      
      {/* Key Light */}
      <directionalLight
        ref={keyLightRef}
        position={[5, 10, 5]}
        intensity={7}
        castShadow
      />
      
      {/* Fill Light */}
      <directionalLight
        ref={fillLightRef}
        position={[-5, 5, 5]}
        intensity={3}
      />
      
      {/* Back Light */}
      <directionalLight
        ref={backLightRef}
        position={[0, 5, -5]}
        intensity={3}
      />
    </>
  );
}
