"""
Script 1: Complete Scenario Creation with Token Tracking
Creates scenario with 3 avatar interactions + documents + tracks all tokens
"""

import asyncio
import requests
import json
from datetime import datetime
from pathlib import Path
from database import get_db
from core.simple_token_logger import log_token_usage

class ScenarioCreationWithTracking:
    def __init__(self, base_url="http://localhost:9000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.total_tokens = 0
        self.token_breakdown = {
            "template_analysis": 0,
            "prompt_generation": 0, 
            "persona_generation": 0,
            "embeddings": 0
        }
        
    def track_tokens(self, step: str, tokens: int):
        """Track tokens for each step"""
        self.total_tokens += tokens
        if step in self.token_breakdown:
            self.token_breakdown[step] += tokens
        print(f"   📊 {step}: {tokens:,} tokens")
    
    async def create_complete_scenario(self, template_text: str, template_name: str, doc_paths: list):
        """Create complete scenario with 3 avatar interactions"""
        
        print(f"🚀 Creating scenario: {template_name}")
        print("=" * 60)
        
        try:
            # Step 1: Analyze template with documents
            template_id = await self._analyze_template_with_docs(template_text, template_name, doc_paths)
            
            # Step 2: Generate final prompts (3 modes)
            await self._generate_final_prompts(template_id)
            
            # Step 3: Generate personas
            personas = await self._generate_personas(template_id)
            
            # Step 4: Create personas in DB
            persona_ids = await self._create_personas_in_db(personas)
            
            # Step 5: Create 3 avatar interactions (learn, try, assess)
            avatar_interactions = await self._create_avatar_interactions(persona_ids)
            
            # Step 6: Create final scenario
            scenario_id = await self._create_scenario_in_module(template_id, avatar_interactions)
            
            # Print results
            self._print_creation_results(scenario_id)
            
            return {
                "scenario_id": scenario_id,
                "template_id": template_id,
                "avatar_interactions": avatar_interactions,
                "total_tokens": self.total_tokens,
                "token_breakdown": self.token_breakdown,
                "estimated_cost": (self.total_tokens / 1000) * 0.03
            }
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return {"error": str(e)}
    
    async def _analyze_template_with_docs(self, template_text: str, template_name: str, doc_paths: list):
        """Step 1: POST /analyze-template-with-optional-docs"""
        print("🔍 Step 1: Analyzing template with documents...")
        
        # Prepare files
        files = []
        for doc_path in doc_paths:
            if Path(doc_path).exists():
                files.append(('supporting_docs', open(doc_path, 'rb')))
        
        data = {
            'scenario_document': template_text,
            'template_name': template_name
        }
        
        try:
            response = requests.post(f"{self.base_url}/analyze-template-with-optional-docs", 
                                   data=data, files=files)
            
            if response.status_code == 200:
                result = response.json()
                template_id = result.get('template_id')
                
                # Estimate tokens (you'd get real tokens from your API response)
                estimated_tokens = len(template_text.split()) * 2 + sum(1000 for _ in doc_paths)
                self.track_tokens("template_analysis", estimated_tokens)
                
                print(f"   ✅ Template created: {template_id}")
                return template_id
            else:
                raise Exception(f"API error: {response.status_code}")
                
        finally:
            for _, file in files:
                file.close()
    
    async def _generate_final_prompts(self, template_id: str):
        """Step 2: POST /generate-final-prompts"""
        print("📝 Step 2: Generating prompts for 3 modes...")
        
        data = {'template_id': template_id}
        response = requests.post(f"{self.base_url}/generate-final-prompts", data=data)
        
        if response.status_code == 200:
            # Estimate tokens for 3 mode prompts
            estimated_tokens = 3500  # Typical for learn/try/assess modes
            self.track_tokens("prompt_generation", estimated_tokens)
            print("   ✅ Generated prompts for learn/try/assess modes")
        else:
            raise Exception(f"Prompt generation failed: {response.status_code}")
    
    async def _generate_personas(self, template_id: str):
        """Step 3: POST /generate-personas"""
        print("👥 Step 3: Generating personas...")
        
        data = {'template_id': template_id, 'num_personas': 3}
        response = requests.post(f"{self.base_url}/generate-personas", data=data)
        
        if response.status_code == 200:
            result = response.json()
            personas = result.get('personas', [])
            
            # Estimate tokens for persona generation
            estimated_tokens = len(personas) * 600  # ~600 tokens per persona
            self.track_tokens("persona_generation", estimated_tokens)
            
            print(f"   ✅ Generated {len(personas)} personas")
            return personas
        else:
            raise Exception(f"Persona generation failed: {response.status_code}")
    
    async def _create_personas_in_db(self, personas: list):
        """Step 4: Create personas in database"""
        print("💾 Step 4: Creating personas in database...")
        
        persona_ids = []
        for persona in personas:
            response = requests.post(f"{self.base_url}/personas/", json=persona)
            if response.status_code == 200:
                result = response.json()
                persona_ids.append(result.get('id'))
        
        print(f"   ✅ Created {len(persona_ids)} personas in DB")
        return persona_ids
    
    async def _create_avatar_interactions(self, persona_ids: list):
        """Step 5: Create 3 avatar interactions"""
        print("🎭 Step 5: Creating 3 avatar interactions...")
        
        modes = ["learn_mode", "try_mode", "assess_mode"]
        avatar_interactions = {}
        
        for i, mode in enumerate(modes):
            persona_id = persona_ids[i % len(persona_ids)]  # Cycle through personas
            
            interaction_data = {
                'mode': mode,
                'persona_id': persona_id,
                'name': f"Avatar Interaction - {mode.replace('_', ' ').title()}"
            }
            
            response = requests.post(f"{self.base_url}/avatar-interactions/", json=interaction_data)
            if response.status_code == 200:
                result = response.json()
                avatar_interactions[mode] = result.get('id')
        
        print(f"   ✅ Created {len(avatar_interactions)} avatar interactions")
        return avatar_interactions
    
    async def _create_scenario_in_module(self, template_id: str, avatar_interactions: dict):
        """Step 6: Create scenario in module"""
        print("🎯 Step 6: Creating final scenario...")
        
        # Use a default module ID or create one
        module_id = "default-module-id"  # You'd get this from your system
        
        scenario_data = {
            'template_id': template_id,
            'title': 'Generated Scenario with Token Tracking',
            'learn_mode': {'avatar_interaction': avatar_interactions.get('learn_mode')},
            'try_mode': {'avatar_interaction': avatar_interactions.get('try_mode')},
            'assess_mode': {'avatar_interaction': avatar_interactions.get('assess_mode')}
        }
        
        response = requests.post(f"{self.base_url}/modules/{module_id}/scenarios", json=scenario_data)
        if response.status_code == 200:
            result = response.json()
            scenario_id = result.get('id')
            print(f"   ✅ Scenario created: {scenario_id}")
            return scenario_id
        else:
            raise Exception(f"Scenario creation failed: {response.status_code}")
    
    def _print_creation_results(self, scenario_id: str):
        """Print final results"""
        print("\n🎉 SCENARIO CREATION COMPLETE!")
        print("=" * 60)
        print(f"📊 TOTAL TOKENS: {self.total_tokens:,}")
        print(f"💰 ESTIMATED COST: ${(self.total_tokens / 1000) * 0.03:.4f}")
        print(f"🎯 SCENARIO ID: {scenario_id}")
        
        print(f"\n📋 TOKEN BREAKDOWN:")
        for step, tokens in self.token_breakdown.items():
            percentage = (tokens / self.total_tokens * 100) if self.total_tokens > 0 else 0
            print(f"   • {step.replace('_', ' ').title()}: {tokens:,} tokens ({percentage:.1f}%)")

# Sample template and documents
SAMPLE_TEMPLATE = """
Healthcare Maternity Sales Training Scenario

Company: CloudNine Hospitals
Training Domain: Maternity Package Sales
Target Learners: Customer Care Executives (Experienced)

Learning Objectives:
1. Master SPIN selling techniques for maternity packages
2. Handle price objections effectively  
3. Build trust with expecting families
4. Recommend appropriate packages based on needs

Customer Context:
- First-time expecting parents
- Budget-conscious but quality-focused
- Comparing multiple hospitals
- Concerned about package inclusions and pricing

Key Challenges:
- Price sensitivity (packages range ₹85K-₹1.2L)
- Package complexity and options
- Competition comparison
- Trust building with medical decisions

Success Metrics:
- 95%+ pricing accuracy
- Effective objection handling
- Customer satisfaction scores
- Package recommendation appropriateness
"""

SAMPLE_DOCUMENTS = [
    "sample_pricing_guide.pdf",  # You'd provide real document paths
    "sample_package_details.pdf"
]

async def main():
    """Run the scenario creation with tracking"""
    
    creator = ScenarioCreationWithTracking()
    
    print("🎯 SCENARIO CREATION WITH TOKEN TRACKING")
    print("=" * 60)
    
    result = await creator.create_complete_scenario(
        template_text=SAMPLE_TEMPLATE,
        template_name="Healthcare Maternity Sales Training",
        doc_paths=SAMPLE_DOCUMENTS
    )
    
    # Save results to file
    with open(f"scenario_creation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    return result

if __name__ == "__main__":
    result = asyncio.run(main())