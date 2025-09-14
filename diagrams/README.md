# Migoto Platform - Architecture Diagrams

This directory contains comprehensive Mermaid diagrams explaining the Migoto training platform architecture.

## 📊 Available Diagrams

### 1. **system-overview.mmd** - Complete System Architecture
- **Purpose:** High-level view of all system components and their relationships
- **Shows:** Client layer, API gateway, business services, AI/ML layer, data storage, and external services
- **Key Features:** 
  - Multi-layered architecture visualization
  - Component dependencies and data flow
  - Color-coded service categories
  - Integration points with Azure services

### 2. **chat-flow.mmd** - Real-time Chat Sequence
- **Purpose:** Detailed sequence diagram of the chat conversation flow
- **Shows:** Complete user journey from authentication to AI-powered conversation
- **Key Features:**
  - Authentication and session initialization
  - Real-time message processing with Server-Sent Events (SSE)
  - AI integration with OpenAI, TTS, and fact-checking
  - Data persistence and analysis generation

### 3. **user-hierarchy.mmd** - Multi-tenant User Structure
- **Purpose:** Visual representation of the hierarchical user management system
- **Shows:** Role-based access control and company isolation
- **Key Features:**
  - Boss Admin → Super Admin → Admin → User hierarchy
  - Multi-company tenant isolation
  - Permission levels and capabilities
  - Demo account management with cascading extensions

### 4. **api-endpoints.mmd** - Complete API Overview
- **Purpose:** Comprehensive view of all API endpoints organized by category
- **Shows:** 100+ endpoints across 8 major API categories
- **Key Features:**
  - Authentication and user management APIs
  - Chat and conversation APIs
  - Learning management system APIs
  - Analytics and progress tracking APIs
  - Company and multi-tenancy APIs
  - File and knowledge management APIs
  - Administrative APIs

### 5. **data-flow.mmd** - System Data Flow
- **Purpose:** How data moves through the system from request to response
- **Shows:** Complete data processing pipelines
- **Key Features:**
  - User authentication and session management
  - Real-time conversation processing
  - Analysis and evaluation pipeline
  - Administrative operations flow
  - Error handling and success paths

### 6. **deployment-architecture.mmd** - Production Infrastructure
- **Purpose:** Production deployment architecture and infrastructure setup
- **Shows:** Scalable, secure, and monitored production environment
- **Key Features:**
  - Load balancing and auto-scaling
  - Database replication and caching
  - AI services integration
  - Security and monitoring layers
  - CI/CD pipeline and development environment

## 🔧 How to View the Diagrams

### Option 1: GitHub/GitLab (Recommended)
- Upload files to GitHub/GitLab repository
- Diagrams will render automatically in the web interface

### Option 2: VS Code
1. Install "Markdown Preview Mermaid Support" extension
2. Open any `.mmd` file
3. Use `Ctrl+Shift+V` to preview

### Option 3: Online Mermaid Editor
1. Go to [mermaid.live](https://mermaid.live)
2. Copy and paste diagram content
3. View and export as needed

### Option 4: Mermaid CLI
```bash
# Install Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Generate PNG images
mmdc -i system-overview.mmd -o system-overview.png
mmdc -i chat-flow.mmd -o chat-flow.png
# ... repeat for all diagrams
```

## 📋 Diagram Usage Guide

### For Developers
- **system-overview.mmd**: Understand overall architecture before coding
- **chat-flow.mmd**: Implement real-time chat features
- **data-flow.mmd**: Debug data processing issues
- **api-endpoints.mmd**: Reference API structure during development

### For DevOps Engineers
- **deployment-architecture.mmd**: Set up production infrastructure
- **system-overview.mmd**: Understand service dependencies
- **data-flow.mmd**: Monitor system performance bottlenecks

### For Product Managers
- **user-hierarchy.mmd**: Understand user roles and permissions
- **api-endpoints.mmd**: Plan feature development
- **chat-flow.mmd**: Understand user experience flow

### For System Architects
- **system-overview.mmd**: Overall system design validation
- **deployment-architecture.mmd**: Infrastructure planning
- **data-flow.mmd**: Performance optimization planning

## 🎨 Diagram Color Coding

### System Overview
- **Blue**: Client and gateway layers
- **Green**: Core business services
- **Orange**: AI/ML services
- **Pink**: Data storage layers
- **Light Green**: External services

### User Hierarchy
- **Red**: Boss Admin (highest privileges)
- **Teal**: Super Admin (company level)
- **Blue**: Admin (team level)
- **Green**: Regular Users (learners)
- **Pink**: Demo accounts

### API Endpoints
- **Red**: Authentication APIs
- **Blue**: User management APIs
- **Green**: Chat and conversation APIs
- **Yellow**: Learning management APIs
- **Purple**: Analytics APIs
- **Pink**: Company management APIs
- **Cyan**: File management APIs
- **Orange**: Administrative APIs

## 🔄 Updating Diagrams

When updating the system architecture:

1. **Modify the relevant `.mmd` file**
2. **Test the diagram** using mermaid.live
3. **Update this README** if new diagrams are added
4. **Regenerate images** if using static exports
5. **Update documentation** references in main architecture files

## 📚 Related Documentation

- **DETAILED_ARCHITECTURE.md**: Comprehensive technical architecture document
- **API_SPECIFICATION.md**: Complete API documentation with examples
- **ARCHITECTURE.md**: High-level architecture overview

These diagrams complement the written documentation and provide visual understanding of the Migoto training platform's complex architecture.