import { DynamicDataBinding } from "./DynamicDataBinding";

const ViewReportModel = ({
  reportModelView,
  setReportModelView,
  selected,
  setSelected,
  scenarioName,
  viewModel,
}) => {
  console.log("Selected ==> ", selected);

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
                  loading="lazy"
                  src="./close.svg"
                  alt="close"
                  className="cursor-pointer"
                  onClick={() => {
                    setReportModelView(!reportModelView);
                    setSelected(null);
                  }}
                />
              </div>
            </div>
            <div
              className="h-[37rem] xl:h-[27rem] 2xl:h-[33rem] w-full flex px-3 py-3 gap-x-[5rem] xl:gap-x-[2rem] 2xl:gap-x-[3rem] bg-[#FFFFFF8F] rounded-[10px] overflow-y-auto  [&::-webkit-scrollbar]:w-1
                                [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-track]:rounded-full
                                [&::-webkit-scrollbar-thumb]:bg-[#3E4580] [&::-webkit-scrollbar-track]:bg-gray-400"
            >
              {viewModel == "report" ? (
                <>
                  <div className="h-hull w-[20rem] xl:w-[16rem] 2xl:w-[20rem] rounded-[10px] bg-[#00000017] border border-white">
                    <div className="flex flex-col place-content-center items-center xl:h-[45%] 2xl:h-[50%]">
                      <span className="text-[12px] 2xl:text-[16px] font-semibold">
                        Overall Score
                      </span>
                      <div className="space-x-2">
                        <span className="text-[50px] xl:text-[40px] 2xl:text-[50px] font-bold text-[#131F49]">
                          {selected &&
                            selected?.analysis.user_communication_clarity
                              .overall_score +
                              selected?.analysis.user_domain_knowledge
                                .overall_score +
                              selected?.analysis.user_engagement_quality
                                .overall_score +
                              selected?.analysis.user_learning_adaptation
                                .overall_score +
                              selected?.analysis.user_problem_solving
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
                          loading="lazy"
                          alt="report_lang"
                          className="h-[16px] xl:h-[14px] 2xl:h-[20px] w-[18px]"
                        />
                        <span className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#747474] flex flex-auto">
                          Communication clarity :
                        </span>
                        <div>
                          <span className="text-[15px] xl:text-[14px] 3xl:text-[20px] text-[#3A3A3A] font-semibold">
                            {
                              selected?.analysis.user_communication_clarity
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
                          loading="lazy"
                          alt="product_knowladge"
                          className="h-[16px] xl:h-[14px] 2xl:h-[20px] w-[18px]"
                        />
                        <span className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#747474] flex flex-auto">
                          Domain knowledge :
                        </span>
                        <div>
                          <span className="text-[15px] xl:text-[14px] 3xl:text-[20px] text-[#3A3A3A] font-semibold">
                            {
                              selected?.analysis.user_domain_knowledge
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
                          loading="lazy"
                          alt="trust"
                          className="h-[16px] xl:h-[14px] 2xl:h-[20px] w-[18px]"
                        />
                        <span className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#747474] flex flex-auto">
                          Engagement quality :
                        </span>
                        <div>
                          <span className="text-[15px] xl:text-[14px] 3xl:text-[20px] text-[#3A3A3A] font-semibold">
                            {
                              selected?.analysis.user_engagement_quality
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
                          loading="lazy"
                          alt="process_clarity"
                          className="h-[16px] xl:h-[14px] 2xl:h-[20px] w-[18px]"
                        />
                        <span className="text-[12px] xl:text-[10px] 2xl:text-[12px] text-[#747474] flex flex-auto">
                          Learning Adaptation :
                        </span>
                        <div>
                          <span className="text-[15px] xl:text-[14px] 3xl:text-[20px] text-[#3A3A3A] font-semibold">
                            {
                              selected?.analysis.user_learning_adaptation
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
                            {
                              selected?.analysis.user_problem_solving
                                .overall_score
                            }
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
                          {selected &&
                          selected?.analysis.user_communication_clarity
                            .communication_challenges.length != 0 &&
                          selected?.analysis.user_communication_clarity
                            .communication_strengths.length != 0 ? (
                            <>
                              {selected &&
                                selected?.analysis.user_communication_clarity.communication_challenges.map(
                                  (value) => <li key={value}>{value}</li>
                                )}
                              {selected &&
                                selected?.analysis.user_communication_clarity.communication_strengths.map(
                                  (value) => <li key={value}>{value}</li>
                                )}
                            </>
                          ) : (
                            <p>No commends</p>
                          )}
                        </p>
                      </div>
                      <div>
                        <span className="text-[14px] xl:text-[12px] 3xl:text-[24px] text-[#202020] font-medium">
                          Domain knowledge:
                        </span>
                        <p className="leading-5 text-[12px] xl:text-[10px] 3xl:text-[20px] text-[#747474] px-3">
                          {selected &&
                          selected?.analysis.user_domain_knowledge
                            .demonstrated_knowledge_areas.length != 0 &&
                          selected?.analysis.user_domain_knowledge
                            .knowledge_gaps.length != 0 ? (
                            <>
                              {selected &&
                                selected?.analysis.user_domain_knowledge.demonstrated_knowledge_areas.map(
                                  (value) => <li key={value}>{value}</li>
                                )}
                              {selected &&
                                selected?.analysis.user_domain_knowledge.knowledge_gaps.map(
                                  (value) => <li key={value}>{value}</li>
                                )}
                            </>
                          ) : (
                            <p>No commends</p>
                          )}
                        </p>
                      </div>
                      <div>
                        <span className="text-[14px] xl:text-[12px] 3xl:text-[24px] text-[#202020] font-medium">
                          Engagement quality:
                        </span>
                        <p className="leading-5 text-[12px] xl:text-[10px] 3xl:text-[20px] text-[#747474] px-3">
                          {selected &&
                          selected?.analysis.user_engagement_quality
                            .engagement_patterns.length == 0 ? (
                            <li>No commends</li>
                          ) : (
                            <>
                              {selected?.analysis.user_engagement_quality.engagement_patterns.map(
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
                          {selected &&
                          selected?.analysis.user_learning_adaptation
                            .learning_indicators.length == 0 ? (
                            <li>No commends</li>
                          ) : (
                            <>
                              {selected?.analysis.user_learning_adaptation.learning_indicators.map(
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
                          {selected &&
                          selected?.analysis.user_problem_solving
                            .problem_solving_strengths.length != 0 &&
                          selected?.analysis.user_problem_solving
                            .problem_solving_weaknesses.length != 0 ? (
                            <>
                              {selected &&
                                selected?.analysis.user_problem_solving.problem_solving_strengths.map(
                                  (value) => <li key={value}>{value}</li>
                                )}
                              {selected &&
                                selected?.analysis.user_problem_solving.problem_solving_weaknesses.map(
                                  (value) => <li key={value}>{value}</li>
                                )}
                            </>
                          ) : (
                            <p>No commends</p>
                          )}
                        </p>
                      </div>
                      <div>
                        <span className="text-[14px] xl:text-[12px] 3xl:text-[24px] text-[#202020] font-medium">
                          Strength :
                        </span>
                        <p className="leading-5 text-[12px] xl:text-[10px] 3xl:text-[20px] text-[#747474] px-3 space-y-2">
                          {selected &&
                          selected?.analysis.overall_evaluation.user_strengths
                            .length == 0 ? (
                            <li>No commends</li>
                          ) : (
                            <>
                              {selected?.analysis.overall_evaluation.user_strengths.map(
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
                          {selected &&
                          selected?.analysis.overall_evaluation
                            .user_improvement_areas.length == 0 ? (
                            <li>No commends</li>
                          ) : (
                            <>
                              {selected?.analysis.overall_evaluation.user_improvement_areas.map(
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
                          {selected &&
                          selected?.analysis.recommendations
                            .communication_improvement_recommendations.length !=
                            0 &&
                          selected?.analysis.recommendations
                            .engagement_enhancement_recommendations.length !=
                            0 &&
                          selected?.analysis.recommendations
                            .knowledge_development_recommendations.length !=
                            0 &&
                          selected?.analysis.recommendations
                            .learning_strategy_recommendations.length != 0 &&
                          selected?.analysis.recommendations
                            .problem_solving_recommendations.length != 0 ? (
                            <>
                              {selected?.analysis.recommendations.communication_improvement_recommendations.map(
                                (value, index) => (
                                  <li key={index}>{value}</li>
                                )
                              )}
                              {selected?.analysis.recommendations.engagement_enhancement_recommendations.map(
                                (value, index) => (
                                  <li key={index}>{value}</li>
                                )
                              )}
                              {selected?.analysis.recommendations.knowledge_development_recommendations.map(
                                (value, index) => (
                                  <li key={index}>{value}</li>
                                )
                              )}
                              {selected?.analysis.recommendations.learning_strategy_recommendations.map(
                                (value, index) => (
                                  <li key={index}>{value}</li>
                                )
                              )}
                              {selected?.analysis.recommendations.problem_solving_recommendations.map(
                                (value, index) => (
                                  <li key={index}>{value}</li>
                                )
                              )}
                            </>
                          ) : (
                            <li>No commends</li>
                          )}
                        </p>
                      </div>
                    </div>
                  </div>
                </>
              ) : (
                <DynamicDataBinding data={selected?.evaluation} />
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ViewReportModel;
