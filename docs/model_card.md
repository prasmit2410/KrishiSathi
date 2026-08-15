# Krishi Sathi Crop Recommendation ML Model Card

## Model Details

### Model Name
Crop Recommendation ML Model

### Model Version
crop_rec_v1.0

### Model Type
Multi-class Classification (Random Forest / XGBoost)

### Purpose
Predict suitability of different crops for a farmer's farm given location, soil, and farming conditions.

### Training Date
Phase 1 - Sprint 3

---

## Intended Use

### Primary Use Case
Provide agricultural crop recommendations to Indian farmers based on their farm characteristics and regional context.

### Intended Users
- Small and marginal farmers in Maharashtra
- Agricultural extension agents
- Krishi Vigyan Kendra (KVK) staff

### Out-of-Scope Uses
- Weather prediction
- Yield estimation
- Market price prediction
- Disease diagnosis
- Pest identification

---

## Factors

### Input Features

| Feature | Type | Description | Values / Range |
|---------|------|-------------|-----------------|
| soil_type | Categorical | Soil classification | Black, Red, Alluvial, Laterite, Sandy, Clay, Loamy |
| state | Categorical | Geographic state | Maharashtra (Phase 1) |
| district | Categorical | Geographic district | Pune, Nashik, Aurangabad, Nagpur, Solapur, Wardha |
| season | Categorical | Farming season | Kharif, Rabi, Zaid |
| climate_zone | Categorical | Climate classification | Tropical, Sub-tropical, Temperate, Semi-arid, Arid |
| irrigation_available | Boolean | Irrigation availability | 0 or 1 |
| land_area_normalized | Continuous | Normalized log(land area) | 0.0 to 6.5 |
| regional_crop_frequency | Continuous | Frequency of crop in region | 0.0 to 1.0 |

### Output Classes
Crop names (20-30 crops depending on training data):
- Soybean
- Cotton
- Jowar
- Groundnut
- Sugarcane
- Wheat
- Gram
- Rice
- Sunflower
- And others

---

## Performance

### Metrics (on validation set)

| Metric | Target | Achieved | Notes |
|--------|--------|----------|-------|
| Top-1 Accuracy | ≥ 70% | TBD | Single best recommendation |
| Top-3 Accuracy | ≥ 85% | TBD | Within top 3 recommendations |
| Top-5 Accuracy | ≥ 90% | TBD | Within top 5 recommendations |
| F1 Score (Macro) | ≥ 0.65 | TBD | Unweighted average across crops |
| Inference Latency | < 200ms | TBD | Time to generate predictions |
| Fallback Rate | < 10% | TBD | Frequency of low-confidence fallback |

### Test Set Performance

- Test set size: TBD (15% of total data)
- Cross-validation: 5-fold
- Class imbalance handling: TBD (class weights or sampling strategy)

### Confidence by Crop

**High confidence crops** (Top 10 by training data):
- [To be determined after training]

**Medium confidence crops** (11-20):
- [To be determined after training]

**Low confidence crops** (< 50 training samples):
- [To be determined after training]

---

## Limitations

### Known Limitations

1. **Geographic Scope**
   - Trained on Maharashtra data only
   - Generalizes poorly to other states (Phase 2 expansion needed)
   - Trained on pilot districts (Pune, Nashik, Aurangabad, Nagpur, Solapur, Wardha)

2. **Feature Limitations**
   - Does not consider weather patterns or rainfall prediction
   - No real-time disease or pest data
   - Soil characteristics limited to type (not pH, nutrients, texture details)
   - Ignores market price and profitability factors

3. **Data Limitations**
   - Historical data may not reflect current climate patterns
   - Imbalanced crop distribution in training data
   - No seasonal sub-regional variations

4. **Model Limitations**
   - Binary features only (irrigation: yes/no, no partial irrigation)
   - Fixed set of supported crops
   - No adaptive learning (model not updated in real-time)
   - Top-k recommendations may include similar crops

5. **Fallback Behavior**
   - Low-confidence predictions fall back to rule-based recommendations
   - Rule-based method may not rank crops optimally

---

## Bias and Fairness

### Known Biases

1. **Geographic Bias**
   - Overrepresentation of high-input crops (Sugarcane, Cotton)
   - Underrepresentation of small-holder crops

2. **Data Bias**
   - Historical data may reflect past farming practices, not current climate reality
   - High rainfall crops may be overrepresented in wet regions

### Mitigation Strategies

- Monitor model performance across soil types and seasons
- Quarterly fairness audits on hold-out test sets
- Collect feedback from farmers to identify systematic errors
- Phase 2: Expand training data to include more diverse regions

---

## Training Data

### Data Source

| Source | Description | Phase 1 Plan |
|--------|-------------|-------------|
| Kaggle Crop Recommendation Dataset | Public agricultural data | Primary source |
| ICAR (Indian Council of Agricultural Research) | Government agricultural statistics | Supplementary |
| State Agricultural Departments | Maharashtra agricultural records | Validation data |

### Training Set Composition

- **Total records**: TBD (target: ≥ 1000)
- **Time period**: TBD
- **Geographic coverage**: Maharashtra (6 pilot districts)
- **Crops represented**: 20-30 crops

### Data Preprocessing

1. **Missing value handling**: TBD (drop / impute / flag)
2. **Outlier removal**: TBD
3. **Class balancing**: TBD (class weights vs. resampling)
4. **Feature scaling**: Normalization and log transforms where appropriate
5. **Train/validation/test split**: 70% / 15% / 15%

---

## Evaluation

### Evaluation Strategy

- **Cross-validation**: 5-fold on training set
- **Hyperparameter tuning**: Grid search on validation set
- **Final evaluation**: Hold-out test set
- **Domain expert review**: 20 recommendations reviewed by agricultural advisor

### Success Criteria (Phase 1 Exit)

- [ ] Top-1 accuracy ≥ 70%
- [ ] Top-3 accuracy ≥ 85%
- [ ] Top-5 accuracy ≥ 90%
- [ ] ≥ 80% of reviewed recommendations rated "acceptable" by domain expert
- [ ] Inference latency < 200ms (95th percentile)

### Ongoing Monitoring

- Weekly: Track prediction distribution and edge cases
- Monthly: Recalculate metrics on accumulating real-world predictions
- Quarterly: Domain expert review of errors and false positives
- Semi-annual: Retrain model with new data

---

## Training and Inference

### Training Pipeline

```
Raw data → Cleaning → Feature engineering → Encoding → 
Train/val/test split → Model training → Hyperparameter tuning → 
Evaluation → Serialization → Deployment
```

### Inference Pipeline

```
Farmer input → Validation → Feature transformation → 
Prediction → Confidence filtering → Rule validation → 
Explanation generation → Response formatting
```

### Computational Requirements

- **Training**: TBD (estimated: 1-2 hours on modern CPU)
- **Inference**: < 200ms per request
- **Memory**: ~100 MB for model artifact
- **Storage**: Model file (.pkl) ~20-50 MB

---

## Ethical Considerations

### Potential Harms

1. **Over-reliance**: Farmer neglecting local knowledge
2. **Recommendation errors**: Crop failure due to incorrect recommendation
3. **Economic harm**: Lost income from failed crop
4. **Vulnerability**: Targeting economically disadvantaged farmers

### Mitigation

- Every response includes mandatory disclaimer
- Recommendations are estimates, not guarantees
- Encourage consultation with local agricultural experts
- Provide explanations to enable informed decisions
- Open-source model card for transparency

---

## Maintenance and Updates

### Model Retraining Schedule

- **Initial deployment**: Phase 1 completion
- **First retrain**: 3 months post-deployment
- **Quarterly**: Retrain with accumulated new data
- **Annual**: Major update with expanded geography/seasons

### Versioning

- Model versions: `crop_rec_v{major}.{minor}`
- Every retraining increments minor version
- Major version: Significant architecture/approach change

### Deprecation

- Model versions supported for 12 months minimum
- 6-month deprecation warning before removal
- Automated migration path for clients

---

## Caveats and Recommendations

### For Farmers

1. Recommendations are **estimates based on historical patterns**
2. Actual results depend on weather, pest management, and practices
3. **Always consult local Krishi Vigyan Kendra for final decision**
4. Consider market prices and input costs (Phase 2 feature)
5. Maintain crop rotation practices for soil health

### For Developers

1. Model assumes stable climate — update when climate shifts
2. Regular validation against real-world outcomes
3. Monitor for demographic biases in recommendations
4. Collect user feedback for model improvement
5. Document assumptions and limitations clearly

### For Agricultural Extension Agents

1. Use as advisory tool, not definitive guide
2. Explain uncertainty to farmers
3. Encourage data collection to improve model
4. Report systematic errors for model updates
5. Supplement with local knowledge and practices

---

## Model Card Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | TBD | Initial model card (Phase 1 planning) |

---

**Last Updated**: TBD  
**Next Review**: TBD  
**Maintained By**: Krishi Sathi Development Team
