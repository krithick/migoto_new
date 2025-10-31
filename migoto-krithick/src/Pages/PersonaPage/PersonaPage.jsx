import React, { useState } from 'react'
import PersonaCreation from './PersonaCreation/PersonaCreation'
import PersonaBuilder from './PersonaBuilder/PersonaBuilder'

function PersonaPage() {
    let [currentPage,setCurrentPage] = useState("Persona Creation")
  return (
    <>
        {currentPage=="Persona Creation" && <PersonaCreation currentPage={currentPage} setCurrentPage={()=>{setCurrentPage("Persona Builder")}}  />}
        {currentPage=="Persona Builder"&& <PersonaBuilder currentPage={currentPage} setCurrentPage={()=>{setCurrentPage("Persona Creation")}}/>}
        
    </>
  )
}

export default PersonaPage