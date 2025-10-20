import React, { useState } from 'react';

const ScenarioWorkflow = () => {
  const [step, setStep] = useState(1);
  const [templateId, setTemplateId] = useState(null);
  const [templateData, setTemplateData] = useState(null);
  const [prompts, setPrompts] = useState(null);
  const [personas, setPersonas] = useState(null);
  const [loading, setLoading] = useState(false);
  const [scenarioText, setScenarioText] = useState('');
  const [templateName, setTemplateName] = useState('');
  
  const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:9000';
  const BEARER_TOKEN = process.env.REACT_APP_BEARER_TOKEN;
  const MODULE_ID = process.env.REACT_APP_MODULE_ID;
  
  const apiCall = async (endpoint, method = 'GET', body = null, isFormData = false) => {
    const headers = { 'Authorization': `Bearer ${BEARER_TOKEN}` };
    if (!isFormData) headers['Content-Type'] = 'application/json';
    
    const options = { method, headers };
    if (body) options.body = isFormData ? body : JSON.stringify(body);
    
    const res = await fetch(`${API_BASE}${endpoint}`, options);
    if (!res.ok) throw new Error(`API Error: ${res.statusText}`);
    return res.json();
  };

  // Step 1: Analyze scenario and create template
  const analyzeScenario = async () => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('scenario_document', scenarioText);
      formData.append('template_name', templateName);

      const result = await apiCall('/scenario/analyze-scenario-enhanced', 'POST', formData, true);
      setTemplateId(result.template_id);
      setTemplateData(result.template_data);
      setStep(2);
    } catch (error) {
      console.error('Error analyzing scenario:', error);
      alert('Error analyzing scenario: ' + error.message);
    }
    setLoading(false);
  };

  // Step 2: Load template from DB (for editing)
  const loadTemplate = async () => {
    setLoading(true);
    try {
      const result = await apiCall(`/scenario/load-template-from-db/${templateId}`);
      
      // Fix missing required fields
      const fixedTemplateData = {
        ...result.template_data,
        context_overview: {
          ...result.template_data.context_overview,
          scenario_description: result.template_data.context_overview?.scenario_description || result.template_data.context_overview?.purpose_of_scenario || 'Training scenario for skill development'
        },
        learning_objectives: {
          ...result.template_data.learning_objectives,
          primary_objectives: result.template_data.learning_objectives?.primary_objectives || [
            'Develop professional communication skills',
            'Learn to handle challenging situations',
            'Apply domain-specific best practices'
          ]
        },
        evaluation_metrics: {
          ...result.template_data.evaluation_metrics,
          evaluation_criteria: result.template_data.evaluation_metrics?.evaluation_criteria || {
            'Communication Skills': 'Assess clarity and professionalism of responses',
            'Problem Solving': 'Evaluate ability to provide appropriate solutions',
            'Domain Knowledge': 'Check accuracy of domain-specific information'
          }
        }
      };
      
      setTemplateData(fixedTemplateData);
      
      // Update template in database with fixed fields
      await apiCall(`/scenario/update-template-in-db/${templateId}`, 'PUT', {
        template_data: fixedTemplateData,
        template_name: templateName
      });
      
      setStep(3);
    } catch (error) {
      console.error('Error loading template:', error);
      alert('Error loading template: ' + error.message);
    }
    setLoading(false);
  };

  // Step 3: Generate prompts from template
  const generatePrompts = async (skipValidation = false) => {
    setLoading(true);
    try {
      const result = await apiCall('/scenario/generate-prompts-from-template', 'POST', {
        template_id: templateId,
        modes: ['learn', 'try', 'assess'],
        validate_before_generation: !skipValidation
      });
      
      // Check if validation failed
      if (result.error && result.error === "Template validation failed") {
        const proceed = confirm(`Template validation failed (Score: ${result.validation.score}/100)\n\nIssues:\n${result.validation.issues.map(issue => `• ${issue.message}`).join('\n')}\n\nDo you want to proceed anyway? (Click OK to skip validation, Cancel to fix issues)`);
        
        if (proceed) {
          // Retry without validation
          return generatePrompts(true);
        } else {
          return;
        }
      }
      
      setPrompts(result.prompts);
      setPersonas(result.prompts.personas);
      setStep(4);
    } catch (error) {
      console.error('Error generating prompts:', error);
      alert('Error generating prompts: ' + error.message);
    }
    setLoading(false);
  };

  // Step 4: Update template in DB
  const updateTemplate = async () => {
    setLoading(true);
    try {
      const result = await apiCall(`/scenario/update-template-in-db/${templateId}`, 'PUT', {
        template_data: templateData,
        template_name: templateName
      });
      setStep(5);
    } catch (error) {
      console.error('Error updating template:', error);
      alert('Error updating template: ' + error.message);
    }
    setLoading(false);
  };

  // Step 5: Create personas, avatars and scenario
  const createScenario = async () => {
    setLoading(true);
    try {
      // Create personas and avatars for each mode
      const createdAssets = [];
      
      if (prompts.learn_mode_prompt && personas.learn_mode_expert) {
        const { persona, avatar } = await createPersonaAndAvatar(personas.learn_mode_expert, 'learn_mode');
        const interaction = await createAvatarInteraction('learn_mode', prompts.learn_mode_prompt, persona, avatar.id);
        createdAssets.push({ mode: 'learn_mode', persona, avatar, interaction });
      }
      
      if (prompts.try_mode_prompt && personas.assess_mode_character) {
        const { persona, avatar } = await createPersonaAndAvatar(personas.assess_mode_character, 'try_mode');
        const interaction = await createAvatarInteraction('try_mode', prompts.try_mode_prompt, persona, avatar.id);
        createdAssets.push({ mode: 'try_mode', persona, avatar, interaction });
      }
      
      if (prompts.assess_mode_prompt && personas.assess_mode_character) {
        const { persona, avatar } = await createPersonaAndAvatar(personas.assess_mode_character, 'assess_mode');
        const interaction = await createAvatarInteraction('assess_mode', prompts.assess_mode_prompt, persona, avatar.id);
        createdAssets.push({ mode: 'assess_mode', persona, avatar, interaction });
      }
      
      // Create scenario with avatar interactions
      const scenarioData = {
        title: templateName,
        description: templateData?.context_overview?.purpose_of_scenario || 'Generated scenario',
        template_id: templateId,
        knowledge_base_id: templateData?.knowledge_base_id,
        learn_mode: createdAssets.find(a => a.mode === 'learn_mode') ? {
          avatar_interaction: createdAssets.find(a => a.mode === 'learn_mode').interaction.avatar_interaction_id,
          prompt: prompts.learn_mode_prompt
        } : null,
        try_mode: createdAssets.find(a => a.mode === 'try_mode') ? {
          avatar_interaction: createdAssets.find(a => a.mode === 'try_mode').interaction.avatar_interaction_id,
          prompt: prompts.try_mode_prompt
        } : null,
        assess_mode: createdAssets.find(a => a.mode === 'assess_mode') ? {
          avatar_interaction: createdAssets.find(a => a.mode === 'assess_mode').interaction.avatar_interaction_id,
          prompt: prompts.assess_mode_prompt
        } : null
      };

      if (!MODULE_ID) {
        throw new Error('Module ID is required in environment variables.');
      }
      
      // Create scenario using your existing scenario API
      const scenario = await apiCall(`/modules/${MODULE_ID}/scenarios`, 'POST', scenarioData);
      alert(`Scenario created successfully! 
Scenario ID: ${scenario.id}
Personas: ${createdAssets.length}
Avatars: ${createdAssets.length}
Interactions: ${createdAssets.length}`);
      
    } catch (error) {
      console.error('Error creating scenario:', error);
      alert('Error creating scenario: ' + error.message);
    }
    setLoading(false);
  };

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

  const createPersonaAndAvatar = async (personaData, mode) => {
    // Step 1: Create persona
    const persona = await apiCall('/personas/', 'POST', {
      name: personaData.name,
      description: personaData.description || 'Generated persona',
      persona_type: personaData.persona_type || 'character',
      gender: personaData.gender,
      age: personaData.age,
      character_goal: personaData.character_goal,
      location: personaData.location,
      persona_details: personaData.persona_details,
      situation: personaData.situation,
      business_or_personal: personaData.context_type || 'business',
      background_story: personaData.background_story
    });
    
    // Step 2: Create avatar with persona and visual preset
    const avatar = await apiCall('/avatars/', 'POST', {
      name: `${personaData.name} Avatar`,
      persona_id: [persona.id],
      gender: personaData.gender,
      thumbnail_url: null,
      fbx: AVATAR_PRESET.fbx,
      animation: AVATAR_PRESET.animation,
      glb: AVATAR_PRESET.glb,
      selected: AVATAR_PRESET.selected
    });
    
    return { persona, avatar };
  };

  const createAvatarInteraction = async (mode, prompt, persona, avatarId) => {
    const result = await apiCall('/avatar-interactions/', 'POST', {
      avatars: [avatarId],
      languages: ["ec489817-553a-4ef4-afb5-154f78f041b6"],
      bot_voices: ["dbb317a2-9891-4d72-b763-a8046ee1bcc8"],
      environments: ["8f0864ae-ec3a-4530-9329-937dc2d6bdbd"],
      bot_role: persona?.role || 'AI Character',
      bot_role_alt: persona?.name || 'Character',
      content: { persona: persona },
      system_prompt: prompt,
      layout: 1,
      mode: mode,
      assigned_documents: [],
      assigned_videos: [],
      archetype: templateData?.archetype_classification?.primary_archetype,
      archetype_sub_type: templateData?.archetype_classification?.sub_type,
      archetype_confidence: templateData?.archetype_classification?.confidence_score
    });
    return { mode, avatar_interaction_id: result.id };
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Scenario Creation Workflow</h1>
      
      {/* Progress indicator */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {[1,2,3,4,5].map(num => (
            <div key={num} className={`w-8 h-8 rounded-full flex items-center justify-center ${
              step >= num ? 'bg-blue-500 text-white' : 'bg-gray-300'
            }`}>
              {num}
            </div>
          ))}
        </div>
        <div className="flex justify-between text-sm mt-2">
          <span>Analyze</span>
          <span>Load</span>
          <span>Generate</span>
          <span>Update</span>
          <span>Create</span>
        </div>
      </div>

      {/* Step 1: Analyze Scenario */}
      {step === 1 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Step 1: Analyze Scenario</h2>
          <div>
            <label className="block text-sm font-medium mb-2">Template Name</label>
            <input
              type="text"
              value={templateName}
              onChange={(e) => setTemplateName(e.target.value)}
              className="w-full p-2 border rounded"
              placeholder="Enter template name"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Target Module ID</label>
            <input
              type="text"
              value={MODULE_ID || ''}
              disabled
              className="w-full p-2 border rounded bg-gray-100"
              placeholder="Module ID from environment variables"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Scenario Description</label>
            <textarea
              value={scenarioText}
              onChange={(e) => setScenarioText(e.target.value)}
              className="w-full p-2 border rounded h-32"
              placeholder="Describe your training scenario..."
            />
          </div>
          <button
            onClick={analyzeScenario}
            disabled={loading || !scenarioText || !templateName || !MODULE_ID}
            className="bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50"
          >
            {loading ? 'Analyzing...' : 'Analyze Scenario'}
          </button>
        </div>
      )}

      {/* Step 2: Load Template */}
      {step === 2 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Step 2: Template Created</h2>
          <div className="bg-green-50 p-4 rounded">
            <p>✅ Template created with ID: {templateId}</p>
            <p>Domain: {templateData?.general_info?.domain}</p>
            <p>Title: {templateData?.context_overview?.scenario_title}</p>
          </div>
          <button
            onClick={loadTemplate}
            disabled={loading}
            className="bg-blue-500 text-white px-4 py-2 rounded"
          >
            {loading ? 'Loading...' : 'Load Template for Editing'}
          </button>
        </div>
      )}

      {/* Step 3: Generate Prompts */}
      {step === 3 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Step 3: Template Details & Prompt Generation</h2>
          
          {/* Template Overview */}
          <div className="bg-blue-50 p-4 rounded">
            <h3 className="font-medium mb-2">Template Overview</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div><strong>Domain:</strong> {templateData?.general_info?.domain}</div>
              <div><strong>Archetype:</strong> {templateData?.archetype_classification?.primary_archetype}</div>
              <div><strong>Title:</strong> {templateData?.context_overview?.scenario_title}</div>
              <div><strong>Target Audience:</strong> {templateData?.general_info?.target_audience}</div>
            </div>
          </div>

          {/* Personas */}
          <div className="bg-gray-50 p-4 rounded">
            <h3 className="font-medium mb-2">Character Definitions</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="border p-3 rounded bg-white">
                <h4 className="font-medium text-green-600">Learn Mode Expert</h4>
                <p className="text-sm"><strong>Role:</strong> {templateData?.persona_definitions?.learn_mode_ai_bot?.role}</p>
                <p className="text-sm"><strong>Background:</strong> {templateData?.persona_definitions?.learn_mode_ai_bot?.background}</p>
              </div>
              <div className="border p-3 rounded bg-white">
                <h4 className="font-medium text-blue-600">Assess Mode Character</h4>
                <p className="text-sm"><strong>Role:</strong> {templateData?.persona_definitions?.assess_mode_ai_bot?.role}</p>
                <p className="text-sm"><strong>Age:</strong> {templateData?.persona_definitions?.assess_mode_ai_bot?.age}</p>
                <p className="text-sm"><strong>Location:</strong> {templateData?.persona_definitions?.assess_mode_ai_bot?.location}</p>
              </div>
            </div>
          </div>

          {/* Knowledge Base */}
          <div className="bg-yellow-50 p-4 rounded">
            <h3 className="font-medium mb-2">Knowledge Base</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <strong>Do's ({templateData?.knowledge_base?.dos?.length || 0}):</strong>
                <ul className="list-disc list-inside mt-1">
                  {templateData?.knowledge_base?.dos?.slice(0, 3).map((item, i) => (
                    <li key={i} className="truncate">{item}</li>
                  ))}
                  {templateData?.knowledge_base?.dos?.length > 3 && <li>...and {templateData.knowledge_base.dos.length - 3} more</li>}
                </ul>
              </div>
              <div>
                <strong>Don'ts ({templateData?.knowledge_base?.donts?.length || 0}):</strong>
                <ul className="list-disc list-inside mt-1">
                  {templateData?.knowledge_base?.donts?.slice(0, 3).map((item, i) => (
                    <li key={i} className="truncate">{item}</li>
                  ))}
                  {templateData?.knowledge_base?.donts?.length > 3 && <li>...and {templateData.knowledge_base.donts.length - 3} more</li>}
                </ul>
              </div>
            </div>
          </div>

          {/* Conversation Topics */}
          <div className="bg-green-50 p-4 rounded">
            <h3 className="font-medium mb-2">Conversation Topics ({templateData?.knowledge_base?.conversation_topics?.length || 0})</h3>
            <div className="flex flex-wrap gap-2">
              {templateData?.knowledge_base?.conversation_topics?.slice(0, 6).map((topic, i) => (
                <span key={i} className="bg-green-200 px-2 py-1 rounded text-sm">{topic}</span>
              ))}
              {templateData?.knowledge_base?.conversation_topics?.length > 6 && 
                <span className="bg-green-300 px-2 py-1 rounded text-sm">+{templateData.knowledge_base.conversation_topics.length - 6} more</span>
              }
            </div>
          </div>

          {/* Learning Objectives */}
          <div className="bg-purple-50 p-4 rounded">
            <h3 className="font-medium mb-2">Learning Objectives</h3>
            <ul className="list-disc list-inside text-sm">
              {templateData?.learning_objectives?.primary_objectives?.map((obj, i) => (
                <li key={i}>{obj}</li>
              ))}
            </ul>
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => generatePrompts(false)}
              disabled={loading}
              className="bg-blue-500 text-white px-4 py-2 rounded"
            >
              {loading ? 'Generating...' : 'Generate Prompts'}
            </button>
            <button
              onClick={() => generatePrompts(true)}
              disabled={loading}
              className="bg-orange-500 text-white px-4 py-2 rounded"
            >
              Skip Validation
            </button>
          </div>
        </div>
      )}

      {/* Step 4: Update Template */}
      {step === 4 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Step 4: Prompts Generated</h2>
          <div className="bg-green-50 p-4 rounded">
            <p>✅ Prompts generated successfully</p>
            <p>Learn Mode: {prompts?.learn_mode_prompt ? '✅' : '❌'}</p>
            <p>Try Mode: {prompts?.try_mode_prompt ? '✅' : '❌'}</p>
            <p>Assess Mode: {prompts?.assess_mode_prompt ? '✅' : '❌'}</p>
            <p>Personas: {personas ? '✅' : '❌'}</p>
          </div>
          <button
            onClick={updateTemplate}
            disabled={loading}
            className="bg-blue-500 text-white px-4 py-2 rounded"
          >
            {loading ? 'Updating...' : 'Update Template in DB'}
          </button>
        </div>
      )}

      {/* Step 5: Create Scenario */}
      {step === 5 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Step 5: Create Scenario</h2>
          <div className="bg-blue-50 p-4 rounded">
            <p>Template updated in database</p>
            <p>Ready to create avatars and scenario</p>
          </div>
          
          {/* Show personas */}
          {personas && (
            <div className="space-y-2">
              <h3 className="font-medium">Generated Personas:</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="border p-3 rounded">
                  <h4 className="font-medium">Learn Mode Expert</h4>
                  <p className="text-sm">{personas.learn_mode_expert?.name}</p>
                  <p className="text-xs text-gray-600">{personas.learn_mode_expert?.role}</p>
                </div>
                <div className="border p-3 rounded">
                  <h4 className="font-medium">Assess Mode Character</h4>
                  <p className="text-sm">{personas.assess_mode_character?.name}</p>
                  <p className="text-xs text-gray-600">{personas.assess_mode_character?.role}</p>
                </div>
              </div>
            </div>
          )}
          
          <button
            onClick={createScenario}
            disabled={loading}
            className="bg-green-500 text-white px-4 py-2 rounded"
          >
            {loading ? 'Creating...' : 'Create Scenario with Avatars'}
          </button>
        </div>
      )}
    </div>
  );
};

export default ScenarioWorkflow;