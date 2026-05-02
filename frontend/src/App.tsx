import { lazy, Suspense } from "react";
import { Routes, Route } from "react-router-dom";
import { Layout } from "./components/Layout";
import { WelcomeModal } from "./components/WelcomeModal";
import { Dashboard } from "./views/Dashboard";

const CitationNetwork = lazy(() =>
  import("./views/CitationNetwork").then((m) => ({ default: m.CitationNetwork }))
);
const CoauthorshipNetwork = lazy(() =>
  import("./views/CoauthorshipNetwork").then((m) => ({
    default: m.CoauthorshipNetwork,
  }))
);
const ContaminationCascade = lazy(() =>
  import("./views/ContaminationCascade").then((m) => ({
    default: m.ContaminationCascade,
  }))
);
const AIDiffusion = lazy(() =>
  import("./views/AIDiffusion").then((m) => ({ default: m.AIDiffusion }))
);
const FieldComparison = lazy(() =>
  import("./views/FieldComparison").then((m) => ({ default: m.FieldComparison }))
);
const AuthorDetail = lazy(() =>
  import("./views/AuthorDetail").then((m) => ({ default: m.AuthorDetail }))
);
const PaperDetail = lazy(() =>
  import("./views/PaperDetail").then((m) => ({ default: m.PaperDetail }))
);
const CitationExplorer = lazy(() =>
  import("./views/CitationExplorer").then((m) => ({ default: m.CitationExplorer }))
);
const Help = lazy(() =>
  import("./views/Help").then((m) => ({ default: m.Help }))
);
function ViewFallback() {
  return (
    <div className="flex-1 flex items-center justify-center">
      <div className="w-8 h-8 border-2 border-[#00d4ff]/30 border-t-[#00d4ff] rounded-full animate-spin" />
    </div>
  );
}

export function App() {
  return (
    <>
    <WelcomeModal />
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route
          path="citation"
          element={
            <Suspense fallback={<ViewFallback />}>
              <CitationNetwork />
            </Suspense>
          }
        />
        <Route
          path="coauthorship"
          element={
            <Suspense fallback={<ViewFallback />}>
              <CoauthorshipNetwork />
            </Suspense>
          }
        />
        <Route
          path="contamination"
          element={
            <Suspense fallback={<ViewFallback />}>
              <ContaminationCascade />
            </Suspense>
          }
        />
        <Route
          path="ai-diffusion"
          element={
            <Suspense fallback={<ViewFallback />}>
              <AIDiffusion />
            </Suspense>
          }
        />
<Route
path="field-comparison"
element={
<Suspense fallback={<ViewFallback />}>
<FieldComparison />
</Suspense>
}
        />
        <Route
          path="author/:id"
          element={
            <Suspense fallback={<ViewFallback />}>
              <AuthorDetail />
            </Suspense>
          }
        />
        <Route
          path="paper/:id"
          element={
            <Suspense fallback={<ViewFallback />}>
              <PaperDetail />
            </Suspense>
          }
        />
        <Route
          path="explore"
          element={
            <Suspense fallback={<ViewFallback />}>
              <CitationExplorer />
            </Suspense>
          }
        />
        <Route
          path="explore/:id"
          element={
            <Suspense fallback={<ViewFallback />}>
              <CitationExplorer />
            </Suspense>
          }
        />
        <Route
          path="help"
          element={
            <Suspense fallback={<ViewFallback />}>
              <Help />
            </Suspense>
          }
        />
      </Route>
    </Routes>
    </>
  );
}
