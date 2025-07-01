"""
Azure Search Setup and Configuration
File: enhanced_system/utils/azure_search_setup.py

Sets up the search index for document-backed chat system
"""

import asyncio
import json
import os
from typing import Dict, Any, List
from azure.search.documents.indexes.aio import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SearchField, SearchFieldDataType, SimpleField, SearchableField,
    VectorSearch, VectorSearchProfile, HnswAlgorithmConfiguration,
    SemanticConfiguration, SemanticSearch, SemanticField,
    CorsOptions
)
from azure.search.documents.aio import SearchClient
from azure.core.credentials import AzureKeyCredential

class AzureSearchIndexManager:
    """Manages Azure Cognitive Search index for RAG system"""
    
    def __init__(self):
        self.endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        self.api_key = os.getenv("AZURE_SEARCH_API_KEY")
        self.index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "enhanced-knowledge-base")
        
        if not self.endpoint or not self.api_key:
            raise ValueError("Azure Search endpoint and API key must be set in environment variables")
        
        self.index_client = SearchIndexClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.api_key)
        )
    
    async def create_knowledge_base_index(self) -> bool:
        """Create the knowledge base search index"""
        try:
            # Define the search index
            index = SearchIndex(
                name=self.index_name,
                fields=[
                    # Basic document fields
                    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                    SearchableField(
                        name="content", 
                        type=SearchFieldDataType.String,
                        analyzer_name="en.microsoft"
                    ),
                    SimpleField(name="document_id", type=SearchFieldDataType.String, filterable=True),
                    SimpleField(name="knowledge_base_id", type=SearchFieldDataType.String, filterable=True),
                    SimpleField(name="scenario_id", type=SearchFieldDataType.String, filterable=True),
                    SimpleField(name="chunk_index", type=SearchFieldDataType.Int32),
                    SimpleField(name="word_count", type=SearchFieldDataType.Int32),
                    SimpleField(name="source_file", type=SearchFieldDataType.String, filterable=True),
                    SimpleField(name="document_type", type=SearchFieldDataType.String, filterable=True),
                    SimpleField(name="section", type=SearchFieldDataType.String, filterable=True),
                    SimpleField(name="page_number", type=SearchFieldDataType.Int32),
                    
                    # Vector field for semantic search
                    SearchField(
                        name="contentVector",
                        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                        searchable=True,
                        vector_search_dimensions=1536,  # OpenAI ada-002 embedding size
                        vector_search_profile_name="myHnswProfile"
                    ),
                    
                    # Additional metadata fields
                    SimpleField(name="created_at", type=SearchFieldDataType.DateTimeOffset),
                    SearchableField(name="keywords", type=SearchFieldDataType.String),
                    SimpleField(name="importance_score", type=SearchFieldDataType.Double)
                ],
                
                # Vector search configuration
                vector_search=VectorSearch(
                    profiles=[
                        VectorSearchProfile(
                            name="myHnswProfile",
                            algorithm_configuration_name="myHnsw"
                        )
                    ],
                    algorithms=[
                        HnswAlgorithmConfiguration(
                            name="myHnsw"
                        )
                    ]
                ),
                
                # Semantic search configuration for better relevance
                semantic_search=SemanticSearch(
                    configurations=[
                        SemanticConfiguration(
                            name="my-semantic-config",
                            prioritized_fields={
                                "title_field": SemanticField(field_name="source_file"),
                                "content_fields": [SemanticField(field_name="content")],
                                "keywords_fields": [SemanticField(field_name="keywords")]
                            }
                        )
                    ]
                ),
                
                # CORS settings for web access
                cors_options=CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
            )
            
            # Create the index
            result = await self.index_client.create_index(index)
            print(f"✅ Index '{self.index_name}' created successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error creating index: {e}")
            return False
        finally:
            # Always close the index client
            await self.index_client.close()
    
    async def delete_index(self) -> bool:
        """Delete the search index"""
        try:
            await self.index_client.delete_index(self.index_name)
            print(f"✅ Index '{self.index_name}' deleted successfully")
            return True
        except Exception as e:
            print(f"❌ Error deleting index: {e}")
            return False
        finally:
            await self.index_client.close()
    
    async def index_exists(self) -> bool:
        """Check if the index exists"""
        try:
            await self.index_client.get_index(self.index_name)
            return True
        except Exception:
            return False
        finally:
            await self.index_client.close()
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        search_client = SearchClient(
            endpoint=self.endpoint,
            index_name=self.index_name,
            credential=AzureKeyCredential(self.api_key)
        )
        
        try:
            # Get document count
            results = await search_client.search("*", include_total_count=True)
            total_count = results.get_count()
            
            # Get index definition
            index_def = await self.index_client.get_index(self.index_name)
            
            return {
                "index_name": self.index_name,
                "document_count": total_count,
                "fields_count": len(index_def.fields),
                "vector_search_enabled": index_def.vector_search is not None,
                "semantic_search_enabled": index_def.semantic_search is not None
            }
            
        except Exception as e:
            return {"error": str(e)}
        finally:
            # Close both clients
            await search_client.close()
            await self.index_client.close()

# Setup and validation functions
async def setup_azure_search():
    """Setup Azure Search for the RAG system"""
    
    print("🔧 Setting up Azure Cognitive Search for Document-Backed Chat...")
    
    # Initialize manager
    try:
        manager = AzureSearchIndexManager()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\n📋 Required environment variables:")
        print("- AZURE_SEARCH_ENDPOINT: Your Azure Search service endpoint")
        print("- AZURE_SEARCH_API_KEY: Your Azure Search admin API key")
        print("- AZURE_SEARCH_INDEX_NAME: Name for your index (optional, defaults to 'enhanced-knowledge-base')")
        return False
    
    # Check if index already exists
    if await manager.index_exists():
        print(f"ℹ️  Index '{manager.index_name}' already exists.")
        
        # Get current stats
        stats = await manager.get_index_stats()
        if "error" not in stats:
            print(f"📊 Current index stats: {json.dumps(stats, indent=2)}")
        
        recreate = input("❓ Do you want to recreate the index? (y/N): ").lower()
        if recreate == 'y':
            if await manager.delete_index():
                print("🗑️  Existing index deleted.")
            else:
                print("❌ Failed to delete existing index.")
                return False
        else:
            print("✅ Using existing index.")
            return True
    
    # Create new index
    if await manager.create_knowledge_base_index():
        print("🎉 Azure Search index created successfully!")
        
        # Verify setup
        stats = await manager.get_index_stats()
        if "error" not in stats:
            print(f"✅ Index verification: {json.dumps(stats, indent=2)}")
        
        return True
    else:
        print("❌ Failed to create Azure Search index.")
        return False

def validate_azure_search_config():
    """Validate Azure Search configuration"""
    required_vars = [
        "AZURE_SEARCH_ENDPOINT",
        "AZURE_SEARCH_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        return False
    
    print("✅ Azure Search configuration is valid")
    return True

# Testing utilities
class SearchTestUtilities:
    """Utilities for testing the search setup"""
    
    @staticmethod
    async def test_search_connection():
        """Test connection to Azure Search"""
        try:
            manager = AzureSearchIndexManager()
            stats = await manager.get_index_stats()
            
            if "error" in stats:
                print(f"❌ Connection test failed: {stats['error']}")
                return False
            else:
                print(f"✅ Connection successful! Index stats: {json.dumps(stats, indent=2)}")
                return True
                
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    @staticmethod
    async def test_document_indexing():
        """Test document indexing with sample data"""
        search_client = SearchClient(
            endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            index_name=os.getenv("AZURE_SEARCH_INDEX_NAME", "enhanced-knowledge-base"),
            credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
        )
        
        try:
            # Sample test document
            test_doc = {
                "id": "test-doc-1",
                "content": "This is a test document for verifying the search index functionality.",
                "document_id": "test-document",
                "knowledge_base_id": "test-kb",
                "scenario_id": "test-scenario",
                "chunk_index": 0,
                "word_count": 12,
                "source_file": "test.txt",
                "document_type": "test",
                "contentVector": [0.1] * 1536,  # Dummy vector
                "created_at": "2024-01-01T00:00:00Z",
                "keywords": "test document search"
            }
            
            # Index the test document
            await search_client.upload_documents([test_doc])
            print("✅ Test document indexed successfully")
            
            # Wait a moment for indexing
            await asyncio.sleep(2)
            
            # Test search functionality
            search_results = await search_client.search("test document")
            result_count = 0
            async for result in search_results:
                result_count += 1
                print(f"📄 Found test document: {result['id']}")
            
            if result_count > 0:
                print("✅ Search functionality verified")
                
                # Clean up test document
                await search_client.delete_documents([{"id": "test-doc-1"}])
                print("🧹 Test document cleaned up")
                return True
            else:
                print("❌ Search test failed - no results found")
                return False
                
        except Exception as e:
            print(f"❌ Document indexing test failed: {e}")
            return False
        finally:
            # Always close the client
            await search_client.close()
    
    @staticmethod
    async def run_all_tests():
        """Run all tests"""
        print("🧪 Running Azure Search setup tests...\n")
        
        # Test 1: Configuration validation
        print("1️⃣ Testing configuration...")
        config_valid = validate_azure_search_config()
        
        if not config_valid:
            print("❌ Configuration test failed. Please fix environment variables.")
            return False
        
        # Test 2: Connection test
        print("\n2️⃣ Testing connection...")
        connection_ok = await SearchTestUtilities.test_search_connection()
        
        if not connection_ok:
            print("❌ Connection test failed. Check your Azure Search service.")
            return False
        
        # Test 3: Document indexing test
        print("\n3️⃣ Testing document indexing...")
        indexing_ok = await SearchTestUtilities.test_document_indexing()
        
        if not indexing_ok:
            print("❌ Document indexing test failed.")
            return False
        
        print("\n🎉 All tests passed! Your Azure Search setup is ready for document-backed chat.")
        return True

# Sample environment file content
SAMPLE_ENV_CONFIG = """
# Azure Search Configuration for Document-Backed Chat
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_API_KEY=your-admin-api-key-here
AZURE_SEARCH_INDEX_NAME=enhanced-knowledge-base

# Your existing Azure OpenAI configuration
api_key=your-openai-api-key
endpoint=https://your-openai-resource.openai.azure.com/
api_version=2024-02-15-preview
"""

# CLI script for setup
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "validate":
            validate_azure_search_config()
        elif command == "setup":
            asyncio.run(setup_azure_search())
        elif command == "test":
            asyncio.run(SearchTestUtilities.run_all_tests())
        elif command == "sample-env":
            print("📝 Sample .env configuration:")
            print(SAMPLE_ENV_CONFIG)
        else:
            print("❓ Available commands:")
            print("  validate    - Validate configuration")
            print("  setup      - Setup Azure Search index")
            print("  test       - Run comprehensive tests")
            print("  sample-env - Show sample environment configuration")
    else:
        print("🔍 Azure Search Setup Script")
        print("Usage: python azure_search_setup.py [command]")
        print("\n📋 Commands:")
        print("  validate    - Validate environment configuration")
        print("  setup      - Create/setup the search index")
        print("  test       - Run comprehensive functionality tests")
        print("  sample-env - Display sample environment variables")
        print("\n🚀 Quick start:")
        print("1. python azure_search_setup.py sample-env")
        print("2. Add environment variables to your .env file")
        print("3. python azure_search_setup.py validate")
        print("4. python azure_search_setup.py setup")
        print("5. python azure_search_setup.py test")