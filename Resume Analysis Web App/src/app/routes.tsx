import { createBrowserRouter } from "react-router";
import RoleSelection from "./pages/RoleSelection";
import Login from "./pages/Login";
import RecruiterDashboard from "./pages/RecruiterDashboard";
import ApplicantDashboard from "./pages/ApplicantDashboard";
import JobPostings from "./pages/JobPostings";
import NotFound from "./pages/NotFound";
import Root from "./pages/Root";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Root,
    children: [
      { index: true, Component: RoleSelection },
      { path: "login/:role", Component: Login },
      { path: "recruiter/dashboard", Component: RecruiterDashboard },
      { path: "recruiter/jobs", Component: JobPostings },
      { path: "applicant/dashboard", Component: ApplicantDashboard },
      { path: "*", Component: NotFound },
    ],
  },
]);
