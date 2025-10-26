import React, { useState, useEffect } from 'react';

const ScenarioWorkflow = () => {
  // Main workflow states
  const [mode, setMode] = useState('create'); // 'create', 'edit', 'view', 'chat'
  const [step, setStep] = useState(1);
  const [templateId, setTemplateId] = useState(null);
  const [templateData, setTemplateData] = useState(null);
  const [prompts, setPrompts] = useState(null);
  const [personas, setPersonas] = useState(null);
  const [loading, setLoading] = useState(false);
  const [scenarioText, setScenarioText] = useState('');
  const [templateName, setTemplateName] = useState('');
  
  // New states for enhanced functionality
  const [scenarios, setScenarios] = useState([]);
  const [selectedScenario, setSelectedScenario] = useState(null);
  const [editingSection, setEditingSection] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatMode, setChatMode] = useState('learn_mode'); // 'learn_mode', 'try_mode', 'assess_mode'
  
  // Document upload states
  const [templateFile, setTemplateFile] = useState(null);
  const [supportingDocs, setSupportingDocs] = useState([]);
  const [uploadMethod, setUploadMethod] = useState('text'); // 'text', 'file', 'file_with_docs'
  
  const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:9000';
  const BEARER_TOKEN = process.env.REACT_APP_BEARER_TOKEN;
  const MODULE_ID = process.env.REACT_APP_MODULE_ID;
  const LANGUAGE_ID = process.env.REACT_APP_LANGUAGE_ID || "ec489817-553a-4ef4-afb5-154f78f041b6";
  const VOICE_ID = process.env.REACT_APP_VOICE_ID || "dbb317a2-9891-4d72-b763-a8046ee1bcc8";
  const ENVIRONMENT_ID = process.env.REACT_APP_ENVIRONMENT_ID || "8f0864ae-ec3a-4530-9329-937dc2d6bdbd";
  
  const apiCall = async (endpoint, method = 'GET', body = null, isFormData = false) => {
    const headers = { 'Authorization': `Bearer ${BEARER_TOKEN}` };
    if (!isFormData) headers['Content-Type'] = 'application/json';
    
    const options = { method, headers };
    if (body) options.body = isFormData ? body : JSON.stringify(body);
    
    const res = await fetch(`${API_BASE}${endpoint}`, options);
    if (!res.ok) throw new Error(`API Error: ${res.statusText}`);
    return res.json();
  };

  // Load scenarios on component mount
  useEffect(() => {
    if (mode === 'view' || mode === 'edit') {
      loadScenarios();
    }
  }, [mode]);

  // Load available scenarios
  const loadScenarios = async () => {
    setLoading(true);
    try {
      const result = await apiCall('/scenarios');
      setScenarios(result);
    } catch (error) {
      console.error('Error loading scenarios:', error);
      alert('Error loading scenarios: ' + error.message);
    }
    setLoading(false);
  };

  // Load specific scenario for editing
  const loadScenarioForEdit = async (scenarioId) => {
    setLoading(true);
    try {
      const result = await apiCall(`/scenarios/${scenarioId}/editing-interface`);
      setSelectedScenario(result.scenario);
      setTemplateData(result.template_data);
      setTemplateId(result.scenario.template_id);
      setTemplateName(result.scenario.title);
      setMode('edit');
    } catch (error) {
      console.error('Error loading scenario:', error);
      alert('Error loading scenario: ' + error.message);
    }
    setLoading(false);
  };

  // Save template changes
  const saveTemplateChanges = async () => {
    if (!selectedScenario || !templateData) return;
    
    setLoading(true);
    try {
      await apiCall(`/scenarios-editor/${selectedScenario.id}/template-data`, 'PUT', templateData);
      alert('Template changes saved successfully!');
    } catch (error) {
      console.error('Error saving changes:', error);
      alert('Error saving changes: ' + error.message);
    }
    setLoading(false);
  };

  // Regenerate scenario from template
  const regenerateScenario = async (modes = ['learn_mode', 'assess_mode', 'try_mode']) => {
    if (!selectedScenario) return;
    
    setLoading(true);
    try {
      const result = await apiCall(`/scenarios/${selectedScenario.id}/regenerate`, 'POST', {
        modes_to_regenerate: modes,
        regenerate_personas: true
      });
      alert('Scenario regenerated successfully!');
      setPrompts(result.generated_prompts);
      setPersonas(result.generated_personas);
    } catch (error) {
      console.error('Error regenerating scenario:', error);
      alert('Error regenerating scenario: ' + error.message);
    }
    setLoading(false);
  };

  // Start chat conversation
  const startChat = async (scenarioId, mode) => {
    setLoading(true);
    try {
      const scenario = await apiCall(`/scenarios/${scenarioId}/full`);
      setSelectedScenario(scenario);
      setChatMode(mode);
      setChatMessages([{
        role: 'system',
        content: `Starting ${mode.replace('_', ' ')} conversation. You can now chat with the AI character.`,
        timestamp: new Date().toISOString()
      }]);
      setMode('chat');
    } catch (error) {
      console.error('Error starting chat:', error);
      alert('Error starting chat: ' + error.message);
    }
    setLoading(false);
  };

  // Auto-scroll to bottom of chat
  const scrollToBottom = () => {
    const chatContainer = document.getElementById('chat-container');
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  };

  // Auto-scroll when messages change
  useEffect(() => {
    if (mode === 'chat') {
      setTimeout(scrollToBottom, 100);
    }
  }, [chatMessages, mode]);

  // Send chat message
  const sendChatMessage = async () => {
    if (!chatInput.trim() || !selectedScenario) return;
    
    const userMessage = {
      role: 'user',
      content: chatInput,
      timestamp: new Date().toISOString()
    };
    
    const currentInput = chatInput;
    setChatMessages(prev => [...prev, userMessage]);
    setChatInput('');
    setLoading(true);
    
    try {
      // Get avatar interaction ID for the current mode
      const avatarInteractionId = selectedScenario[chatMode]?.avatar_interaction;
      if (avatarInteractionId) {
        // Call the simple chat API
        const response = await apiCall(`/chat/${avatarInteractionId}`, 'POST', {
          message: currentInput,
          conversation_history: chatMessages
        });
        
        const aiMessage = {
          role: 'assistant',
          content: response.message,
          timestamp: new Date().toISOString()
        };
        
        setChatMessages(prev => [...prev, aiMessage]);
      } else {
        throw new Error(`No avatar interaction found for ${chatMode}`);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'system',
        content: 'Error: Could not send message. ' + error.message,
        timestamp: new Date().toISOString()
      };
      setChatMessages(prev => [...prev, errorMessage]);
    }
    setLoading(false);
  };

  // Update template section
  const updateTemplateSection = (sectionName, newData) => {
    setTemplateData(prev => ({
      ...prev,
      [sectionName]: {
        ...prev[sectionName],
        ...newData
      }
    }));
  };

  // Add/remove items from arrays in template
  // Handle file uploads
  const handleTemplateFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setTemplateFile(file);
      setTemplateName(file.name.replace(/\.[^/.]+$/, '')); // Remove extension
    }
  };

  const handleSupportingDocsChange = (e) => {
    setSupportingDocs(Array.from(e.target.files));
  };

  // Validation for step 1
  const isStep1Valid = () => {
    if (!templateName.trim()) return false;
    
    if (uploadMethod === 'text') {
      return scenarioText.trim().length > 0;
    } else if (uploadMethod === 'file') {
      return templateFile !== null;
    } else if (uploadMethod === 'file_with_docs') {
      return templateFile !== null;
    }
    
    return false;
  };

  const updateTemplateArray = (sectionName, arrayName, action, item, index = -1) => {
    setTemplateData(prev => {
      const section = prev[sectionName] || {};
      const array = section[arrayName] || [];
      
      let newArray;
      if (action === 'add') {
        newArray = [...array, item];
      } else if (action === 'remove' && index >= 0) {
        newArray = array.filter((_, i) => i !== index);
      } else if (action === 'edit' && index >= 0) {
        newArray = array.map((existing, i) => i === index ? item : existing);
      } else {
        newArray = array;
      }
      
      return {
        ...prev,
        [sectionName]: {
          ...section,
          [arrayName]: newArray
        }
      };
    });
  };

  // Step 1: Analyze scenario and create template (enhanced with file support)
  const analyzeScenario = async () => {
    setLoading(true);
    try {
      let result;
      
      if (uploadMethod === 'text') {
        // Text-based analysis (existing method)
        const formData = new FormData();
        formData.append('scenario_document', scenarioText);
        formData.append('template_name', templateName);
        
        // Add supporting docs if any
        supportingDocs.forEach((doc, index) => {
          formData.append('supporting_docs', doc);
        });
        
        result = await apiCall('/scenario/analyze-scenario-enhanced', 'POST', formData, true);
      } else if (uploadMethod === 'file') {
        // Single file upload
        if (!templateFile) {
          alert('Please select a template file');
          return;
        }
        
        const formData = new FormData();
        formData.append('file', templateFile);
        
        result = await apiCall('/scenario/file-to-template', 'POST', formData, true);
        result = { template_id: 'temp_' + Date.now(), template_data: result };
      } else if (uploadMethod === 'file_with_docs') {
        // Template file + supporting documents
        if (!templateFile) {
          alert('Please select a template file');
          return;
        }
        
        const formData = new FormData();
        formData.append('template_file', templateFile);
        formData.append('template_name', templateName);
        
        // Add supporting docs
        supportingDocs.forEach((doc) => {
          formData.append('supporting_docs', doc);
        });
        
        result = await apiCall('/scenario/analyze-template-with-optional-docs', 'POST', formData, true);
      }
      
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
      background_story: personaData.background_story,
      full_persona: personaData
    });
    
    // Step 2: Create avatar with persona and visual preset
    const avatar = await apiCall('/avatars/', 'POST', {
      name: `${personaData.name} Avatar`,
      persona_id: [persona.id],
      gender: personaData.gender,
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
      languages: [LANGUAGE_ID],
      bot_voices: [VOICE_ID],
      environments: [ENVIRONMENT_ID],
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
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Scenario Management System</h1>
      
      {/* Mode Navigation */}
      <div className="mb-6">
        <div className="flex space-x-4 border-b">
          <button
            onClick={() => { setMode('create'); setStep(1); }}
            className={`px-4 py-2 font-medium ${
              mode === 'create' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-600'
            }`}
          >
            Create New Scenario
          </button>
          <button
            onClick={() => setMode('view')}
            className={`px-4 py-2 font-medium ${
              mode === 'view' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-600'
            }`}
          >
            View Scenarios
          </button>
          <button
            onClick={() => setMode('edit')}
            className={`px-4 py-2 font-medium ${
              mode === 'edit' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-600'
            }`}
          >
            Edit Templates
          </button>
          <button
            onClick={() => setMode('chat')}
            className={`px-4 py-2 font-medium ${
              mode === 'chat' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-600'
            }`}
          >
            Test Conversations
          </button>
        </div>
      </div>

      {/* Progress indicator - only show in create mode */}
      {mode === 'create' && (
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
      )}

      {/* View Scenarios Mode */}
      {mode === 'view' && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Available Scenarios</h2>
          
          {loading ? (
            <div className="text-center py-8">Loading scenarios...</div>
          ) : scenarios.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No scenarios found. Create your first scenario!
            </div>
          ) : (
            <div className="grid gap-4">
              {scenarios.map((scenario) => (
                <div key={scenario.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg">{scenario.title}</h3>
                      <p className="text-gray-600 text-sm mb-2">{scenario.description}</p>
                      <div className="flex space-x-4 text-sm text-gray-500">
                        <span>Created: {new Date(scenario.created_at).toLocaleDateString()}</span>
                        {scenario.updated_at && (
                          <span>Updated: {new Date(scenario.updated_at).toLocaleDateString()}</span>
                        )}
                      </div>
                      
                      {/* Available modes */}
                      <div className="mt-2 flex space-x-2">
                        {scenario.learn_mode && (
                          <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">Learn</span>
                        )}
                        {scenario.try_mode && (
                          <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">Try</span>
                        )}
                        {scenario.assess_mode && (
                          <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded">Assess</span>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex flex-col space-y-2 ml-4">
                      <button
                        onClick={() => loadScenarioForEdit(scenario.id)}
                        className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
                      >
                        Edit
                      </button>
                      
                      {/* Chat buttons for each mode */}
                      <div className="flex flex-col space-y-1">
                        {scenario.learn_mode && (
                          <button
                            onClick={() => startChat(scenario.id, 'learn_mode')}
                            className="px-3 py-1 bg-green-500 text-white text-xs rounded hover:bg-green-600"
                          >
                            Chat: Learn
                          </button>
                        )}
                        {scenario.try_mode && (
                          <button
                            onClick={() => startChat(scenario.id, 'try_mode')}
                            className="px-3 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600"
                          >
                            Chat: Try
                          </button>
                        )}
                        {scenario.assess_mode && (
                          <button
                            onClick={() => startChat(scenario.id, 'assess_mode')}
                            className="px-3 py-1 bg-purple-500 text-white text-xs rounded hover:bg-purple-600"
                          >
                            Chat: Assess
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Template Editing Mode */}
      {mode === 'edit' && templateData && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Edit Template: {templateName}</h2>
            <div className="space-x-2">
              <button
                onClick={saveTemplateChanges}
                disabled={loading}
                className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
              >
                {loading ? 'Saving...' : 'Save Changes'}
              </button>
              <button
                onClick={() => regenerateScenario()}
                disabled={loading}
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
              >
                {loading ? 'Regenerating...' : 'Regenerate Prompts'}
              </button>
            </div>
          </div>

          {/* Template Sections */}
          <div className="grid gap-6">
            {/* General Info Section */}
            <div className="border rounded-lg p-4">
              <h3 className="font-medium mb-3 flex justify-between items-center">
                General Information
                <button
                  onClick={() => setEditingSection(editingSection === 'general_info' ? null : 'general_info')}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  {editingSection === 'general_info' ? 'Cancel' : 'Edit'}
                </button>
              </h3>
              
              {editingSection === 'general_info' ? (
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium mb-1">Domain</label>
                    <input
                      type="text"
                      value={templateData.general_info?.domain || ''}
                      onChange={(e) => updateTemplateSection('general_info', { domain: e.target.value })}
                      className="w-full p-2 border rounded"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Target Audience</label>
                    <input
                      type="text"
                      value={templateData.general_info?.target_audience || ''}
                      onChange={(e) => updateTemplateSection('general_info', { target_audience: e.target.value })}
                      className="w-full p-2 border rounded"
                    />
                  </div>
                  <button
                    onClick={() => setEditingSection(null)}
                    className="px-3 py-1 bg-green-500 text-white rounded text-sm"
                  >
                    Done
                  </button>
                </div>
              ) : (
                <div className="text-sm space-y-1">
                  <div><strong>Domain:</strong> {templateData.general_info?.domain}</div>
                  <div><strong>Target Audience:</strong> {templateData.general_info?.target_audience}</div>
                </div>
              )}
            </div>

            {/* Knowledge Base Section */}
            <div className="border rounded-lg p-4">
              <h3 className="font-medium mb-3 flex justify-between items-center">
                Knowledge Base
                <button
                  onClick={() => setEditingSection(editingSection === 'knowledge_base' ? null : 'knowledge_base')}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  {editingSection === 'knowledge_base' ? 'Cancel' : 'Edit'}
                </button>
              </h3>
              
              {editingSection === 'knowledge_base' ? (
                <div className="space-y-4">
                  {/* Do's */}
                  <div>
                    <label className="block text-sm font-medium mb-2">Do's</label>
                    {(templateData.knowledge_base?.dos || []).map((item, index) => (
                      <div key={index} className="flex items-center space-x-2 mb-2">
                        <input
                          type="text"
                          value={item}
                          onChange={(e) => updateTemplateArray('knowledge_base', 'dos', 'edit', e.target.value, index)}
                          className="flex-1 p-2 border rounded text-sm"
                        />
                        <button
                          onClick={() => updateTemplateArray('knowledge_base', 'dos', 'remove', null, index)}
                          className="px-2 py-1 bg-red-500 text-white rounded text-xs"
                        >
                          Remove
                        </button>
                      </div>
                    ))}
                    <button
                      onClick={() => updateTemplateArray('knowledge_base', 'dos', 'add', 'New best practice')}
                      className="px-3 py-1 bg-green-500 text-white rounded text-sm"
                    >
                      Add Do
                    </button>
                  </div>
                  
                  {/* Don'ts */}
                  <div>
                    <label className="block text-sm font-medium mb-2">Don'ts</label>
                    {(templateData.knowledge_base?.donts || []).map((item, index) => (
                      <div key={index} className="flex items-center space-x-2 mb-2">
                        <input
                          type="text"
                          value={item}
                          onChange={(e) => updateTemplateArray('knowledge_base', 'donts', 'edit', e.target.value, index)}
                          className="flex-1 p-2 border rounded text-sm"
                        />
                        <button
                          onClick={() => updateTemplateArray('knowledge_base', 'donts', 'remove', null, index)}
                          className="px-2 py-1 bg-red-500 text-white rounded text-xs"
                        >
                          Remove
                        </button>
                      </div>
                    ))}
                    <button
                      onClick={() => updateTemplateArray('knowledge_base', 'donts', 'add', 'New thing to avoid')}
                      className="px-3 py-1 bg-green-500 text-white rounded text-sm"
                    >
                      Add Don't
                    </button>
                  </div>
                  
                  <button
                    onClick={() => setEditingSection(null)}
                    className="px-3 py-1 bg-green-500 text-white rounded text-sm"
                  >
                    Done
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <strong>Do's ({(templateData.knowledge_base?.dos || []).length}):</strong>
                    <ul className="list-disc list-inside mt-1">
                      {(templateData.knowledge_base?.dos || []).slice(0, 3).map((item, i) => (
                        <li key={i} className="truncate">{item}</li>
                      ))}
                      {(templateData.knowledge_base?.dos || []).length > 3 && (
                        <li>...and {templateData.knowledge_base.dos.length - 3} more</li>
                      )}
                    </ul>
                  </div>
                  <div>
                    <strong>Don'ts ({(templateData.knowledge_base?.donts || []).length}):</strong>
                    <ul className="list-disc list-inside mt-1">
                      {(templateData.knowledge_base?.donts || []).slice(0, 3).map((item, i) => (
                        <li key={i} className="truncate">{item}</li>
                      ))}
                      {(templateData.knowledge_base?.donts || []).length > 3 && (
                        <li>...and {templateData.knowledge_base.donts.length - 3} more</li>
                      )}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Chat/Conversation Mode */}
      {mode === 'chat' && selectedScenario && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">
              Chat: {selectedScenario.title} ({chatMode.replace('_', ' ')})
            </h2>
            <div className="flex space-x-2">
              <select
                value={chatMode}
                onChange={(e) => setChatMode(e.target.value)}
                className="px-3 py-1 border rounded"
              >
                {selectedScenario.learn_mode && <option value="learn_mode">Learn Mode</option>}
                {selectedScenario.try_mode && <option value="try_mode">Try Mode</option>}
                {selectedScenario.assess_mode && <option value="assess_mode">Assess Mode</option>}
              </select>
              <button
                onClick={() => setChatMessages([])}
                className="px-3 py-1 bg-gray-500 text-white rounded text-sm"
              >
                Clear Chat
              </button>
              <button
                onClick={() => setMode('view')}
                className="px-3 py-1 bg-blue-500 text-white rounded text-sm"
              >
                Back to Scenarios
              </button>
            </div>
          </div>

          {/* Chat Messages */}
          <div className="border rounded-lg p-4 h-96 overflow-y-auto bg-gray-50">
            {chatMessages.length === 0 ? (
              <div className="text-center text-gray-500 mt-20">
                Start a conversation by typing a message below
              </div>
            ) : (
              <div className="space-y-3">
                {chatMessages.map((message, index) => (
                  <div key={index} className={`flex ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}>
                    <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      message.role === 'user' 
                        ? 'bg-blue-500 text-white' 
                        : message.role === 'assistant'
                        ? 'bg-white border'
                        : 'bg-yellow-100 border-yellow-300'
                    }`}>
                      <div className="text-sm">{message.content}</div>
                      <div className="text-xs opacity-70 mt-1">
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Chat Input */}
          <div className="flex space-x-2">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendChatMessage();
                }
              }}
              placeholder={`Type your message to the ${chatMode.replace('_', ' ')} character...`}
              className="flex-1 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={loading}
            />
            <button
              onClick={sendChatMessage}
              disabled={loading || !chatInput.trim()}
              className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Sending...</span>
                </div>
              ) : (
                'Send'
              )}
            </button>
          </div>
          
          {/* Chat Instructions */}
          <div className="text-xs text-gray-500 bg-gray-100 p-3 rounded">
            <strong>💡 Tips:</strong> 
            • Press Enter to send your message
            • Switch between modes using the dropdown above
            • The AI character will respond based on the scenario and mode
            • Use "Clear Chat" to start fresh
          </div>
        </div>
      )}
      
      {/* Loading Overlay */}
      {loading && mode !== 'chat' && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg">
            <div className="flex items-center space-x-3">
              <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              <span>Processing...</span>
            </div>
          </div>
        </div>
      )}

      {/* Create Mode - Step 1: Analyze Scenario */}
      {mode === 'create' && step === 1 && (
        <div className="space-y-6">
          <h2 className="text-xl font-semibold">Step 1: Create Your Training Scenario</h2>
          
          {/* Upload Method Selection */}
          <div>
            <label className="block text-sm font-medium mb-3">How would you like to create your scenario?</label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <label className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
                uploadMethod === 'text' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
              }`}>
                <input
                  type="radio"
                  value="text"
                  checked={uploadMethod === 'text'}
                  onChange={(e) => setUploadMethod(e.target.value)}
                  className="sr-only"
                />
                <div className="text-center">
                  <div className="text-2xl mb-2">📝</div>
                  <div className="font-medium">Text Description</div>
                  <div className="text-sm text-gray-600 mt-1">Describe your scenario in text</div>
                </div>
              </label>
              
              <label className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
                uploadMethod === 'file' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
              }`}>
                <input
                  type="radio"
                  value="file"
                  checked={uploadMethod === 'file'}
                  onChange={(e) => setUploadMethod(e.target.value)}
                  className="sr-only"
                />
                <div className="text-center">
                  <div className="text-2xl mb-2">📄</div>
                  <div className="font-medium">Upload Template File</div>
                  <div className="text-sm text-gray-600 mt-1">Upload a Word/PDF template</div>
                </div>
              </label>
              
              <label className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
                uploadMethod === 'file_with_docs' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
              }`}>
                <input
                  type="radio"
                  value="file_with_docs"
                  checked={uploadMethod === 'file_with_docs'}
                  onChange={(e) => setUploadMethod(e.target.value)}
                  className="sr-only"
                />
                <div className="text-center">
                  <div className="text-2xl mb-2">📚</div>
                  <div className="font-medium">Template + Knowledge Base</div>
                  <div className="text-sm text-gray-600 mt-1">Upload template with supporting docs</div>
                </div>
              </label>
            </div>
          </div>
          
          {/* Template Name */}
          <div>
            <label className="block text-sm font-medium mb-2">Template Name</label>
            <input
              type="text"
              value={templateName}
              onChange={(e) => setTemplateName(e.target.value)}
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter template name"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Target Module ID</label>
            <input
              type="text"
              value={MODULE_ID || ''}
              disabled
              className="w-full p-3 border rounded-lg bg-gray-100"
              placeholder="Module ID from environment variables"
            />
          </div>
          
          {/* Text Method */}
          {uploadMethod === 'text' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Scenario Description</label>
                <textarea
                  value={scenarioText}
                  onChange={(e) => setScenarioText(e.target.value)}
                  className="w-full p-3 border rounded-lg h-32 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Describe your training scenario in detail..."
                />
              </div>
              
              {/* Optional supporting docs for text method */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <label className="block text-sm font-medium mb-2">Supporting Documents (Optional)</label>
                <input
                  type="file"
                  multiple
                  onChange={handleSupportingDocsChange}
                  accept=".pdf,.doc,.docx,.txt"
                  className="w-full p-2 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-400 focus:border-blue-500"
                />
                {supportingDocs.length > 0 && (
                  <div className="mt-3 space-y-2">
                    <div className="text-sm font-medium text-gray-700">Selected files:</div>
                    {supportingDocs.map((file, index) => (
                      <div key={index} className="flex items-center justify-between bg-white p-2 rounded border">
                        <span className="text-sm">📎 {file.name}</span>
                        <span className="text-xs text-gray-500">({(file.size / 1024).toFixed(1)} KB)</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
          
          {/* File Method */}
          {uploadMethod === 'file' && (
            <div>
              <label className="block text-sm font-medium mb-2">Template File</label>
              <input
                type="file"
                onChange={handleTemplateFileChange}
                accept=".pdf,.doc,.docx,.txt"
                className="w-full p-3 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-400 focus:border-blue-500"
              />
              {templateFile && (
                <div className="mt-3 bg-blue-50 p-3 rounded-lg">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">📄 {templateFile.name}</span>
                    <span className="text-xs text-gray-600">({(templateFile.size / 1024).toFixed(1)} KB)</span>
                  </div>
                </div>
              )}
            </div>
          )}
          
          {/* File + Docs Method */}
          {uploadMethod === 'file_with_docs' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Template File</label>
                <input
                  type="file"
                  onChange={handleTemplateFileChange}
                  accept=".pdf,.doc,.docx,.txt"
                  className="w-full p-3 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-400 focus:border-blue-500"
                />
                {templateFile && (
                  <div className="mt-3 bg-blue-50 p-3 rounded-lg">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">📄 {templateFile.name}</span>
                      <span className="text-xs text-gray-600">({(templateFile.size / 1024).toFixed(1)} KB)</span>
                    </div>
                  </div>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Supporting Documents</label>
                <input
                  type="file"
                  multiple
                  onChange={handleSupportingDocsChange}
                  accept=".pdf,.doc,.docx,.txt"
                  className="w-full p-3 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-400 focus:border-blue-500"
                />
                {supportingDocs.length > 0 && (
                  <div className="mt-3 space-y-2">
                    <div className="text-sm font-medium text-gray-700">Knowledge base documents ({supportingDocs.length}):</div>
                    {supportingDocs.map((file, index) => (
                      <div key={index} className="flex items-center justify-between bg-white p-2 rounded border">
                        <span className="text-sm">📎 {file.name}</span>
                        <span className="text-xs text-gray-500">({(file.size / 1024).toFixed(1)} KB)</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
          
          <button
            onClick={analyzeScenario}
            disabled={loading || !isStep1Valid() || !MODULE_ID}
            className="w-full bg-blue-500 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <div className="flex items-center justify-center space-x-2">
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Processing...</span>
              </div>
            ) : (
              'Create Template'
            )}
          </button>
          
          {/* Help text */}
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="text-sm text-blue-800">
              <strong>💡 Tips:</strong>
              <ul className="mt-2 space-y-1 list-disc list-inside">
                <li><strong>Text Description:</strong> Best for quick scenario creation from your ideas</li>
                <li><strong>Template File:</strong> Upload existing Word/PDF templates to convert them</li>
                <li><strong>Template + Knowledge Base:</strong> Upload template with supporting documents for fact-checking and enhanced AI responses</li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Create Mode - Step 2: Load Template */}
      {mode === 'create' && step === 2 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Step 2: Template Created</h2>
          <div className="bg-green-50 p-4 rounded">
            <p>✅ Template created with ID: {templateId}</p>
            <p>Domain: {templateData?.general_info?.domain}</p>
            <p>Title: {templateData?.context_overview?.scenario_title}</p>
            {templateData?.knowledge_base_id && (
              <p>📚 Knowledge Base: {templateData.supporting_documents_count} documents indexed</p>
            )}
            {templateData?.has_supporting_docs && (
              <p>🔍 Fact-checking enabled with supporting documents</p>
            )}
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

      {/* Create Mode - Step 3: Generate Prompts */}
      {mode === 'create' && step === 3 && (
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

      {/* Create Mode - Step 4: Update Template */}
      {mode === 'create' && step === 4 && (
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

      {/* Create Mode - Step 5: Create Scenario */}
      {mode === 'create' && step === 5 && (
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