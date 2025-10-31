# Add this to your main.py or wherever you register routers

from flexible_endpoints import router as flexible_router

# In your FastAPI app setup:
# app.include_router(flexible_router)

"""
INTEGRATION STEPS:

1. Add to main.py:
   from flexible_endpoints import router as flexible_router
   app.include_router(flexible_router)

2. Database collections needed:
   - flexible_templates (stores extracted/validated templates)
   - flexible_scenarios (stores generated scenarios)

3. Usage Flow:
   
   DOCUMENT PATH:
   POST /flexible/analyze-document (upload file + name)
   → GET /flexible/template/{id} (review extracted data)
   → PUT /flexible/template/{id} (edit if needed)
   → POST /flexible/generate-scenarios/{id} (generate final scenarios)
   
   PROMPT PATH:
   POST /flexible/analyze-prompt (text prompt + name)
   → GET /flexible/template/{id} (review extracted data)
   → PUT /flexible/template/{id} (edit if needed)
   → POST /flexible/generate-scenarios/{id} (generate final scenarios)

4. Key Features:
   - Flexible extraction (adapts to content)
   - User validation/editing before generation
   - Dynamic template creation
   - Persona-specific feedback
   - Iterative approval process

5. Benefits over existing system:
   - No rigid JSON schema
   - User can edit before generation
   - Better document understanding
   - Domain-agnostic but context-aware
   - Validation and enhancement steps
"""

# Example usage in frontend:

"""
// Step 1: Analyze document or prompt
const analyzeResponse = await fetch('/flexible/analyze-document', {
    method: 'POST',
    body: formData // file + template_name
});

// Step 2: Review and edit extracted data
const templateData = await fetch(`/flexible/template/${templateId}`);
// Show user the extracted data for editing

// Step 3: Update if needed
await fetch(`/flexible/template/${templateId}`, {
    method: 'PUT',
    body: JSON.stringify(editedData)
});

// Step 4: Generate scenarios
const scenarios = await fetch(`/flexible/generate-scenarios/${templateId}`, {
    method: 'POST'
});
"""