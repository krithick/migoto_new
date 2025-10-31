import React, { useState } from 'react'
import AiScenarioBuilder from './AiScenarioBuilder'
import EditDocument from './EditDocument/EditDocument'

function AIScenario() {
    let [currentPage, setCurrentPage] = useState("AiScenarioBuilder");
  return (
    <>
        {currentPage=="AiScenarioBuilder"&&<AiScenarioBuilder currentPage={currentPage} setCurrentPage={(item)=>{setCurrentPage(item)}} />}
        {currentPage=="editDocument"&&<EditDocument currentPage={currentPage} setCurrentPage={()=>{setCurrentPage("editDocument")}} />}
    </>
  )
} 

export default AIScenario