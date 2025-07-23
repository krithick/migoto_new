from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form ,Body 
from typing import List, Any ,Dict
from uuid import uuid4
from datetime import datetime
from database import get_db
from models.user_models import UserDB
from core.user import get_current_user
from core.document_processor import DocumentProcessor
from core.azure_search_manager import AzureVectorSearchManager

router = APIRouter(prefix="/knowledge-base", tags=["Knowledge Base Management"])

@router.post("/create/{template_id}")
async def create_knowledge_base_for_template(
    template_id: str,
    supporting_docs: List[UploadFile] = File(...),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Create knowledge base for existing template"""
    
    # Get template
    template = await db.templates.find_one({"id": template_id})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Create knowledge base
    knowledge_base_id = f"kb_{template_id}"
    
    # Process documents
    docs_metadata = await process_and_index_documents(supporting_docs, knowledge_base_id, db)
    
    # Create knowledge base record
    kb_record = {
        "_id": knowledge_base_id,
        "template_id": template_id,
        "scenario_title": template.get("name", "Unknown"),
        "supporting_documents": docs_metadata,
        "total_documents": len(docs_metadata),
        "created_at": datetime.now(),
        "last_updated": datetime.now(),
        "fact_checking_enabled": len(docs_metadata) > 0
    }
    
    await db.knowledge_bases.insert_one(kb_record)
    
    # Update template to reference knowledge base
    await db.templates.update_one(
        {"id": template_id},
        {"$set": {
            "knowledge_base_id": knowledge_base_id,
            "fact_checking_enabled": True
        }}
    )
    
    return {
        "knowledge_base_id": knowledge_base_id,
        "documents_processed": len(docs_metadata),
        "template_updated": True
    }

@router.get("/{knowledge_base_id}")
async def get_knowledge_base_details(
    knowledge_base_id: str,
    db: Any = Depends(get_db)
):
    """Get knowledge base details"""
    
    kb = await db.knowledge_bases.find_one({"_id": knowledge_base_id})
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    return kb

@router.put("/{knowledge_base_id}/documents")
async def update_knowledge_base_documents(
    knowledge_base_id: str,
    action: str = Form(...),  # "add", "remove", "replace"
    new_docs: List[UploadFile] = File(default=[]),
    remove_doc_ids: List[str] = Form(default=[]),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Update documents in knowledge base - HANDLES VECTOR CLEANUP"""
    
    kb = await db.knowledge_bases.find_one({"_id": knowledge_base_id})
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    existing_docs = kb.get("supporting_documents", [])
    
    if action == "add":
        # Add new documents
        new_docs_metadata = await process_and_index_documents(new_docs, knowledge_base_id, db)
        all_docs = existing_docs + new_docs_metadata
        
        await db.knowledge_bases.update_one(
            {"_id": knowledge_base_id},
            {"$set": {
                "supporting_documents": all_docs,
                "total_documents": len(all_docs),
                "last_updated": datetime.now()
            }}
        )
        
        return {
            "action": "add",
            "new_documents": len(new_docs_metadata),
            "total_documents": len(all_docs)
        }
        
    elif action == "remove":
        # Remove documents AND their vector data
        await remove_documents_and_vectors(remove_doc_ids, knowledge_base_id, db)
        remaining_docs = [doc for doc in existing_docs if doc["_id"] not in remove_doc_ids]
        
        await db.knowledge_bases.update_one(
            {"_id": knowledge_base_id},
            {"$set": {
                "supporting_documents": remaining_docs,
                "total_documents": len(remaining_docs),
                "last_updated": datetime.now(),
                "fact_checking_enabled": len(remaining_docs) > 0
            }}
        )
        
        return {
            "action": "remove",
            "removed_documents": len(remove_doc_ids),
            "remaining_documents": len(remaining_docs),
            "vector_data_cleaned": True
        }
        
    elif action == "replace":
        # Remove all existing documents and vectors
        if existing_docs:
            existing_ids = [doc["_id"] for doc in existing_docs]
            await remove_documents_and_vectors(existing_ids, knowledge_base_id, db)
        
        # Add new documents
        new_docs_metadata = await process_and_index_documents(new_docs, knowledge_base_id, db)
        
        await db.knowledge_bases.update_one(
            {"_id": knowledge_base_id},
            {"$set": {
                "supporting_documents": new_docs_metadata,
                "total_documents": len(new_docs_metadata),
                "last_updated": datetime.now(),
                "fact_checking_enabled": len(new_docs_metadata) > 0
            }}
        )
        
        return {
            "action": "replace",
            "old_documents_removed": len(existing_docs),
            "new_documents_added": len(new_docs_metadata),
            "vector_data_replaced": True
        }
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'add', 'remove', or 'replace'")

@router.delete("/{knowledge_base_id}")
async def delete_knowledge_base(
    knowledge_base_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Delete entire knowledge base and all vector data"""
    
    kb = await db.knowledge_bases.find_one({"_id": knowledge_base_id})
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    # Remove all documents and vectors
    all_doc_ids = [doc["_id"] for doc in kb.get("supporting_documents", [])]
    if all_doc_ids:
        await remove_documents_and_vectors(all_doc_ids, knowledge_base_id, db)
    
    # Delete knowledge base record
    await db.knowledge_bases.delete_one({"_id": knowledge_base_id})
    
    # Update template
    if kb.get("template_id"):
        await db.templates.update_one(
            {"id": kb["template_id"]},
            {"$unset": {"knowledge_base_id": "", "fact_checking_enabled": ""}}
        )
    
    return {
        "message": "Knowledge base deleted successfully",
        "documents_removed": len(all_doc_ids),
        "vector_data_cleaned": True
    }

@router.get("/{knowledge_base_id}/search-test")
async def test_knowledge_base_search(
    knowledge_base_id: str,
    query: str,
    top_k: int = 5,
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Test search functionality of knowledge base"""
    
    try:
        from openai import AsyncAzureOpenAI
        import os
        
        openai_client = AsyncAzureOpenAI(
            api_key=os.getenv("api_key"),
            azure_endpoint=os.getenv("endpoint"),
            api_version=os.getenv("api_version")
        )
        
        vector_search = AzureVectorSearchManager()
        search_results = await vector_search.vector_search(
            query, knowledge_base_id, top_k, openai_client
        )
        
        return {
            "query": query,
            "knowledge_base_id": knowledge_base_id,
            "results_found": len(search_results),
            "results": search_results,
            "search_successful": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search test failed: {str(e)}")


# @router.get("/{knowledge_base_id}/stats")
# async def get_knowledge_base_stats(
#     knowledge_base_id: str,
#     current_user: UserDB = Depends(get_current_user),
#     db: Any = Depends(get_db)
# ):
#     """Get knowledge base statistics - FIXED VERSION"""
    
#     # GET DATA FROM supporting_documents (not knowledge_bases)
#     docs = await db.supporting_documents.find(
#         {"knowledge_base_id": knowledge_base_id}
#     ).to_list(length=1000)
    
#     if not docs:
#         raise HTTPException(status_code=404, detail="Knowledge base not found")
    
#     # Calculate stats from supporting_documents
#     total_chunks = sum(doc.get("chunk_count", 0) for doc in docs)
#     total_size = sum(doc.get("file_size", 0) for doc in docs)
    
#     # CORRECT: Get processing status from supporting_documents
#     status_breakdown = {}
#     for doc in docs:
#         status = doc.get("processing_status", "unknown")  # This should now read "completed"
#         status_breakdown[status] = status_breakdown.get(status, 0) + 1
    
#     # Get knowledge base info
#     kb = await db.knowledge_bases.find_one({"_id": knowledge_base_id})
    
#     return {
#         "knowledge_base_id": knowledge_base_id,
#         "total_documents": len(docs),
#         "total_chunks": total_chunks,
#         "total_size_bytes": total_size,
#         "processing_status": status_breakdown,  # Should now show {"completed": 8}
#         "fact_checking_enabled": True,
#         "created_at": kb.get("created_at") if kb else None,
#         "last_updated": kb.get("last_updated") if kb else None
#     }
@router.get("/{knowledge_base_id}/stats")
async def get_knowledge_base_stats(
    knowledge_base_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Get knowledge base statistics - FIXED VERSION"""
    
    # GET DATA FROM supporting_documents (not knowledge_bases)
    docs = await db.supporting_documents.find(
        {"knowledge_base_id": knowledge_base_id}
    ).to_list(length=1000)
    
    if not docs:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    # Calculate stats from supporting_documents
    total_chunks = sum(doc.get("chunk_count", 0) for doc in docs)
    total_size = sum(doc.get("file_size", 0) for doc in docs)
    
    # CORRECT: Get processing status from supporting_documents
    status_breakdown = {}
    indexed_count = 0
    
    for doc in docs:
        print(doc)
        status = doc.get("processing_status", "unknown")  # This should now read "completed"
        status_breakdown[status] = status_breakdown.get(status, 0) + 1
        
        # ✅ ADDED: Count successfully indexed documents
        if status == "completed" or doc.get("indexed_in_vector_search", False):
            indexed_count += 1
    
    # ✅ ADDED: Determine if search is ready
    # Search is ready if we have:
    # 1. At least one document indexed successfully
    # 2. Total chunks > 0 (means documents were processed)
    search_ready = indexed_count > 0 and total_chunks > 0
    
    # Get knowledge base info
    kb = await db.knowledge_bases.find_one({"_id": knowledge_base_id})
    
    return {
        "knowledge_base_id": knowledge_base_id,
        "total_documents": len(docs),
        "total_chunks": total_chunks,
        "indexed_documents": indexed_count,        # ✅ ADDED: Frontend expects this
        "search_ready": search_ready,              # ✅ ADDED: Frontend expects this
        
        # Keep existing fields for backward compatibility
        "total_size_bytes": total_size,
        "processing_status": status_breakdown,     # Should now show {"completed": 8}
        "fact_checking_enabled": True,
        "created_at": kb.get("created_at") if kb else None,
        "last_updated": kb.get("last_updated") if kb else None
    }
# Helper functions (same as original proposal)
async def process_and_index_documents(supporting_docs: List[UploadFile], knowledge_base_id: str, db: Any) -> List[dict]:
    """Process documents and index in Azure Search"""
    
    documents_metadata = []
    
    from openai import AsyncAzureOpenAI
    import os
    
    openai_client = AsyncAzureOpenAI(
        api_key=os.getenv("api_key"),
        azure_endpoint=os.getenv("endpoint"),
        api_version=os.getenv("api_version")
    )
    
    document_processor = DocumentProcessor(openai_client, db)
    vector_search = AzureVectorSearchManager()
    
    for doc_file in supporting_docs:
        try:
            content = await doc_file.read()
            doc_id = str(uuid4())
            
            # Process document (extract text, create chunks, embeddings)
            chunks = await document_processor.process_document(doc_id, content, doc_file.filename)
            
            # Set knowledge base for chunks
            for chunk in chunks:
                chunk.knowledge_base_id = knowledge_base_id
                print(f"✅ Chunk {chunk.id[:8]}... assigned to KB {knowledge_base_id[:8]}...")
            # Index in Azure Search
            # await vector_search.index_document_chunks(chunks, knowledge_base_id)
            success = await vector_search.index_document_chunks(chunks, knowledge_base_id)
            if not success:
                print(f"❌ Failed to index chunks for {doc_file.filename}")
                continue            
            # Create metadata
            doc_metadata = {
                "_id": doc_id,
                "knowledge_base_id": knowledge_base_id,
                "filename": doc_file.filename,
                "original_filename": doc_file.filename,
                "file_size": len(content),
                "content_type": doc_file.content_type,
                "processing_status": "completed",
                "chunk_count": len(chunks),
                "processed_at": datetime.now().isoformat(),
                "indexed_in_vector_search": True
            }
            
            # Store in DB
            await db.supporting_documents.insert_one(doc_metadata)
            documents_metadata.append(doc_metadata)
            
        except Exception as e:
            print(f"Error processing {doc_file.filename}: {e}")
            # Store failed document
            failed_metadata = {
                "_id": doc_id,
                "filename": doc_file.filename,
                "processing_status": "failed",
                "error_message": str(e),
                "processed_at": datetime.now().isoformat()
            }
            await db.supporting_documents.insert_one(failed_metadata)
            documents_metadata.append(failed_metadata)
    
    return documents_metadata

async def remove_documents_and_vectors(document_ids: List[str], knowledge_base_id: str, db: Any):
    """Remove documents and their vector data from Azure Search"""
    
    try:
        vector_search = AzureVectorSearchManager()
        
        for doc_id in document_ids:
            # Get document chunks to remove from vector search
            doc_metadata = await db.supporting_documents.find_one({"_id": doc_id})
            
            if doc_metadata and doc_metadata.get("indexed_in_vector_search"):
                # Remove chunks from Azure Search
                await remove_document_chunks_from_search(doc_id, knowledge_base_id, vector_search)
            
            # Remove document metadata from DB
            await db.supporting_documents.delete_one({"_id": doc_id})
            
        print(f"✅ Removed {len(document_ids)} documents and their vector data")
        
    except Exception as e:
        print(f"❌ Error removing documents: {e}")
        raise

async def remove_document_chunks_from_search(doc_id: str, knowledge_base_id: str, vector_search):
    """Remove document chunks from Azure Search index"""
    try:
        search_client = vector_search.get_search_client(knowledge_base_id)
        
        # Find all chunks for this document
        results = await search_client.search(
            search_text="*",
            filter=f"document_id eq '{doc_id}'",
            select=["id"]
        )
        
        # Delete chunks
        chunk_ids = []
        async for result in results:
            chunk_ids.append({"id": result["id"]})
        
        if chunk_ids:
            await search_client.delete_documents(chunk_ids)
            print(f"✅ Removed {len(chunk_ids)} chunks for document {doc_id}")
            
    except Exception as e:
        print(f"❌ Error removing chunks from search: {e}")
@router.post("/debug/fix-document-status/{knowledge_base_id}")
async def fix_document_status(
    knowledge_base_id: str,
    db: Any = Depends(get_db)
):
    """Fix processing status for existing documents"""
    
    # Update all documents in this knowledge base to "completed"
    result = await db.supporting_documents.update_many(
        {"knowledge_base_id": knowledge_base_id},
        {"$set": {"processing_status": "completed"}}
    )
    
    return {
        "updated_documents": result.modified_count,
        "message": "Fixed processing status"
    }

# FILE: core/knowledge_base_manager.py
# ADD these new endpoints at the end of the file:

@router.get("/{knowledge_base_id}/documents")
async def list_knowledge_base_documents(
    knowledge_base_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """List all documents in a knowledge base with preview"""
    
    try:
        # Get all documents for this knowledge base
        docs = await db.supporting_documents.find(
            {"knowledge_base_id": knowledge_base_id}
        ).to_list(length=1000)
        
        # Add content preview for each document
        for doc in docs:
            # Get first few chunks for preview
            chunks = await db.document_chunks.find(
                {"document_id": doc["_id"]},
                {"content": 1, "chunk_index": 1}
            ).sort("chunk_index", 1).limit(3).to_list(length=3)
            
            doc["content_preview"] = " ".join([chunk["content"][:200] for chunk in chunks])
            doc["total_chunks"] = await db.document_chunks.count_documents({"document_id": doc["_id"]})
        
        return {
            "knowledge_base_id": knowledge_base_id,
            "documents": docs,
            "total_documents": len(docs)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{knowledge_base_id}/documents/{document_id}/content")
async def get_document_content(
    knowledge_base_id: str,
    document_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Get full content of a specific document for editing"""
    
    try:
        # Verify document belongs to this knowledge base
        doc = await db.supporting_documents.find_one({
            "_id": document_id,
            "knowledge_base_id": knowledge_base_id
        })
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get all chunks for this document
        chunks = await db.document_chunks.find(
            {"document_id": document_id}
        ).sort("chunk_index", 1).to_list(length=1000)
        
        # Reconstruct full content
        full_content = "\n\n".join([chunk["content"] for chunk in chunks])
        
        return {
            "document_id": document_id,
            "filename": doc["filename"],
            "full_content": full_content,
            "chunk_count": len(chunks),
            "metadata": {
                "file_size": doc.get("file_size", 0),
                "processed_at": doc.get("processed_at"),
                "processing_status": doc.get("processing_status")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{knowledge_base_id}/documents/{document_id}/content")
async def update_document_content(
    knowledge_base_id: str,
    document_id: str,
    new_content: str = Body(..., embed=True),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Update document content and re-process vectors"""
    
    try:
        # Verify document exists and belongs to this knowledge base
        doc = await db.supporting_documents.find_one({
            "_id": document_id,
            "knowledge_base_id": knowledge_base_id
        })
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Remove old chunks from vector search
        await remove_document_chunks_from_search(document_id, knowledge_base_id, AzureVectorSearchManager())
        
        # Remove old chunks from database
        await db.document_chunks.delete_many({"document_id": document_id})
        
        # Re-process the updated content
        from core.document_processor import DocumentProcessor
        from openai import AsyncAzureOpenAI
        import os
        
        openai_client = AsyncAzureOpenAI(
            api_key=os.getenv("api_key"),
            azure_endpoint=os.getenv("endpoint"),
            api_version=os.getenv("api_version")
        )
        
        processor = DocumentProcessor(openai_client, db)
        
        # Create new chunks from updated content
        chunks = await processor._create_chunks(
            new_content, 
            document_id, 
            doc["filename"]
        )
        
        # Set knowledge base for chunks
        for chunk in chunks:
            chunk.knowledge_base_id = knowledge_base_id
        
        # Generate embeddings
        chunks_with_embeddings = await processor._generate_embeddings(chunks)
        
        # Store new chunks in database
        chunk_docs = [chunk.dict() for chunk in chunks_with_embeddings]
        if chunk_docs:
            await db.document_chunks.insert_many(chunk_docs)
        
        # Index in Azure Search
        vector_search = AzureVectorSearchManager()
        await vector_search.index_document_chunks(chunks_with_embeddings, knowledge_base_id)
        
        # Update document metadata
        await db.supporting_documents.update_one(
            {"_id": document_id},
            {"$set": {
                "chunk_count": len(chunks_with_embeddings),
                "processing_status": "completed",
                "updated_at": datetime.now().isoformat(),
                "updated_by": str(current_user.id)
            }}
        )
        
        return {
            "message": "Document content updated successfully",
            "document_id": document_id,
            "new_chunk_count": len(chunks_with_embeddings),
            "updated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating document: {str(e)}")

@router.post("/{knowledge_base_id}/documents/{document_id}/duplicate")
async def duplicate_document(
    knowledge_base_id: str,
    document_id: str,
    new_filename: str = Body(..., embed=True),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Duplicate a document within the same knowledge base"""
    
    try:
        # Get original document
        original_doc = await db.supporting_documents.find_one({
            "_id": document_id,
            "knowledge_base_id": knowledge_base_id
        })
        
        if not original_doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get all chunks from original document
        original_chunks = await db.document_chunks.find(
            {"document_id": document_id}
        ).to_list(length=1000)
        
        # Create new document ID
        new_doc_id = str(uuid4())
        
        # Create new document record
        new_doc = original_doc.copy()
        new_doc["_id"] = new_doc_id
        new_doc["filename"] = new_filename
        new_doc["original_filename"] = new_filename
        new_doc["processed_at"] = datetime.now().isoformat()
        new_doc["duplicated_from"] = document_id
        new_doc["created_by"] = str(current_user.id)
        
        await db.supporting_documents.insert_one(new_doc)
        
        # Duplicate chunks
        new_chunks = []
        for chunk in original_chunks:
            new_chunk = chunk.copy()
            new_chunk["_id"] = str(uuid4())
            new_chunk["document_id"] = new_doc_id
            new_chunks.append(new_chunk)
        
        if new_chunks:
            await db.document_chunks.insert_many(new_chunks)
        
        # Index in Azure Search
        from core.document_processor import DocumentChunk
        chunk_objects = [DocumentChunk(**chunk) for chunk in new_chunks]
        
        vector_search = AzureVectorSearchManager()
        await vector_search.index_document_chunks(chunk_objects, knowledge_base_id)
        
        return {
            "message": "Document duplicated successfully",
            "original_document_id": document_id,
            "new_document_id": new_doc_id,
            "new_filename": new_filename,
            "chunk_count": len(new_chunks)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/knowledge-base/{knowledge_base_id}/documents/batch-update")
async def batch_update_knowledge_base_documents(
    knowledge_base_id: str,
    batch_actions: Dict[str, Any] = Body(...),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Perform multiple document operations in one request"""
    try:
        kb = await db.knowledge_bases.find_one({"_id": knowledge_base_id})
        if not kb:
            raise HTTPException(status_code=404, detail="Knowledge base not found")
        
        results = []
        
        # Remove documents if specified
        if "remove_document_ids" in batch_actions and batch_actions["remove_document_ids"]:
            remove_ids = batch_actions["remove_document_ids"]
            await remove_documents_and_vectors(remove_ids, knowledge_base_id, db)
            results.append(f"Removed {len(remove_ids)} documents")
        
        # Add new documents if specified
        if "add_documents" in batch_actions and batch_actions["add_documents"]:
            # This would need to handle file uploads differently
            # For now, return instruction to use separate add endpoint
            results.append("Use PUT /knowledge-base/{id}/documents with action=add for new files")
        
        # Update knowledge base stats
        remaining_docs = await db.supporting_documents.find(
            {"knowledge_base_id": knowledge_base_id}
        ).to_list(length=1000)
        
        await db.knowledge_bases.update_one(
            {"_id": knowledge_base_id},
            {"$set": {
                "supporting_documents": remaining_docs,
                "total_documents": len(remaining_docs),
                "last_updated": datetime.now(),
                "fact_checking_enabled": len(remaining_docs) > 0
            }}
        )
        
        return {
            "message": "Batch update completed",
            "knowledge_base_id": knowledge_base_id,
            "operations": results,
            "remaining_documents": len(remaining_docs)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))