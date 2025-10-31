// import Axios from "axios";
// import { useLoaderStore } from "./store";

// const site = "http://172.23.198.45:9000/";
// // const site = "https://meta.novactech.in:6445";
// // Get Token
// let Token = localStorage.getItem("migoto-cms-token") || "";
// let Auth;
// if (Token == "") {
//   Auth = null;
// } else {
//   Auth = Token;
// }

// // Base function
// const instance = Axios.create({
//   baseURL: site,
//   headers: {
//     "Content-Type": "application/json",
//     authorization: Auth,
//   },
// });
// const loaderStore = useLoaderStore.getState();

// // Request function 
// instance.interceptors.request.use(
//   (request) => {
//     const token = localStorage.getItem("migoto-cms-token");
//     if (token) {
//       request.headers.authorization = token;
//     }
//     loaderStore.setLoading(true);
//     return request;
//   },
//   (error) => {
//     loaderStore.setLoading(false);
//     return Promise.reject(error);
//   }
// );
// // Response function
// instance.interceptors.response.use(
//   (response) => {
//     loaderStore.setLoading(false);
//     return response;
//   },
//   (error) => {
//     loaderStore.setLoading(false);
//     return Promise.reject(error);
//   }
// );
// export default instance;

import Axios from "axios";
import { useLoaderStore } from "./store";
import { useNavigate } from "react-router-dom";

// const site = "http://172.23.198.45:9000/";
const site = "http://172.23.198.149:9000/";
// const site = "https://meta.novactech.in:5885";
// const site = "https://meta.novactech.in:6445";

// Get Token
let Token = localStorage.getItem("migoto-cms-token") || "";
let Auth = Token ? Token : null;


// Base function
const instance = Axios.create({
  baseURL: site,
  headers: {
    "Content-Type": "application/json",
    authorization: Auth,
  },
});

const loaderStore = useLoaderStore.getState();
// let activeRequests = 0;

// // Request interceptor
// instance.interceptors.request.use(
//   (request) => {
//     const token = localStorage.getItem("migoto-cms-token");
//     if (token) {
//       request.headers.authorization = token;
//     }

//     activeRequests++;
//     loaderStore.setLoading(true);
//     return request;
//   },
//   (error) => {
//     activeRequests = Math.max(activeRequests - 1, 0);
//     if (activeRequests === 0) loaderStore.setLoading(false);
//     return Promise.reject(error);
//   }
// );

// // Response interceptor
// instance.interceptors.response.use(
//   (response) => {
//     activeRequests--;
//     if (activeRequests === 0) loaderStore.setLoading(false);
//     return response;
//   },
//   (error) => {
//     activeRequests = Math.max(activeRequests - 1, 0);
//     if (activeRequests === 0) loaderStore.setLoading(false);
//     return Promise.reject(error);
//   }
// );

let activeRequests = 0;

instance.interceptors.request.use(
  (request) => {
    const token = localStorage.getItem("migoto-cms-token");
    if (token) {
      request.headers.authorization = token;
    }

    // Default to "mini" loader if not specified
    const loaderType = request.loaderType || "mini";

    // Store loaderType on request itself (so we can access in response)
    request._loaderType = loaderType;

    if (loaderType !== "none") {
      activeRequests++;
      useLoaderStore.getState().setLoader(loaderType);
    }

    return request;
  },
  (error) => {
    activeRequests = Math.max(activeRequests - 1, 0);
    if (activeRequests === 0) {
      useLoaderStore.getState().setLoader("none");
    }
    return Promise.reject(error);
  }
);

instance.interceptors.response.use(
  (response) => {
    const { _loaderType } = response.config;

    if (_loaderType !== "none") {
      activeRequests = Math.max(activeRequests - 1, 0);
      if (activeRequests === 0) {
        useLoaderStore.getState().setLoader("none");
      }
    }

    return response;
  },
  (error) => {
    const { _loaderType } = error.config || {};

    if (_loaderType !== "none") {
      activeRequests = Math.max(activeRequests - 1, 0);
      if (activeRequests === 0) {
        useLoaderStore.getState().setLoader("none");
      }
    }
    if (error.response?.status === 401) {
      // Only redirect if not on login page
      const currentPath = window.location.pathname;
      if (currentPath !== '/migoto-cms' && !currentPath.includes('login')) {
        localStorage.clear();
        window.location.href = "/migoto-cms";
      }
    }

    return Promise.reject(error);
  }
);

export default instance;
