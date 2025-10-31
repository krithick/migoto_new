import { useState } from "react";
import instance from "../service";
import axios from "axios";
import { Baseurl } from "../route";

const useLLM = (
  setMic,
  voice,
  conversationHistory,
  startTotalDurationTime,
  setStartTotalDurationTime,
  startAverageDurationTime,
  setIntervals,
  avatar,
  mode,
  language,
  setConversationHistory,
  onBotResponse,
  setSessionId,
  sessionId,
  setCoachMessage
) => {
  // const [sessionId, setSessionId] = useState(null);
  const sendMessage = async (userMessage, onMessageSent) => {
    if (onMessageSent) onMessageSent();
    if (conversationHistory.length != 0) {
      const lastQuestionIndex = conversationHistory
        .map((item, i) => ({ ...item, i }))
        .filter((item) => item.role === "bot")
        .map((item) => item.i)
        .pop();

      // Update if found
      if (lastQuestionIndex !== undefined) {
        conversationHistory[lastQuestionIndex].stream = false;
      }
    }
    setMic(true);
    // Function to get the current time in hh:mm:ss format
    const getFormattedTime = () => {
      const now = new Date();
      const hours = String(now.getHours()).padStart(2, "0");
      const minutes = String(now.getMinutes()).padStart(2, "0");
      const seconds = String(now.getSeconds()).padStart(2, "0");
      return `${hours}:${minutes}:${seconds}`;
    };

    if (sessionId == null) {
      setConversationHistory((prev) => [
        ...prev,
        { role: "user", message: userMessage, correct: true },
      ]);
      if (conversationHistory.length == 0 && startTotalDurationTime == null) {
        const start = new Date().getTime(); // Get current time in milliseconds
        setStartTotalDurationTime(start);
      }
      if (conversationHistory.length >= 1) {
        // setEndAverageDurationTime(getFormattedTime());
        const start = new Date(`1970-01-01T${startAverageDurationTime}Z`);
        const end = new Date(`1970-01-01T${getFormattedTime()}Z`);
        const interval = (end - start) / 1000; // Time difference in seconds
        setIntervals((prevIntervals) => [...prevIntervals, interval]);
      }
      // initialize the chat with the selected avatar, mode, and language
      const formdata = new FormData();
      formdata.append("avatar_interaction_id", mode?.avatar_interaction);
      formdata.append(
        "mode",
        `${
          mode?.title == "Try Mode"
            ? "try_mode"
            : mode?.title == "Learn Mode"
            ? "learn_mode"
            : "assess_mode"
        }`
      );
      formdata.append("persona_id", avatar?.selected.persona_id[0].id);
      formdata.append("language_id", language?.id);
      formdata.append("avatar_id", avatar?.selected.id);

      // initialize api header
      // Fetch and load token
      const headers = {
        "Content-Type": "multipart/form-data",
        Authorization: `Bearer ` + localStorage.getItem("migoto-token"),
      };

      // await instance.post("/chat/initialize", formdata, { headers })

      await axios
        .post(`${Baseurl}chat/initialize`, formdata, {
          headers,
        })
        .then(async (res) => {
          // localStorage.setItem("migoto-sessionId", res.data.id);
          setSessionId(res.data.id);
          const formData = new FormData();

          formData.append("id", res.data.id);
          formData.append("name", avatar?.selected.name);
          formData.append("message", userMessage);

          try {
            // const res = await instance.post("/chat", formData, {
            //   headers: { "Content-type": "multipart/form-data" },
            // });

            const res = await axios.post(
              `${Baseurl}chat`,
              formData,
              {
                headers: { "Content-type": "multipart/form-data" },
              }
            );

            const eventSource = new EventSource(
              `${Baseurl}chat/stream?id=${res.data.id}&name=${avatar?.selected.name}&voice_id=${voice?.voice_id}`,
            );

            let bot = null;

            eventSource.onmessage = (event) => {
              try {
                bot = JSON.parse(event.data);
                // process bot here
              } catch (e) {
                console.log("e: ", e);
                console.error("Invalid JSON:", event.data);
              }
            };

            eventSource.onerror = (error) => {
              console.error("EventSource error:", error);
              eventSource.close();

              // Handle null bot response (stream error)
              if (!bot) {
                console.error("No bot response received from stream");
                setMic(false);
                return;
              }

              // After streaming ends
              onBotResponse(bot);

              if (bot?.correct === true) {
                setConversationHistory((x) => [
                  ...x,
                  {
                    role: "bot",
                    message: bot.response,
                    stream: true,
                    correct: true,
                  },
                ]);
              } else {
                if (
                  mode?.title == "Try Mode" &&
                  bot?.correct_answer.length != 0
                ) {
                  setCoachMessage(bot.correct_answer);
                  setConversationHistory((x) => [
                    ...x,
                    {
                      role: "bot",
                      message: bot.correct_answer,
                      correct: bot.correct,
                    },
                    {
                      role: "bot",
                      message: bot.response,
                      stream: true,
                      correct: true,
                    },
                  ]);
                } else {
                  setConversationHistory((x) => [
                    ...x,
                    {
                      role: "bot",
                      message: bot.response,
                      stream: true,
                      correct: true,
                    },
                  ]);
                }
              }
            };

            // const response = await fetch(
            //   `https://meta.novactech.in:7445/chat/stream?id=${res.data.id}&name=${avatar?.selected.name}`,
            //   {
            //     headers: {
            //       Authorization:
            //         `Bearer ` + localStorage.getItem("migoto-token"),
            //     },
            //   }
            // );

            // const response = await fetch(
            //   `http://172.23.198.149:8000/chat/stream?id=${res.data.id}&name=${avatar?.selected.name}`,
            //   // `http://172.23.198.149:8000/chat/stream?id=${res.data.id}&name=${avatar?.selected.name}`,
            //   {
            //     headers: {
            //       Authorization:
            //         `Bearer ` + localStorage.getItem("migoto-token"),
            //     },
            //   }
            // );
            // const reader = response.body.getReader();
            // const decoder = new TextDecoder("utf-8");

            // let bot = null;
            // let buffer = "";

            // while (true) {
            //   const { value, done } = await reader.read();
            //   if (done) break;

            //   const chunk = decoder.decode(value, { stream: true });
            //   buffer += chunk;

            //   // Try to parse full events
            //   const lines = buffer.split("\n");
            //   buffer = ""; // Reset buffer for next round

            //   for (let line of lines) {
            //     if (line.startsWith("data: ")) {
            //       const jsonStr = line.slice(6);
            //       try {
            //         bot = JSON.parse(jsonStr);
            //         // process bot here
            //       } catch (e) {
            //         console.log("e: ", e);
            //         console.error("Invalid JSON chunk:", jsonStr);
            //         buffer += line + "\n"; // Keep unparsed lines for next read
            //       }
            //     }
            //   }
            // }

            // // After streaming ends
            // onBotResponse(bot);

            // if (bot?.correct === true) {
            //   setConversationHistory((x) => [
            //     ...x,
            //     {
            //       role: "bot",
            //       message: bot.response,
            //       correct: true,
            //     },
            //   ]);
            // } else {
            //   if (
            //     mode?.title == "Try Mode" &&
            //     bot?.correct_answer.length != 0
            //   ) {
            //     setCoachMessage(bot.correct_answer);
            //     setConversationHistory((x) => [
            //       ...x,
            //       {
            //         role: "bot",
            //         message: bot.correct_answer,
            //         correct: bot.correct,
            //       },
            //       {
            //         role: "bot",
            //         message: bot.response,
            //         correct: true,
            //       },
            //     ]);
            //   } else {
            //     setConversationHistory((x) => [
            //       ...x,
            //       {
            //         role: "bot",
            //         message: bot.response,
            //         correct: true,
            //       },
            //     ]);
            //   }
            // }
          } catch (err) {
            setMic(false);
            setIsThinking(false); // Hide thinking on error
            console.error("LLM chat error:", err);
          }
        })
        .catch((err) => {
          setMic(false);
          console.log("error: ", err);
        });
    } else {
      setConversationHistory((prev) => [
        ...prev,
        { role: "user", message: userMessage, correct: true },
      ]);

      const formData = new FormData();

      formData.append("id", sessionId);
      formData.append("name", avatar?.selected.name);
      formData.append("message", userMessage);

      try {
        // const res = await instance.post("/chat", formData, {
        //   headers: { "Content-type": "multipart/form-data" },
        // });

        const res = await axios.post(
          `${Baseurl}chat`,
          formData,
          {
            headers: { "Content-type": "multipart/form-data" },
          }
        );

        // const response = await fetch(
        //   `https://meta.novactech.in:7445/chat/stream?id=${res.data.id}&name=${avatar?.selected.name}`,
        //   {
        //     headers: {
        //       Authorization: `Bearer ` + localStorage.getItem("migoto-token"),
        //     },
        //   }
        // );

        const eventSource = new EventSource(
          `${Baseurl}chat/stream?id=${res.data.id}&name=${avatar?.selected.name}&voice_id=${voice?.voice_id}`,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("migoto-token")}`,
            },
          }
        );

        let bot = null;

        eventSource.onmessage = (event) => {
          try {
            bot = JSON.parse(event.data);
            // process bot here
          } catch (e) {
            console.log("e: ", e);
            console.error("Invalid JSON:", event.data);
          }
        };

        eventSource.onerror = (error) => {
          console.error("EventSource error:", error);
          eventSource.close();

          // Handle null bot response (stream error)
          if (!bot) {
            console.error("No bot response received from stream");
            setMic(false);
            return;
          }

          // After streaming ends
          onBotResponse(bot);

          if (bot?.correct === true) {
            setConversationHistory((x) => [
              ...x,
              {
                role: "bot",
                message: bot.response,
                stream: true,
                correct: true,
              },
            ]);
          } else {
            if (mode?.title == "Try Mode" && bot?.correct_answer.length != 0) {
              setCoachMessage(bot.correct_answer);
              setConversationHistory((x) => [
                ...x,
                {
                  role: "bot",
                  message: bot.correct_answer,
                  correct: bot.correct,
                },
                {
                  role: "bot",
                  message: bot.response,
                  stream: true,
                  correct: true,
                },
              ]);
            } else {
              setConversationHistory((x) => [
                ...x,
                {
                  role: "bot",
                  message: bot.response,
                  stream: true,
                  correct: true,
                },
              ]);
            }
          }
        };
      } catch (err) {
        setMic(false);
        setIsThinking(false); // Hide thinking on error
        console.error("LLM chat error:", err);
      }
    }
  };

  return { sendMessage };
};

export default useLLM;
