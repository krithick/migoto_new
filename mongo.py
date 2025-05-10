"""
MongoDB Client Class

This module provides a MongoDB client class for connecting to MongoDB
and accessing the various collections in the database.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Type
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI, HTTPException, Depends
import importlib
import inspect
from fastapi import FastAPI, HTTPException, Depends, Form
from pydantic import BaseModel,Field
from typing import Dict, List, Optional
from datetime import datetime
import motor.motor_asyncio
import uuid
from fastapi.middleware.cors import CORSMiddleware
import json
import random
import uvicorn
import re
import os
from dotenv import load_dotenv
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import StreamingResponse
import io
import asyncio
from models_old import BotConfig,BotConfigAnalyser,ChatReport,ChatSession,Message ,ChatReport_
from models.evaluation_models import Evaluation
# Any helper class

class MongoDB:
    def __init__(self,MONGO_URL,DATABASE_NAME):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL, uuidRepresentation='standard')
        self.db = self.client[DATABASE_NAME]
        
        # Original collections
        self.sessions = self.db.sessions
        self.analysis = self.db.analysis
        self.bot_configs = self.db.bot_configs
        self.bot_configs_analyser = self.db.bot_configs_analyser
        self.courses = self.db.courses
        self.modules = self.db.modules
        self.scenarios = self.db.scenarios
        self.personas = self.db.personas
        self.avatars = self.db.avatars
        self.languages = self.db.languages
        self.bot_voices = self.db.bot_voices
        self.environments = self.db.environments
        self.videos = self.db.videos
        self.documents = self.db.documents
        self.avatar_interactions = self.db.avatar_interactions
        self.users = self.db.users
        self.file_uploads = self.db.file_uploads
        
        # Existing course assignment collection
        self.user_course_assignments = self.db.user_course_assignments
        
        # New collections for module and scenario assignments
        self.user_module_assignments = self.db.user_module_assignments
        self.user_scenario_assignments = self.db.user_scenario_assignments
        
    # Existing functions
    async def create_session(self, session: ChatSession) -> str:
        await self.sessions.insert_one(session.dict())
        return session.session_id
    
    # for evaluation 
    async def create_conversation_analysis(self,report:ChatReport) -> str:
        reprot_dict=report.dict()
        if "_id" in reprot_dict:
            reprot_dict["_id"] = str(reprot_dict["_id"]) 
        await self.analysis.insert_one(reprot_dict)
        
    # for sales
    async def create_conversation_analysis_(self,report:ChatReport_) -> str:
        await self.analysis.insert_one(report.dict())
    
    # get sessions 
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        session_data = await self.sessions.find_one({"session_id": session_id})
        if session_data:
            return ChatSession(**session_data)
        return None
    
    # get sessions raw
    async def get_session_raw(self, session_id: str) -> Optional[ChatSession]:
        session_data = await self.sessions.find_one({"_id": str(session_id)})
        if session_data:
            return session_data
        return None
    
    # get session analysis for evaluation
    async def get_session_analysis(self, session_id: str) -> Optional[ChatSession]:
        session_data = await self.analysis.find_one({"session_id": str(session_id)})
        if session_data:
            return Evaluation(**session_data)
        return None
    
    # for sales
    async def get_session_analysis_(self, session_id: str) -> Optional[ChatSession]:
        session_data = await self.analysis.find_one({"session_id": session_id})
        print("here")
        if session_data:
            return ChatReport_(**session_data)
        return None
    
    async def update_session(self, session: ChatSession):
        session.last_updated = datetime.now()
        await self.sessions.update_one(
            {"session_id": session.session_id},
            {"$set": session.dict()}
        )
    
    async def create_bot(self,bot_config:BotConfig):
        bot= await self.bot_configs.insert_one(bot_config.dict())
        if bot :
            return bot
        else:
            HTTPException(status_code=400,detail="Error creating Bot")
    
    async def create_bot_analyser(self,bot_config:BotConfigAnalyser):
        bot= await self.bot_configs_analyser.insert_one(bot_config.dict())
        if bot :
            return bot
        else:
            HTTPException(status_code=400,detail="Error creating Bot")
            
    async def update_bot_analyser(self, bot_id: str, bot: BotConfigAnalyser):
        """
        Update an existing bot analyser with new data
        Returns True if update was successful, False if bot not found
        """
        # Update last_updated timestamp if field exists in model
        if hasattr(bot, 'last_updated'):
            bot.last_updated = datetime.now()
    
        result = await self.bot_configs_analyser.update_one(
            {"bot_id": bot_id},
            {"$set": bot.dict()}
        )
    
        if result.matched_count == 0:
            return False
        return True

    async def get_all_bot_analysers(self):
        """
        Retrieve all bot analysers from the database
        """
        cursor = self.bot_configs_analyser.find({})
        bots = await cursor.to_list(length=100)  # Adjust length as needed for pagination

        # Convert MongoDB _id to string for JSON serialization if needed
        for bot in bots:
            if '_id' in bot:
                bot['_id'] = str(bot['_id'])
    
        return bots

    async def get_bot_analyser(self, bot_id: str):
        """
        Retrieve a specific bot analyser by ID
        Returns None if bot not found
        """
        bot = await self.bot_configs_analyser.find_one({"bot_id": bot_id})
    
        # Convert MongoDB _id to string for JSON serialization if needed
        if bot and '_id' in bot:
            bot['_id'] = str(bot['_id'])
    
        return bot

    async def delete_bot_analyser(self, bot_id: str):
        """
        Delete a bot analyser by ID
        Returns True if deletion was successful, False if bot not found
        """
        result = await self.bot_configs_analyser.delete_one({"bot_id": bot_id})
        return result.deleted_count > 0

    async def get_active_bot_analysers(self):
        """
        Retrieve only active bot analysers
        """
        cursor = self.bot_configs_analyser.find({"is_active": True})
        bots = await cursor.to_list(length=100)
    
        # Convert MongoDB _id to string for JSON serialization if needed
        for bot in bots:
            if '_id' in bot:
                bot['_id'] = str(bot['_id'])
    
        return bots

    async def search_bot_analysers(self, query: str):
        """
        Search for bot analysers by name or description
        """
        # Create a case-insensitive text search query
        search_query = {
            "$or": [
                {"bot_name": {"$regex": query, "$options": "i"}},
                {"bot_description": {"$regex": query, "$options": "i"}}
            ]
        }
    
        cursor = self.bot_configs_analyser.find(search_query)
        bots = await cursor.to_list(length=100)
    
        # Convert MongoDB _id to string for JSON serialization if needed
        for bot in bots:
            if '_id' in bot:
                bot['_id'] = str(bot['_id'])
    
        return bots
    
    async def update_bot(self, bot_id: str, bot: BotConfig):
        """
        Update an existing bot with new data
        Returns True if update was successful, False if bot not found
        """
        if hasattr(bot, 'last_updated'):
            bot.last_updated = datetime.now()
    
        result = await self.bot_configs.update_one(
            {"bot_id": bot_id},
            {"$set": bot.dict()}
        )
    
        if result.matched_count == 0:
            return False
        return True

    async def get_all_bots(self):
        """
        Retrieve all bots from the database
        """
        cursor = self.bot_configs.find({})
        bots = await cursor.to_list(length=100)
    
        # Convert MongoDB _id to string for JSON serialization
        for bot in bots:
            if '_id' in bot:
                bot['_id'] = str(bot['_id'])
    
        return bots

    async def get_bot(self, bot_id: str):
        """
        Retrieve a specific bot by ID
        Returns None if bot not found
        """
        bot = await self.bot_configs.find_one({"bot_id": bot_id})
    
        # Convert MongoDB _id to string for JSON serialization
        if bot and '_id' in bot:
            bot['_id'] = str(bot['_id'])
    
        return bot
        
    # New methods for module and scenario assignments
    
    async def initialize_module_assignments_collection(self):
        """
        Create indexes for the module assignments collection
        """
        # Create compound index on user_id and module_id for faster lookups
        await self.user_module_assignments.create_index([
            ("user_id", 1), 
            ("module_id", 1)
        ], unique=True)
        
        # Create index on course_id for filtering by course
        await self.user_module_assignments.create_index([
            ("user_id", 1), 
            ("course_id", 1)
        ])
        
        # Create index on completion status
        await self.user_module_assignments.create_index([
            ("user_id", 1), 
            ("completed", 1)
        ])
    
    async def initialize_scenario_assignments_collection(self):
        """
        Create indexes for the scenario assignments collection
        """
        # Create compound index on user_id and scenario_id for faster lookups
        await self.user_scenario_assignments.create_index([
            ("user_id", 1), 
            ("scenario_id", 1)
        ], unique=True)
        
        # Create index on module_id for filtering by module
        await self.user_scenario_assignments.create_index([
            ("user_id", 1), 
            ("module_id", 1)
        ])
        
        # Create index on completion status
        await self.user_scenario_assignments.create_index([
            ("user_id", 1), 
            ("completed", 1)
        ])
        
        # Create index on assigned_modes for filtering by mode
        await self.user_scenario_assignments.create_index([
            ("user_id", 1), 
            ("assigned_modes", 1)
        ])
    
    async def get_collection_names(self):
        """
        Get a list of all collection names in the database
        """
        return await self.db.list_collection_names()
        
    async def initialize_collections(self):
        """
        Initialize all collections and create necessary indexes
        """
        # Get all collection names
        collections = await self.get_collection_names()
        
        # Check if the new collections exist, create indexes if they do
        if "user_module_assignments" in collections:
            await self.initialize_module_assignments_collection()
        
        if "user_scenario_assignments" in collections:
            await self.initialize_scenario_assignments_collection()