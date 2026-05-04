# 🏥 AI-Powered Patient Triage & Care Routing Agent

A healthcare MedTech system that uses AI (Claude LLM) to intelligently assess patient-reported symptoms, classify severity, detect life-threatening red-flag patterns, and route patients to appropriate departments via a REST API.

## 📋 Overview

**Domain:** Healthcare / MedTech  
**Category:** LLM Integration + REST API + Safety-Critical Logic

### Business Context

MediAssist Health Network operates walk-in clinics and emergency departments across multiple cities. Their triage nurses are overwhelmed during peak hours, leading to dangerous delays in identifying critical patients. This system provides AI-powered assistance while maintaining strict safety overrides for life-threatening conditions.

## 🎯 Functional Requirements

| ID | Requirement | Status |
|----|-------------|--------|
| **FR-1** | Patient Input Ingestion | ✅ Implemented |
| **FR-2** | LLM Triage Assessment | ✅ Implemented |
| **FR-3** | Red-Flag Detection (Safety Override) | ✅ Implemented |
| **FR-4** | Department/Provider Matching | ✅ Implemented |
| **FR-5** | Triage Report Generation | ✅ Implemented |
| **FR-6** | Capacity Fallback | ✅ Implemented |

### FR-3: Safety Override Rules (CRITICAL)

These hard-coded rules **MUST** bypass LLM output:

1. **Cardiac Event Risk**: Chest pain + shortness of breath → **EMERGENCY** + flag: `CARDIAC_EVENT_RISK`
2. **Stroke Risk**: FAST indicators (face drooping / arm weakness / speech difficulty) → **EMERGENCY** + flag: `STROKE_RISK`
3. **Pediatric High Fever**: Age < 12 with fever > 39°C → **URGENT** + flag: `PEDIATRIC_HIGH_FEVER`

## 🏗️ Architecture

```
Patient Input
    ↓
Red-Flag Detector (Safety Override)
    ↓
LLM Triage Assessment (Claude API)
    ↓
Department Matcher
    ↓
Capacity Check
    ↓
Triage Report (JSON)
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.9+
- Anthropic API key (for Claude LLM)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Set Up API Key

Create a `.env` file or set environment variable:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Or create `.env` file:
```
ANTHROPIC_API_KEY=your-api-key-here
```

### Step 3: Run the Server

```bash
python triage_agent.py
```

Or with uvicorn for hot-reload:
```bash
uvicorn triage_agent:app --reload
```

Server runs at: `http://localhost:8000`

### Step 4: Run Tests

In a separate terminal:

```bash
python test_triage.py
```

## 📡 API Endpoints

### 1. POST /triage

Main endpoint for patient triage assessment.

**Request Body:**
```json
{
  "patient_name": "John Doe",
  "age": 45,
  "gender": "Male",
  "symptoms": ["chest pain", "shortness of breath", "sweating"],
  "medical_history_notes": "History of hypertension"
}
```

**Response:**
```json
{
  "patient_id": "PT-20260504132421-JOH",
  "patient_name": "John Doe",
  "triage_level": "EMERGENCY",
  "confidence_score": 1.0,
  "reasoning": "SAFETY OVERRIDE: Critical red flags detected - CARDIAC_EVENT_RISK",
  "red_flags": ["CARDIAC_EVENT_RISK"],
  "matched_department": "Emergency Room",
  "recommended_action": "🚨 CRITICAL: Call 911 immediately or proceed to nearest Emergency Room.",
  "estimated_wait_minutes": 5,
  "capacity_flag": false,
  "timestamp": "2026-05-04T13:24:21.123456"
}
```

### 2. GET /departments

List all available departments and current capacity.

**Response:**
```json
[
  {
    "id": "dept_er",
    "name": "Emergency Room",
    "accepts_triage_levels": ["EMERGENCY"],
    "available_slots": 3,
    "estimated_wait_minutes": 5
  },
  ...
]
```

### 3. GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "Patient Triage Agent",
  "timestamp": "2026-05-04T13:24:21.123456"
}
```

## 🔍 Triage Levels

| Level | Description | Time Frame |
|-------|-------------|------------|
| **EMERGENCY** | Life-threatening, immediate attention | < 5 min |
| **URGENT** | Serious but not immediately life-threatening | < 30 min |
| **STANDARD** | Non-urgent medical attention needed | < 2 hours |
| **SELF_CARE** | Minor issues, may not need professional care | Monitor at home |

## 🏥 Mock Departments

The system includes 4 mock departments:

1. **Emergency Room**: EMERGENCY patients, 5 min wait
2. **Urgent Care**: URGENT/EMERGENCY patients, 20 min wait
3. **General Practice**: STANDARD/URGENT patients, 45 min wait
4. **Walk-in Clinic**: STANDARD/SELF_CARE patients, 30 min wait

## 🧪 Testing

### Manual Testing with curl

**Test 1: Standard Patient**
```bash
curl -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "Jane Smith",
    "age": 35,
    "gender": "Female",
    "symptoms": ["headache", "fever", "fatigue"],
    "medical_history_notes": "No significant history"
  }'
```

**Test 2: Cardiac Emergency (Red Flag)**
```bash
curl -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "Robert Williams",
    "age": 58,
    "gender": "Male",
    "symptoms": ["chest pain", "shortness of breath", "sweating"],
    "medical_history_notes": "Smoker"
  }'
```

**Test 3: Stroke Indicators (Red Flag)**
```bash
curl -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "Margaret Chen",
    "age": 67,
    "gender": "Female",
    "symptoms": ["face drooping", "arm weakness", "slurred speech"]
  }'
```

### Automated Testing

Run the comprehensive test suite:
```bash
python test_triage.py
```

This tests all 6 functional requirements with multiple scenarios.

## 🔐 Security Considerations

1. **API Key Management**: Never commit API keys to version control
2. **Input Validation**: All inputs validated via Pydantic models
3. **Safety Overrides**: Critical conditions bypass AI for guaranteed safety
4. **Error Handling**: Graceful degradation if LLM unavailable
5. **Rate Limiting**: Consider implementing in production

## 📊 System Performance

- **Average Response Time**: < 2 seconds (depends on LLM latency)
- **Safety Override Detection**: < 50ms (instant)
- **Confidence Scoring**: 0.0 - 1.0 scale
- **LLM Model**: Claude Sonnet 4 (fast, accurate, medically aware)

## 🔧 Customization

### Adding New Departments

Edit `MOCK_DEPARTMENTS` in `triage_agent.py`:

```python
MOCK_DEPARTMENTS.append(
    Department(
        id="dept_custom",
        name="Custom Department",
        accepts_triage_levels=[TriageLevel.STANDARD],
        available_slots=10,
        estimated_wait_minutes=25
    )
)
```

### Adding New Red Flags

Add to `RedFlagDetector.detect_red_flags()` method:

```python
# Example: Severe allergic reaction
has_severe_allergy = any(term in symptoms_text for term in 
    ["anaphylaxis", "throat swelling", "can't swallow"])

if has_severe_allergy:
    red_flags.append(RedFlag.ANAPHYLAXIS)
    override_level = TriageLevel.EMERGENCY
```

### Adjusting LLM Prompt

Modify the prompt in `LLMTriageAssessor.assess_patient()` to:
- Add medical context
- Include specific protocols
- Change assessment criteria

## 📚 API Documentation

Interactive API docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🐛 Troubleshooting

### Issue: LLM Assessment Failing

**Symptom**: Getting low confidence scores or "LLM assessment unavailable"

**Solutions**:
1. Check API key is set correctly
2. Verify internet connection
3. Check Anthropic API status
4. Review logs for specific error messages

### Issue: No Department Matched

**Symptom**: `matched_department: null`

**Solutions**:
1. Check department availability
2. Verify triage level mapping
3. Ensure mock departments include all triage levels

### Issue: Red Flags Not Triggering

**Symptom**: Safety overrides not activating

**Solutions**:
1. Check symptom text matches exact keywords
2. Verify age for pediatric rules
3. Review `detect_red_flags()` logic

## 📝 Development Roadmap

- [ ] Database integration (replace mock departments)
- [ ] Real-time capacity updates
- [ ] Patient history lookup
- [ ] Multi-language support
- [ ] Clinical decision support system (CDSS) integration
- [ ] Audit logging and compliance
- [ ] Integration with EHR systems
- [ ] Mobile app interface
- [ ] Analytics dashboard

## 🤝 Contributing

This is an assessment project. For production use:
1. Add proper database
2. Implement authentication/authorization
3. Add comprehensive logging
4. Set up monitoring and alerting
5. Conduct medical compliance review
6. Add extensive unit and integration tests

## ⚖️ Legal & Compliance

**IMPORTANT**: This is a demonstration system. For production medical use:
- Consult with medical professionals
- Ensure HIPAA compliance (if US)
- Get necessary medical device certifications
- Implement proper audit trails
- Add clinical validation
- Consider malpractice insurance

## 📄 License

Assessment/Educational purposes only.

## 👥 Support

For issues or questions about this implementation, review the code comments and test suite.

---

**Built with**: FastAPI, Claude LLM (Anthropic), Python 3.9+  
**Assessment**: Real-World Coding Assessment © 2026
