#!/usr/bin/env python3
from datetime import datetime, timedelta
from uuid import UUID, uuid4
import json
from pymongo import MongoClient
import bcrypt
from typing import Dict, List, Any

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["learning_platform"]

# Clear existing collections to prevent duplicates
collections = [
    "users", "avatars", "bot_voices", "courses", "documents", 
    "environments", "languages", "modules", "personas", 
    "scenarios", "videos", "avatar_interactions"
]

for collection in collections:
    db[collection].drop()

# Helper function to hash passwords
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

# Generate consistent UUIDs (for referential integrity)
ids = {
    "superadmin": uuid4(),
    "admin1": uuid4(),
    "admin2": uuid4(),
    "user1": uuid4(),
    "user2": uuid4(),
    "user3": uuid4(),
    "user4": uuid4(),
    "persona1": uuid4(),
    "persona2": uuid4(),
    "avatar1": uuid4(),
    "avatar2": uuid4(),
    "language1": uuid4(),
    "language2": uuid4(),
    "voice1": uuid4(),
    "voice2": uuid4(),
    "env1": uuid4(),
    "env2": uuid4(),
    "interaction1": uuid4(),
    "interaction2": uuid4(),
    "scenario1": uuid4(),
    "scenario2": uuid4(),
    "scenario3": uuid4(),
    "module1": uuid4(),
    "module2": uuid4(),
    "course1": uuid4(),
    "course2": uuid4(),
    "video1": uuid4(),
    "doc1": uuid4(),
}

# Current time (for created_at/updated_at fields)
now = datetime.now()

# Insert SuperAdmin
superadmin = {
    "_id": ids["superadmin"],
    "email": "superadmin@example.com",
    "first_name": "Super",
    "last_name": "Admin",
    "is_active": True,
    "role": "superadmin",
    "hashed_password": hash_password("SuperPassword123!"),
    "created_at": now,
    "updated_at": now,
    "assigned_courses": []
}
db.users.insert_one(superadmin)

# Insert Admins (managed by superadmin)
admin1 = {
    "_id": ids["admin1"],
    "email": "admin1@example.com",
    "first_name": "Admin",
    "last_name": "One",
    "is_active": True,
    "role": "admin",
    "hashed_password": hash_password("AdminPassword1!"),
    "created_at": now,
    "updated_at": now,
    "assigned_courses": [ids["course1"]],
    "managed_users": [ids["user1"], ids["user2"]]
}

admin2 = {
    "_id": ids["admin2"],
    "email": "admin2@example.com",
    "first_name": "Admin",
    "last_name": "Two",
    "is_active": True,
    "role": "admin",
    "hashed_password": hash_password("AdminPassword2!"),
    "created_at": now,
    "updated_at": now,
    "assigned_courses": [ids["course2"]],
    "managed_users": [ids["user3"], ids["user4"]]
}

db.users.insert_many([admin1, admin2])

# Insert Regular Users
users = [
    {
        "_id": ids["user1"],
        "email": "user1@example.com",
        "first_name": "User",
        "last_name": "One",
        "is_active": True,
        "role": "user",
        "hashed_password": hash_password("UserPassword1!"),
        "created_at": now,
        "updated_at": now,
        "assigned_courses": [ids["course1"]]
    },
    {
        "_id": ids["user2"],
        "email": "user2@example.com",
        "first_name": "User",
        "last_name": "Two",
        "is_active": True,
        "role": "user",
        "hashed_password": hash_password("UserPassword2!"),
        "created_at": now,
        "updated_at": now,
        "assigned_courses": [ids["course1"]]
    },
    {
        "_id": ids["user3"],
        "email": "user3@example.com",
        "first_name": "User",
        "last_name": "Three",
        "is_active": True,
        "role": "user",
        "hashed_password": hash_password("UserPassword3!"),
        "created_at": now,
        "updated_at": now,
        "assigned_courses": [ids["course2"]]
    },
    {
        "_id": ids["user4"],
        "email": "user4@example.com",
        "first_name": "User",
        "last_name": "Four",
        "is_active": True,
        "role": "user",
        "hashed_password": hash_password("UserPassword4!"),
        "created_at": now,
        "updated_at": now,
        "assigned_courses": [ids["course2"]]
    }
]
db.users.insert_many(users)

# Create Personas
personas = [
    {
        "_id": ids["persona1"],
        "name": "Bank Customer",
        "description": "A customer seeking banking services",
        "persona_type": "customer",
        "character_goal": "Open a premium savings account",
        "location": "Mumbai",
        "persona_details": "Tech-savvy 35-year-old professional looking for premium banking services",
        "situation": "Has recently received a significant bonus and wants to invest safely",
        "business_or_personal": "personal",
        "background_story": "Recently promoted to senior management and looking to grow savings",
        "full_persona": {
            "name": "Aditya Sharma",
            "age": 35,
            "occupation": "IT Manager",
            "financial_goals": ["Savings", "Investment", "Retirement Planning"],
            "preferences": ["Digital banking", "Premium service", "Low fees"]
        },
        "created_by": ids["admin1"],
        "created_at": now,
        "updated_at": now
    },
    {
        "_id": ids["persona2"],
        "name": "Banking Agent",
        "description": "A financial advisor at the bank",
        "persona_type": "employee",
        "character_goal": "Provide excellent customer service and recommend appropriate products",
        "location": "Mumbai",
        "persona_details": "Experienced banking professional with expertise in premium client services",
        "situation": "Working at the premium customer service desk",
        "business_or_personal": "business",
        "background_story": "5 years experience in banking with specialized training in wealth management",
        "full_persona": {
            "name": "Priya Desai",
            "age": 29,
            "experience": "5 years",
            "expertise": ["Savings products", "Wealth management", "Premium client relations"],
            "communication_style": "Professional, friendly, and knowledgeable"
        },
        "created_by": ids["admin1"],
        "created_at": now,
        "updated_at": now
    }
]
db.personas.insert_many(personas)

# Create Avatars
avatars = [
    {
        "_id": ids["avatar1"],
        "name": "Professional Man",
        "model_url": "https://storage.example.com/avatars/professional_man.glb",
        "thumbnail_url": "https://storage.example.com/avatars/thumbnails/professional_man.jpg",
        "created_by": ids["admin1"],
        "created_at": now,
        "updated_at": now
    },
    {
        "_id": ids["avatar2"],
        "name": "Banking Agent Woman",
        "model_url": "https://storage.example.com/avatars/banking_agent.glb",
        "thumbnail_url": "https://storage.example.com/avatars/thumbnails/banking_agent.jpg",
        "created_by": ids["admin1"],
        "created_at": now,
        "updated_at": now
    }
]
db.avatars.insert_many(avatars)

# Create Languages
languages = [
    {
        "_id": ids["language1"],
        "code": "en",
        "name": "English",
        "created_by": ids["superadmin"],
        "created_at": now,
        "updated_at": now
    },
    {
        "_id": ids["language2"],
        "code": "hi",
        "name": "Hindi",
        "created_by": ids["superadmin"],
        "created_at": now,
        "updated_at": now
    }
]
db.languages.insert_many(languages)

# Create Bot Voices
bot_voices = [
    {
        "_id": ids["voice1"],
        "name": "Professional Male",
        "voice_id": "en-US-Standard-D",
        "language_code": "en-US",
        "created_by": ids["admin1"],
        "created_at": now,
        "updated_at": now
    },
    {
        "_id": ids["voice2"],
        "name": "Professional Female",
        "voice_id": "en-US-Standard-F",
        "language_code": "en-US",
        "created_by": ids["admin1"],
        "created_at": now,
        "updated_at": now
    }
]
db.bot_voices.insert_many(bot_voices)

# Create Environments
environments = [
    {
        "_id": ids["env1"],
        "name": "Modern Bank Office",
        "scene_url": "https://storage.example.com/environments/bank_office.glb",
        "thumbnail_url": "https://storage.example.com/environments/thumbnails/bank_office.jpg",
        "created_by": ids["admin1"],
        "created_at": now,
        "updated_at": now
    },
    {
        "_id": ids["env2"],
        "name": "Premium Banking Lounge",
        "scene_url": "https://storage.example.com/environments/premium_lounge.glb",
        "thumbnail_url": "https://storage.example.com/environments/thumbnails/premium_lounge.jpg",
        "created_by": ids["admin1"],
        "created_at": now,
        "updated_at": now
    }
]
db.environments.insert_many(environments)

# Create Videos
videos = [
    {
        "_id": ids["video1"],
        "title": "Introduction to Premium Banking",
        "url": "https://storage.example.com/videos/premium_banking_intro.mp4",
        "description": "An overview of our premium banking services and benefits",
        "duration": 180,  # 3 minutes
        "created_by": ids["admin1"],
        "created_at": now,
        "updated_at": now
    }
]
db.videos.insert_many(videos)

# Create Documents
documents = [
    {
        "_id": ids["doc1"],
        "title": "Premium Account Benefits Guide",
        "file_url": "https://storage.example.com/documents/premium_account_guide.pdf",
        "file_type": "pdf",
        "description": "Comprehensive guide to all premium account benefits and features",
        "created_by": ids["admin1"],
        "created_at": now,
        "updated_at": now
    }
]
db.documents.insert_many(documents)

# Create Avatar Interactions
avatar_interactions = [
    {
        "_id": ids["interaction1"],
        "personas": [ids["persona1"], ids["persona2"]],
        "avatars": [ids["avatar1"], ids["avatar2"]],
        "languages": [ids["language1"]],
        "bot_voices": [ids["voice1"], ids["voice2"]],
        "environments": [ids["env1"]],
        "created_by": ids["admin1"],
        "created_at": now,
        "updated_at": now
    },
    {
        "_id": ids["interaction2"],
        "personas": [ids["persona1"], ids["persona2"]],
        "avatars": [ids["avatar1"], ids["avatar2"]],
        "languages": [ids["language1"]],
        "bot_voices": [ids["voice1"], ids["voice2"]],
        "environments": [ids["env2"]],
        "created_by": ids["admin1"],
        "created_at": now,
        "updated_at": now
    }
]
db.avatar_interactions.insert_many(avatar_interactions)

# Create Scenarios with Learn, Try and Assess modes
scenarios = [
    {
        "_id": ids["scenario1"],
        "title": "Premium Account Opening Process",
        "description": "Learn how to assist customers with opening premium accounts",
        "learn_mode": {
            "avatar_interaction": ids["interaction1"],
            "system_prompt": "You are a banking trainer explaining the premium account opening process.",
            "bot_role": "Banking Trainer",
            "bot_role_alt": "Experienced Banker",
            "content": {
                "learning_objectives": [
                    "Understand premium account features",
                    "Learn the documentation process",
                    "Master customer eligibility assessment"
                ],
                "key_points": [
                    "Premium accounts require minimum balance of ₹500,000",
                    "Customer ID verification is mandatory",
                    "Benefits include preferential rates and free services"
                ]
            }
        },
        "try_mode": {
            "avatar_interaction": ids["interaction1"],
            "system_prompt": "You are a banking agent practicing the premium account opening process with a simulated customer.",
            "bot_role": "Banking Agent",
            "content": {
                "scenario_description": "Practice helping a customer open a premium account",
                "customer_profile": "35-year-old tech professional with ₹1,000,000 to deposit"
            }
        },
        "assess_mode": {
            "avatar_interaction": ids["interaction1"],
            "system_prompt": "You are being assessed on your ability to handle the premium account opening process.",
            "bot_role": "Banking Agent",
            "content": {
                "assessment_criteria": [
                    "Correctly explaining account features",
                    "Proper document verification process",
                    "Clear communication of terms and conditions"
                ]
            }
        },
        "created_by": ids["admin1"],
        "created_at": now,
        "updated_at": now
    },
    {
        "_id": ids["scenario2"],
        "title": "Premium Customer Relationship Management",
        "description": "Learn effective relationship management for premium banking customers",
        "learn_mode": {
            "avatar_interaction": ids["interaction2"],
            "system_prompt": "You are a senior relationship manager training new staff on premium customer service.",
            "bot_role": "Senior Relationship Manager",
            "content": {
                "learning_objectives": [
                    "Understand premium customer expectations",
                    "Learn personalized service approaches",
                    "Master complaint resolution for high-value clients"
                ]
            }
        },
        "try_mode": {
            "avatar_interaction": ids["interaction2"],
            "system_prompt": "Practice handling premium customer inquiries and concerns.",
            "bot_role": "Relationship Manager",
            "content": {
                "scenario_description": "Handle a premium customer with questions about investment options"
            }
        },
        "created_by": ids["admin1"],
        "created_at": now,
        "updated_at": now
    },
    {
        "_id": ids["scenario3"],
        "title": "Premium Banking Product Cross-Selling",
        "description": "Learn techniques for effectively cross-selling premium banking products",
        "learn_mode": {
            "avatar_interaction": ids["interaction1"],
            "system_prompt": "You are learning how to identify opportunities and cross-sell premium banking products.",
            "bot_role": "Sales Trainer",
            "content": {
                "learning_objectives": [
                    "Identify cross-selling opportunities",
                    "Match customer needs with appropriate products",
                    "Present value propositions effectively"
                ]
            }
        },
        "assess_mode": {
            "avatar_interaction": ids["interaction1"],
            "system_prompt": "You are being assessed on your ability to cross-sell premium banking products.",
            "bot_role": "Banking Agent",
            "content": {
                "assessment_criteria": [
                    "Needs assessment accuracy",
                    "Product knowledge",
                    "Persuasion techniques",
                    "Objection handling"
                ]
            }
        },
        "created_by": ids["admin2"],
        "created_at": now,
        "updated_at": now
    }
]
db.scenarios.insert_many(scenarios)

# Create Modules
modules = [
    {
        "_id": ids["module1"],
        "title": "Premium Account Management",
        "description": "Comprehensive training on managing premium bank accounts",
        "scenarios": [ids["scenario1"], ids["scenario2"]],
        "created_by": ids["admin1"],
        "created_at": now,
        "updated_at": now
    },
    {
        "_id": ids["module2"],
        "title": "Premium Banking Sales Techniques",
        "description": "Advanced techniques for promoting premium banking products",
        "scenarios": [ids["scenario3"]],
        "created_by": ids["admin2"],
        "created_at": now,
        "updated_at": now
    }
]
db.modules.insert_many(modules)

# Create Courses
courses = [
    {
        "_id": ids["course1"],
        "title": "Premium Banking Fundamentals",
        "description": "Complete course covering all aspects of premium banking services",
        "is_published": True,
        "modules": [ids["module1"], ids["module2"]],
        "created_by": ids["admin1"],
        "created_at": now,
        "updated_at": now
    },
    {
        "_id": ids["course2"],
        "title": "Advanced Premium Banking",
        "description": "Advanced topics in premium banking for experienced staff",
        "is_published": False,
        "modules": [ids["module2"]],
        "created_by": ids["admin2"],
        "created_at": now,
        "updated_at": now
    }
]
db.courses.insert_many(courses)

print("MongoDB initialization completed successfully!")
print(f"Created {db.users.count_documents({})} users")
print(f"Created {db.courses.count_documents({})} courses")
print(f"Created {db.modules.count_documents({})} modules")
print(f"Created {db.scenarios.count_documents({})} scenarios")