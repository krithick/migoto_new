import React, { useState, useCallback } from 'react';
import axios from 'axios';

// Configuration - Update these values
const API_BASE_URL = 'http://172.23.198.149:9000'; // Change to your API URL
const BEARER_TOKEN = 'your-bearer-token-here'; // Add your bearer token

interface ExtractedData {
  scenario_understanding: {
    main_topic: string;
    learning_situation: string;
    target_skills: string[];
    key_challenges: string;
    extraction_source?: string;
  };
  knowledge_base: {
    dos: string[];
    donts: string[];
    key_facts: string[];
    conversation_topics: string[];
    extraction_source?: string;
  };
  coaching_rules: {
    process_requirements: {
      mentioned_methodology: string;
      required_steps: string;
      validation_criteria: string;
    };
    correction_preferences: {
      preferred_tone: string;
      feedback_timing: string;
      correction_method: string;
    };
    extraction_source?: string;
  };
  success_metrics: {
    kpis_for_interaction: string[];
    learning_objectives: string;
    evaluation_criteria: string[];
    extraction_source?: string;
  };
  variations_challenges: {
    scenario_variations: string[];
    edge_cases: string[];
    difficulty_levels: string[];
    extraction_source?: string;
  };
  feedback_mechanism: {
    positive_closing: string;
    negative_closing: string;
    neutral_closing: string;
    extraction_source?: string;
  };
  participant_roles: {
    learner_role: string;
    expert_role: string;
    practice_role: string;
    extraction_source?: string;
  };
  conversation_dynamics: {
    learn_mode_purpose: string;
    practice_mode_purpose: string;
    typical_interactions: string[];
    success_looks_like: string;
    failure_patterns: string[];
    extraction_source?: string;
  };
  content_specifics: {
    key_knowledge: string[];
    procedures_mentioned: string[];
    policies_referenced: string[];
    examples_given: string[];
    extraction_source?: string;
  };
  conversation_examples?: {
    dialogue_samples: string[];
    question_patterns: string[];
    response_patterns: string[];
    extraction_source?: string;
  };
  knowledge_base_integration?: {
    requires_knowledge_base: string;
    fact_checking_areas: string[];
    accuracy_requirements: string;
    extraction_source?: string;
  };
}

interface ValidationData {
  validated_extraction: ExtractedData;
  template_enhancements: {
    persona_suggestions: {
      expert_persona: string;
      practice_persona: string;
      extraction_source?: string;
    };
    conversation_flows: {
      learn_mode_flow: string;
      practice_mode_flow: string;
      extraction_source?: string;
    };
    feedback_mechanisms: {
      positive_responses: string[];
      negative_responses: string[];
      neutral_responses: string[];
      extraction_source?: string;
    };
    extraction_source?: string;
  };
  validation_notes: {
    completeness_score: string;
    missing_elements: string[];
    suggestions: string[];
  };
}

interface Template {
  template_id: string;
  template_name: string;
  source_type: 'document' | 'prompt';
  extracted_data: ExtractedData;
  validated_data: ValidationData;
  status: string;
}

interface GeneratedScenario {
  scenario_id: string;
  learn_mode: string;
  assess_mode: string;
  try_mode: string;
  recommended_personas: {
    learn_mode_personas: Array<{
      name: string;
      description: string;
      persona_type: string;
      gender: string;
      age: number;
      character_goal: string;
      location: string;
      persona_details: string;
      situation: string;
      business_or_personal: string;
      background_story: string;
    }>;
    practice_mode_personas: Array<{
      name: string;
      description: string;
      persona_type: string;
      gender: string;
      age: number;
      character_goal: string;
      location: string;
      persona_details: string;
      situation: string;
      business_or_personal: string;
      background_story: string;
      sample_opener: string;
    }>;
  };
  scenario_metadata: {
    title: string;
    domain: string;
    difficulty: string;
  };
}

const FlexibleScenarioGenerator: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'upload' | 'prompt'>('upload');
  const [file, setFile] = useState<File | null>(null);
  const [templateName, setTemplateName] = useState('');
  const [promptText, setPromptText] = useState('');
  const [loading, setLoading] = useState(false);
  const [extractedDetails, setExtractedDetails] = useState<any>(null);
  const [template, setTemplate] = useState<Template | null>(null);
  const [generatedScenario, setGeneratedScenario] = useState<GeneratedScenario | null>(null);
  const [editMode, setEditMode] = useState(false);
  const [editedData, setEditedData] = useState<ExtractedData | null>(null);
  const [individualPrompt, setIndividualPrompt] = useState<{type: string, content: string} | null>(null);
  const [previewPrompt, setPreviewPrompt] = useState<{type: string, content: string} | null>(null);
  const [currentStep, setCurrentStep] = useState<'upload' | 'extracted' | 'template' | 'scenarios'>('upload');
  const [conversationSim, setConversationSim] = useState<any>(null);
  const [selectedPersona, setSelectedPersona] = useState<any>(null);

  const handleFileUpload = useCallback(async () => {
    if (!file || !templateName.trim()) {
      alert('Please select a file and enter a template name');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('template_name', templateName);

    try {
      const response = await axios.post(`${API_BASE_URL}/flexible/analyze-document`, formData, {
        headers: { 
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${BEARER_TOKEN}`
        }
      });
      
      setExtractedDetails({
        template_id: response.data.template_id,
        extracted_data: response.data.extracted_data,
        validation_score: response.data.validation_score,
        missing_elements: response.data.missing_elements,
        suggestions: response.data.suggestions
      });
      setCurrentStep('extracted');
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Error analyzing document');
    } finally {
      setLoading(false);
    }
  }, [file, templateName]);

  const handlePromptAnalysis = useCallback(async () => {
    if (!promptText.trim() || !templateName.trim()) {
      alert('Please enter both prompt text and template name');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/flexible/analyze-prompt`, {
        scenario_prompt: promptText,
        template_name: templateName
      }, {
        headers: { 'Authorization': `Bearer ${BEARER_TOKEN}` }
      });
      
      const templateId = response.data.template_id;
      const templateResponse = await axios.get(`${API_BASE_URL}/flexible/template/${templateId}`, {
        headers: { 'Authorization': `Bearer ${BEARER_TOKEN}` }
      });
      setTemplate(templateResponse.data);
      setEditedData(templateResponse.data.extracted_data);
    } catch (error) {
      console.error('Error analyzing prompt:', error);
      alert('Error analyzing prompt');
    } finally {
      setLoading(false);
    }
  }, [promptText, templateName]);

  const handleSaveTemplate = useCallback(async () => {
    if (!template || !editedData) return;

    setLoading(true);
    try {
      await axios.put(`${API_BASE_URL}/flexible/template/${template.template_id}`, editedData, {
        headers: { 'Authorization': `Bearer ${BEARER_TOKEN}` }
      });
      setEditMode(false);
      alert('Template updated successfully');
    } catch (error) {
      console.error('Error saving template:', error);
      alert('Error saving template');
    } finally {
      setLoading(false);
    }
  }, [template, editedData]);

  const handleApproveTemplate = useCallback(async () => {
    if (!template) return;

    setLoading(true);
    try {
      await axios.post(`${API_BASE_URL}/flexible/approve-template/${template.template_id}`, {}, {
        headers: { 'Authorization': `Bearer ${BEARER_TOKEN}` }
      });
      setTemplate(prev => prev ? { ...prev, status: 'approved' } : null);
      alert('Template approved successfully');
    } catch (error) {
      console.error('Error approving template:', error);
      alert('Error approving template');
    } finally {
      setLoading(false);
    }
  }, [template]);

  const handleGenerateScenarios = useCallback(async () => {
    if (!template) return;

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/flexible/generate-scenarios/${template.template_id}`, {}, {
        headers: { 'Authorization': `Bearer ${BEARER_TOKEN}` }
      });
      setGeneratedScenario(response.data.scenarios);
      setIndividualPrompt(null);
      setPreviewPrompt(null);
    } catch (error) {
      console.error('Error generating scenarios:', error);
      alert('Error generating scenarios');
    } finally {
      setLoading(false);
    }
  }, [template]);

  const handleGenerateIndividualPrompt = useCallback(async (promptType: string) => {
    if (!template) return;

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/flexible/generate-prompt/${template.template_id}`, {
        prompt_type: promptType
      }, {
        headers: { 'Authorization': `Bearer ${BEARER_TOKEN}` }
      });
      setIndividualPrompt({
        type: promptType,
        content: response.data.generated_prompt
      });
      setGeneratedScenario(null);
      setPreviewPrompt(null);
    } catch (error) {
      console.error('Error generating individual prompt:', error);
      alert('Error generating individual prompt');
    } finally {
      setLoading(false);
    }
  }, [template]);

  const handlePreviewPrompt = useCallback(async (promptType: string) => {
    if (!template) return;

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/flexible/preview-prompt/${template.template_id}`, {
        prompt_type: promptType
      }, {
        headers: { 'Authorization': `Bearer ${BEARER_TOKEN}` }
      });
      setPreviewPrompt({
        type: promptType,
        content: response.data.preview_prompt
      });
      setGeneratedScenario(null);
      setIndividualPrompt(null);
    } catch (error) {
      console.error('Error previewing prompt:', error);
      alert('Error previewing prompt');
    } finally {
      setLoading(false);
    }
  }, [template]);

  const handleSimulateConversation = useCallback(async (persona: any, mode: string = 'assess_mode') => {
    if (!template) return;

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/flexible/simulate-conversation/${template.template_id}`, {
        persona_details: {
          name: String(persona.name || 'Test Persona'),
          description: String(persona.description || 'Leadership scenario participant'),
          persona_type: String(persona.persona_type || 'Workplace Issue Participant'),
          gender: String(persona.gender || 'Female'),
          age: String(persona.age || 35),
          character_goal: String(persona.character_goal || 'Seek guidance on workplace leadership issues'),
          location: String(persona.location || 'Corporate Office'),
          persona_details: String(persona.persona_details || 'Professional seeking leadership guidance'),
          situation: String(persona.situation || 'Workplace leadership challenge'),
          business_or_personal: String(persona.business_or_personal || 'business'),
          background_story: String(persona.background_story || 'Experiencing workplace leadership challenges and needs guidance')
        },
        mode: mode
      }, {
        headers: { 
          'Authorization': `Bearer ${BEARER_TOKEN}`,
          'Content-Type': 'application/json'
        }
      });
      setConversationSim(response.data.simulation);
      setSelectedPersona(persona);
    } catch (error) {
      console.error('Error simulating conversation:', error);
      console.error('Error details:', error.response?.data);
      alert(`Error simulating conversation: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  }, [template]);

  const updateEditedField = (path: string, value: any) => {
    if (!editedData) return;
    
    const pathArray = path.split('.');
    const newData = { ...editedData };
    let current: any = newData;
    
    for (let i = 0; i < pathArray.length - 1; i++) {
      current = current[pathArray[i]];
    }
    current[pathArray[pathArray.length - 1]] = value;
    
    setEditedData(newData);
  };

  return (
    <div className="max-w-6xl mx-auto p-6 bg-white">
      <h1 className="text-3xl font-bold text-gray-800 mb-8">Flexible Scenario Generator</h1>
      
      {/* Step 1: Upload */}
      {currentStep === 'upload' && (
        <div className="bg-gray-50 rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Step 1: Create Template</h2>
          
          <div className="flex mb-4">
            <button
              onClick={() => setActiveTab('upload')}
              className={`px-4 py-2 mr-2 rounded ${activeTab === 'upload' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
            >
              Upload Document
            </button>
            <button
              onClick={() => setActiveTab('prompt')}
              className={`px-4 py-2 rounded ${activeTab === 'prompt' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
            >
              Text Prompt
            </button>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Template Name</label>
            <input
              type="text"
              value={templateName}
              onChange={(e) => setTemplateName(e.target.value)}
              className="w-full p-3 border rounded-lg"
              placeholder="Enter template name"
            />
          </div>

          {activeTab === 'upload' ? (
            <div>
              <label className="block text-sm font-medium mb-2">Upload Document</label>
              <input
                type="file"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                accept=".pdf,.doc,.docx,.txt"
                className="w-full p-3 border rounded-lg"
              />
              <button
                onClick={handleFileUpload}
                disabled={loading}
                className="mt-4 bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50"
              >
                {loading ? 'Analyzing...' : 'Analyze Document'}
              </button>
            </div>
          ) : (
            <div>
              <label className="block text-sm font-medium mb-2">Scenario Description</label>
              <textarea
                value={promptText}
                onChange={(e) => setPromptText(e.target.value)}
                className="w-full p-3 border rounded-lg h-32"
                placeholder="Describe your training scenario..."
              />
              <button
                onClick={handlePromptAnalysis}
                disabled={loading}
                className="mt-4 bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50"
              >
                {loading ? 'Analyzing...' : 'Analyze Prompt'}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Step 2: Show Extracted Details */}
      {currentStep === 'extracted' && extractedDetails && (
        <div className="bg-gray-50 rounded-lg p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Step 2: Extracted Details</h2>
            <div className="flex gap-2">
              <button
                onClick={async () => {
                  setLoading(true);
                  try {
                    const templateResponse = await axios.get(`${API_BASE_URL}/flexible/template/${extractedDetails.template_id}`, {
                      headers: { 'Authorization': `Bearer ${BEARER_TOKEN}` }
                    });
                    setTemplate(templateResponse.data);
                    setEditedData(templateResponse.data.extracted_data);
                    setCurrentStep('template');
                  } catch (error) {
                    alert('Error loading template');
                  } finally {
                    setLoading(false);
                  }
                }}
                disabled={loading}
                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50"
              >
                {loading ? 'Loading...' : 'Generate Template'}
              </button>
            </div>
          </div>

          <div className="bg-white p-4 rounded border mb-4">
            <h3 className="font-semibold mb-3">Extraction Summary</h3>
            <div className="grid grid-cols-3 gap-4">
              <div><strong>Score:</strong> {extractedDetails.validation_score}</div>
              <div><strong>Missing:</strong> {extractedDetails.missing_elements?.length || 0}</div>
              <div><strong>ID:</strong> {extractedDetails.template_id}</div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
            {extractedDetails.extracted_data?.scenario_understanding && (
              <div className="bg-white p-4 rounded border">
                <h3 className="font-semibold mb-3">Scenario Understanding</h3>
                <p><strong>Topic:</strong> {extractedDetails.extracted_data.scenario_understanding.main_topic}</p>
                <p><strong>Skills:</strong> {extractedDetails.extracted_data.scenario_understanding.target_skills?.length || 0}</p>
              </div>
            )}
            {extractedDetails.extracted_data?.participant_roles && (
              <div className="bg-white p-4 rounded border">
                <h3 className="font-semibold mb-3">Participant Roles</h3>
                <p><strong>Expert:</strong> {extractedDetails.extracted_data.participant_roles.expert_role}</p>
                <p><strong>Practice:</strong> {extractedDetails.extracted_data.participant_roles.practice_role}</p>
              </div>
            )}
            {extractedDetails.extracted_data?.knowledge_base && (
              <div className="bg-white p-4 rounded border">
                <h3 className="font-semibold mb-3">Knowledge Base</h3>
                <p><strong>Do's:</strong> {extractedDetails.extracted_data.knowledge_base.dos?.length || 0}</p>
                <p><strong>Don'ts:</strong> {extractedDetails.extracted_data.knowledge_base.donts?.length || 0}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Step 3: Review & Edit Template */}
      {currentStep === 'template' && template && !generatedScenario && (
        <div className="bg-gray-50 rounded-lg p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Step 3: Review & Edit Template</h2>
            <div className="flex gap-2">
              <button
                onClick={() => setEditMode(!editMode)}
                className="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600"
              >
                {editMode ? 'Cancel Edit' : 'Edit Template'}
              </button>
              {editMode && (
                <button
                  onClick={handleSaveTemplate}
                  disabled={loading}
                  className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 disabled:opacity-50"
                >
                  Save Changes
                </button>
              )}
              {template.status !== 'approved' && (
                <button
                  onClick={handleApproveTemplate}
                  disabled={loading}
                  className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 disabled:opacity-50"
                >
                  {loading ? 'Approving...' : 'Approve Template'}
                </button>
              )}
              {template.status === 'approved' && (
                <div className="flex gap-2">
                  <button
                    onClick={handleGenerateScenarios}
                    disabled={loading}
                    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50"
                  >
                    {loading ? 'Generating...' : 'Generate All Scenarios'}
                  </button>
                  <button
                    onClick={() => handleGenerateIndividualPrompt('learn_mode')}
                    disabled={loading}
                    className="bg-green-500 text-white px-3 py-2 rounded hover:bg-green-600 disabled:opacity-50 text-sm"
                  >
                    Learn Mode
                  </button>
                  <button
                    onClick={() => handleGenerateIndividualPrompt('assess_mode')}
                    disabled={loading}
                    className="bg-orange-500 text-white px-3 py-2 rounded hover:bg-orange-600 disabled:opacity-50 text-sm"
                  >
                    Assess Mode
                  </button>
                  <button
                    onClick={() => handleGenerateIndividualPrompt('try_mode')}
                    disabled={loading}
                    className="bg-purple-500 text-white px-3 py-2 rounded hover:bg-purple-600 disabled:opacity-50 text-sm"
                  >
                    Try Mode
                  </button>
                </div>
              )}
              {template.status !== 'approved' && (
                <div className="flex gap-2">
                  <button
                    onClick={() => handlePreviewPrompt('learn_mode')}
                    disabled={loading}
                    className="bg-gray-500 text-white px-3 py-2 rounded hover:bg-gray-600 disabled:opacity-50 text-sm"
                  >
                    Preview Learn
                  </button>
                  <button
                    onClick={() => handlePreviewPrompt('assess_mode')}
                    disabled={loading}
                    className="bg-gray-500 text-white px-3 py-2 rounded hover:bg-gray-600 disabled:opacity-50 text-sm"
                  >
                    Preview Assess
                  </button>
                </div>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
            {/* Scenario Understanding */}
            <div className="bg-white p-4 rounded border">
              <h3 className="font-semibold mb-3">Scenario Understanding 
                <span className="text-xs text-blue-600">
                  ({template.extracted_data.scenario_understanding?.extraction_source?.includes('FROM_DOCUMENT') ? '📄 From Document' : '🤖 Generated'})
                </span>
              </h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium">Main Topic</label>
                  {editMode ? (
                    <input
                      type="text"
                      value={editedData?.scenario_understanding.main_topic || ''}
                      onChange={(e) => updateEditedField('scenario_understanding.main_topic', e.target.value)}
                      className="w-full p-2 border rounded"
                    />
                  ) : (
                    <p className="text-gray-700">{template.extracted_data.scenario_understanding.main_topic}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium">Learning Situation</label>
                  {editMode ? (
                    <textarea
                      value={editedData?.scenario_understanding.learning_situation || ''}
                      onChange={(e) => updateEditedField('scenario_understanding.learning_situation', e.target.value)}
                      className="w-full p-2 border rounded h-20"
                    />
                  ) : (
                    <p className="text-gray-700">{template.extracted_data.scenario_understanding.learning_situation}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium">Target Skills</label>
                  <ul className="list-disc list-inside text-gray-700">
                    {template.extracted_data.scenario_understanding.target_skills.map((skill, idx) => (
                      <li key={idx}>{skill}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            {/* Knowledge Base */}
            <div className="bg-white p-4 rounded border">
              <h3 className="font-semibold mb-3">Knowledge Base 
                <span className="text-xs text-blue-600">
                  ({template.extracted_data.knowledge_base?.extraction_source?.includes('FROM_DOCUMENT') ? '📄 From Document' : '🤖 Generated'})
                </span>
              </h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium">Do's 
                    <span className="text-xs text-blue-600">
                      ({template.extracted_data.knowledge_base?.extraction_source?.includes('FROM_DOCUMENT') ? '📄 From Document' : '🤖 Generated'})
                    </span>
                  </label>
                  <ul className="list-disc list-inside text-gray-700">
                    {template.extracted_data.knowledge_base?.dos?.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    )) || []}
                  </ul>
                </div>
                <div>
                  <label className="block text-sm font-medium">Don'ts 
                    <span className="text-xs text-blue-600">
                      ({template.extracted_data.knowledge_base?.extraction_source?.includes('FROM_DOCUMENT') ? '📄 From Document' : '🤖 Generated'})
                    </span>
                  </label>
                  <ul className="list-disc list-inside text-red-600">
                    {template.extracted_data.knowledge_base?.donts?.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    )) || []}
                  </ul>
                </div>
                <div>
                  <label className="block text-sm font-medium">Key Facts 
                    <span className="text-xs text-blue-600">
                      ({template.extracted_data.knowledge_base?.extraction_source?.includes('FROM_DOCUMENT') ? '📄 From Document' : '🤖 Generated'})
                    </span>
                  </label>
                  <ul className="list-disc list-inside text-gray-700">
                    {template.extracted_data.knowledge_base?.key_facts?.map((fact, idx) => (
                      <li key={idx}>{fact}</li>
                    )) || []}
                  </ul>
                </div>
              </div>
            </div>

            {/* Coaching Rules */}
            <div className="bg-white p-4 rounded border">
              <h3 className="font-semibold mb-3">Coaching Rules 
                <span className="text-xs text-blue-600">
                  ({template.extracted_data.coaching_rules?.extraction_source?.includes('FROM_DOCUMENT') ? '📄 From Document' : '🤖 Generated'})
                </span>
              </h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium">Methodology</label>
                  <p className="text-gray-700">{template.extracted_data.coaching_rules?.process_requirements?.mentioned_methodology || 'Not specified'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium">Required Steps</label>
                  <p className="text-gray-700">{template.extracted_data.coaching_rules?.process_requirements?.required_steps || 'Not specified'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium">Correction Tone</label>
                  <p className="text-gray-700">{template.extracted_data.coaching_rules?.correction_preferences?.preferred_tone || 'Not specified'}</p>
                </div>
              </div>
            </div>

            {/* Success Metrics */}
            <div className="bg-white p-4 rounded border">
              <h3 className="font-semibold mb-3">Success Metrics 
                <span className="text-xs text-blue-600">
                  ({template.extracted_data.success_metrics?.extraction_source?.includes('FROM_DOCUMENT') ? '📄 From Document' : '🤖 Generated'})
                </span>
              </h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium">Learning Objectives</label>
                  <p className="text-gray-700">{template.extracted_data.success_metrics?.learning_objectives || 'Not specified'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium">KPIs</label>
                  <ul className="list-disc list-inside text-gray-700">
                    {template.extracted_data.success_metrics?.kpis_for_interaction?.map((kpi, idx) => (
                      <li key={idx}>{kpi}</li>
                    )) || []}
                  </ul>
                </div>
              </div>
            </div>

            {/* Variations & Challenges */}
            <div className="bg-white p-4 rounded border">
              <h3 className="font-semibold mb-3">Variations & Challenges 
                <span className="text-xs text-blue-600">
                  ({template.extracted_data.variations_challenges?.extraction_source?.includes('FROM_DOCUMENT') ? '📄 From Document' : '🤖 Generated'})
                </span>
              </h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium">Scenario Variations</label>
                  <ul className="list-disc list-inside text-gray-700">
                    {template.extracted_data.variations_challenges?.scenario_variations?.map((variation, idx) => (
                      <li key={idx}>{variation}</li>
                    )) || []}
                  </ul>
                </div>
                <div>
                  <label className="block text-sm font-medium">Edge Cases</label>
                  <ul className="list-disc list-inside text-orange-600">
                    {template.extracted_data.variations_challenges?.edge_cases?.map((edge, idx) => (
                      <li key={idx}>{edge}</li>
                    )) || []}
                  </ul>
                </div>
              </div>
            </div>

            {/* Feedback Mechanisms */}
            <div className="bg-white p-4 rounded border">
              <h3 className="font-semibold mb-3">Feedback Mechanisms 
                <span className="text-xs text-blue-600">
                  ({template.extracted_data.feedback_mechanism?.extraction_source?.includes('FROM_DOCUMENT') ? '📄 From Document' : '🤖 Generated'})
                </span>
              </h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium">Positive Closing</label>
                  <p className="text-green-600">{template.extracted_data.feedback_mechanism?.positive_closing || 'Not specified'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium">Negative Closing</label>
                  <p className="text-red-600">{template.extracted_data.feedback_mechanism?.negative_closing || 'Not specified'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium">Neutral Closing</label>
                  <p className="text-gray-600">{template.extracted_data.feedback_mechanism?.neutral_closing || 'Not specified'}</p>
                </div>
              </div>
            </div>

            {/* Content Specifics */}
            <div className="bg-white p-4 rounded border">
              <h3 className="font-semibold mb-3">Content Specifics 
                <span className="text-xs text-blue-600">
                  ({template.extracted_data.content_specifics?.extraction_source?.includes('FROM_DOCUMENT') ? '📄 From Document' : '🤖 Generated'})
                </span>
              </h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium">Key Knowledge</label>
                  <ul className="list-disc list-inside text-gray-700">
                    {template.extracted_data.content_specifics?.key_knowledge?.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    )) || []}
                  </ul>
                </div>
                <div>
                  <label className="block text-sm font-medium">Procedures Mentioned</label>
                  <ul className="list-disc list-inside text-blue-600">
                    {template.extracted_data.content_specifics?.procedures_mentioned?.map((proc, idx) => (
                      <li key={idx}>{proc}</li>
                    )) || []}
                  </ul>
                </div>
                <div>
                  <label className="block text-sm font-medium">Policies Referenced</label>
                  <ul className="list-disc list-inside text-purple-600">
                    {template.extracted_data.content_specifics?.policies_referenced?.map((policy, idx) => (
                      <li key={idx}>{policy}</li>
                    )) || []}
                  </ul>
                </div>
              </div>
            </div>

            {/* Conversation Examples */}
            <div className="bg-white p-4 rounded border">
              <h3 className="font-semibold mb-3">Conversation Examples 
                <span className="text-xs text-blue-600">
                  ({template.extracted_data.conversation_examples?.extraction_source?.includes('FROM_DOCUMENT') ? '📄 From Document' : '🤖 Generated'})
                </span>
              </h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium">Dialogue Samples</label>
                  <ul className="list-disc list-inside text-gray-700">
                    {template.extracted_data.conversation_examples?.dialogue_samples?.map((sample, idx) => (
                      <li key={idx} className="text-sm">{sample}</li>
                    )) || []}
                  </ul>
                </div>
                <div>
                  <label className="block text-sm font-medium">Question Patterns</label>
                  <ul className="list-disc list-inside text-green-600">
                    {template.extracted_data.conversation_examples?.question_patterns?.map((pattern, idx) => (
                      <li key={idx}>{pattern}</li>
                    )) || []}
                  </ul>
                </div>
              </div>
            </div>

            {/* Template Enhancements */}
            {template.validated_data?.template_enhancements && (
              <div className="bg-white p-4 rounded border">
                <h3 className="font-semibold mb-3">Template Enhancements 
                  <span className="text-xs text-orange-600">
                    (🤖 AI Generated)
                  </span>
                </h3>
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium">Expert Persona Suggestion 
                      <span className="text-xs text-orange-600">
                        ({template.validated_data.template_enhancements?.persona_suggestions?.extraction_source?.includes('FROM_DOCUMENT') ? '📄 From Document' : '🤖 Generated'})
                      </span>
                    </label>
                    <p className="text-gray-700 text-sm">{template.validated_data.template_enhancements?.persona_suggestions?.expert_persona || 'Not specified'}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium">Practice Persona Suggestion 
                      <span className="text-xs text-orange-600">
                        ({template.validated_data.template_enhancements?.persona_suggestions?.extraction_source?.includes('FROM_DOCUMENT') ? '📄 From Document' : '🤖 Generated'})
                      </span>
                    </label>
                    <p className="text-gray-700 text-sm">{template.validated_data.template_enhancements?.persona_suggestions?.practice_persona || 'Not specified'}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium">Learn Mode Flow 
                      <span className="text-xs text-orange-600">
                        ({template.validated_data.template_enhancements?.conversation_flows?.extraction_source?.includes('FROM_DOCUMENT') ? '📄 From Document' : '🤖 Generated'})
                      </span>
                    </label>
                    <p className="text-blue-600 text-sm">{template.validated_data.template_enhancements?.conversation_flows?.learn_mode_flow || 'Not specified'}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium">Practice Mode Flow 
                      <span className="text-xs text-orange-600">
                        ({template.validated_data.template_enhancements?.conversation_flows?.extraction_source?.includes('FROM_DOCUMENT') ? '📄 From Document' : '🤖 Generated'})
                      </span>
                    </label>
                    <p className="text-green-600 text-sm">{template.validated_data.template_enhancements?.conversation_flows?.practice_mode_flow || 'Not specified'}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Knowledge Base Integration */}
            <div className="bg-white p-4 rounded border">
              <h3 className="font-semibold mb-3">Knowledge Base Integration 
                <span className="text-xs text-blue-600">
                  ({template.extracted_data.knowledge_base_integration?.extraction_source?.includes('FROM_DOCUMENT') ? '📄 From Document' : '🤖 Generated'})
                </span>
              </h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium">Requires Knowledge Base</label>
                  <p className="text-gray-700">{template.extracted_data.knowledge_base_integration?.requires_knowledge_base || 'Not specified'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium">Fact-Checking Areas</label>
                  <ul className="list-disc list-inside text-orange-600">
                    {template.extracted_data.knowledge_base_integration?.fact_checking_areas?.map((area, idx) => (
                      <li key={idx}>{area}</li>
                    )) || []}
                  </ul>
                </div>
                <div>
                  <label className="block text-sm font-medium">Accuracy Requirements</label>
                  <p className="text-red-600 text-sm">{template.extracted_data.knowledge_base_integration?.accuracy_requirements || 'Not specified'}</p>
                </div>
              </div>
            </div>

            {/* Validation Notes */}
            {template.validated_data?.validation_notes && (
              <div className="bg-white p-4 rounded border">
                <h3 className="font-semibold mb-3">Validation Notes</h3>
                <div className="space-y-2">
                  <p><strong>Completeness Score:</strong> {template.validated_data.validation_notes?.completeness_score || 'N/A'}</p>
                  {template.validated_data.validation_notes?.missing_elements?.length > 0 && (
                    <div>
                      <strong>Missing Elements:</strong>
                      <ul className="list-disc list-inside text-red-600">
                        {template.validated_data.validation_notes.missing_elements.map((element, idx) => (
                          <li key={idx}>{element}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {template.validated_data.validation_notes?.suggestions?.length > 0 && (
                    <div>
                      <strong>Suggestions:</strong>
                      <ul className="list-disc list-inside text-blue-600">
                        {template.validated_data.validation_notes.suggestions.map((suggestion, idx) => (
                          <li key={idx}>{suggestion}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Step 4: Generated Content */}
      {(generatedScenario || individualPrompt || previewPrompt) && (
        <div className="bg-gray-50 rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">
            {generatedScenario ? 'Step 4: Generated Scenarios' : 
             individualPrompt ? `Generated ${individualPrompt.type.replace('_', ' ').toUpperCase()} Prompt` :
             `Preview ${previewPrompt?.type.replace('_', ' ').toUpperCase()} Prompt`}
          </h2>
          
          {/* Full Scenarios */}
          {generatedScenario && (
            <>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white p-4 rounded border">
                  <h3 className="font-semibold mb-3">Learn Mode Prompt</h3>
                  <pre className="text-sm bg-gray-100 p-3 rounded overflow-auto max-h-96 whitespace-pre-wrap">
                    {generatedScenario.learn_mode}
                  </pre>
                </div>
                
                <div className="bg-white p-4 rounded border">
                  <h3 className="font-semibold mb-3">Assess/Try Mode Prompt</h3>
                  <pre className="text-sm bg-gray-100 p-3 rounded overflow-auto max-h-96 whitespace-pre-wrap">
                    {generatedScenario.assess_mode}
                  </pre>
                </div>
              </div>

              <div className="mt-6 bg-white p-4 rounded border">
                <h3 className="font-semibold mb-3">Scenario Metadata</h3>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <strong>Title:</strong> {generatedScenario.scenario_metadata.title}
                  </div>
                  <div>
                    <strong>Domain:</strong> {generatedScenario.scenario_metadata.domain}
                  </div>
                  <div>
                    <strong>Difficulty:</strong> {generatedScenario.scenario_metadata.difficulty}
                  </div>
                </div>
              </div>

              {/* Recommended Personas */}
              {generatedScenario.recommended_personas && (
                <div className="mt-6 bg-white p-4 rounded border">
                  <h3 className="font-semibold mb-3">Recommended Personas</h3>
                  
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-medium mb-3 text-blue-600">Learn Mode Personas</h4>
                      <div className="space-y-3">
                        {generatedScenario.recommended_personas.learn_mode_personas.map((persona, idx) => (
                          <div key={idx} className="border rounded p-3 bg-blue-50">
                            <div className="font-medium">{persona.name} ({persona.age}, {persona.gender})</div>
                            <div className="text-sm text-gray-600 mb-1">{persona.description}</div>
                            <div className="text-xs text-blue-600 mb-1">Goal: {persona.character_goal}</div>
                            <div className="text-xs text-gray-500">Background: {persona.background_story}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-medium mb-3 text-green-600">Practice Mode Personas</h4>
                      <div className="space-y-3">
                        {generatedScenario.recommended_personas.practice_mode_personas.map((persona, idx) => (
                          <div key={idx} className="border rounded p-3 bg-green-50">
                            <div className="font-medium">{persona.name} ({persona.age}, {persona.gender})</div>
                            <div className="text-sm text-gray-600 mb-1">{persona.description}</div>
                            <div className="text-xs text-green-600 mb-1">Goal: {persona.character_goal}</div>
                            <div className="text-xs text-gray-500 mb-2">Location: {persona.location}</div>
                            <div className="text-xs bg-white p-2 rounded border-l-2 border-green-400 mb-2">
                              <strong>Background:</strong> {persona.background_story}
                            </div>
                            <div className="text-xs bg-white p-2 rounded border-l-2 border-green-400 mb-2">
                              <strong>Sample:</strong> "{persona.sample_opener}"
                            </div>
                            <button
                              onClick={() => handleSimulateConversation(persona, 'assess_mode')}
                              disabled={loading}
                              className="mt-2 bg-green-500 text-white px-3 py-1 rounded text-xs hover:bg-green-600 disabled:opacity-50"
                            >
                              {loading ? 'Loading...' : 'Preview Conversation'}
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}

          {/* Individual Prompt */}
          {individualPrompt && (
            <div className="bg-white p-4 rounded border">
              <h3 className="font-semibold mb-3 text-green-600">
                {individualPrompt.type.replace('_', ' ').toUpperCase()} Prompt (Final)
              </h3>
              <pre className="text-sm bg-gray-100 p-3 rounded overflow-auto max-h-96 whitespace-pre-wrap">
                {individualPrompt.content}
              </pre>
            </div>
          )}

          {/* Preview Prompt */}
          {previewPrompt && (
            <div className="bg-white p-4 rounded border">
              <h3 className="font-semibold mb-3 text-orange-600">
                {previewPrompt.type.replace('_', ' ').toUpperCase()} Prompt (Preview)
              </h3>
              <div className="bg-yellow-50 border-l-4 border-yellow-400 p-3 mb-3">
                <p className="text-sm text-yellow-700">
                  <strong>Note:</strong> This is a preview. Approve the template to generate final prompts.
                </p>
              </div>
              <pre className="text-sm bg-gray-100 p-3 rounded overflow-auto max-h-96 whitespace-pre-wrap">
                {previewPrompt.content}
              </pre>
            </div>
          )}

          {/* Conversation Simulation */}
          {conversationSim && (
            <div className="mt-6 bg-white p-4 rounded border">
              <h3 className="font-semibold mb-3 text-purple-600">
                Conversation Preview: {selectedPersona?.name}
              </h3>
              <div className="bg-yellow-50 border-l-4 border-yellow-400 p-3 mb-3">
                <p className="text-sm text-yellow-700">
                  <strong>⚠️ This is just a preview!</strong> In the actual training:
                </p>
                <ul className="text-xs text-yellow-600 mt-1 ml-4 list-disc">
                  <li><strong>You (the learner)</strong> will provide leadership guidance</li>
                  <li><strong>{selectedPersona?.name} (AI)</strong> will ask for help and respond to your advice</li>
                  <li>The roles shown below are for demonstration only</li>
                </ul>
              </div>
              <div className="bg-purple-50 p-3 rounded mb-3">
                <div className="text-sm text-purple-700 mb-2">
                  <strong>Persona:</strong> {conversationSim.persona?.name} ({conversationSim.persona?.age}, {conversationSim.persona?.gender})
                </div>
                <div className="text-xs text-purple-600 mb-1">
                  <strong>Role:</strong> {conversationSim.persona?.persona_type}
                </div>
                <div className="text-xs text-purple-600 mb-1">
                  <strong>Goal:</strong> {conversationSim.persona?.character_goal}
                </div>
                <div className="text-xs text-purple-600">
                  <strong>Background:</strong> {conversationSim.persona?.background_story}
                </div>
              </div>
              <div className="bg-gray-100 p-4 rounded">
                <h4 className="font-medium mb-2">Sample Conversation Preview:</h4>
                <pre className="text-sm whitespace-pre-wrap font-mono">
                  {conversationSim.conversation}
                </pre>
              </div>
              <button
                onClick={() => setConversationSim(null)}
                className="mt-3 bg-gray-500 text-white px-3 py-1 rounded text-sm hover:bg-gray-600"
              >
                Close Preview
              </button>
            </div>
          )}

          <div className="mt-4 flex gap-2">
            <button
              onClick={() => {
                setTemplate(null);
                setGeneratedScenario(null);
                setIndividualPrompt(null);
                setPreviewPrompt(null);
                setConversationSim(null);
                setSelectedPersona(null);
                setFile(null);
                setTemplateName('');
                setPromptText('');
                setEditMode(false);
                setEditedData(null);
                setExtractedDetails(null);
                setCurrentStep('upload');
              }}
              className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
            >
              Create New Scenario
            </button>
            {(individualPrompt || previewPrompt) && (
              <button
                onClick={() => {
                  setIndividualPrompt(null);
                  setPreviewPrompt(null);
                }}
                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
              >
                Back to Template
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default FlexibleScenarioGenerator;