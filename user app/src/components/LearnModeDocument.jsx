import React, { useEffect, useState } from "react";
import instance from "../service";
import PDFReader from "./PDFReader";

const LearnModeDocument = () => {
  const [selectedPDF, setSelectedPDF] = useState(null);
  const [pdfDetails, setPDFDetails] = useState([]);
  useEffect(() => {
    fetchAssignedLearnModeVideoDetails();
  }, []);
  // fetch assigned avatar details
  const fetchAssignedLearnModeVideoDetails = async () => {
    try {
      let avatarIntraction;
      if (localStorage.getItem("migoto-mode") != null) {
        avatarIntraction = JSON.parse(localStorage.getItem("migoto-mode"));
      }
      // Fetch and load token
      const headers = {
        "Content-Type": "application/json",
        Authorization: `Bearer ` + localStorage.getItem("migoto-token"),
      };
      instance
        .get(
          `/avatar-interactions/${avatarIntraction?.avatar_interaction}?expand=assigned_documents
`,
          {
            headers,
          }
        )
        .then((response) => {
          setPDFDetails(response.data.assigned_documents);
          setSelectedPDF(response.data.assigned_documents[0]);
        })
        .catch((error) => {
          console.error("Error fetching learning document's:", error);
        });
    } catch (error) {
      console.error("Error fetching learning document's:", error);
    }
  };
  return (
    <div className="h-[40.8rem] xl:h-[24.5rem] 2xl:h-[39rem] w-full px-[3.5rem] xl:px-[2rem] 2xl:px-[3.5rem] py-[15px] xl:py-[10px] 2xl:py-[15px]">
      {pdfDetails && pdfDetails?.length == 0 ? (
        <>
          <div className="h-full w-full flex px-3 py-3 gap-x-[5rem] xl:gap-x-[2rem] 2xl:gap-x-[3rem] bg-[#FFFFFF8F] rounded-[10px] justify-center items-center">
            No available PDF, please contact to admin
          </div>
        </>
      ) : (
        <div className="h-full w-full flex justify-center gap-x-[5rem] xl:gap-x-[1rem] 2xl:gap-x-[3rem]">
          <div className="h-[35rem] xl:h-[23rem] 2xl:h-[35.5rem] w-[25rem] xl:w-[14rem] 2xl:w-[20rem] bg-[#FFFFFF8F] rounded-[10px]">
            <div className="h-[3rem] w-full flex items-center px-3 text-[#FFFFFF] text-[14px] rounded-t-[10px] bg-[#131F49]">
              Document
            </div>
            <div className="h-[34rem] xl:h-[21rem] 2xl:h-[32rem] w-full pr-2 py-2 space-y-3 ">
              <div className="h-full w-full px-2 space-y-2 overflow-y-auto [&::-webkit-scrollbar]:w-[3px] [&::-webkit-scrollbar-track]:bg-[#d3e4ebef] [&::-webkit-scrollbar-thumb]:bg-[#3E4580] [&::-webkit-scrollbar-track]:rounded-[22px] [&::-webkit-scrollbar-thumb]:rounded-[22px]">
                {pdfDetails &&
                  pdfDetails.map((value, index) => (
                    <div
                      key={index}
                      className="[6rem] w-full p-2 space-x-2 flex items-center rounded-[10px] bg-[#FFFFFF] border border-[#7070706E]"
                    >
                      <img
                        loading="lazy"
                        src={
                          selectedPDF?.id == value.id
                            ? "./LearnPDF_select.svg"
                            : "./LearnPDF.svg"
                        }
                        alt={value?.title}
                        className="h-[3rem] w-auto object-contain"
                      />
                      <div className="space-y-1.5 w-full">
                        <p className="text-[#131F49] text-[12px] xl:text-[10px] font-medium">
                          {value?.title}
                        </p>
                        <p className="text-[#707070] text-[10px] xl:text-[8px] font-normal line-clamp-2">
                          {value?.description}
                        </p>
                        <div
                          onClick={() => setSelectedPDF(value)}
                          className="flex justify-end text-[#F68D1E] text-[12px] xl:text-[10px] underline cursor-pointer"
                        >
                          {selectedPDF?.id == value.id ? "Opened" : "Open"}
                        </div>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          </div>
          <div className="h-[35rem] xl:h-[23rem] 2xl:h-[35.5rem] w-[25rem] xl:w-[40rem] 2xl:w-[55rem] bg-[#FFFFFF8F] rounded-[10px]">
            <div className="h-[3rem] w-full flex items-center px-3 text-[#FFFFFF] text-[14px] rounded-t-[10px] bg-[#131F49]">
              Document Title
            </div>
            <div className="h-[34rem] xl:h-[10rem] 2xl:h-[33rem] w-full pr-2 py-2 space-y-3 ">
              <div className="text-[#131F49] text-[14px] xl:text-[12px] 2xl:text-[14px] px-5">
                {selectedPDF?.title}
              </div>
              <div className="flex justify-center h-[31rem] xl:h-[17.5rem] 2xl:h-[30rem] rounded-b-[10px] w-full overflow-y-auto [&::-webkit-scrollbar]:w-[6px] [&::-webkit-scrollbar-track]:bg-[#d3e4ebef] [&::-webkit-scrollbar-thumb]:bg-[#3E4580] [&::-webkit-scrollbar-track]:rounded-[22px] [&::-webkit-scrollbar-thumb]:rounded-[22px] ">
                {selectedPDF && <PDFReader pdf={selectedPDF.file_url} />}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LearnModeDocument;
