# Flexible Scenario Generator Frontend

## Overview
Professional React TypeScript frontend for testing the flexible scenario generation system.

## Features

### 🎯 **Core Workflow**
1. **Input Phase**: Upload document OR enter text prompt
2. **Review Phase**: Edit extracted template data
3. **Generation Phase**: Create final scenario prompts

### 🔧 **Key Components**

**FlexibleScenarioGenerator.tsx**
- Main component handling the complete workflow
- TypeScript interfaces for type safety
- Professional UI with Tailwind CSS
- Real-time editing capabilities

**Features:**
- ✅ File upload (PDF, DOC, DOCX, TXT)
- ✅ Text prompt input
- ✅ Template review and editing
- ✅ Validation feedback display
- ✅ Scenario generation and preview
- ✅ Professional styling

### 📋 **Usage Instructions**

**For Your Team:**

1. **Setup** (if creating new React app):
```bash
npx create-react-app flexible-frontend --template typescript
cd flexible-frontend
npm install axios react-router-dom
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

2. **Integration**:
- Copy `FlexibleScenarioGenerator.tsx` to your `src/` folder
- Copy `App.tsx` and `App.css` 
- Update your backend to include the flexible endpoints
- Ensure CORS is configured for frontend requests

3. **Backend Integration**:
```python
# Add to main.py
from flexible_endpoints import router as flexible_router
app.include_router(flexible_router)
```

### 🎨 **UI Features**

**Professional Design:**
- Clean, modern interface
- Responsive grid layout
- Loading states and error handling
- Intuitive step-by-step workflow
- Real-time validation feedback

**User Experience:**
- Tab-based input selection
- Inline editing capabilities
- Progress indicators
- Clear action buttons
- Comprehensive data display

### 🔄 **Workflow Steps**

**Step 1: Create Template**
- Choose between document upload or text prompt
- Enter template name
- System analyzes and extracts data

**Step 2: Review Template**
- View extracted scenario understanding
- Edit participant roles
- Modify conversation dynamics
- Review validation notes
- Save changes when satisfied

**Step 3: Generate Scenarios**
- Create final learn/assess/try mode prompts
- View generated personas
- See scenario metadata
- Option to create new scenarios

### 🛠 **Technical Details**

**TypeScript Interfaces:**
- Strongly typed data structures
- IntelliSense support
- Runtime error prevention

**State Management:**
- React hooks for local state
- Proper loading states
- Error boundary handling

**API Integration:**
- Axios for HTTP requests
- Proper error handling
- File upload support

### 📝 **Customization**

**For Team Development:**
- All components are modular
- Easy to extend with new features
- Professional code structure
- Clear separation of concerns

**Styling:**
- Tailwind CSS for rapid development
- Custom CSS for specific needs
- Responsive design patterns
- Consistent color scheme

### 🚀 **Deployment**

**Development:**
```bash
npm start
# Runs on http://localhost:3000
# Proxy configured for backend on :9000
```

**Production:**
```bash
npm run build
# Creates optimized build in /build folder
```

### 🔧 **Backend Requirements**

Ensure these endpoints are available:
- `POST /flexible/analyze-document`
- `POST /flexible/analyze-prompt`
- `GET /flexible/template/{id}`
- `PUT /flexible/template/{id}`
- `POST /flexible/generate-scenarios/{id}`

### 📊 **Testing**

The frontend provides a complete testing interface for:
- Document analysis accuracy
- Prompt extraction quality
- Template editing functionality
- Scenario generation results
- User experience validation

This gives your team a professional tool to test and validate the flexible scenario generation system before full integration.