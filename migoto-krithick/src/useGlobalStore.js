import { create } from 'zustand';
    
export const useRenderStore = create((set) => ({
  isRender: false,
  setIsRender: (value) => set({ isRender: value }),

  isPath: "",
  setIsPath: (value) => set({ isPath: value }),
}));

const useGlobalStore = create((set) => ({
  myArray: [],
  addElement: (element) => set((state) => ({ myArray: [...state.myArray, element] })),
  removeElement: (index) =>
    set((state) => ({
      myArray: state.myArray.filter((_, i) => i !== index),
    })),
  updateElement: (index, newElement) =>
    set((state) => ({
      myArray: state.myArray.map((element, i) =>
        i === index ? newElement : element
      ),
    })),
  setArray: (newArray) => set({ myArray: newArray }),
  clearArray: () => set({ myArray: [] }),
}));

export default useGlobalStore;