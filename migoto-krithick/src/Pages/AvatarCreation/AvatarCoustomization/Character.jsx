import { useThree } from '@react-three/fiber';
import AnimatedModel from './AnimatedModel';
import { useEffect } from 'react';

function Character({ modelConfigs,modelVisibility, animationClips, play,onLoaded }) {
  useEffect(() => {
    // wait until all GLBs are loaded
    // then call:
    onLoaded?.(); // Call when done
  }, []);

  return (
    <>
      {
        modelConfigs?.map(model=>( 
          <AnimatedModel
            key={model.id}
            url={model.url}
            animationClips={animationClips}
            play={play}
            visible={modelVisibility[model.id]}
            // handleModel={handleModel}
          />
        ))
      }
      
    </>
  );
}


export default Character


