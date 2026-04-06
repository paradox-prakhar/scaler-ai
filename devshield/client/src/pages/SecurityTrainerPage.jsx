import React, { useState, useEffect } from 'react';
import { getScenarios, getScenario, submitDecision } from '../services/api';
import ScenarioSelector from '../components/security/ScenarioSelector';
import PhishingEmailView from '../components/security/PhishingEmailView';
import MalwareAlertView from '../components/security/MalwareAlertView';
import LogsView from '../components/security/LogsView';
import DecisionPanel from '../components/security/DecisionPanel';
import FeedbackPanel from '../components/security/FeedbackPanel';

export default function SecurityTrainerPage() {
  const [scenarios, setScenarios] = useState([]);
  const [selectedScenario, setSelectedScenario] = useState(null);
  const [currentView, setCurrentView] = useState(null); // null, 'scenario', 'feedback'
  const [userChoice, setUserChoice] = useState(null);
  const [result, setResult] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    getScenarios().then(setScenarios).catch(console.error);
  }, []);

  const handleSelectScenario = async (id) => {
    // Reset state
    setUserChoice(null);
    setResult(null);
    setCurrentView('scenario');
    
    // Fetch full scenario data
    const fullScenario = await getScenario(id);
    setSelectedScenario(fullScenario);
  };

  const handleChoiceSelect = (choiceId) => {
    setUserChoice(choiceId);
  };

  const handleConfirm = async () => {
    if (!selectedScenario || !userChoice) return;
    setIsSubmitting(true);
    try {
      const res = await submitDecision(selectedScenario.id, userChoice);
      setResult(res);
      setCurrentView('feedback');
    } catch (err) {
      console.error(err);
    }
    setIsSubmitting(false);
  };

  const handleReset = () => {
    setUserChoice(null);
    setResult(null);
    setCurrentView(null);
    setSelectedScenario(null);
  };

  const renderScenarioView = () => {
    if (!selectedScenario) return null;
    switch (selectedScenario.type) {
      case 'phishing': return <PhishingEmailView content={selectedScenario.content} />;
      case 'malware': return <MalwareAlertView content={selectedScenario.content} />;
      case 'logs': return <LogsView content={selectedScenario.content} />;
      default: return <div>Unknown scenario type</div>;
    }
  };

  return (
    <div className="h-[calc(100vh-64px)] w-full flex bg-[#0f111a]">
      {/* Left Panel: Selector */}
      <div className="w-1/3 border-r border-gray-800 bg-[#161925] overflow-y-auto">
        <ScenarioSelector 
          scenarios={scenarios} 
          selectedId={selectedScenario?.id} 
          onSelect={handleSelectScenario} 
        />
      </div>

      {/* Right Panel: Content */}
      <div className="w-2/3 flex flex-col bg-[#1b1e2e]">
        {currentView === null && (
          <div className="flex-1 flex flex-col items-center justify-center text-gray-500 text-center p-10">
            <span className="text-6xl mb-6 opacity-30">🛡️</span>
            <h2 className="text-2xl font-bold text-gray-400 mb-2">Cyber Security Trainer</h2>
            <p>Select a scenario from the left to start the simulation.</p>
          </div>
        )}

        {currentView === 'scenario' && selectedScenario && (
          <>
            {/* Scenario Content Area (takes most of the height) */}
            <div className="flex-1 overflow-y-auto bg-black/20 flex items-center p-6">
              {renderScenarioView()}
            </div>
            
            {/* Decision Panel (fixed at bottom) */}
            <div className="shrink-0">
              <DecisionPanel 
                options={selectedScenario.options}
                userChoice={userChoice}
                onChoiceSelect={handleChoiceSelect}
                onConfirm={handleConfirm}
                disabled={isSubmitting}
              />
            </div>
          </>
        )}

        {currentView === 'feedback' && result && (
          <div className="flex-1">
            <FeedbackPanel 
              result={result} 
              onReset={handleReset} 
            />
          </div>
        )}
      </div>
    </div>
  );
}
