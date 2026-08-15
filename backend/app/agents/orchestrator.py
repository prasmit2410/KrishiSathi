"""
CrewAI Agent tasks and orchestrator definitions
"""

from crewai import Agent, Task, Crew, Process
from app.core.config import Settings
from app.agents.tools.regional_context_tool import get_regional_context_tool
from app.agents.tools.ml_prediction_tool import predict_crop_suitability_tool
from app.agents.tools.rule_validation_tool import validate_recommendations_tool


class CropRecommendationOrchestrator:
    """Orchestrator for crop recommendation using CrewAI"""
    
    def __init__(self, config: Settings):
        self.config = config
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create the orchestrator agent"""
        return Agent(
            role="Agricultural Recommendation Coordinator",
            goal="Produce accurate, explained crop recommendations for a farmer's farm profile",
            backstory="""You are an expert agricultural advisor that uses data tools to make crop recommendations. 
            Your role is to:
            1. Understand the farmer's profile (location, soil type, land area, season, irrigation)
            2. Gather regional crop patterns and context
            3. Use ML model to score crop suitability
            4. Apply business rules to validate and filter recommendations
            5. Generate clear, farmer-friendly explanations for each recommended crop
            
            Important guidelines:
            - Use ONLY data from tool outputs for suitability scores
            - Do NOT invent crop scores or regional facts
            - Provide plain-language explanations suitable for farmers
            - Always note that recommendations are estimates
            - Consider both ML scores and regional constraints""",
            llm_model=self.config.openrouter_model,
            tools=[
                get_regional_context_tool(),
                predict_crop_suitability_tool(),
                validate_recommendations_tool()
            ],
            verbose=self.config.crewai_verbose,
            max_iterations=self.config.crewai_max_iterations,
            allow_delegation=False,
        )
    
    def create_recommendation_task(self, farmer_profile: dict) -> Task:
        """Create recommendation task for the given farmer profile"""
        
        task_description = f"""
        Generate crop recommendations for the following farmer profile:
        
        Profile Details:
        - State: {farmer_profile.get('state')}
        - District: {farmer_profile.get('district')}
        - Village: {farmer_profile.get('village', 'Not specified')}
        - Land Area: {farmer_profile.get('land_area')} {farmer_profile.get('land_unit')}
        - Soil Type: {farmer_profile.get('soil_type')}
        - Season: {farmer_profile.get('season', 'Not specified')}
        - Irrigation Available: {farmer_profile.get('irrigation_available', 'Not specified')}
        
        Recommended Steps:
        1. Call get_regional_context to understand regional crop patterns for this state/district
        2. Call predict_crop_suitability with all farmer inputs to get ML scores
        3. Call validate_recommendations to filter invalid combinations and adjust scores
        4. Synthesize results into ranked recommendations with explanations
        
        Output Format (JSON):
        {{
            "recommendations": [
                {{
                    "rank": 1,
                    "crop_name": "Crop Name",
                    "suitability": "High/Moderate/Low",
                    "suitability_score": 0.87,
                    "estimated_risk": "Low/Medium/High",
                    "estimated_return_potential": "Low/Medium/High",
                    "explanation": "Detailed explanation for this crop"
                }},
                ...
            ],
            "summary": "Brief summary paragraph",
            "metadata": {{
                "method": "ml" or "rule_fallback",
                "confidence": "high" or "low"
            }}
        }}
        
        Rules:
        - Return 3-5 ranked crops
        - Use ONLY data from tool outputs for scores
        - Do NOT invent crops or scores
        - Provide plain-language explanations
        - Always include summary
        """
        
        return Task(
            description=task_description,
            agent=self.agent,
            expected_output="JSON object with ranked crop recommendations and explanations",
            output_file=None,  # Return as string, not file
        )
    
    def run_recommendation(self, farmer_profile: dict) -> dict:
        """
        Run the recommendation workflow for a farmer profile.
        
        Args:
            farmer_profile: Dictionary with farmer inputs
            
        Returns:
            Dictionary with recommendations and metadata
        """
        task = self.create_recommendation_task(farmer_profile)
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            process=Process.sequential,
            verbose=self.config.crewai_verbose,
            max_rpm=None,  # No rate limit for single agent
        )
        
        # Execute the crew
        result = crew.kickoff()
        
        return {
            "raw_output": str(result),
            "task": task,
            "agent_name": self.agent.role,
        }
