# Archetype System - Complete File Index

## 📚 Quick Navigation

This index helps you find the right document for your needs.

---

## 🎯 Start Here

### New to the Archetype System?
1. **[ARCHETYPE_QUICK_START.md](ARCHETYPE_QUICK_START.md)** - 5-minute overview
2. **[ARCHETYPE_TEST_SCENARIOS.md](ARCHETYPE_TEST_SCENARIOS.md)** - See examples
3. **[WEEK1_COMPLETE.md](WEEK1_COMPLETE.md)** - What's implemented

### Want to Understand the Full System?
1. **[ARCHETYPE_SYSTEM_PLAN.md](ARCHETYPE_SYSTEM_PLAN.md)** - Complete 7-phase plan
2. **[WEEK1_INTEGRATION_SUMMARY.md](WEEK1_INTEGRATION_SUMMARY.md)** - Implementation details

### Need to Migrate Existing Scenarios?
1. **[ARCHETYPE_MIGRATION_GUIDE.md](ARCHETYPE_MIGRATION_GUIDE.md)** - Migration scripts

---

## 📖 Documentation Files

### Overview & Planning
| File | Purpose | Audience | Length |
|------|---------|----------|--------|
| **ARCHETYPE_SYSTEM_PLAN.md** | Complete 7-phase implementation plan | Developers, PMs | Long |
| **WEEK1_COMPLETE.md** | Week 1 completion summary | Everyone | Medium |
| **ARCHETYPE_INDEX.md** | This file - navigation guide | Everyone | Short |

### User Guides
| File | Purpose | Audience | Length |
|------|---------|----------|--------|
| **ARCHETYPE_QUICK_START.md** | Quick start guide with examples | Content creators, Trainers | Medium |
| **ARCHETYPE_TEST_SCENARIOS.md** | 10 test scenarios for each archetype | Testers, Content creators | Medium |

### Technical Documentation
| File | Purpose | Audience | Length |
|------|---------|----------|--------|
| **WEEK1_INTEGRATION_SUMMARY.md** | Detailed implementation notes | Developers | Long |
| **ARCHETYPE_MIGRATION_GUIDE.md** | Migration scripts and strategies | Developers, Admins | Long |

---

## 💻 Code Files

### Core System (Week 1 - Complete)
| File | Purpose | Lines | Status |
|------|---------|-------|--------|
| **core/archetype_models.py** | Pydantic data models | ~300 | ✅ Complete |
| **core/archetype_definitions.py** | Master archetype configs | ~250 | ✅ Complete |
| **core/archetype_classifier.py** | LLM classification engine | ~200 | ✅ Complete |
| **core/archetype_extractors.py** | Extraction logic | ~400 | ✅ Complete |
| **core/archetype_persona_generator.py** | Persona generation | ~500 | ✅ Complete |

### Integration Updates (Week 1 - Complete)
| File | Changes | Status |
|------|---------|--------|
| **main.py** | Added archetype seeding to startup | ✅ Complete |
| **scenario_generator.py** | Integrated classifier | ✅ Complete |
| **models/avatarInteraction_models.py** | Added 3 archetype fields | ✅ Complete |

### Testing
| File | Purpose | Status |
|------|---------|--------|
| **test_week1_integration.py** | Automated test script | ✅ Complete |

---

## 🎓 Learning Paths

### Path 1: Content Creator (30 minutes)
```
1. ARCHETYPE_QUICK_START.md (10 min)
   ↓
2. ARCHETYPE_TEST_SCENARIOS.md (15 min)
   ↓
3. Test with /test-archetype-classification (5 min)
```

**Goal:** Understand 5 archetypes and create scenarios

---

### Path 2: Developer (2 hours)
```
1. WEEK1_COMPLETE.md (15 min)
   ↓
2. WEEK1_INTEGRATION_SUMMARY.md (30 min)
   ↓
3. core/archetype_models.py (20 min)
   ↓
4. core/archetype_classifier.py (20 min)
   ↓
5. test_week1_integration.py (15 min)
   ↓
6. Run tests and verify (20 min)
```

**Goal:** Understand implementation and extend system

---

### Path 3: System Administrator (1 hour)
```
1. WEEK1_COMPLETE.md (15 min)
   ↓
2. ARCHETYPE_MIGRATION_GUIDE.md (30 min)
   ↓
3. Run verification scripts (15 min)
```

**Goal:** Deploy and maintain archetype system

---

### Path 4: Project Manager (45 minutes)
```
1. ARCHETYPE_SYSTEM_PLAN.md (20 min)
   ↓
2. WEEK1_COMPLETE.md (15 min)
   ↓
3. ARCHETYPE_QUICK_START.md (10 min)
```

**Goal:** Understand scope, status, and roadmap

---

## 🔍 Find Information By Topic

### Understanding Archetypes
- **What are the 5 archetypes?** → ARCHETYPE_QUICK_START.md
- **How do I identify archetype patterns?** → ARCHETYPE_QUICK_START.md (Decision Tree)
- **What are examples of each archetype?** → ARCHETYPE_TEST_SCENARIOS.md

### Implementation Details
- **How does classification work?** → core/archetype_classifier.py
- **What data models are used?** → core/archetype_models.py
- **How are archetypes stored?** → WEEK1_INTEGRATION_SUMMARY.md
- **What fields were added?** → models/avatarInteraction_models.py

### Testing & Validation
- **How do I test classification?** → test_week1_integration.py
- **What test scenarios exist?** → ARCHETYPE_TEST_SCENARIOS.md
- **How do I verify migration?** → ARCHETYPE_MIGRATION_GUIDE.md

### Migration & Deployment
- **How do I migrate existing scenarios?** → ARCHETYPE_MIGRATION_GUIDE.md
- **What's the deployment checklist?** → WEEK1_COMPLETE.md
- **How do I verify the system?** → WEEK1_COMPLETE.md (Verification Steps)

### Future Development
- **What's the full roadmap?** → ARCHETYPE_SYSTEM_PLAN.md
- **What's next after Week 1?** → ARCHETYPE_SYSTEM_PLAN.md (Phase 2)
- **What are known limitations?** → WEEK1_COMPLETE.md (Known Limitations)

---

## 🎯 Quick Reference

### 5 Archetype Types
1. **HELP_SEEKING** - Character has problem, needs help
2. **PERSUASION** - Character satisfied, learner creates interest
3. **CONFRONTATION** - Address wrongdoing (3 sub-types)
4. **INVESTIGATION** - Gather information through questions
5. **NEGOTIATION** - Find middle ground

### Key Endpoints
- `POST /scenario/test-archetype-classification` - Test classification
- `POST /scenario/analyze-scenario` - Full scenario generation with classification

### Key Database Collections
- `archetype_definitions` - 5 archetype configurations
- `avatar_interactions` - Has archetype, archetype_sub_type, archetype_confidence fields
- `templates` - Has archetype_classification in template_data

### Key Files to Modify
- **Add new archetype?** → core/archetype_definitions.py
- **Change classification logic?** → core/archetype_classifier.py
- **Update data models?** → core/archetype_models.py
- **Modify extraction?** → core/archetype_extractors.py

---

## 📊 File Statistics

### Documentation
- **Total docs:** 7 files
- **Total pages:** ~50 pages
- **Total words:** ~15,000 words

### Code
- **Core files:** 5 files
- **Updated files:** 3 files
- **Test files:** 1 file
- **Total lines:** ~2,000 lines

### Test Coverage
- **Test scenarios:** 10 scenarios
- **Automated tests:** 6 tests
- **Archetype coverage:** 100% (all 5 types)

---

## 🗺️ System Architecture Map

```
┌─────────────────────────────────────────────────────────┐
│                    USER INPUT                           │
│              (Scenario Description)                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           EnhancedScenarioGenerator                     │
│         (scenario_generator.py)                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           ArchetypeClassifier                           │
│         (core/archetype_classifier.py)                  │
│                                                          │
│  Uses: archetype_definitions.py                         │
│  Returns: ArchetypeClassificationResult                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           Template Data + Classification                │
│         (Stored in MongoDB)                             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           AvatarInteraction                             │
│         (models/avatarInteraction_models.py)            │
│                                                          │
│  Fields: archetype, archetype_sub_type,                 │
│          archetype_confidence                           │
└─────────────────────────────────────────────────────────┘
```

---

## 🔗 External Resources

### Related Systems
- **Scenario Generation:** scenario_generator.py
- **Chat System:** dynamic_chat.py
- **Persona System:** core/persona.py
- **Evaluation:** core/chat.py (evaluation functions)

### Dependencies
- **OpenAI:** For LLM classification
- **MongoDB:** For data storage
- **Pydantic:** For data validation
- **FastAPI:** For API endpoints

---

## 📝 Version History

### Week 1 (Current)
- ✅ Core archetype system implemented
- ✅ Classification integrated
- ✅ Models updated
- ✅ Tests created
- ✅ Documentation complete

### Week 2 (Planned)
- ⏳ Archetype-specific extraction
- ⏳ Multi-variant scenarios
- ⏳ Enhanced persona generation

### Week 3+ (Future)
- ⏳ Frontend integration
- ⏳ Validation layer
- ⏳ Migration tools
- ⏳ Analytics dashboard

---

## 🎯 Common Tasks

### I want to...

**...understand the archetype system**
→ Read ARCHETYPE_QUICK_START.md

**...see examples of each archetype**
→ Read ARCHETYPE_TEST_SCENARIOS.md

**...test classification**
→ Use POST /scenario/test-archetype-classification

**...implement Week 2 features**
→ Read ARCHETYPE_SYSTEM_PLAN.md Phase 2

**...migrate existing scenarios**
→ Read ARCHETYPE_MIGRATION_GUIDE.md

**...understand the code**
→ Read WEEK1_INTEGRATION_SUMMARY.md

**...verify the system works**
→ Run test_week1_integration.py

**...add a new archetype**
→ Modify core/archetype_definitions.py

**...change classification logic**
→ Modify core/archetype_classifier.py

**...update data models**
→ Modify core/archetype_models.py

---

## 📞 Getting Help

### Documentation Issues
- Check this index for the right file
- Use Ctrl+F to search within files
- Follow learning paths above

### Technical Issues
- Check WEEK1_COMPLETE.md verification steps
- Run test_week1_integration.py
- Review logs in main.py startup

### Classification Issues
- Check ARCHETYPE_QUICK_START.md decision tree
- Review ARCHETYPE_TEST_SCENARIOS.md examples
- Test with /test-archetype-classification endpoint

---

## ✅ Quick Checklist

Before starting work:
- [ ] Read relevant documentation from this index
- [ ] Understand which files you need to modify
- [ ] Check if tests exist for your changes
- [ ] Review examples in test scenarios

After making changes:
- [ ] Run test_week1_integration.py
- [ ] Update relevant documentation
- [ ] Test with sample scenarios
- [ ] Verify database changes

---

**Use this index to navigate the archetype system efficiently!** 🗺️
