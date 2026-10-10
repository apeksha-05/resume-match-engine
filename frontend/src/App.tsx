import { Route, Routes } from "react-router-dom";
import { AppLayout } from "@/components/layout/AppLayout";
import { RequireAuth } from "@/components/RequireAuth";
import { HistoryPage } from "@/pages/HistoryPage";
import { JobsPage } from "@/pages/JobsPage";
import { LandingPage } from "@/pages/LandingPage";
import { LoginPage } from "@/pages/LoginPage";
import { NewAnalysisPage } from "@/pages/NewAnalysisPage";
import { NotFoundPage } from "@/pages/NotFoundPage";
import { ResultsPage } from "@/pages/ResultsPage";
import { SettingsPage } from "@/pages/SettingsPage";
import { SignupPage } from "@/pages/SignupPage";

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