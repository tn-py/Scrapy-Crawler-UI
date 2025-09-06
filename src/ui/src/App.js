import React from 'react';
import { Tabs, Tab } from 'react-bootstrap';
import UrlTester from './UrlTester';
import SelectorTester from './SelectorTester';
import SelectorExplainer from './SelectorExplainer';
import SelectorRepairer from './SelectorRepairer';
import SpiderScaffolder from './SpiderScaffolder';
import CrawlRunner from './CrawlRunner';

function App() {
  return (
    <div className="container mt-3">
      <Tabs defaultActiveKey="url-tester" id="main-tabs">
        <Tab eventKey="url-tester" title="URL Tester">
          <UrlTester />
        </Tab>
        <Tab eventKey="selector-tester" title="Selector Tester">
          <SelectorTester />
        </Tab>
        <Tab eventKey="selector-explainer" title="Selector Explainer">
          <SelectorExplainer />
        </Tab>
        <Tab eventKey="selector-repairer" title="Selector Repairer">
          <SelectorRepairer />
        </Tab>
        <Tab eventKey="spider-scaffolder" title="Spider Scaffolder">
          <SpiderScaffolder />
        </Tab>
        <Tab eventKey="crawl-runner" title="Crawl Runner">
          <CrawlRunner />
        </Tab>
      </Tabs>
    </div>
  );
}

export default App;