import React from 'react'
import Avatar from './Avatar'
import { useGLTF } from '@react-three/drei';

function ModelLoader({glb, data, onLoad, animation, isPlaying, audioRef}) {
  const { animations } = animation ? useGLTF(animation) : { animations: null };

  return (
    <>
        {/* Render Avatar components for each GLB model */}
        {glb && glb?.map((item, index)=>(
            <Avatar 
              key={index} 
              url={item?.file} 
              animation={animations || null}
              isPlaying={isPlaying}
              audioRef={audioRef}
              // Only trigger onLoad for the first model to avoid multiple calls
              onLoad={index === 0 ? onLoad : null}
            />
        ))}
    </>
  )
}

export default ModelLoader