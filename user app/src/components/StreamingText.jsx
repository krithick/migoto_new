import React, { useState, useEffect } from "react";

const StreamingText = ({ message, audioRef, mic }) => {
  const cleanMessage = message.replace(/[\*\#]|\[CORRECT\]/g, "");
  const words = cleanMessage.split(" ");
  const [currentIndex, setCurrentIndex] = useState(-1);

  useEffect(() => {
    if (!audioRef?.current) return;

    const handlePlay = () => {
      const timePerWord = audioRef.current.duration / words.length;

      words.forEach((_, i) => {
        setTimeout(() => {
          setCurrentIndex(i);
        }, i * timePerWord * 1000);
      });
    };

    audioRef.current.addEventListener("playing", handlePlay);

    return () => {
      audioRef.current.removeEventListener("playing", handlePlay);
    };
  }, [audioRef, words]);

  return (
    <span>
      {words.map((word, i) => (
        <span
          key={i}
          className={
            i === currentIndex && mic ? "bg-yellow-200 px-1 rounded" : ""
          }
        >
          {word}{" "}
        </span>
      ))}
    </span>
  );
};

export default StreamingText;
