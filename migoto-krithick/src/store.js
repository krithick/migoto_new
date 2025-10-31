import { create } from "zustand";


export const useLOIData = create((set) => ({
  selectedData: {},

  setSelectedData: (type, data) =>
    set((state) => ({
      selectedData: {
        ...state.selectedData,
        [type]: data,
      },
    })),

    setClean: (x) => set(()=>({selectedData:x}))
}));

export const useModeData = create((set) => ({
  isOpen: {},

  setIsOpen: (mode, enable) =>
    set((state) => ({
      isOpen: {
        ...state.isOpen,
        [mode]: { enable },
      },
    })),

}));

export const useReportStore = create((set) => ({
  report: {state:false , id:null},
  setReport: (x) => set(() => ({ report: x })),
}));

// export const usePathLocation = create((set)=>({
//   pathLocation:[],
  
//   setPathLocation:(newdata)=>{
//     set((state)=>({
//       pathLocation:[
//         ...state.pathLocation,
//         newdata
//       ]
//     }))
//   }
// }))

export const usePreviewStore = create((set) => ({
  isPreview: { enable: false, msg: [], value: "",resolve: null },
  setIsPreview: (x) => set(() => ({ isPreview: x })),
}));

export const useLangStore = create((set) => ({
  localLang: [],
  setLocalLang: (x) => set(() => ({ localLang: x })),
}));

export const useUserPopupStore = create((set) => ({
  userPopup: { state: false, id: null },
  setUserPopup: (x) => set(() => ({ userPopup: x })),

  message:{ enable: false, msg: "", state: true },
  setMessage:(x)=> set(() => ({ message: x })),

}));

// export const useMiniLoaderStore = create((set) => ({
//   loading: false,
//   setLoading: (status) => set({ loading: status }),
//   }));
export const useLoaderStore = create((set) => ({
  loaderType: "none", // "none" | "mini" | "full"
  setLoader: (type) => set({ loaderType: type }),
}));
