import * as React from "react";

const Watch = ({filter}) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="30"
    height="30"
    viewBox="0 0 30 30"
  >
    <g
      id="Group_20422"
      data-name="Group 20422"
      transform="translate(-16059 10094)"
    >
      <path
        id="Rectangle_3112"
        fill="none"
        d="M0 0h30v30H0z"
        data-name="Rectangle 3112"
        transform="translate(16059 -10094)"
      ></path>
      <g
        id="Group_20423"
        fill ={filter=== "Watch"?  "#FFFFFF" : "#0085DB" }
        data-name="Group 20423"
        transform="translate(77.432 -114)"
      >
        <path
          id="Path_3585"
          d="M43.429 75.6a11.61 11.61 0 0 1-11.133 0l.87 4.894h9.4Z"
          data-name="Path 3585"
          transform="translate(15957.283 -10030.496)"
        ></path>
        <path
          id="Path_3586"
          d="M43.432 16.894 42.564 12h-9.4l-.864 4.894a11.6 11.6 0 0 1 11.132 0"
          data-name="Path 3586"
          transform="translate(15957.28 -9992)"
        ></path>
        <path
          id="Path_3587"
          d="M76.862 49.26v-.632A.624.624 0 0 0 76.23 48h-.63v1.9h.632a.62.62 0 0 0 .632-.631Z"
          data-name="Path 3587"
          transform="translate(15931.074 -10013.787)"
        ></path>
        <path
          id="Path_3588"
          d="M21.2 34.748a9.947 9.947 0 1 0 9.946-9.948 9.957 9.957 0 0 0-9.946 9.948m9.157-5.289a.789.789 0 0 1 1.579 0v4.5h3.079a.789.789 0 0 1 0 1.579h-3.869a.79.79 0 0 1-.789-.789Z"
          data-name="Path 3588"
          transform="translate(15964 -9999.748)"
        ></path>
      </g>
    </g>
  </svg>
);

export default Watch;
