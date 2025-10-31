// ✅ Safe setter for sessionStorage
  export function setSessionStorage(key, value) {
    try {
      // If value is object or array → stringify
      if (typeof value === "object") {
        sessionStorage.setItem(key, JSON.stringify(value));
      } else {
        sessionStorage.setItem(key, value);
      }
    } catch (e) {
      console.error("Error saving to sessionStorage", e);
    }
  }

  // ✅ Getter that parses JSON if needed
  export function getSessionStorage(key) {
    try {
      const value = sessionStorage.getItem(key);
      if (value === null) return null;
  
      // Try parsing JSON safely
      try {
        const parsed = JSON.parse(value);
  
        // If parsed is an array or object, return it
        if (Array.isArray(parsed) || typeof parsed === "object") {
          return parsed;
        }
  
        // If it's a primitive (number, string, boolean), return as is
        return parsed;
      } catch {
        // If not JSON, just return the string
        return value;
      }
    } catch (e) {
      console.error("Error reading from sessionStorage", e);
      return null;
    }
  }
  

  // ✅ Clear a specific key from sessionStorage
export function clearSessionStorage(key) {
  try {
    if (key && sessionStorage.getItem(key) !== null) {
      sessionStorage.removeItem(key);
      console.log(`SessionStorage key "${key}" cleared`);
    } 
  } catch (e) {
    console.error("Error clearing from sessionStorage", e);
  }
}

export function clearScenarioData() {
  try {
      sessionStorage.removeItem("Document");
      sessionStorage.removeItem("Layout");
      sessionStorage.removeItem("ListOfAvatar");
      sessionStorage.removeItem("PersonaSelection");
      sessionStorage.removeItem("Video");
      sessionStorage.removeItem("avatarSelection");
      sessionStorage.removeItem("scenarioData");
      sessionStorage.removeItem("personaName");
      sessionStorage.removeItem("scenarioResponse");
      sessionStorage.removeItem("template_id");
      sessionStorage.setItem("personaLimit",0);
  } catch (e) {
    console.error("Error clearing from sessionStorage", e);
  }
}
export function clearAllData() {
  try {
      sessionStorage.removeItem("Document");
      sessionStorage.removeItem("Layout");
      sessionStorage.removeItem("ListOfAvatar");
      sessionStorage.removeItem("PersonaSelection");
      sessionStorage.removeItem("Video");
      sessionStorage.removeItem("avatarSelection");
      sessionStorage.removeItem("scenarioData");
      sessionStorage.removeItem("personaName");
      sessionStorage.removeItem("scenarioResponse");
      sessionStorage.removeItem("template_id");
      sessionStorage.removeItem("courseId");
      sessionStorage.removeItem("createdUser");
      sessionStorage.removeItem("moduleId");
      sessionStorage.setItem("personaLimit",0);
  } catch (e) {
    console.error("Error clearing from sessionStorage", e);
  }
}
export function clearCourseData() {
  try {
      sessionStorage.removeItem("PersonaSelection");
      sessionStorage.removeItem("personaName");
      sessionStorage.removeItem("template_id");
      sessionStorage.removeItem("TryModeAvatar");
      sessionStorage.removeItem("LearnModeAvatar");
      sessionStorage.removeItem("AssessModeAvatar");
      sessionStorage.removeItem("LearnModeAvatarInteractionId");
      sessionStorage.removeItem("TryModeAvatarInteractionId");
      sessionStorage.removeItem("AssessModeAvatarInteractionId");
      sessionStorage.removeItem("List Of Courses");
      sessionStorage.removeItem("List Of Scenario");
      sessionStorage.removeItem("List Of Modules");
      sessionStorage.removeItem("showModule");
      sessionStorage.removeItem("showCourse");
      sessionStorage.removeItem("showScenario");
      sessionStorage.removeItem("showAvatarInteraction");
      sessionStorage.removeItem("modifyAvaInterIn");
      sessionStorage.setItem("personaLimit",0);
      
  } catch (e) {
    console.error("Error clearing from sessionStorage", e);
  }
}

// Helper to add unique items to session storage array
export function addUniqueToSessionArray(key, newItem, idField = 'id') {
  try {
    const existingArray = JSON.parse(sessionStorage.getItem(key)) || [];
    
    // Check if item already exists
    const exists = existingArray.some(item => item[idField] === newItem[idField]);
    
    if (!exists) {
      existingArray.push(newItem);
      sessionStorage.setItem(key, JSON.stringify(existingArray));
    }
    
    return existingArray;
  } catch (e) {
    console.error("Error adding unique item to session storage", e);
    return [];
  }
}