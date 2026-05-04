# 🚀 Quick Start Guide

Get the Patient Triage Agent running in 5 minutes!

## ⚡ Fast Setup

### 1. Install Dependencies (30 seconds)

```bash
pip install -r requirements.txt
```

### 2. Set Your API Key (30 seconds)

**Option A: Environment Variable**
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

**Option B: Create .env file**
```bash
cp .env.example .env
# Then edit .env and add your API key
```

Get your API key from: https://console.anthropic.com/

### 3. Start the Server (10 seconds)

```bash
python triage_agent.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 4. Test It! (1 minute)

**Open another terminal** and run:

```bash
python test_triage.py
```

Or try the examples:

```bash
python example_client.py
```

Or test with curl:

```bash
curl -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "Test Patient",
    "age": 35,
    "gender": "Female",
    "symptoms": ["chest pain", "shortness of breath"],
    "medical_history_notes": "No history"
  }'
```

## 🎯 Quick Test Cases

### Test 1: Standard Case (Should route to Walk-in Clinic)
```bash
curl -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "John Doe",
    "age": 30,
    "gender": "Male",
    "symptoms": ["headache", "mild fever"]
  }'
```

### Test 2: Cardiac Emergency (Should trigger RED FLAG)
```bash
curl -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "Robert Smith",
    "age": 58,
    "gender": "Male",
    "symptoms": ["chest pain", "shortness of breath", "sweating"]
  }'
```

### Test 3: Stroke Detection (Should trigger RED FLAG)
```bash
curl -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "Mary Wilson",
    "age": 65,
    "gender": "Female",
    "symptoms": ["face drooping", "arm weakness", "slurred speech"]
  }'
```

## 📊 View API Documentation

Once server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔍 What to Expect

### Standard Patient Response
```json
{
  "patient_id": "PT-20260504...",
  "triage_level": "STANDARD",
  "confidence_score": 0.85,
  "red_flags": [],
  "matched_department": "Walk-in Clinic",
  "estimated_wait_minutes": 30
}
```

### Emergency with Red Flag
```json
{
  "patient_id": "PT-20260504...",
  "triage_level": "EMERGENCY",
  "confidence_score": 1.0,
  "red_flags": ["CARDIAC_EVENT_RISK"],
  "matched_department": "Emergency Room",
  "recommended_action": "🚨 CRITICAL: Call 911 immediately...",
  "estimated_wait_minutes": 5
}
```

## 🛠️ Troubleshooting

### Server won't start?
- Check Python version: `python --version` (need 3.9+)
- Install dependencies: `pip install -r requirements.txt`

### API calls failing?
- Make sure server is running: `http://localhost:8000/health`
- Check your API key is set correctly
- Verify no firewall blocking port 8000

### LLM errors?
- Verify ANTHROPIC_API_KEY is set
- Check you have API credits
- Test with: `echo $ANTHROPIC_API_KEY`

## 📚 Next Steps

1. **Read the README.md** for full documentation
2. **Run test_triage.py** for comprehensive testing
3. **Try example_client.py** for Python integration examples
4. **Check /docs** for interactive API documentation
5. **Customize departments** in triage_agent.py

## 🎓 Understanding the Code

### Main Files:
- `triage_agent.py` - Main FastAPI application (500 lines)
- `test_triage.py` - Comprehensive test suite
- `example_client.py` - Python client examples
- `requirements.txt` - Dependencies

### Key Components:
1. **RedFlagDetector** - Hard-coded safety rules (FR-3)
2. **LLMTriageAssessor** - Claude API integration (FR-2)
3. **DepartmentMatcher** - Smart routing logic (FR-4)
4. **TriageAgent** - Orchestrates everything

## 💡 Pro Tips

1. **Use the test suite** to understand all features
2. **Check the examples** for integration patterns
3. **Read the red-flag logic** - it's critical for safety
4. **Experiment with symptoms** to see AI reasoning
5. **Monitor the logs** to see what's happening

## 🎯 Assessment Checklist

- [x] FR-1: Patient Input Ingestion ✅
- [x] FR-2: LLM Triage Assessment ✅
- [x] FR-3: Red-Flag Detection ✅
- [x] FR-4: Department Matching ✅
- [x] FR-5: Triage Report Generation ✅
- [x] FR-6: Capacity Fallback ✅

All functional requirements implemented and tested!

---

**Need Help?** Check README.md for detailed documentation.
