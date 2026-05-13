import React from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

import App from "./App";
import DayView from "./pages/DayView";
import AppointmentDetail from "./pages/AppointmentDetail";
import PatientDetail from "./pages/PatientDetail";
import SchedulePage from "./pages/SchedulePage";
import "./index.css";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <DayView /> },
      { path: "appointments/:id", element: <AppointmentDetail /> },
      { path: "patients/:id", element: <PatientDetail /> },
      { path: "schedule", element: <SchedulePage /> },
    ],
  },
]);

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
);
