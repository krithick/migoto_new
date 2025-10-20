import React, { useState } from 'react';

const ScenarioCreator = () => {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const [scenarioText, setScenarioText] = useState('');
  const [templateName, setTemplateName] = useState('');
  const [templateId, setTemplateId] = useState(null);
  const [templateData, setTemplateData] = useState(null);
  const [validationResults, setValidationResults] = useState(null);
  const [generatedPrompts, setGeneratedPrompts] = useState(null);
  const [qualityTestResults, setQualityTestResults] = useState(null);
  const [testingMode, setTestingMode] = useState(null); // 'automated' or 'interactive'
  const [interactiveTest, setInteractiveTest] = useState(null);
  const [scenarioId, setScenarioId] = useState(null);
  const [avatarInteractions, setAvatarInteractions] = useState([]);
  const [recommendedPersona, setRecommendedPersona] = useState(null);
  
  const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:9000';
  const BEARER_TOKEN = process.env.REACT_APP_BEARER_TOKEN;
  const MODULE_ID = process.env.REACT_APP_MODULE_ID;
  
  const AVATAR_PRESET = {
    fbx: "Da",
    animation: "https://meta.novactech.in:7445/uploads/other/20250513093452_3d82864a.glb",
    glb: [
      { file: "https://meta.novactech.in:7445/uploads/other/20250513093452_2cb788b6.glb", thumbnail: "", name: "Body" },
      { file: "https://meta.novactech.in:7445/uploads/other/20250513093452_98da1caa.glb", thumbnail: "https://meta.novactech.in:7445/uploads/other/20250513120224_469e23b3.png", name: "Glass" },
      { file: "https://meta.novactech.in:7445/uploads/other/20250513093452_c331f08c.glb", thumbnail: "https://meta.novactech.in:7445/uploads/other/20250514045348_f4eb9f70.png", name: "Hair" },
      { file: "https://meta.novactech.in:7445/uploads/other/20250513093452_0c9661fb.glb", thumbnail: "https://meta.novactech.in:7445/uploads/other/20250514045348_3dd06f89.png", name: "Pant" },
      { file: "https://meta.novactech.in:7445/uploads/other/20250513093452_29dc7a08.glb", thumbnail: "https://meta.novactech.in:7445/uploads/other/20250514045348_26f75795.png", name: "Shirt" },
      { file: "https://meta.novactech.in:7445/uploads/other/20250513093452_5e825a76.glb", thumbnail: "", name: "Shoes" }
    ],
    selected: [
      { category: "Body", file_name: "Da_Body_B1" },
      { category: "Glass", file_name: "Da_Glass_Gls2" },
      { category: "Hair", file_name: "Da_Hair_Hr3" },
      { category: "Pant", file_name: "Da_Pant_Pt3" },
      { category: "Shirt", file_name: "Da_Shirt_St1" },
      { category: "Shoes", file_name: "Da_Shoes_Sh1" }
    ]
  };

  const apiCall = async (endpoint, method = 'GET', body = null, isFormData = false) => {
    const headers = { 'Authorization': `Bearer ${BEARER_TOKEN}` };
    if (!isFormData) headers['Content-Type'] = 'application/json';
    
    const options = { method, headers };
    if (body) options.body = isFormData ? body : JSON.stringify(body);
    
    const res = await fetch(`${API_BASE}${endpoint}`, options);
    if (!res.ok) throw new Error(`API Error: ${res.statusText}`);
    return res.json();
  };

  const analyzeScenario = async () => {
    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append('scenario_document', scenarioText);
      formData.append('template_name', templateName);
      
      const result = await apiCall('/scenario/analyze-scenario-enhanced', 'POST', formData, true);
      setTemplateId(result.template_id);
      setTemplateData(result.template_data);
      
      const validation = validateTemplate(result.template_data);
      setValidationResults(validation);
      
      console.log('📊 Template Data:', result.template_data);
      console.log('🎯 Archetype:', result.template_data.archetype_classification);
      
      setStep(2);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const validateTemplate = (data) => {
    const issues = [];
    const warnings = [];
    
    if (!data.context_overview?.scenario_title) issues.push('Missing scenario title');
    if (!data.context_overview?.scenario_description) issues.push('Missing scenario description');
    if (!data.knowledge_base?.conversation_topics?.length) warnings.push('No conversation topics');
    if (!data.learning_objectives?.primary_objectives?.length) warnings.push('No learning objectives');
    
    const score = 100 - (issues.length * 20) - (warnings.length * 5);
    
    return {
      valid: issues.length === 0,
      score: Math.max(0, score),
      issues,
      warnings
    };
  };

  const updateTemplateField = (section, field, value) => {
    const updated = {
      ...templateData,
      [section]: { ...templateData[section], [field]: value }
    };
    setTemplateData(updated);
    setValidationResults(validateTemplate(updated));
  };

  const saveTemplate = async () => {
    setLoading(true);
    setError(null);
    try {
      await apiCall(`/scenario/update-template-in-db/${templateId}`, 'PUT', { 
        template_data: templateData,
        template_name: templateName 
      });
      alert('Template saved!');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const generatePrompts = async () => {
    setLoading(true);
    setError(null);
    try {
      const promptsResult = await apiCall('/scenario/generate-prompts-from-template', 'POST', {
        template_id: templateId,
        modes: ['learn', 'try', 'assess']
      });
      
      setGeneratedPrompts(promptsResult);
      
      // Generate recommended persona
      await generateRecommendedPersona();
      
      setStep(3);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  const generateRecommendedPersona = async () => {
    try {
      const assessPersona = await apiCall('/scenario/generate-personas', 'POST', {
        template_id: templateId,
        persona_type: 'assess_mode_character',
        gender: '',
        prompt: '',
        count: 1
      });
      
      console.log('👤 Recommended Persona:', assessPersona.personas[0]);
      setRecommendedPersona(assessPersona.personas[0]);
      
    } catch (err) {
      console.error('Error generating persona:', err);
    }
  };

  const testPromptQuality = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiCall('/scenario/test-prompt-quality', 'POST', {
        system_prompt: generatedPrompts.assess_mode_prompt || generatedPrompts.prompts?.assess_mode_prompt,
        persona: generatedPrompts.personas?.assess_mode_character || generatedPrompts.prompts?.personas?.assess_mode_character,
        template_data: templateData,
        mode: 'assess'
      });
      
      setQualityTestResults(result);
      setTestingMode('automated');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const startInteractiveTest = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiCall('/scenario/start-interactive-test', 'POST', {
        system_prompt: generatedPrompts.assess_mode_prompt || generatedPrompts.prompts?.assess_mode_prompt,
        persona: generatedPrompts.personas?.assess_mode_character || generatedPrompts.prompts?.personas?.assess_mode_character,
        initial_message: "Hi, I need some help"
      });
      
      setInteractiveTest(result);
      setTestingMode('interactive');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const continueInteractiveTest = async (message) => {
    setLoading(true);
    try {
      const result = await apiCall('/scenario/continue-interactive-test', 'POST', {
        system_prompt: generatedPrompts.assess_mode_prompt || generatedPrompts.prompts?.assess_mode_prompt,
        user_message: message,
        conversation_history: interactiveTest.conversation_history || []
      });
      
      setInteractiveTest(prev => ({
        ...prev,
        conversation_history: result.conversation_history
      }));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const createScenario = async () => {
    setLoading(true);
    setError(null);
    try {
      // Create 3 avatars with recommended persona
      const interactions = [];
      for (let i = 0; i < 3; i++) {
        const avatarData = {
          module_id: MODULE_ID,
          name: `${recommendedPersona?.name || 'Character'} ${i + 1}`,
          language_id: 'ec489817-553a-4ef4-afb5-154f78f041b6',
          environment_id: '8f0864ae-ec3a-4530-9329-937dc2d6bdbd', 
          bot_voice_id: 'dbb317a2-9891-4d72-b763-a8046ee1bcc8',
          system_prompt: generatedPrompts.prompts?.assess_mode_prompt || generatedPrompts.assess_mode,
          ...AVATAR_PRESET,
          persona: recommendedPersona || generatedPrompts.personas?.assess_mode_character
        };
        const avatar = await apiCall('/avatar-interactions', 'POST', avatarData);
        interactions.push(avatar);
      }
      setAvatarInteractions(interactions);

      const scenarioData = {
        module_id: MODULE_ID,
        template_id: templateId,
        title: templateData.context_overview?.scenario_title || templateName,
        description: templateData.context_overview?.assess_mode_description || 'Training scenario',
        difficulty_level: templateData.context_overview?.difficulty_level || 'Mixed',
        learn_mode_prompt: generatedPrompts.prompts?.learn_mode_prompt || generatedPrompts.learn_mode,
        try_mode_prompt: generatedPrompts.prompts?.try_mode_prompt || generatedPrompts.try_mode,
        assess_mode_prompt: generatedPrompts.prompts?.assess_mode_prompt || generatedPrompts.assess_mode,
        avatar_interaction_ids: interactions.map(a => a.id),
        archetype: templateData.archetype_classification?.primary_archetype,
        archetype_sub_type: templateData.archetype_classification?.sub_type,
        archetype_confidence: templateData.archetype_classification?.confidence_score
      };
      
      const scenario = await apiCall('/scenarios', 'POST', scenarioData);
      setScenarioId(scenario.id);
      setStep(4);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      <h1>Scenario Creator with Validation</h1>
      
      {error && <div style={{ background: '#fee', padding: '10px', borderRadius: '4px', marginBottom: '20px', color: '#c00' }}>{error}</div>}
      
      {step === 1 && (
        <div>
          <h2>Step 1: Describe Your Scenario</h2>
          <input
            type="text"
            placeholder="Template Name"
            value={templateName}
            onChange={(e) => setTemplateName(e.target.value)}
            style={{ width: '100%', padding: '10px', marginBottom: '10px', border: '1px solid #ddd', borderRadius: '4px' }}
          />
          <textarea
            placeholder="Describe your training scenario..."
            value={scenarioText}
            onChange={(e) => setScenarioText(e.target.value)}
            rows={10}
            style={{ width: '100%', padding: '10px', marginBottom: '10px', border: '1px solid #ddd', borderRadius: '4px' }}
          />
          <button onClick={analyzeScenario} disabled={loading || !scenarioText || !templateName} style={{ padding: '10px 20px', background: '#2196F3', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
            {loading ? 'Analyzing...' : 'Analyze & Create Template'}
          </button>
        </div>
      )}

      {step === 2 && templateData && (
        <div>
          <h2>Step 2: Edit & Validate Template</h2>
          
          {validationResults && (
            <div style={{ marginBottom: '20px', padding: '15px', border: `2px solid ${validationResults.valid ? '#4CAF50' : '#ff9800'}`, borderRadius: '4px', background: validationResults.valid ? '#f1f8f4' : '#fff8e1' }}>
              <h3>Validation Score: {validationResults.score}/100</h3>
              {validationResults.issues.length > 0 && (
                <div style={{ color: '#d32f2f', marginBottom: '10px' }}>
                  <strong>Issues:</strong>
                  <ul>{validationResults.issues.map((issue, i) => <li key={i}>{issue}</li>)}</ul>
                </div>
              )}
              {validationResults.warnings.length > 0 && (
                <div style={{ color: '#f57c00' }}>
                  <strong>Warnings:</strong>
                  <ul>{validationResults.warnings.map((warn, i) => <li key={i}>{warn}</li>)}</ul>
                </div>
              )}
            </div>
          )}
          
          <div style={{ marginBottom: '30px', padding: '15px', border: '1px solid #ddd', borderRadius: '4px' }}>
            <h3>Context Overview</h3>
            <label>Scenario Title:</label>
            <input
              type="text"
              value={templateData.context_overview?.scenario_title || ''}
              onChange={(e) => updateTemplateField('context_overview', 'scenario_title', e.target.value)}
              style={{ width: '100%', padding: '8px', marginBottom: '10px', border: '1px solid #ddd', borderRadius: '4px' }}
            />
            <label>Description:</label>
            <textarea
              value={templateData.context_overview?.scenario_description || ''}
              onChange={(e) => updateTemplateField('context_overview', 'scenario_description', e.target.value)}
              rows={4}
              style={{ width: '100%', padding: '8px', marginBottom: '10px', border: '1px solid #ddd', borderRadius: '4px' }}
            />
          </div>

          {/* Display Template Analysis */}
          {templateData && (
            <div style={{ marginBottom: '30px', padding: '15px', border: '1px solid #e0e0e0', borderRadius: '4px', background: '#fafafa' }}>
              <h3>📋 Extracted Template Data</h3>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '15px' }}>
                <div>
                  <h4>🎯 Scenario Overview</h4>
                  <p><strong>Title:</strong> {templateData.context_overview?.scenario_title}</p>
                  <p><strong>Domain:</strong> {templateData.general_info?.domain}</p>
                </div>
                <div>
                  <h4>🤖 Archetype Classification</h4>
                  <p><strong>Type:</strong> {templateData.archetype_classification?.primary_archetype}</p>
                  <p><strong>Confidence:</strong> {Math.round(templateData.archetype_classification?.confidence_score * 100)}%</p>
                </div>
              </div>
              <div>
                <h4>👥 Character Roles</h4>
                <p><strong>Learn Mode (Trainer):</strong> {templateData.persona_definitions?.learn_mode_ai_bot?.role}</p>
                <p><strong>Assess Mode (Character):</strong> {templateData.persona_definitions?.assess_mode_ai_bot?.role}</p>
              </div>
              <div>
                <h4>💬 Conversation Topics</h4>
                <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
                  {templateData.knowledge_base?.conversation_topics?.slice(0, 3).map((topic, idx) => (
                    <li key={idx}>{topic}</li>
                  ))}
                  {templateData.knowledge_base?.conversation_topics?.length > 3 && <li>...and {templateData.knowledge_base.conversation_topics.length - 3} more</li>}
                </ul>
              </div>
            </div>
          )}

          <div style={{ display: 'flex', gap: '10px' }}>
            <button onClick={saveTemplate} disabled={loading} style={{ padding: '10px 20px', background: '#2196F3', color: 'white', border: 'none', borderRadius: '4px' }}>
              {loading ? 'Saving...' : 'Save Template'}
            </button>
            <button onClick={generatePrompts} disabled={loading || !validationResults?.valid} style={{ padding: '10px 20px', background: validationResults?.valid ? '#4CAF50' : '#ccc', color: 'white', border: 'none', borderRadius: '4px' }}>
              {loading ? 'Generating...' : 'Generate Prompts →'}
            </button>
          </div>
        </div>
      )}

      {step === 3 && generatedPrompts && (
        <div>
          <h2>Step 3: Review Prompts & Character</h2>
          
          {/* Display Recommended Persona */}
          {recommendedPersona && (
            <div style={{ marginBottom: '20px', padding: '15px', border: '2px solid #9C27B0', borderRadius: '4px', background: '#f3e5f5' }}>
              <h3>🎭 Recommended Character</h3>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                <div>
                  <h4>{recommendedPersona.name}</h4>
                  <p><strong>Role:</strong> {recommendedPersona.persona_type}</p>
                  <p><strong>Age:</strong> {recommendedPersona.age} | <strong>Gender:</strong> {recommendedPersona.gender}</p>
                  <p><strong>Location:</strong> {recommendedPersona.location}</p>
                </div>
                <div>
                  <p><strong>Background:</strong> {recommendedPersona.background_story}</p>
                  <p><strong>Goal:</strong> {recommendedPersona.character_goal}</p>
                </div>
              </div>
            </div>
          )}
          
          <div style={{ marginBottom: '20px', padding: '15px', border: '1px solid #4CAF50', borderRadius: '4px', background: '#f1f8f4' }}>
            <h3>📝 Generated Prompts</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
              <div>
                <h4>Learn Mode (Trainer)</h4>
                <textarea 
                  value={generatedPrompts.prompts?.learn_mode_prompt || generatedPrompts.learn_mode || ''} 
                  readOnly 
                  rows={4}
                  style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px', fontSize: '12px' }}
                />
              </div>
              <div>
                <h4>Assess Mode (Character)</h4>
                <textarea 
                  value={generatedPrompts.prompts?.assess_mode_prompt || generatedPrompts.assess_mode || ''} 
                  readOnly 
                  rows={4}
                  style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px', fontSize: '12px' }}
                />
              </div>
            </div>
          </div>

          <div style={{ marginBottom: '20px', display: 'flex', gap: '10px' }}>
            <button onClick={testPromptQuality} disabled={loading} style={{ padding: '10px 20px', background: '#FF9800', color: 'white', border: 'none', borderRadius: '4px' }}>
              {loading ? 'Testing...' : '🤖 Run Automated Tests'}
            </button>
            <button onClick={startInteractiveTest} disabled={loading} style={{ padding: '10px 20px', background: '#9C27B0', color: 'white', border: 'none', borderRadius: '4px' }}>
              {loading ? 'Starting...' : '💬 Start Interactive Test'}
            </button>
          </div>

          {qualityTestResults && testingMode === 'automated' && (
            <div style={{ marginBottom: '20px', padding: '15px', border: '2px solid #4CAF50', borderRadius: '4px' }}>
              <h3>Test Results: {(qualityTestResults.overall_score * 100).toFixed(0)}%</h3>
              <p><strong>Pass Rate:</strong> {qualityTestResults.test_summary.pass_rate.toFixed(0)}%</p>
              
              <h4>Conversation Examples:</h4>
              {qualityTestResults.conversation_examples.map((ex, i) => (
                <div key={i} style={{ marginBottom: '10px', padding: '10px', background: ex.passed ? '#e8f5e9' : '#fff3e0', borderRadius: '4px' }}>
                  <p><strong>User:</strong> {ex.user}</p>
                  <p><strong>AI:</strong> {ex.ai}</p>
                  <p><strong>{ex.passed ? '✅' : '⚠️'}</strong> {ex.evaluation}</p>
                </div>
              ))}
              
              {qualityTestResults.recommendations.length > 0 && (
                <div>
                  <h4>Recommendations:</h4>
                  <ul>{qualityTestResults.recommendations.map((rec, i) => <li key={i}>{rec}</li>)}</ul>
                </div>
              )}
            </div>
          )}

          {interactiveTest && testingMode === 'interactive' && (
            <div style={{ marginBottom: '20px', padding: '15px', border: '2px solid #9C27B0', borderRadius: '4px' }}>
              <h3>💬 Interactive Test with {interactiveTest.persona}</h3>
              <div style={{ maxHeight: '300px', overflowY: 'auto', marginBottom: '10px' }}>
                {interactiveTest.conversation_history?.map((msg, i) => (
                  <div key={i} style={{ marginBottom: '10px', padding: '8px', background: msg.role === 'user' ? '#e3f2fd' : '#f3e5f5', borderRadius: '4px' }}>
                    <strong>{msg.role === 'user' ? 'You' : 'AI'}:</strong> {msg.content}
                  </div>
                ))}
              </div>
              <input
                type="text"
                placeholder="Type your message..."
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && e.target.value) {
                    continueInteractiveTest(e.target.value);
                    e.target.value = '';
                  }
                }}
                style={{ width: '100%', padding: '10px', border: '1px solid #ddd', borderRadius: '4px' }}
              />
            </div>
          )}

          <div style={{ marginTop: '30px', textAlign: 'center' }}>
            <button onClick={createScenario} disabled={loading} style={{ padding: '15px 30px', background: '#4CAF50', color: 'white', border: 'none', borderRadius: '4px', fontSize: '16px', fontWeight: 'bold' }}>
              {loading ? '🚀 Creating Scenario...' : '🚀 Create Scenario with 3 Avatars'}
            </button>
            <p style={{ marginTop: '10px', color: '#666', fontSize: '14px' }}>This will create 3 avatars with the recommended character persona</p>
          </div>
        </div>
      )}

      {step === 4 && (
        <div style={{ padding: '20px', background: '#e8f5e9', borderRadius: '4px' }}>
          <h2>✅ Scenario Created Successfully!</h2>
          <p><strong>Scenario ID:</strong> {scenarioId}</p>
          <p><strong>Avatars Created:</strong> {avatarInteractions.length}</p>
          <button onClick={() => { setStep(1); setTemplateData(null); setGeneratedPrompts(null); setScenarioId(null); }} style={{ padding: '10px 20px', marginTop: '20px', background: '#2196F3', color: 'white', border: 'none', borderRadius: '4px' }}>
            Create Another Scenario
          </button>
        </div>
      )}
    </div>
  );
};

export default ScenarioCreator;
