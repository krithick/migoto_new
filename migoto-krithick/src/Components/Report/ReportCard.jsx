import React, { useEffect, useState } from "react";
import styles from "./ReportCard.module.css";
import axios from "../../service";
import { useReportStore, useUserPopupStore } from "../../store";
import LoadingSpinner from "../Loaders/LoadingSpinner";
import LoaderFull from "../Loaders/LoaderFull";
import Loader from "../Loader/Loader";

const ReportCard = () => {
  const [userReport, setUserReport] = useState();
  const [conversationHistory, setConversationHistory] = useState();
  const [loading, setLoading] = useState(false);
  let { report, setReport } = useReportStore();
  const { message, setMessage } = useUserPopupStore();

  const arr = [
    {
      name: "Domain knowledge",
      value: userReport?.user_domain_knowledge?.overall_score,
    },
    {
      name: "Communication clarity",
      value: userReport?.user_communication_clarity?.overall_score,
    },
    {
      name: "Engagement Quality",
      value: userReport?.user_engagement_quality?.overall_score,
    },
    {
      name: "Learning Adaptation",
      value: userReport?.user_learning_adaptation?.overall_score,
    },
    {
      name: "Problem solving",
      value: userReport?.user_problem_solving?.overall_score,
    },
  ];

  const fetchReportFromSessionId = async () => {
    const token = localStorage.getItem("migoto-cms-token");
    const headers = {
      "Content-Type": "multipart/form-data", // Let browser set boundary
      authorization: token,
    };

    try {
      setLoading(true);
      const res = await axios.get(
        `sessionAnalyser/${report?.id}`,
        { headers }
      );
      const convoData = await axios.get(
        `chat/history/${report?.id}`,
        { headers }
      );
      setUserReport(res.data);
      setConversationHistory(convoData.data);
      setLoading(false)

    } catch (e) {
      console.log("Unable to fetch report data", e);
      setLoading(false)
      setMessage({
        enable: true,
        msg: "Something Went Wrong",
        state: false,
      })

    }
  };

  useEffect(() => {
    fetchReportFromSessionId();
  }, []);

  return (
    <>
    {/* {loading &&<LoaderFull />} */}
    <div className={styles.overlay}>
      <div className={styles.modal}>
        <div className={styles.bg}>
          <div className={styles.pinkContainer}>
            <div className={styles.pink}></div>
          </div>
          <div className={styles.blueContainer}>
            <div className={styles.blue}></div>
          </div>
        </div>
        {/* Header */}
        <div className={styles.header}>
          <h2 className={styles.headerTitle}>Report Card</h2>
        </div>

        {/* Content */}
        <div className={styles.content}>
          {/* Left */}
          <div className={styles.leftPanel}>
            <div className={styles.scoreBox}>
              <div className={styles.scoreContainer}>
                <p className={styles.scoreLabel}>OVERALL SCORE</p>
                <p className={styles.scoreValue}>
                  {userReport &&
                    userReport?.user_communication_clarity?.overall_score +
                      userReport?.user_domain_knowledge?.overall_score +
                      userReport?.user_engagement_quality?.overall_score +
                      userReport?.user_learning_adaptation?.overall_score +
                      userReport?.user_problem_solving?.overall_score}
                </p>
              </div>
              <div className={styles.metrics}>
                <div className={styles.evenScores}>
                  {arr?.map((item, i) => (
                    <>
                      {i % 2 === 0 && (
                        <div key={item?.name} className={styles.metricItem}>
                          <span>{item?.name}:</span>
                          <span className={styles.metricValue}>
                            {item?.value}
                          </span>
                        </div>
                      )}
                    </>
                  ))}{" "}
                </div>{" "}
                <div className={styles.oddScores}>
                  {arr?.map((item, i) => (
                    <>
                      {i % 2 !== 0 && (
                        <div key={item?.name} className={styles.metricItem}>
                          <span>{item?.name}:</span>
                          <span className={styles.metricValue}>
                            {item?.value}
                          </span>
                        </div>
                      )}
                    </>
                  ))}
                </div>
              </div>
            </div>

            <div className={styles.analysis}>
              <h3 className={styles.sectionTitle}>Analysis & Feedback</h3>
              <p className={styles.subTitle}>Communication Improvement :</p>
              {userReport &&
                userReport.recommendations?.communication_improvement_recommendations?.map(
                  (val, i) => {
                    return <li className={styles.text}>{val}</li>;
                  }
                )}
              <p className={styles.subTitle}>Engagement Enhancement :</p>
              {userReport &&
                userReport?.recommendations?.engagement_enhancement_recommendations?.map(
                  (val, i) => {
                    return <li className={styles.text}>{val}</li>;
                  }
                )}
              <p className={styles.subTitle}>Knowledge Development :</p>
              {userReport &&
                userReport?.recommendations?.knowledge_development_recommendations?.map(
                  (val, i) => {
                    return <li className={styles.text}>{val}</li>;
                  }
                )}
              <p className={styles.subTitle}>Learning Strategy :</p>
              {userReport &&
                userReport?.recommendations?.learning_strategy_recommendations?.map(
                  (val, i) => {
                    return <li className={styles.text}>{val}</li>;
                  }
                )}
              <p className={styles.subTitle}>Problem Solving :</p>
              {userReport &&
                userReport?.recommendations?.problem_solving_recommendations?.map(
                  (val, i) => {
                    return <li className={styles.text}>{val}</li>;
                  }
                )}
            </div>
          </div>

          {/* Right */}
          <div className={styles.rightPanel}>
            <div className={styles.chatHeader}>Conversation</div>
            <div className={styles.messagesContainer}>
              {conversationHistory &&
                conversationHistory.conversation_history.map((msg, i) => (
                  <div
                    key={i}
                    className={`${styles.message} ${
                      i % 2 !== 0 ? styles.botMessage : styles.userMessage
                    }`}
                  >
                    <div className={styles.messageContent}>
                      <span className={styles.sender}>
                        {i % 2 == 0 ? msg.role : msg.role}
                      </span>
                      <p className={styles.chat}>{msg.content}</p>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className={styles.footer}>
          <button
            className={styles.cancelBtn}
            onClick={() => {setReport({ state: false, id: null })}}
          >
            Close
          </button>
          {/* <button className={styles.downloadBtn}>Download Report</button> */}
        </div>
      </div>
    </div>
    </>
  );
};

export default ReportCard;
