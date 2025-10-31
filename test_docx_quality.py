import asyncio
import sys
import os

async def test_docx_extraction():
    try:
        # Import the extraction function
        from scenario_generator import extract_text_from_docx
        
        # Read the DOCX file
        docx_path = "Leadership Fundamentals and Styles.docx"
        if not os.path.exists(docx_path):
            print(f"❌ File not found: {docx_path}")
            return
            
        with open(docx_path, 'rb') as f:
            content = f.read()
        
        print(f"📄 Testing DOCX extraction on {docx_path}")
        print(f"📊 File size: {len(content)} bytes")
        
        # Extract text
        extracted_text = await extract_text_from_docx(content)
        
        if not extracted_text:
            print("❌ EXTRACTION FAILED - No text extracted")
            return
            
        print(f"✅ EXTRACTION SUCCESS")
        print(f"📊 Total characters extracted: {len(extracted_text)}")
        
        # Analyze structure
        table_markers = []
        for i in range(10):
            if f"TABLE_{i}_START:" in extracted_text:
                table_markers.append(f"TABLE_{i}")
        
        print(f"🎯 TABLE STRUCTURES FOUND ({len(table_markers)}/10):")
        for marker in table_markers:
            print(f"  ✅ {marker}")
        
        # Check for key content
        key_content = {
            "Company/Course info": "Course" in extracted_text and "Module" in extracted_text,
            "Leadership content": "leadership" in extracted_text.lower(),
            "AI Trainer Role": "AI Trainer Role" in extracted_text,
            "Success Metrics": "Success Metrics" in extracted_text,
            "Common Mistakes": "Common Mistake" in extracted_text
        }
        
        print(f"📋 KEY CONTENT CHECK:")
        for content_type, found in key_content.items():
            status = "✅" if found else "❌"
            print(f"  {status} {content_type}")
        
        # Show sample extraction
        print(f"\n📝 SAMPLE EXTRACTED CONTENT (first 1000 chars):")
        print("-" * 50)
        print(extracted_text[:1000])
        print("-" * 50)
        
        # Quality assessment
        quality_score = len(table_markers) * 10 + sum(key_content.values()) * 5
        print(f"\n🎯 EXTRACTION QUALITY SCORE: {quality_score}/125")
        
        if quality_score >= 100:
            print("🎉 EXCELLENT QUALITY - Ready for production!")
        elif quality_score >= 75:
            print("✅ GOOD QUALITY - Minor improvements needed")
        elif quality_score >= 50:
            print("⚠️ MODERATE QUALITY - Some issues to fix")
        else:
            print("❌ POOR QUALITY - Major fixes needed")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_docx_extraction())