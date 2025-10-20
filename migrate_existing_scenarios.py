"""
Migration Script: Classify Existing Scenarios
Adds archetype classification to existing scenarios and personas
"""

import asyncio
import sys
import os
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from openai import AsyncAzureOpenAI
from motor.motor_asyncio import AsyncIOMotorClient
from core.archetype_classifier import ArchetypeClassifier
from models.archetype_models import ScenarioArchetype

load_dotenv(".env")


async def get_database():
    """Get database connection"""
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongo_url)
    db_name = os.getenv("DB_NAME", "migoto")
    return client[db_name]


async def classify_scenario(classifier: ArchetypeClassifier, scenario_text: str) -> Dict[str, Any]:
    """Classify a single scenario"""
    try:
        result = await classifier.classify_scenario(scenario_text)
        return {
            "primary_archetype": result.primary_archetype,
            "sub_type": result.sub_type,
            "confidence_score": result.confidence_score,
            "conversation_pattern": result.conversation_pattern
        }
    except Exception as e:
        print(f"   ❌ Classification error: {e}")
        return None


async def migrate_scenarios(dry_run: bool = True):
    """Migrate existing scenarios to include archetype classification"""
    
    print("\n" + "=" * 80)
    print("ARCHETYPE MIGRATION SCRIPT")
    print("=" * 80)
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (will update database)'}")
    print()
    
    # Initialize
    db = await get_database()
    
    api_key = os.getenv("api_key")
    endpoint = os.getenv("endpoint")
    api_version = os.getenv("api_version")
    
    client = AsyncAzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint
    )
    
    classifier = ArchetypeClassifier(llm_client=client, model="gpt-4o")
    
    # Get all scenarios
    scenarios = await db.scenarios.find({}).to_list(length=None)
    print(f"📊 Found {len(scenarios)} scenarios to process\n")
    
    stats = {
        "total": len(scenarios),
        "classified": 0,
        "skipped": 0,
        "errors": 0,
        "by_archetype": {}
    }
    
    for i, scenario in enumerate(scenarios, 1):
        scenario_id = scenario.get("_id")
        scenario_name = scenario.get("scenario_name", "Unknown")
        
        print(f"[{i}/{len(scenarios)}] Processing: {scenario_name}")
        
        # Check if already classified
        if scenario.get("archetype"):
            print(f"   ⏭️  Already classified as {scenario.get('archetype')}")
            stats["skipped"] += 1
            continue
        
        # Build scenario text from available fields
        scenario_text_parts = []
        
        if scenario.get("scenario_name"):
            scenario_text_parts.append(f"Scenario: {scenario['scenario_name']}")
        
        if scenario.get("scenario_description"):
            scenario_text_parts.append(scenario["scenario_description"])
        
        # Try to get system prompt from avatar interactions
        for mode in ["learn_mode", "try_mode", "assess_mode"]:
            mode_data = scenario.get(mode, {})
            avatar_id = mode_data.get("avatar_interaction")
            if avatar_id:
                avatar = await db.avatar_interactions.find_one({"_id": str(avatar_id)})
                if avatar and avatar.get("system_prompt"):
                    scenario_text_parts.append(avatar["system_prompt"][:500])
                    break
        
        scenario_text = "\n".join(scenario_text_parts)
        
        if not scenario_text or len(scenario_text) < 50:
            print(f"   ⚠️  Insufficient text for classification")
            stats["errors"] += 1
            continue
        
        # Classify
        print(f"   🔍 Classifying... ({len(scenario_text)} chars)")
        classification = await classify_scenario(classifier, scenario_text)
        
        if not classification:
            stats["errors"] += 1
            continue
        
        archetype = classification["primary_archetype"]
        confidence = classification["confidence_score"]
        sub_type = classification.get("sub_type")
        
        print(f"   ✅ Classified as: {archetype}" + (f" ({sub_type})" if sub_type else ""))
        print(f"      Confidence: {confidence:.2f}")
        
        # Update statistics
        stats["classified"] += 1
        archetype_str = str(archetype).split(".")[-1] if "." in str(archetype) else str(archetype)
        stats["by_archetype"][archetype_str] = stats["by_archetype"].get(archetype_str, 0) + 1
        
        # Update database (if not dry run)
        if not dry_run:
            update_data = {
                "archetype": archetype_str,
                "archetype_sub_type": sub_type,
                "archetype_confidence": confidence
            }
            
            await db.scenarios.update_one(
                {"_id": scenario_id},
                {"$set": update_data}
            )
            print(f"   💾 Database updated")
        
        print()
    
    # Print summary
    print("=" * 80)
    print("MIGRATION SUMMARY")
    print("=" * 80)
    print(f"Total scenarios: {stats['total']}")
    print(f"Classified: {stats['classified']}")
    print(f"Already classified (skipped): {stats['skipped']}")
    print(f"Errors: {stats['errors']}")
    print()
    print("Distribution by archetype:")
    for archetype, count in sorted(stats["by_archetype"].items()):
        print(f"  {archetype}: {count}")
    print()
    
    if dry_run:
        print("⚠️  DRY RUN MODE - No changes were made to the database")
        print("   Run with --live flag to apply changes")
    else:
        print("✅ Migration completed successfully")


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate existing scenarios to include archetype classification")
    parser.add_argument("--live", action="store_true", help="Apply changes to database (default is dry run)")
    args = parser.parse_args()
    
    try:
        await migrate_scenarios(dry_run=not args.live)
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
