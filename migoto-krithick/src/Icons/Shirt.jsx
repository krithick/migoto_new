import * as React from "react";

const Shirt = ({filter}) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="30"
    height="30"
    viewBox="0 0 30 30"
  >
    <g
      id="Group_20424"
      data-name="Group 20424"
      transform="translate(-15837 10115)"
    >
      <path
        id="Rectangle_3113"
        fill="none"
        d="M0 0h30v30H0z"
        data-name="Rectangle 3113"
        transform="translate(15837 -10115)"
      ></path>
      <path
        id="Path_3589"
        fill ={filter=== "Shirt"?  "#FFFFFF" : "#0085DB" }
        d="m35.658 10.648-8.572-4.286a1.1 1.1 0 0 0-.479-.112H15.892a1.1 1.1 0 0 0-.479.112l-8.572 4.286A1.073 1.073 0 0 0 6.326 12l2.143 5.357a1.07 1.07 0 0 0 1.334.619l1.8-.6v16.731a1.07 1.07 0 0 0 1.071 1.071h18.218a1.07 1.07 0 0 0 1.071-1.071V17.379l1.8.6a1.07 1.07 0 0 0 1.389-.806l1.071-5.357a1.07 1.07 0 0 0-.571-1.169Zm-14.36.959a4.266 4.266 0 0 1-4.045-3.214h8.007a4.26 4.26 0 0 1-3.96 3.214Z"
        data-name="Path 3589"
        transform="translate(15830.751 -10120.715)"
      ></path>
    </g>
  </svg>
);

export default Shirt;
