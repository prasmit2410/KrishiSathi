"""
Initial PostgreSQL database schema migration
"""

# This migration creates all core tables for Krishi Sathi Phase 1

CREATE TABLE IF NOT EXISTS farmer_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    state VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    village VARCHAR(100),
    land_area DECIMAL NOT NULL,
    land_unit VARCHAR(20) NOT NULL,
    soil_type VARCHAR(50) NOT NULL,
    season VARCHAR(20),
    irrigation_available BOOLEAN,
    previous_crop VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recommendation_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    farmer_profile_id UUID NOT NULL REFERENCES farmer_profiles(id),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recommendation_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID NOT NULL UNIQUE REFERENCES recommendation_requests(id),
    summary TEXT NOT NULL,
    disclaimer TEXT NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    processing_time_ms INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS crop_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    result_id UUID NOT NULL REFERENCES recommendation_results(id),
    rank INTEGER NOT NULL,
    crop_name VARCHAR(100) NOT NULL,
    suitability VARCHAR(20) NOT NULL,
    suitability_score DECIMAL(4, 3) NOT NULL,
    estimated_risk VARCHAR(20),
    estimated_return_potential VARCHAR(20),
    explanation TEXT NOT NULL,
    method VARCHAR(30) NOT NULL DEFAULT 'ml'
);

CREATE TABLE IF NOT EXISTS agent_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID NOT NULL UNIQUE REFERENCES recommendation_requests(id),
    agent_name VARCHAR(100) NOT NULL,
    llm_model VARCHAR(100) NOT NULL,
    tools_called JSONB NOT NULL,
    token_usage JSONB,
    status VARCHAR(20) NOT NULL,
    error_message TEXT,
    processing_time_ms INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tool_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_execution_id UUID NOT NULL REFERENCES agent_executions(id),
    tool_name VARCHAR(100) NOT NULL,
    input_data JSONB NOT NULL,
    output_data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL,
    error_message TEXT,
    processing_time_ms INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS regional_context (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    state VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    climate_zone VARCHAR(50) NOT NULL,
    dominant_crops JSONB NOT NULL,
    avg_rainfall_mm INTEGER,
    major_soil_types JSONB,
    kharif_crops JSONB,
    rabi_crops JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(state, district)
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_recommendation_requests_farmer_profile_id ON recommendation_requests(farmer_profile_id);
CREATE INDEX IF NOT EXISTS idx_recommendation_requests_status ON recommendation_requests(status);
CREATE INDEX IF NOT EXISTS idx_recommendation_results_request_id ON recommendation_results(request_id);
CREATE INDEX IF NOT EXISTS idx_crop_recommendations_result_id ON crop_recommendations(result_id);
CREATE INDEX IF NOT EXISTS idx_agent_executions_request_id ON agent_executions(request_id);
CREATE INDEX IF NOT EXISTS idx_tool_executions_agent_execution_id ON tool_executions(agent_execution_id);
CREATE INDEX IF NOT EXISTS idx_regional_context_state_district ON regional_context(state, district);
