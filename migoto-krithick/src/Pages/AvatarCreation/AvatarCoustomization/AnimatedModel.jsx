import { useGLTF } from '@react-three/drei';
import useModelAnimation from './useModelAnimation';



function AnimatedModel({ url, animationClips, visible, play }) {

  useGLTF.preload(url);

  const { scene } = useGLTF(url, true);
  useModelAnimation(scene, animationClips, play);

  return <primitive 
    name= {url} object={scene} visible={visible} position={[0, -1, 0]} />;

}

export default AnimatedModel
