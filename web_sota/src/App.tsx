import { AppLayout } from "@/components/layout/app-layout";
import { ApiDocs } from "@/pages/ApiDocs";
import { AppsHub } from "@/pages/AppsHub";
import Logging from "@/pages/Logging";
import { Skills } from "@/pages/Skills";
import { Chat } from "@/pages/chat";
import { Dashboard } from "@/pages/dashboard";
import { Help } from "@/pages/help";
import { Settings } from "@/pages/settings";
import { Tools } from "@/pages/tools";
import {
  Navigate,
  Route,
  BrowserRouter as Router,
  Routes,
} from "react-router-dom";

function App() {
  return (
    <Router>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/tools" element={<Tools />} />
          <Route path="/skills" element={<Skills />} />
          <Route path="/apps" element={<AppsHub />} />
          <Route path="/logging" element={<Logging />} />
          <Route path="/api-docs" element={<ApiDocs />} />
          <Route path="/help" element={<Help />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppLayout>
    </Router>
  );
}

export default App;
