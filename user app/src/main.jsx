// Importing necessary libraries and components
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router";
import "./index.css"; // Importing global CSS styles
import Login from "./Login.jsx"; // Importing the Login component
import AssignedCourses from "./AssignedCourses.jsx"; // Importing the AssignedCourses component
import AssignModule from "./AssignedModules.jsx"; // Importing the AssignModule component
import AssignedScenarios from "./AssignedScenarios.jsx"; // Importing the AssignedScenarios component
import AssignedMode from "./AssignedMode.jsx"; // Importing the AssignedMode component
// import AssignedPersona from "./AssignedPersona.jsx"; // Importing the AssignedPersona component
import AssignedAvatar from "./AssignedAvatar.jsx"; // Importing the AssignedAvatar component
import AssignedLanguage from "./AssignedLanguage.jsx"; // Importing the AssignedLanguage component
import AssignedBotVoice from "./AssignedBotVoice.jsx"; // Importing the AssignedBotVoice component
import AssignedEnvironment from "./AssignedEnvironment.jsx"; // Importing the AssignedEnvironment component
import LearnModeConversation from "./LearnModeConversation.jsx"; // Importing the LearnModeConversation component
import Confirmation from "./Confirmation.jsx"; // Importing the Confirmation component
import { Toaster } from "react-hot-toast"; // Importing the Toaster component for notifications
// import Conversation from "./Conversation.jsx"; // Importing the Conversation component
import Report from "./Report.jsx"; // Importing the Report component
import ConversationHook from "./ConversationHook.jsx"; // Importing the Main conversation hook component
import ViewReport from "./viewReport.jsx";
import NotFoundPageOnMobile from "./NotFoundPageOnMobile.jsx";
import PersonalizedReport from "./personalizedReport.jsx";

// Rendering the root React component
createRoot(document.getElementById("root")).render(
  <div className="h-screen w-screen fixed">
    {/* Toast notifications */}
    <Toaster />

    {/* Top background blur effect */}
    <div className="absolute inset-x-0 top-0 flex h-80 w-screen items-end justify-end pr-[15rem] 2xl:pt-[1rem]">
      <div className="flex h-full w-[55rem]">
        <div className="h-96 w-full bg-[#0085DB] opacity-[0.25] blur-[75px] [clip-path:ellipse(50%_45%_at_50%_50%)]"></div>
      </div>
    </div>

    {/* Bottom background blur effect */}
    <div className="absolute inset-x-0 bottom-0 flex h-[50%] w-screen justify-center">
      <div className="flex h-full w-full">
        <div className="h-[30rem] xl:h-[20rem] 2xl:h-[30rem] w-full bg-[#0085DB] opacity-[0.25] blur-[75px] [clip-path:ellipse(70%_80%_at_80%_90%)]"></div>
      </div>
    </div>

    {/* Left background blur effect */}
    <div className="absolute top-0 left-0 flex h-screen w-screen">
      <div className="flex h-[95%] w-[50%]">
        <div className="h-full w-full bg-[#7900D5] opacity-[0.25] blur-[75px] [clip-path:ellipse(75%_80%_at_25%_10%)]"></div>
      </div>
    </div>

    {/* Right background blur effect */}
    <div className="absolute inset-y-0 right-0 flex h-screen w-screen justify-end">
      <div className="flex h-full w-[25%]">
        <div className="h-full w-full bg-[#7900D5] opacity-[0.25] blur-[75px] [clip-path:ellipse(60%_40%_at_75%_50%)]"></div>
      </div>
    </div>

    {/* React Router for handling routes */}
    <BrowserRouter basename="/migoto-ai">
      <Routes>
        {/* Route for the login page */}
        <Route path="*" element={<NotFoundPageOnMobile />} />
        <Route path="/" element={<Login />} />

        {/* Routes for assigned components */}
        <Route path="/assigned-course" element={<AssignedCourses />} />
        <Route path="/assigned-module" element={<AssignModule />} />
        <Route path="/assigned-scenario" element={<AssignedScenarios />} />
        <Route path="/assigned-mode" element={<AssignedMode />} />
        <Route path="/assigned-avatar" element={<AssignedAvatar />} />
        <Route path="/assigned-language" element={<AssignedLanguage />} />
        <Route path="/assigned-botvoice" element={<AssignedBotVoice />} />
        <Route path="/assigned-environment" element={<AssignedEnvironment />} />
        <Route path="/confirmation" element={<Confirmation />} />
        <Route path="/personalized-report" element={<PersonalizedReport />} />
        {/* Routes for learning modes */}
        <Route path="/learn-mode-bot" element={<LearnModeConversation />} />

        {/* Route for the conversation page */}
        <Route path="/conversation" element={<ConversationHook />} />

        {/* Route for the report page */}
        <Route path="/report" element={<Report />} />
        <Route path="/view-report" element={<ViewReport />} />
      </Routes>
    </BrowserRouter>
  </div>
);
