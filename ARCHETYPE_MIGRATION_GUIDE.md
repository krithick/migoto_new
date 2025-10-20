# Archetype System - Migration Guide for Existing Scenarios

## 🎯 Overview

This guide helps you migrate existing scenarios to the new archetype system without breaking functionality.

## ✅ Good News: Backward Compatibility

**Your existing scenarios will continue to work!**

- Archetype fields are **optional** in AvatarInteractionBase
- Existing avatar_interactions without archetype data remain valid
- No immediate migration required
- System gracefully handles missing archetype fields

## 📊 Migration Strategy

### Option 1: Gradual Migration (Recommended)
Migrate scenarios as they're edited or updated.

**Pros:**
- No downtime
- Test with small batches
- Learn from early migrations

**Cons:**
- Mixed data state during transition
- Takes longer to complete

---

### Option 2: Bulk Migration
Classify all existing scenarios at once.

**Pros:**
- Complete quickly
- Consistent data state
- Easier to analyze patterns

**Cons:**
- Requires API quota for classification
- Potential for errors at scale
- Needs careful testing

---

## 🔧 Migration Scripts

### Script 1: Classify Single Scenario

```python
"""
Classify and update a single existing scenario
"""
import asyncio
from database import get_db
from scenario_generator import EnhancedScenarioGenerator
from openai import AsyncAzureOpenAI
import os

async def classify_existing_scenario(scenario_id: str):
    """Classify an existing scenario and update its avatar_interactions"""
    
    db = await get_db()
    
    # Get scenario
    scenario = await db.scenarios.find_one({"_id": scenario_id})
    if not scenario:
        print(f"❌ Scenario {scenario_id} not found")
        return
    
    # Get template data
    template_id = scenario.get("template_id")
    if not template_id:
        print(f"⚠️ Scenario {scenario_id} has no template_id")
        return
    
    template = await db.templates.find_one({"id": template_id})
    if not template:
        print(f"❌ Template {template_id} not found")
        return
    
    template_data = template.get("template_data", {})
    
    # Initialize classifier
    client = AsyncAzureOpenAI(
        api_key=os.getenv("api_key"),
        api_version=os.getenv("api_version"),
        azure_endpoint=os.getenv("endpoint")
    )
    
    generator = EnhancedScenarioGenerator(client)
    
    # Classify
    print(f"🔍 Classifying scenario: {scenario.get('title', 'Unknown')}")
    
    # Get scenario description from template
    scenario_description = template_data.get("context_overview", {}).get("scenario_title", "")
    
    if not scenario_description:
        print(f"⚠️ No scenario description found")
        return
    
    # Classify
    classification = await generator.archetype_classifier.classify_scenario(
        scenario_description, 
        template_data
    )
    
    print(f"✅ Classified as: {classification.primary_archetype}")
    print(f"   Confidence: {classification.confidence_score:.2f}")
    print(f"   Sub-type: {classification.sub_type}")
    
    # Update avatar_interactions
    modes = ["learn_mode", "assess_mode", "try_mode"]
    
    for mode in modes:
        mode_data = scenario.get(mode)
        if not mode_data:
            continue
        
        avatar_interaction_id = mode_data.get("avatar_interaction")
        if not avatar_interaction_id:
            continue
        
        # Update avatar_interaction
        result = await db.avatar_interactions.update_one(
            {"_id": str(avatar_interaction_id)},
            {"$set": {
                "archetype": classification.primary_archetype,
                "archetype_sub_type": classification.sub_type,
                "archetype_confidence": classification.confidence_score
            }}
        )
        
        if result.modified_count > 0:
            print(f"   ✅ Updated {mode} avatar_interaction")
        else:
            print(f"   ⚠️ {mode} avatar_interaction not updated")
    
    # Update template with classification
    await db.templates.update_one(
        {"id": template_id},
        {"$set": {
            "template_data.archetype_classification": {
                "primary_archetype": classification.primary_archetype,
                "confidence_score": classification.confidence_score,
                "alternative_archetypes": classification.alternative_archetypes,
                "reasoning": classification.reasoning,
                "sub_type": classification.sub_type
            }
        }}
    )
    
    print(f"✅ Migration complete for scenario {scenario_id}")

# Usage
if __name__ == "__main__":
    scenario_id = "your-scenario-id-here"
    asyncio.run(classify_existing_scenario(scenario_id))
```

---

### Script 2: Bulk Migration

```python
"""
Classify all existing scenarios in batches
"""
import asyncio
from database import get_db
from scenario_generator import EnhancedScenarioGenerator
from openai import AsyncAzureOpenAI
import os
from datetime import datetime

async def bulk_migrate_scenarios(batch_size: int = 10, dry_run: bool = True):
    """
    Migrate all scenarios to archetype system
    
    Args:
        batch_size: Number of scenarios to process at once
        dry_run: If True, only simulate without updating database
    """
    
    db = await get_db()
    
    # Initialize classifier
    client = AsyncAzureOpenAI(
        api_key=os.getenv("api_key"),
        api_version=os.getenv("api_version"),
        azure_endpoint=os.getenv("endpoint")
    )
    
    generator = EnhancedScenarioGenerator(client)
    
    # Get all scenarios
    total_scenarios = await db.scenarios.count_documents({})
    print(f"📊 Found {total_scenarios} scenarios to migrate")
    
    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
    
    # Process in batches
    processed = 0
    successful = 0
    failed = 0
    
    cursor = db.scenarios.find({})
    
    async for scenario in cursor:
        scenario_id = scenario["_id"]
        scenario_title = scenario.get("title", "Unknown")
        
        print(f"\n{'='*60}")
        print(f"Processing: {scenario_title} ({processed+1}/{total_scenarios})")
        
        try:
            # Get template
            template_id = scenario.get("template_id")
            if not template_id:
                print(f"⚠️ No template_id, skipping")
                failed += 1
                processed += 1
                continue
            
            template = await db.templates.find_one({"id": template_id})
            if not template:
                print(f"⚠️ Template not found, skipping")
                failed += 1
                processed += 1
                continue
            
            template_data = template.get("template_data", {})
            
            # Get scenario description
            scenario_description = (
                template_data.get("context_overview", {}).get("scenario_title", "") or
                scenario.get("description", "") or
                scenario_title
            )
            
            # Classify
            classification = await generator.archetype_classifier.classify_scenario(
                scenario_description,
                template_data
            )
            
            print(f"✅ Classified: {classification.primary_archetype} ({classification.confidence_score:.2f})")
            
            if not dry_run:
                # Update avatar_interactions
                for mode in ["learn_mode", "assess_mode", "try_mode"]:
                    mode_data = scenario.get(mode)
                    if mode_data and mode_data.get("avatar_interaction"):
                        await db.avatar_interactions.update_one(
                            {"_id": str(mode_data["avatar_interaction"])},
                            {"$set": {
                                "archetype": classification.primary_archetype,
                                "archetype_sub_type": classification.sub_type,
                                "archetype_confidence": classification.confidence_score
                            }}
                        )
                
                # Update template
                await db.templates.update_one(
                    {"id": template_id},
                    {"$set": {
                        "template_data.archetype_classification": {
                            "primary_archetype": classification.primary_archetype,
                            "confidence_score": classification.confidence_score,
                            "alternative_archetypes": classification.alternative_archetypes,
                            "reasoning": classification.reasoning,
                            "sub_type": classification.sub_type
                        },
                        "migrated_at": datetime.now().isoformat()
                    }}
                )
            
            successful += 1
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            failed += 1
        
        processed += 1
        
        # Batch delay to avoid rate limits
        if processed % batch_size == 0:
            print(f"\n⏸️ Batch complete. Processed {processed}/{total_scenarios}")
            await asyncio.sleep(2)  # Rate limit protection
    
    # Summary
    print(f"\n{'='*60}")
    print("MIGRATION SUMMARY")
    print(f"{'='*60}")
    print(f"Total scenarios: {total_scenarios}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(successful/total_scenarios)*100:.1f}%")
    
    if dry_run:
        print("\n⚠️ This was a DRY RUN - no changes were made")
        print("Run with dry_run=False to apply changes")

# Usage
if __name__ == "__main__":
    # First run in dry-run mode to test
    asyncio.run(bulk_migrate_scenarios(batch_size=10, dry_run=True))
    
    # Then run for real
    # asyncio.run(bulk_migrate_scenarios(batch_size=10, dry_run=False))
```

---

### Script 3: Verify Migration

```python
"""
Verify migration completeness and accuracy
"""
import asyncio
from database import get_db

async def verify_migration():
    """Check migration status and data quality"""
    
    db = await get_db()
    
    print("🔍 MIGRATION VERIFICATION REPORT")
    print("="*60)
    
    # Count scenarios
    total_scenarios = await db.scenarios.count_documents({})
    print(f"\nTotal scenarios: {total_scenarios}")
    
    # Count templates with archetype classification
    templates_with_archetype = await db.templates.count_documents({
        "template_data.archetype_classification": {"$exists": True}
    })
    print(f"Templates with archetype: {templates_with_archetype}")
    
    # Count avatar_interactions with archetype
    interactions_with_archetype = await db.avatar_interactions.count_documents({
        "archetype": {"$exists": True}
    })
    total_interactions = await db.avatar_interactions.count_documents({})
    print(f"Avatar interactions with archetype: {interactions_with_archetype}/{total_interactions}")
    
    # Archetype distribution
    print("\n📊 ARCHETYPE DISTRIBUTION")
    print("-"*60)
    
    pipeline = [
        {"$match": {"archetype": {"$exists": True}}},
        {"$group": {"_id": "$archetype", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    async for result in db.avatar_interactions.aggregate(pipeline):
        archetype = result["_id"]
        count = result["count"]
        percentage = (count / interactions_with_archetype) * 100
        print(f"{archetype:<20} {count:>5} ({percentage:>5.1f}%)")
    
    # Confidence score distribution
    print("\n📈 CONFIDENCE SCORE DISTRIBUTION")
    print("-"*60)
    
    pipeline = [
        {"$match": {"archetype_confidence": {"$exists": True}}},
        {"$bucket": {
            "groupBy": "$archetype_confidence",
            "boundaries": [0, 0.5, 0.7, 0.9, 1.0],
            "default": "Other",
            "output": {"count": {"$sum": 1}}
        }}
    ]
    
    async for result in db.avatar_interactions.aggregate(pipeline):
        range_start = result["_id"]
        count = result["count"]
        
        if range_start == 0:
            label = "Low (0.0-0.5)"
        elif range_start == 0.5:
            label = "Medium (0.5-0.7)"
        elif range_start == 0.7:
            label = "High (0.7-0.9)"
        elif range_start == 0.9:
            label = "Very High (0.9-1.0)"
        else:
            label = "Other"
        
        print(f"{label:<25} {count:>5}")
    
    # Low confidence scenarios (need review)
    print("\n⚠️ LOW CONFIDENCE SCENARIOS (< 0.6)")
    print("-"*60)
    
    cursor = db.avatar_interactions.find({
        "archetype_confidence": {"$lt": 0.6}
    }).limit(10)
    
    count = 0
    async for interaction in cursor:
        count += 1
        archetype = interaction.get("archetype", "Unknown")
        confidence = interaction.get("archetype_confidence", 0)
        interaction_id = interaction.get("_id")
        print(f"{interaction_id}: {archetype} (confidence: {confidence:.2f})")
    
    if count == 0:
        print("✅ No low confidence scenarios found")
    
    # Migration completeness
    print("\n✅ MIGRATION COMPLETENESS")
    print("-"*60)
    
    completion_rate = (templates_with_archetype / total_scenarios) * 100 if total_scenarios > 0 else 0
    
    print(f"Templates migrated: {completion_rate:.1f}%")
    
    if completion_rate == 100:
        print("🎉 Migration is COMPLETE!")
    elif completion_rate >= 90:
        print("✅ Migration is mostly complete")
    elif completion_rate >= 50:
        print("⚠️ Migration is in progress")
    else:
        print("❌ Migration needs attention")
    
    print("\n" + "="*60)

# Usage
if __name__ == "__main__":
    asyncio.run(verify_migration())
```

---

## 📋 Migration Checklist

### Pre-Migration
- [ ] Backup database
- [ ] Test classification with sample scenarios
- [ ] Verify OpenAI API quota
- [ ] Review archetype definitions
- [ ] Test migration script in dry-run mode

### During Migration
- [ ] Run bulk migration in batches
- [ ] Monitor API rate limits
- [ ] Check logs for errors
- [ ] Verify confidence scores
- [ ] Review low-confidence classifications

### Post-Migration
- [ ] Run verification script
- [ ] Check archetype distribution
- [ ] Review low-confidence scenarios
- [ ] Update documentation
- [ ] Train team on new system

---

## 🎯 Best Practices

### 1. Start Small
Migrate 10-20 scenarios first to:
- Test the process
- Identify issues
- Refine classification prompts
- Build confidence

### 2. Review Low Confidence
Scenarios with confidence < 0.6 need manual review:
- Check if description is clear
- Verify archetype makes sense
- Consider reclassifying manually
- Update scenario description if needed

### 3. Handle Edge Cases
Some scenarios may not fit standard archetypes:
- Document these as special cases
- Consider creating custom sub-types
- Use alternative_archetypes for guidance
- Add notes in template_data

### 4. Monitor API Usage
Classification uses OpenAI API:
- Track token usage
- Implement rate limiting
- Use batch processing
- Consider caching results

---

## 🔍 Troubleshooting

### Issue: Classification fails for some scenarios

**Solution:**
```python
# Add error handling and fallback
try:
    classification = await classifier.classify_scenario(...)
except Exception as e:
    print(f"Classification failed: {e}")
    # Manual fallback
    classification = ArchetypeClassificationResult(
        primary_archetype="HELP_SEEKING",  # Safe default
        confidence_score=0.3,  # Low confidence indicates manual classification
        reasoning="Auto-classification failed, needs manual review"
    )
```

---

### Issue: Confidence scores are consistently low

**Possible causes:**
- Scenario descriptions are vague
- Scenarios don't fit standard patterns
- Template data is incomplete

**Solutions:**
1. Improve scenario descriptions
2. Add more context to templates
3. Review archetype definitions
4. Consider custom archetypes

---

### Issue: Wrong archetype assigned

**Steps:**
1. Check the reasoning field
2. Review alternative_archetypes
3. Verify scenario description
4. Manually reclassify if needed

**Manual reclassification:**
```python
await db.avatar_interactions.update_one(
    {"_id": interaction_id},
    {"$set": {
        "archetype": "CORRECT_ARCHETYPE",
        "archetype_confidence": 1.0,  # Manual = high confidence
        "archetype_sub_type": "SUB_TYPE_IF_NEEDED"
    }}
)
```

---

## 📊 Expected Results

After successful migration:

### Archetype Distribution (Typical)
- HELP_SEEKING: 30-40%
- PERSUASION: 20-30%
- CONFRONTATION: 15-25%
- INVESTIGATION: 10-15%
- NEGOTIATION: 5-10%

### Confidence Distribution (Target)
- Very High (0.9-1.0): 40-50%
- High (0.7-0.9): 30-40%
- Medium (0.5-0.7): 10-20%
- Low (< 0.5): < 10%

---

## 🚀 Next Steps After Migration

1. **Update UI** to show archetype badges
2. **Add filtering** by archetype type
3. **Create reports** on archetype usage
4. **Train content creators** on archetype patterns
5. **Implement archetype-specific features** (Week 2+)

---

## 📞 Support

If you encounter issues during migration:

1. **Check logs** for detailed error messages
2. **Run verification script** to identify problems
3. **Review low-confidence scenarios** manually
4. **Consult archetype definitions** for guidance
5. **Test with sample scenarios** before bulk migration

---

**Ready to migrate your scenarios to the archetype system!** 🎉
