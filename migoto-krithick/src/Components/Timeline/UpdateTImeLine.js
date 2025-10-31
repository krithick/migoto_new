import { useLOIData } from "../../store";

export function UpdateTimeline(itemId, updates,setSelectedData) {
    
    // 1. Read localStorage
    const raw = localStorage.getItem("TLData");
    if (!raw) return;
  
    let data;
    try {
      data = JSON.parse(raw);
    } catch (e) {
      console.error("Invalid JSON in localStorage:", e);
      return;
    }
    
    // 3. Map & update the item with matching id
    const updatedArray = data.map((item) =>
        item.id === itemId ? { ...item, ...updates } : item
      );
      
    // 4. Replace the route with updated array
    localStorage.setItem("TLData", JSON.stringify(updatedArray));
    setSelectedData("TLRenderer", (prev) => (prev || 1) + 1);  
  }
  