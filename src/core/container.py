from dependency_injector import containers, providers
from motor.motor_asyncio import AsyncIOMotorClient
import os

from src.infrastructure.repositories.user_repository import UserRepository
from src.application.user.services import UserService
from src.core.events import EventBus

class Container(containers.DeclarativeContainer):
    # Configuration
    config = providers.Configuration()
    print(config)
    # Database
    mongo_client = providers.Singleton(
        AsyncIOMotorClient,
        config.mongodb_uri
    )
    
    # database = providers.Singleton(
    #     lambda client: client[config.database_name],
    #     mongo_client
    # )
    database = providers.Factory(
        lambda client, db_name: client[db_name],
        client=mongo_client,
        db_name=config.database_name
    )
    
    # Event Bus
    event_bus = providers.Singleton(EventBus)
    
    # User Module
    user_repository = providers.Singleton(
        UserRepository,
        database
    )
    
    user_service = providers.Singleton(
        UserService,
        user_repository=user_repository,
        event_bus=event_bus,
        secret_key=config.secret_key,
        algorithm=config.algorithm,
        token_expire_minutes=config.token_expire_minutes
    )