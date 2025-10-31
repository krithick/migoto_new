import { useEffect, useState } from "react";
import { DynamicDataBinding } from "./DynamicDataBinding";
import instance from "../service";

const ReportCard = ({
  reportModelView,
  setReportModelView,
  scenarioName,
  viewModel,
  session_id,
  reload,
}) => {
  const [userReport, setUserReport] = useState(null);
  const [loading, setLoading] = useState(false); // State to track login errors

  useEffect(() => {
    setLoading(true);
    if (viewModel == "report") {
      fetchReportByUserConversation();
    } else {
      fetchPersonalizeReportByUserConversation();
    }
  }, [reload]);

  // Fetch User Report by the trail conversation
  const fetchReportByUserConversation = () => {
    setLoading(true); // Set loading state to true

    // Set headers for the API request
    const headers = {
      "Content-Type": "application/json",
      Authorization: `Bearer ` + localStorage.getItem("migoto-token"),
    };
    instance
      .get(`/sessionAnalyser/${session_id}`, { headers })
      .then((responce) => {
        console.log(responce)
        setUserReport(responce.data);
        setLoading(false);
      })
      .catch((error) => {
        console.log("Report API error: ", error);
        setLoading(false);
      });
  };

  // Fetch User Report by the trail conversation
  const fetchPersonalizeReportByUserConversation = () => {
    setLoading(true); // Set loading state to true

    const headers = {
      "Content-Type": "application/json",
      Authorization: `Bearer ${localStorage.getItem("migoto-token")}`,
    };

    // Call POST API to generate the report
    instance
      .post(`/chat/evaluate/${session_id}`, {}, { headers })
      .then((response) => {
        setUserReport(response.data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error generating report:", error);
        setLoading(false);
      });
  };

  return (
    <>
      {reportModelView && (
        <div className="absolute inset-0 h-[35.5rem] xl:h-[35.8rem] 2xl:h-[56.5rem]  w-screen mt-[58px] xl:mt-[44px] 2xl:mt-[58px]  z-20 flex justify-center items-center bg-[#00000065] backdrop-blur-[10px]">
          <div className="h-[40rem] xl:h-[30rem] 2xl:h-[36rem] w-[70rem] xl:w-[50rem] 2xl:w-[56rem] bg-[#FFFFFF] inset-shadow-[6px] rounded-[10px]">
            <div className="h-[2.5rem] w-full px-5 flex items-center">
              <div className="text-[#131F49] text-[16px] font-medium flex flex-auto">
                {scenarioName}
              </div>
              <div>
                <img
                  src="./close.svg"
                  loading="lazy"
                  alt="close"
                  className="cursor-pointer"
                  onClick={() => {
                    setReportModelView(!reportModelView);
                    setUserReport(null);
                  }}
                />
              </div>
            </div>
            <div
              className="h-[37rem] xl:h-[27rem] 2xl:h-[33rem] w-full flex px-3 py-3 gap-x-[5rem] xl:gap-x-[2rem] 2xl:gap-x-[3rem] bg-[#FFFFFF8F] rounded-[10px] overflow-y-auto  [&::-webkit-scrollbar]:w-1
                                [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-track]:rounded-full
                                [&::-webkit-scrollbar-thumb]:bg-[#3E4580] [&::-webkit-scrollbar-track]:bg-gray-400"
            >
              {!loading ? (
                <>
                  {viewModel == "report" ? (
                    <>
                      <div className="h-hull w-[20rem] xl:w-[16rem] 2xl:w-[20rem] rounded-[10px] bg-[#00000017] border border-white">
                        <div className="flex flex-col place-content-center items-center xl:h-[45%] 2xl:h-[50%]">
                          <span className="text-[12px] 2xl:text-[16px] font-semibold">
                            Overall Score
                          </span>
                          <div className="space-x-2">
                            <span className="text-[50px] xl:text-[40px] 2xl:text-[50px] font-bold text-[#131F49]">
                              {userReport &&
                                userReport?.user_communication_clarity
                                  .overall_score +
                                  userReport?.user_domain_knowledge
                                    .overall_score +
                                  userReport?.user_engagement_quality
                                    .overall_score +
                                  userReport?.user_learning_adaptation
                                    .overall_score +
                                  userReport?.user_problem_solving
                                    .overall_score}
                            </span>
                            <span className="text-[40px] xl:text-[30px] 2xl:text-[36px] 3xl:text-[8rem] font-bold text-[#131F49]">
                              / 100
                            </span>
                          </div>
                        </div>
                        <div
                          className="h-[50%] xl:h-[60%] 2xl:h-[50%] w-auto flex flex-col place-content-start items-center gap-1.5 2xl:gap-2.5 py-2 px-2 overflow-y-auto [&::-webkit-scrollbar]:w-1
                                [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-track]:rounded-full
                                [&::-webkit-scrollbar-thumb]:bg-[#3E4580] [&::-webkit-scrollbar-track]:bg-gray-400"
                        >
                          <div className="h-[45px] w-[15rem] xl:h-[35px] xl:w-[14rem] 2xl:h-[46px] 2xl:w-[18rem] flex items-center py-1 px-3 space-x-2.5 2xl:space-x-3.5 rounded-md bg-[#EFFFFF]">
                            <img
                              src="./report_lang.svg"
                              alt="report_lang"
                              className="h-[16px] xl:h-[14px] 2xl:h-[20px] w-[18px]"
                              loading="lazy"
                            />
                            <span className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#747474] flex flex-auto">
                              Communication clarity :
                            </span>
                            <div>
                              <span className="text-[15px] xl:text-[14px] 3xl:text-[20px] text-[#3A3A3A] font-semibold">
                                {
                                  userReport?.user_communication_clarity
                                    .overall_score
                                }
                              </span>
                              <span className="text-[12px] xl:text-[10px] 3xl:text-[20px] text-[#3A3A3A]">
                                /20
                              </span>
                            </div>
                          </div>
                          <div className="h-[45px] w-[15rem] xl:h-[35px] xl:w-[14rem] 2xl:h-[46px] 2xl:w-[18rem] flex items-center py-1 px-3 space-x-2.5 2xl:space-x-3.5 rounded-md bg-[#EFFFFF]">
                            <img
                              src="./product_knowladge.svg"
                              alt="product_knowladge"
                              className="h-[16px] xl:h-[14px] 2xl:h-[20px] w-[18px]"
                              loading="lazy"
                            />
                            <span className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#747474] flex flex-auto">
                              Domain knowledge :
                            </span>
                            <div>
                              <span className="text-[15px] xl:text-[14px] 3xl:text-[20px] text-[#3A3A3A] font-semibold">
                                {
                                  userReport?.user_domain_knowledge
                                    .overall_score
                                }
                              </span>
                              <span className="text-[12px] xl:text-[10px] 3xl:text-[20px] text-[#3A3A3A]">
                                /20
                              </span>
                            </div>
                          </div>
                          <div className="h-[45px] w-[15rem] xl:h-[35px] xl:w-[14rem] 2xl:h-[46px] 2xl:w-[18rem] flex items-center py-1 px-3 space-x-2.5 2xl:space-x-3.5 rounded-md bg-[#EFFFFF]">
                            <img
                              src="./trust.svg"
                              alt="trust"
                              className="h-[16px] xl:h-[14px] 2xl:h-[20px] w-[18px]"
                              loading="lazy"
                            />
                            <span className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#747474] flex flex-auto">
                              Engagement quality :
                            </span>
                            <div>
                              <span className="text-[15px] xl:text-[14px] 3xl:text-[20px] text-[#3A3A3A] font-semibold">
                                {
                                  userReport?.user_engagement_quality
                                    .overall_score
                                }
                              </span>
                              <span className="text-[12px] xl:text-[10px] 3xl:text-[20px] text-[#3A3A3A]">
                                /20
                              </span>
                            </div>
                          </div>
                          <div className="h-[45px] w-[15rem] xl:h-[35px] xl:w-[14rem] 2xl:h-[46px] 2xl:w-[18rem] flex items-center py-1 px-3 space-x-2.5 2xl:space-x-3.5 rounded-md bg-[#EFFFFF]">
                            <img
                              src="./process_clarity.svg"
                              alt="process_clarity"
                              className="h-[16px] xl:h-[14px] 2xl:h-[20px] w-[18px]"
                              loading="lazy"
                            />
                            <span className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#747474] flex flex-auto">
                              Learning Adaptation :
                            </span>
                            <div>
                              <span className="text-[15px] xl:text-[14px] 3xl:text-[20px] text-[#3A3A3A] font-semibold">
                                {
                                  userReport?.user_learning_adaptation
                                    .overall_score
                                }
                              </span>
                              <span className="text-[12px] xl:text-[10px] 3xl:text-[20px] text-[#3A3A3A]">
                                /20
                              </span>
                            </div>
                          </div>
                          <div className="h-[45px] w-[15rem] xl:h-[35px] xl:w-[14rem] 2xl:h-[46px] 2xl:w-[18rem] flex items-center py-1 px-3 space-x-2.5 2xl:space-x-3.5 rounded-md bg-[#EFFFFF]">
                            <img
                              src="./product_suitability.svg"
                              alt="product_suitability"
                              className="h-[16px] xl:h-[14px] 2xl:h-[20px] w-[18px]"
                              loading="lazy"
                            />
                            <span className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#747474] flex flex-auto">
                              Problem solving :
                            </span>
                            <div>
                              <span className="text-[15px] xl:text-[14px] 3xl:text-[20px] text-[#3A3A3A] font-semibold">
                                {userReport?.user_problem_solving.overall_score}
                              </span>
                              <span className="text-[12px] xl:text-[10px] 3xl:text-[20px] text-[#3A3A3A]">
                                /20
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="h-hull w-[48.5rem] xl:w-[31rem] 2xl:w-[80rem] rounded-[10px] pr-5 pl-6 py-5">
                        <div className="space-y-1 h-[8%]">
                          <span className="text-[16px] xl:text-[14px] 2xl:text-[18px] font-semibold">
                            Analysis & Feedback
                          </span>
                          <hr className="h-0.5 w-48 3xl:w-96 bg-[#131f4934]" />
                        </div>
                        <div
                          className="flex flex-col place-content-start px-3 py-0 space-y-3 xl:space-y-1 2xl:space-y-3 h-[94%] w-auto  overflow-y-auto  [&::-webkit-scrollbar]:w-1
                                [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-track]:rounded-full
                                [&::-webkit-scrollbar-thumb]:bg-[#3E4580] [&::-webkit-scrollbar-track]:bg-gray-400"
                        >
                          <div>
                            <span className="text-[14px] xl:text-[12px] 3xl:text-[24px] text-[#202020] font-medium">
                              Communication clarity:
                            </span>
                            <p className="leading-5 text-[12px] xl:text-[10px] 3xl:text-[20px] text-[#747474] px-3">
                              {userReport &&
                              userReport?.user_communication_clarity
                                .communication_challenges.length != 0 &&
                              userReport?.user_communication_clarity
                                .communication_strengths.length != 0 ? (
                                <>
                                  {userReport &&
                                    userReport?.user_communication_clarity.communication_challenges.map(
                                      (value) => <li key={value}>{value}</li>
                                    )}
                                  {userReport &&
                                    userReport?.user_communication_clarity.communication_strengths.map(
                                      (value) => <li key={value}>{value}</li>
                                    )}
                                </>
                              ) : (
                                <li>No comments</li>
                              )}
                            </p>
                          </div>
                          <div>
                            <span className="text-[14px] xl:text-[12px] 3xl:text-[24px] text-[#202020] font-medium">
                              Domain knowledge:
                            </span>
                            <p className="leading-5 text-[12px] xl:text-[10px] 3xl:text-[20px] text-[#747474] px-3">
                              {userReport &&
                              userReport?.user_domain_knowledge
                                .demonstrated_knowledge_areas.length != 0 &&
                              userReport?.user_domain_knowledge.knowledge_gaps
                                .length != 0 ? (
                                <>
                                  {userReport &&
                                    userReport?.user_domain_knowledge.demonstrated_knowledge_areas.map(
                                      (value) => <li key={value}>{value}</li>
                                    )}
                                  {userReport &&
                                    userReport?.user_domain_knowledge.knowledge_gaps.map(
                                      (value) => <li key={value}>{value}</li>
                                    )}
                                </>
                              ) : (
                                <li>No comments</li>
                              )}
                            </p>
                          </div>
                          <div>
                            <span className="text-[14px] xl:text-[12px] 3xl:text-[24px] text-[#202020] font-medium">
                              Engagement quality:
                            </span>
                            <p className="leading-5 text-[12px] xl:text-[10px] 3xl:text-[20px] text-[#747474] px-3">
                              {userReport &&
                              userReport?.user_engagement_quality
                                .engagement_patterns.length == 0 ? (
                                <li>No comments</li>
                              ) : (
                                <>
                                  {userReport?.user_engagement_quality.engagement_patterns.map(
                                    (value) => (
                                      <li key={value}>{value}</li>
                                    )
                                  )}
                                </>
                              )}
                            </p>
                          </div>
                          <div>
                            <span className="text-[14px] xl:text-[12px] 3xl:text-[24px] text-[#202020] font-medium">
                              Learning Adaptation:
                            </span>
                            <p className="leading-5 text-[12px] xl:text-[10px] 3xl:text-[20px] text-[#747474] px-3">
                              {userReport &&
                              userReport?.user_learning_adaptation
                                .learning_indicators.length == 0 ? (
                                <li>No comments</li>
                              ) : (
                                <>
                                  {userReport?.user_learning_adaptation.learning_indicators.map(
                                    (value) => (
                                      <li key={value}>{value}</li>
                                    )
                                  )}
                                </>
                              )}
                            </p>
                          </div>
                          <div>
                            <span className="text-[14px] xl:text-[12px] 3xl:text-[24px] text-[#202020] font-medium">
                              Problem solving:
                            </span>
                            <p className="leading-5 text-[12px] xl:text-[10px] 3xl:text-[20px] text-[#747474] px-3">
                              {userReport &&
                              userReport?.user_problem_solving
                                .problem_solving_strengths.length != 0 &&
                              userReport?.user_problem_solving
                                .problem_solving_weaknesses.length != 0 ? (
                                <>
                                  {userReport &&
                                    userReport?.user_problem_solving.problem_solving_strengths.map(
                                      (value) => <li key={value}>{value}</li>
                                    )}
                                  {userReport &&
                                    userReport?.user_problem_solving.problem_solving_weaknesses.map(
                                      (value) => <li key={value}>{value}</li>
                                    )}
                                </>
                              ) : (
                                <li>No comments</li>
                              )}
                            </p>
                          </div>
                          <div>
                            <span className="text-[14px] xl:text-[12px] 3xl:text-[24px] text-[#202020] font-medium">
                              Strength :
                            </span>
                            <p className="leading-5 text-[12px] xl:text-[10px] 3xl:text-[20px] text-[#747474] px-3 space-y-2">
                              {userReport &&
                              userReport?.overall_evaluation.user_strengths
                                .length == 0 ? (
                                <li>No comments</li>
                              ) : (
                                <>
                                  {userReport?.overall_evaluation.user_strengths.map(
                                    (value) => (
                                      <li key={value}>{value}</li>
                                    )
                                  )}
                                </>
                              )}
                            </p>
                          </div>
                          <div>
                            <span className="text-[14px] xl:text-[12px] 3xl:text-[24px] text-[#202020] font-medium">
                              Area of improvements :
                            </span>
                            <p className="leading-5 text-[12px] xl:text-[10px] 3xl:text-[20px] text-[#747474] px-3 space-y-2">
                              {userReport &&
                              userReport?.overall_evaluation
                                .user_improvement_areas.length == 0 ? (
                                <li>No comments</li>
                              ) : (
                                <>
                                  {userReport?.overall_evaluation.user_improvement_areas.map(
                                    (value) => (
                                      <li key={value}>{value}</li>
                                    )
                                  )}
                                </>
                              )}
                            </p>
                          </div>
                          <div>
                            <span className="text-[14px] xl:text-[12px] 3xl:text-[24px] text-[#202020] font-medium">
                              Recommendation :
                            </span>
                            <p className="leading-5 text-[12px] xl:text-[10px] 3xl:text-[20px] text-[#747474] px-3 space-y-2">
                              {userReport &&
                              userReport?.recommendations
                                .communication_improvement_recommendations
                                .length != 0 &&
                              userReport?.recommendations
                                .engagement_enhancement_recommendations
                                .length != 0 &&
                              userReport?.recommendations
                                .knowledge_development_recommendations.length !=
                                0 &&
                              userReport?.recommendations
                                .learning_strategy_recommendations.length !=
                                0 &&
                              userReport?.recommendations
                                .problem_solving_recommendations.length != 0 ? (
                                <>
                                  {userReport?.recommendations.communication_improvement_recommendations.map(
                                    (value, index) => (
                                      <li key={index}>{value}</li>
                                    )
                                  )}
                                  {userReport?.recommendations.engagement_enhancement_recommendations.map(
                                    (value, index) => (
                                      <li key={index}>{value}</li>
                                    )
                                  )}
                                  {userReport?.recommendations.knowledge_development_recommendations.map(
                                    (value, index) => (
                                      <li key={index}>{value}</li>
                                    )
                                  )}
                                  {userReport?.recommendations.learning_strategy_recommendations.map(
                                    (value, index) => (
                                      <li key={index}>{value}</li>
                                    )
                                  )}
                                  {userReport?.recommendations.problem_solving_recommendations.map(
                                    (value, index) => (
                                      <li key={index}>{value}</li>
                                    )
                                  )}
                                </>
                              ) : (
                                <li>No comments</li>
                              )}
                            </p>
                          </div>
                        </div>
                      </div>
                    </>
                  ) : (
                    <DynamicDataBinding data={userReport?.evaluation} />
                  )}
                </>
              ) : (
                <div className="h-full w-full flex px-3 py-3 gap-x-[5rem] xl:gap-x-[2rem] 2xl:gap-x-[3rem] bg-[#FFFFFF8F] rounded-[10px] justify-center items-center">
                  <div role="status">
                    <svg
                      aria-hidden="true"
                      className="w-8 h-8 text-gray-200 animate-spin dark:text-gray-600 fill-[#597bd1]"
                      viewBox="0 0 100 101"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
                        fill="currentColor"
                      />
                      <path
                        d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
                        fill="currentFill"
                      />
                    </svg>
                    <span className="sr-only">Loading...</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ReportCard;
