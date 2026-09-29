import { Route, Routes } from "react-router-dom";
import { AppLayout } from "@/components/layout/AppLayout";
import { HistoryPage } from "@/pages/HistoryPage";
import { JobsPage } from "@/pages/JobsPage";
import { LandingPage } from "@/pages/LandingPage";
import { NewAnalysisPage } from "@/pages/NewAnalysisPage";
import { NotFoundPage } from "@/pages/NotFoundPage";
import { ResultsPage } from "@/pages/ResultsPage";
import { SettingsPage } from "@/pages/SettingsPage";

function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<LandingPage />} />
        <Route path="analyze" element={<NewAnalysisPage />} />
        <Route path="results/:id" element={<ResultsPage />} />
        <Route path="jobs" element={<JobsPage />} />
        <Route path="history" element={<HistoryPage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}

export default App;