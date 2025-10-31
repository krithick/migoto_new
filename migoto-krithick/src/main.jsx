import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import Login from './Pages/Login/Login.jsx'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import UplaodAction from './Components/UplaodAction/UploadAction.jsx'
import Dashboard from './Pages/Dashboard/Dashboard.jsx'
import NotFound from './Utils/NotFound/NotFound.jsx'

const router = createBrowserRouter([
  {
    path: "/migoto-cms",
    element: (
        <Login />
    ),
  },
  {
    path: '/migoto-cms/*',
    element: <App />,
    children: [
      {
        path: 'dashboard',
        element: <Dashboard />,
      },
      {
        path: '*',
        element: <NotFound />    
      }
    ]
  },
  // {
  //   path: '*',
  //   element: <NotFound />
  // }
]);
createRoot(document.getElementById('root')).render(
    <RouterProvider router={router} />
)

// createRoot(document.getElementById('root')).render(
//   <StrictMode>
//     <Login />
//     {/* <App/> */}
//   </StrictMode>,
// )
