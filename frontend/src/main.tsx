import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import "./styles/global.css";
import { App } from "./App";

import cytoscape from "cytoscape";
import coseBilkent from "cytoscape-cose-bilkent";
import fcose from "cytoscape-fcose";
import nodeHtmlLabel from "cytoscape-node-html-label";

cytoscape.use(coseBilkent);
cytoscape.use(fcose);
nodeHtmlLabel(cytoscape);

const rootEl = document.getElementById("root");
if (rootEl) {
  createRoot(rootEl).render(
    <StrictMode>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </StrictMode>,
  );
}
