from datetime import datetime, timedelta  
from uuid import UUID  
from models.tier_models import CompanyTier, CompanyUsage  
from models.company_models import CompanyType  
from core.tier_management import tier_manager  
  
# Migration Functions  
async def migrate_companies_to_tier_system(db):  
    """Migrate existing companies to use the tier system"""  
    print("🚀 Starting tier system migration for your application...")  
    try:  
        await tier_manager.initialize_tier_system(db)  
        companies_updated = 0  
        cursor = db.companies.find({})  
          
        async for company_doc in cursor:  
            company_id = company_doc["_id"]  
            company_type = company_doc.get("company_type", "client")  
            company_name = company_doc.get("name", "Unknown")  
  
            if company_type == "mother":  
                new_tier = CompanyTier.UNLIMITED  
            else:  
                user_count = await db.users.count_documents({"company_id": company_id})  
                course_count = await db.courses.count_documents({"company_id": company_id})  
  
                if user_count > 100 or course_count > 25:  
                    new_tier = CompanyTier.ENTERPRISE  
                elif user_count > 25 or course_count > 5:  
                    new_tier = CompanyTier.PROFESSIONAL  
                else:  
                    new_tier = CompanyTier.BASIC  
  
            update_data = {  
                "tier": new_tier.value,  
                "tier_upgraded_at": datetime.now(),  
                "updated_at": datetime.now()  
            }  
  
            if new_tier != CompanyTier.UNLIMITED:  
                update_data["tier_expires_at"] = datetime.now() + timedelta(days=365)  
  
            await db.companies.update_one({"_id": company_id}, {"$set": update_data})  
            companies_updated += 1  
            print(f"  ✅ Updated {company_name} to {new_tier.value} tier")  
  
        await create_initial_usage_tracking(db)  
        print(f"✅ Migration completed! Updated {companies_updated} companies")  
        await print_tier_migration_summary(db)  
  
    except Exception as e:  
        print(f"❌ Migration failed: {e}")  
        raise  
  
async def create_initial_usage_tracking(db):  
    """Create initial usage tracking documents for all companies"""  
    print("📊 Creating initial usage tracking...")  
    try:  
        companies_cursor = db.companies.find({})  
        usage_docs_created = 0  
  
        async for company in companies_cursor:  
            company_id = company["_id"]  
            existing_usage = await db.company_usage.find_one({"company_id": company_id})  
  
            if existing_usage:  
                continue  
  
            current_period = datetime.now().strftime("%Y-%m")  
            initial_usage_entries = []  
  
            chat_count = await db.sessions.count_documents({  
                "created_at": {"$gte": datetime.now().replace(day=1)}  
            })  
  
            if chat_count > 0:  
                initial_usage_entries.append({  
                    "usage_key": "chat_sessions_per_month",  
                    "current_value": chat_count,  
                    "period_start": datetime.now().replace(day=1),  
                    "last_reset": datetime.now().replace(day=1)  
                })  
  
            analysis_count = await db.analysis.count_documents({  
                "timestamp": {"$gte": datetime.now().replace(day=1)}  
            })  
  
            if analysis_count > 0:  
                initial_usage_entries.append({  
                    "usage_key": "analysis_reports_per_month",  
                    "current_value": analysis_count,  
                    "period_start": datetime.now().replace(day=1),  
                    "last_reset": datetime.now().replace(day=1)  
                })  
  
            usage_doc = {  
                "company_id": company_id,  
                "current_period": current_period,  
                "usage_entries": initial_usage_entries,  
                "last_updated": datetime.now()  
            }  
  
            await db.company_usage.insert_one(usage_doc)  
            usage_docs_created += 1  
  
        print(f"✅ Created usage tracking for {usage_docs_created} companies")  
  
    except Exception as e:  
        print(f"❌ Error creating usage tracking: {e}")  
        raise  
  
async def print_tier_migration_summary(db):  
    """Print a summary of the tier migration"""  
    print("\n" + "="*60)  
    print("TIER SYSTEM MIGRATION SUMMARY")  
    print("="*60)  
    try:  
        tier_counts = {}  
        for tier in CompanyTier:  
            count = await db.companies.count_documents({"tier": tier.value})  
            tier_counts[tier.value] = count  
  
        print("TIER DISTRIBUTION:")  
        total_companies = sum(tier_counts.values())  
        for tier, count in tier_counts.items():  
            percentage = (count / total_companies * 100) if total_companies > 0 else 0  
            print(f"  {tier.upper():<12}: {count:>3} companies ({percentage:>5.1f}%)")  
  
        print(f"\nTOTAL COMPANIES: {total_companies}")  
        usage_docs = await db.company_usage.count_documents({})  
        print(f"USAGE TRACKING:  {usage_docs} companies")  
  
        basic_config = tier_manager.tier_configs[CompanyTier.BASIC]  
        print(f"\nBASIC TIER LIMITS:")  
        for limit in basic_config.limits[:5]:  
            value_display = "Unlimited" if limit.limit_value == -1 else str(limit.limit_value)  
            print(f"  {limit.limit_name:<25}: {value_display}")  
        print("="*60)  
  
    except Exception as e:  
        print(f"❌ Summary failed: {e}")  
        raise  
  
async def verify_tier_system(db):  
    """Verify that the tier system is working correctly"""  
    print("🔍 Verifying tier system...")  
    try:  
        companies_without_tiers = await db.companies.count_documents({"tier": {"$exists": False}})  
        if companies_without_tiers > 0:  
            print(f"⚠️  Warning: {companies_without_tiers} companies missing tier info")  
        else:  
            print("✅ All companies have tier information")  
  
        companies_with_usage = await db.company_usage.count_documents({})  
        total_companies = await db.companies.count_documents({})  
        print(f"✅ Usage tracking: {companies_with_usage}/{total_companies} companies")  
  
        sample_company = await db.companies.find_one({"tier": {"$ne": "unlimited"}})  
        if sample_company:  
            company_id = UUID(sample_company["_id"])  
            course_check = await tier_manager.can_create_course(db, company_id)  
            print(f"✅ Course creation check: {'Allowed' if course_check.allowed else 'Blocked'} "  
                  f"({course_check.current_usage}/{course_check.limit_value})")  
  
            chat_check = await tier_manager.can_start_chat_session(db, company_id)  
            print(f"✅ Chat session check: {'Allowed' if chat_check.allowed else 'Blocked'} "  
                  f"({chat_check.current_usage}/{chat_check.limit_value})")  
  
        tier_configs = await db.tier_configurations.count_documents({})  
        expected_tiers = len(CompanyTier)  
        if tier_configs == expected_tiers:  
            print(f"✅ Tier configurations: {tier_configs}/{expected_tiers} tiers configured")  
        else:  
            print(f"⚠️  Warning: {tier_configs}/{expected_tiers} tier configurations found")  
  
        print("✅ Tier system verification completed")  
  
    except Exception as e:  
        print(f"❌ Verification failed: {e}")  
        raise  
  
async def run_complete_tier_migration(db):  
    """Run the complete tier system migration"""  
    print("🎯 STARTING COMPLETE TIER SYSTEM MIGRATION")  
    print("="*50)  
    try:  
        await migrate_companies_to_tier_system(db)  
        await verify_tier_system(db)  
        print("\n🎉 TIER SYSTEM MIGRATION COMPLETED SUCCESSFULLY!")  
        print("="*50)  
        print("\nNext Steps:")  
        print("1. Add tier checking to your existing endpoints")  
        print("2. Update your frontend to show tier information")  
        print("3. Set up monthly usage reset scheduled task")  
        print("4. Test tier upgrades and downgrades")  
        print("5. Configure billing integration (if needed)")  
  
    except Exception as e:  
        print(f"\n💥 MIGRATION FAILED: {e}")  
        print("Please fix the error and try again.")  
        raise  
  
# Rollback Function  
async def rollback_tier_migration(db):  
    """Rollback tier system migration if needed"""  
    print("🔄 Rolling back tier system migration...")  
    try:  
        await db.companies.update_many(  
            {},  
            {"$unset": {  
                "tier": "",  
                "tier_expires_at": "",  
                "tier_upgraded_by": "",  
                "tier_upgraded_at": "",  
                "tier_notes": ""  
            }}  
        )  
  
        await db.company_usage.drop()  
        await db.company_usage_history.drop()  
        await db.tier_configurations.drop()  
        print("✅ Rollback completed successfully")  
  
    except Exception as e:  
        print(f"❌ Rollback failed: {e}")  
        raise  
    
async def run_migration():  
    from database import db
     # This function should return your database connection  
    await run_complete_tier_migration(db)  
import asyncio  
  
if __name__ == "__main__":  
    asyncio.run(run_migration())  