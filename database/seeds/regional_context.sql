"""
Seed data for regional_context table (Maharashtra initial data)
"""

-- Maharashtra - Pune
INSERT INTO regional_context 
(state, district, climate_zone, dominant_crops, avg_rainfall_mm, major_soil_types, kharif_crops, rabi_crops)
VALUES (
    'Maharashtra',
    'Pune',
    'Semi-arid',
    '["Soybean", "Cotton", "Jowar", "Sugarcane"]'::jsonb,
    700,
    '["Black", "Red"]'::jsonb,
    '["Soybean", "Cotton", "Jowar", "Rice", "Groundnut"]'::jsonb,
    '["Wheat", "Gram", "Sunflower", "Safflower"]'::jsonb
)
ON CONFLICT (state, district) DO UPDATE SET
    climate_zone = EXCLUDED.climate_zone,
    dominant_crops = EXCLUDED.dominant_crops,
    updated_at = CURRENT_TIMESTAMP;

-- Maharashtra - Nashik
INSERT INTO regional_context 
(state, district, climate_zone, dominant_crops, avg_rainfall_mm, major_soil_types, kharif_crops, rabi_crops)
VALUES (
    'Maharashtra',
    'Nashik',
    'Semi-arid',
    '["Sugarcane", "Cotton", "Jowar", "Soybean"]'::jsonb,
    600,
    '["Black", "Red"]'::jsonb,
    '["Cotton", "Jowar", "Soybean", "Rice"]'::jsonb,
    '["Wheat", "Gram", "Onion"]'::jsonb
)
ON CONFLICT (state, district) DO UPDATE SET
    climate_zone = EXCLUDED.climate_zone,
    dominant_crops = EXCLUDED.dominant_crops,
    updated_at = CURRENT_TIMESTAMP;

-- Maharashtra - Aurangabad
INSERT INTO regional_context 
(state, district, climate_zone, dominant_crops, avg_rainfall_mm, major_soil_types, kharif_crops, rabi_crops)
VALUES (
    'Maharashtra',
    'Aurangabad',
    'Semi-arid',
    '["Jowar", "Cotton", "Groundnut", "Soybean"]'::jsonb,
    650,
    '["Black", "Red", "Laterite"]'::jsonb,
    '["Jowar", "Cotton", "Groundnut", "Soybean"]'::jsonb,
    '["Gram", "Wheat", "Sunflower"]'::jsonb
)
ON CONFLICT (state, district) DO UPDATE SET
    climate_zone = EXCLUDED.climate_zone,
    dominant_crops = EXCLUDED.dominant_crops,
    updated_at = CURRENT_TIMESTAMP;

-- Maharashtra - Nagpur
INSERT INTO regional_context 
(state, district, climate_zone, dominant_crops, avg_rainfall_mm, major_soil_types, kharif_crops, rabi_crops)
VALUES (
    'Maharashtra',
    'Nagpur',
    'Sub-tropical',
    '["Cotton", "Soybean", "Groundnut", "Jowar"]'::jsonb,
    1000,
    '["Black", "Red"]'::jsonb,
    '["Cotton", "Soybean", "Groundnut", "Rice"]'::jsonb,
    '["Gram", "Wheat", "Linseed"]'::jsonb
)
ON CONFLICT (state, district) DO UPDATE SET
    climate_zone = EXCLUDED.climate_zone,
    dominant_crops = EXCLUDED.dominant_crops,
    updated_at = CURRENT_TIMESTAMP;

-- Maharashtra - Solapur
INSERT INTO regional_context 
(state, district, climate_zone, dominant_crops, avg_rainfall_mm, major_soil_types, kharif_crops, rabi_crops)
VALUES (
    'Maharashtra',
    'Solapur',
    'Semi-arid',
    '["Sugarcane", "Jowar", "Cotton", "Groundnut"]'::jsonb,
    500,
    '["Black", "Sandy"]'::jsonb,
    '["Jowar", "Cotton", "Groundnut"]'::jsonb,
    '["Wheat", "Gram", "Onion"]'::jsonb
)
ON CONFLICT (state, district) DO UPDATE SET
    climate_zone = EXCLUDED.climate_zone,
    dominant_crops = EXCLUDED.dominant_crops,
    updated_at = CURRENT_TIMESTAMP;

-- Maharashtra - Vidarbha Region (representative)
INSERT INTO regional_context 
(state, district, climate_zone, dominant_crops, avg_rainfall_mm, major_soil_types, kharif_crops, rabi_crops)
VALUES (
    'Maharashtra',
    'Wardha',
    'Sub-tropical',
    '["Cotton", "Soybean", "Groundnut", "Jowar"]'::jsonb,
    950,
    '["Black", "Red"]'::jsonb,
    '["Cotton", "Soybean", "Groundnut", "Rice"]'::jsonb,
    '["Gram", "Wheat"]'::jsonb
)
ON CONFLICT (state, district) DO UPDATE SET
    climate_zone = EXCLUDED.climate_zone,
    dominant_crops = EXCLUDED.dominant_crops,
    updated_at = CURRENT_TIMESTAMP;
