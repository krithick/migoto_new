import { useAnimations, useGLTF } from '@react-three/drei';
import React, { useEffect, useRef } from 'react'

function Avatar({url, onLoad,animation,isPlaying, audioRef}) {
  console.log('isPlaying: ', isPlaying);
      // Preload the GLB model for better performance
      useGLTF.preload(url);
      let analyserRef = useRef()
    
      const { scene } = useGLTF(url);
      const { actions, names } = useAnimations(animation, scene); // Load animations
      // console.log('names: ', names);
      // console.log('actions: ', actions);

      // useEffect(() => {
      //   // Only setup audio analysis when audio is playing and audioRef exists
      //   if (audioRef?.current && isPlaying) {
      //     // Create Web Audio API context for audio processing
      //     const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      //     // Create analyser node for frequency analysis
      //     const analyser = audioContext.createAnalyser();
      //     console.log('analyser: ', analyser);
      //     // Create source node from HTML audio element
      //     const source = audioContext.createMediaElementSource(audioRef.current);
      //     console.log('source: ', source);
          
      //     // Set FFT size for frequency analysis (256 = good balance of performance/accuracy)
      //     analyser.fftSize = 256;
      //     // Connect audio source to analyser
      //     source.connect(analyser);
      //     // Connect analyser to audio output (speakers)
      //     analyser.connect(audioContext.destination);
      //     // Store analyser reference for cleanup
      //     analyserRef.current = analyser;
          
      //     // Create array to store frequency data
      //     const dataArray = new Uint8Array(analyser.frequencyBinCount);
          
      //     /**
      //      * Recursive function to continuously analyze audio levels
      //      * Updates audio level state based on frequency data
      //      */
      //     const updateAudioLevel = () => {
      //       // Get current frequency data from analyser
      //       analyser.getByteFrequencyData(dataArray);
      //       // Calculate average frequency level
      //       const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
      //       // Normalize to 0-1 range and update state
      //       setAudioLevel(average / 255);
      //       // Schedule next analysis frame
      //       animationFrameRef.current = requestAnimationFrame(updateAudioLevel);
      //     };

      //     // Start audio analysis loop
      //     updateAudioLevel();

      //     // Cleanup function - runs when effect dependencies change or component unmounts
      //     return () => {
      //       // Cancel ongoing animation frame to prevent memory leaks
      //       if (animationFrameRef.current) {
      //         cancelAnimationFrame(animationFrameRef.current);
      //       }
      //     };
      //   }
      // }, [isPlaying, audioRef]);
      
      useEffect(()=>{
        // Only proceed if animation actions are available
        if(actions){
          if(isPlaying){
            // When audio is playing: stop idle animation and start talk animation
            actions["idle"]?.reset().fadeOut(0.5).stop();
            actions["talk"]?.reset().fadeIn(0.5).play();
          }else{
            // When audio stops: stop talk animation and start idle animation
            actions["talk"]?.reset().fadeOut(0.5).stop();
            actions["idle"]?.reset().fadeIn(0.5).play();
          }
        }
      },[isPlaying, actions])

      useEffect(() => {
        if (scene && onLoad) {
          onLoad();
        }
      }, [scene, onLoad]);
    
  return (
    <primitive object={scene} position={[0, -1, .5]}></primitive>
  )
}

export default Avatar