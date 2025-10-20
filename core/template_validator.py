from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class ValidationIssue(BaseModel):
    field: str
    severity: str  # "error", "warning", "info"
    message: str
    suggestion: Optional[str] = None

class ValidationResult(BaseModel):
    valid: bool
    score: float = Field(ge=0, le=100)
    issues: List[ValidationIssue] = []
    completeness: Dict[str, bool] = {}
    quality_metrics: Dict[str, float] = {}

class TemplateValidator:
    """Validates template data quality for scenario generation"""
    
    @staticmethod
    def validate_template(template_data: Dict[str, Any]) -> ValidationResult:
        issues = []
        completeness = {}
        quality_metrics = {}
        
        # 1. Context Overview Validation
        context = template_data.get("context_overview", {})
        completeness["context"] = bool(
            context.get("scenario_title") and 
            context.get("scenario_description")
        )
        
        if not context.get("scenario_title"):
            issues.append(ValidationIssue(
                field="context_overview.scenario_title",
                severity="error",
                message="Scenario title is required",
                suggestion="Provide a clear, descriptive title for the scenario"
            ))
        elif len(context.get("scenario_title", "")) < 5:
            issues.append(ValidationIssue(
                field="context_overview.scenario_title",
                severity="warning",
                message="Scenario title is too short",
                suggestion="Use a more descriptive title (at least 5 characters)"
            ))
        
        if not context.get("scenario_description"):
            issues.append(ValidationIssue(
                field="context_overview.scenario_description",
                severity="error",
                message="Scenario description is required",
                suggestion="Provide a detailed description of the training scenario"
            ))
        elif len(context.get("scenario_description", "")) < 20:
            issues.append(ValidationIssue(
                field="context_overview.scenario_description",
                severity="warning",
                message="Scenario description is too brief",
                suggestion="Provide more context (at least 20 characters)"
            ))
        
        quality_metrics["context_quality"] = TemplateValidator._calculate_context_quality(context)
        
        # 2. Knowledge Base Validation
        kb = template_data.get("knowledge_base", {})
        topics = kb.get("conversation_topics", [])
        facts = kb.get("key_facts", [])
        
        completeness["knowledge_base"] = len(topics) > 0 or len(facts) > 0
        
        if len(topics) == 0:
            issues.append(ValidationIssue(
                field="knowledge_base.conversation_topics",
                severity="warning",
                message="No conversation topics defined",
                suggestion="Add topics to guide the conversation flow"
            ))
        elif len(topics) < 3:
            issues.append(ValidationIssue(
                field="knowledge_base.conversation_topics",
                severity="info",
                message="Limited conversation topics",
                suggestion="Consider adding more topics for richer interactions (recommended: 3-7)"
            ))
        
        if len(facts) == 0:
            issues.append(ValidationIssue(
                field="knowledge_base.key_facts",
                severity="info",
                message="No key facts defined",
                suggestion="Add important facts to enhance scenario realism"
            ))
        
        quality_metrics["knowledge_base_quality"] = TemplateValidator._calculate_kb_quality(kb)
        
        # 3. Learning Objectives Validation
        objectives = template_data.get("learning_objectives", {})
        primary = objectives.get("primary_objectives", [])
        
        completeness["learning_objectives"] = len(primary) > 0
        
        if len(primary) == 0:
            issues.append(ValidationIssue(
                field="learning_objectives.primary_objectives",
                severity="warning",
                message="No learning objectives defined",
                suggestion="Define clear learning goals for trainees"
            ))
        elif len(primary) < 2:
            issues.append(ValidationIssue(
                field="learning_objectives.primary_objectives",
                severity="info",
                message="Limited learning objectives",
                suggestion="Consider adding more objectives (recommended: 2-5)"
            ))
        
        quality_metrics["objectives_quality"] = TemplateValidator._calculate_objectives_quality(objectives)
        
        # 4. Archetype Classification Validation
        archetype = template_data.get("archetype_classification")
        completeness["archetype"] = archetype is not None
        
        if not archetype:
            issues.append(ValidationIssue(
                field="archetype_classification",
                severity="info",
                message="No archetype classification",
                suggestion="Archetype will be auto-classified during generation"
            ))
        elif archetype.get("confidence_score", 0) < 0.7:
            issues.append(ValidationIssue(
                field="archetype_classification.confidence_score",
                severity="info",
                message=f"Low archetype confidence ({archetype.get('confidence_score', 0):.1%})",
                suggestion="Review scenario description for clarity"
            ))
        
        quality_metrics["archetype_confidence"] = archetype.get("confidence_score", 0) if archetype else 0
        
        # 5. Evaluation Metrics Validation
        eval_metrics = template_data.get("evaluation_metrics", {})
        completeness["evaluation_metrics"] = bool(eval_metrics.get("evaluation_criteria"))
        
        if not eval_metrics.get("evaluation_criteria"):
            issues.append(ValidationIssue(
                field="evaluation_metrics.evaluation_criteria",
                severity="info",
                message="No evaluation criteria defined",
                suggestion="Define how trainee performance will be assessed"
            ))
        
        quality_metrics["evaluation_quality"] = TemplateValidator._calculate_eval_quality(eval_metrics)
        
        # Calculate overall score
        score = TemplateValidator._calculate_overall_score(issues, quality_metrics, completeness)
        
        # Determine if valid (no errors)
        valid = not any(issue.severity == "error" for issue in issues)
        
        return ValidationResult(
            valid=valid,
            score=score,
            issues=issues,
            completeness=completeness,
            quality_metrics=quality_metrics
        )
    
    @staticmethod
    def _calculate_context_quality(context: Dict) -> float:
        score = 0.0
        if context.get("scenario_title"):
            score += 0.3
            if len(context["scenario_title"]) >= 10:
                score += 0.2
        if context.get("scenario_description"):
            score += 0.3
            if len(context["scenario_description"]) >= 50:
                score += 0.2
        return min(score, 1.0)
    
    @staticmethod
    def _calculate_kb_quality(kb: Dict) -> float:
        topics = len(kb.get("conversation_topics", []))
        facts = len(kb.get("key_facts", []))
        score = min(topics / 5, 0.5) + min(facts / 5, 0.5)
        return min(score, 1.0)
    
    @staticmethod
    def _calculate_objectives_quality(objectives: Dict) -> float:
        primary = len(objectives.get("primary_objectives", []))
        secondary = len(objectives.get("secondary_objectives", []))
        score = min(primary / 3, 0.7) + min(secondary / 2, 0.3)
        return min(score, 1.0)
    
    @staticmethod
    def _calculate_eval_quality(eval_metrics: Dict) -> float:
        score = 0.0
        if eval_metrics.get("evaluation_criteria"):
            score += 0.5
        if eval_metrics.get("scoring_rubric"):
            score += 0.5
        return score
    
    @staticmethod
    def _calculate_overall_score(issues: List[ValidationIssue], quality_metrics: Dict, completeness: Dict) -> float:
        # Start with 100
        score = 100.0
        
        # Deduct for issues
        for issue in issues:
            if issue.severity == "error":
                score -= 20
            elif issue.severity == "warning":
                score -= 10
            elif issue.severity == "info":
                score -= 5
        
        # Bonus for quality metrics
        avg_quality = sum(quality_metrics.values()) / len(quality_metrics) if quality_metrics else 0
        score += (avg_quality * 10)
        
        # Bonus for completeness
        completeness_ratio = sum(completeness.values()) / len(completeness) if completeness else 0
        score += (completeness_ratio * 10)
        
        return max(0, min(100, score))


class PromptsValidator:
    """Validates generated prompts quality"""
    
    @staticmethod
    def validate_prompts(prompts_data: Dict[str, Any]) -> ValidationResult:
        issues = []
        completeness = {}
        quality_metrics = {}
        
        # Check mode prompts
        for mode in ["learn_mode_prompt", "try_mode_prompt", "assess_mode_prompt"]:
            prompt = prompts_data.get(mode, "")
            completeness[mode] = bool(prompt)
            
            if not prompt:
                issues.append(ValidationIssue(
                    field=mode,
                    severity="error",
                    message=f"{mode.replace('_', ' ').title()} is missing",
                    suggestion="Regenerate prompts from template"
                ))
            elif len(prompt) < 50:
                issues.append(ValidationIssue(
                    field=mode,
                    severity="warning",
                    message=f"{mode.replace('_', ' ').title()} is too short",
                    suggestion="Prompt should be more detailed"
                ))
            
            quality_metrics[f"{mode}_quality"] = min(len(prompt) / 200, 1.0)
        
        # Check personas
        personas = prompts_data.get("personas", [])
        completeness["personas"] = len(personas) > 0
        
        if len(personas) == 0:
            issues.append(ValidationIssue(
                field="personas",
                severity="error",
                message="No personas generated",
                suggestion="Regenerate prompts from template"
            ))
        elif len(personas) < 3:
            issues.append(ValidationIssue(
                field="personas",
                severity="warning",
                message=f"Only {len(personas)} persona(s) generated",
                suggestion="Recommended: 3 personas for variety"
            ))
        
        # Validate persona structure
        for i, persona in enumerate(personas):
            if not persona.get("name"):
                issues.append(ValidationIssue(
                    field=f"personas[{i}].name",
                    severity="error",
                    message=f"Persona {i+1} missing name",
                    suggestion="Regenerate prompts"
                ))
            if not persona.get("role"):
                issues.append(ValidationIssue(
                    field=f"personas[{i}].role",
                    severity="warning",
                    message=f"Persona {i+1} missing role",
                    suggestion="Define persona role"
                ))
        
        quality_metrics["personas_quality"] = min(len(personas) / 3, 1.0)
        
        # Calculate score
        score = PromptsValidator._calculate_prompts_score(issues, quality_metrics, completeness)
        valid = not any(issue.severity == "error" for issue in issues)
        
        return ValidationResult(
            valid=valid,
            score=score,
            issues=issues,
            completeness=completeness,
            quality_metrics=quality_metrics
        )
    
    @staticmethod
    def _calculate_prompts_score(issues: List[ValidationIssue], quality_metrics: Dict, completeness: Dict) -> float:
        score = 100.0
        
        for issue in issues:
            if issue.severity == "error":
                score -= 25
            elif issue.severity == "warning":
                score -= 10
            elif issue.severity == "info":
                score -= 5
        
        avg_quality = sum(quality_metrics.values()) / len(quality_metrics) if quality_metrics else 0
        score += (avg_quality * 10)
        
        return max(0, min(100, score))
