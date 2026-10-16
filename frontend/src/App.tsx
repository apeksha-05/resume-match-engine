import { lazy } from "react";
import { Route, Routes } from "react-router-dom";
import { AppLayout } from "@/components/layout/AppLayout";
import { RequireAuth } from "@/components/RequireAuth";
import { LandingPage } from "@/pages/LandingPage";
import { LoginPage } from "@/pages/LoginPage";
import { NotFoundPage } from "@/pages/NotFoundPage";
import { SignupPage } from "@/pages/SignupPage";

// Heavier pages load on demand, so the first visit downloads less code.
// React.lazy needs a default export, so each named export is wrapped.
const NewAnalysisPage = lazy(() =>
  import("@/pages/NewAnalysisPage").then((module) => ({ default: module.NewAnalysisPage })),
);
const ResultsPage = lazy(() =>
  import("@/pages/ResultsPage").then((module) => ({ default: module.ResultsPage })),
);
const JobsPage = lazy(() =>
  import("@/pages/JobsPage").then((module) => ({ default: module.JobsPage })),
);
const HistoryPage = lazy(() =>
  import("@/pages/HistoryPage").then((module) => ({ default: module.HistoryPage })),
);
const SettingsPage = lazy(() =>
  import("@/pages/SettingsPage").then((module) => ({ default: module.SettingsPage })),
);

function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<LandingPage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="signup" element={<SignupPage />} />
        <Route path="results/:id" element={<ResultsPage />} />
        <Route path="jobs" element={<JobsPage />} />

        <Route element={<RequireAuth />}>
          <Route path="analyze" element={<NewAnalysisPage />} />
          <Route path="history" element={<HistoryPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>

        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}

export default App;
