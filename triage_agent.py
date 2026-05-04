"""
AI-Powered Patient Triage & Care Routing Agent
Healthcare MedTech System with LLM Integration
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
#import anthropic
from google import genai
import os
from datetime import datetime

# ==================== MODELS ====================

class TriageLevel(str, Enum):
    EMERGENCY = "EMERGENCY"
    URGENT = "URGENT"
    STANDARD = "STANDARD"
    SELF_CARE = "SELF_CARE"

class RedFlag(str, Enum):
    CARDIAC_EVENT_RISK = "CARDIAC_EVENT_RISK"
    STROKE_RISK = "STROKE_RISK"
    PEDIATRIC_HIGH_FEVER = "PEDIATRIC_HIGH_FEVER"

class PatientInput(BaseModel):
    patient_name: str
    age: int
    gender: str
    symptoms: List[str] = Field(..., description="List of symptom strings")
    medical_history_notes: Optional[str] = None

class Department(BaseModel):
    id: str
    name: str
    accepts_triage_levels: List[TriageLevel]
    available_slots: int
    estimated_wait_minutes: int

class TriageReport(BaseModel):
    patient_id: str
    patient_name: str
    triage_level: TriageLevel
    confidence_score: float
    reasoning: str
    red_flags: List[RedFlag]
    matched_department: Optional[str]
    recommended_action: str
    estimated_wait_minutes: Optional[int]
    capacity_flag: bool
    timestamp: str

# ==================== MOCK DATA ====================

# Real provider database from requirements
MOCK_DEPARTMENTS = [
    Department(
        id="DEPT-1001",
        name="Emergency Department",
        accepts_triage_levels=[TriageLevel.EMERGENCY, TriageLevel.URGENT],
        available_slots=3,
        estimated_wait_minutes=5
    ),
    Department(
        id="DEPT-1002",
        name="Cardiology Department",
        accepts_triage_levels=[TriageLevel.EMERGENCY, TriageLevel.URGENT],
        available_slots=1,
        estimated_wait_minutes=15
    ),
    Department(
        id="DEPT-1003",
        name="Pediatrics Department",
        accepts_triage_levels=[TriageLevel.EMERGENCY, TriageLevel.URGENT, TriageLevel.STANDARD],
        available_slots=2,
        estimated_wait_minutes=20
    ),
    Department(
        id="DEPT-1004",
        name="General Care",
        accepts_triage_levels=[TriageLevel.STANDARD, TriageLevel.SELF_CARE],
        available_slots=5,
        estimated_wait_minutes=45
    )
]

# ==================== RED-FLAG DETECTION ====================

class RedFlagDetector:
    """Hard-coded safety overrides that MUST bypass LLM output"""
    
    @staticmethod
    def detect_red_flags(patient: PatientInput) -> tuple[Optional[TriageLevel], List[RedFlag]]:
        """
        Returns: (override_triage_level, red_flags)
        If override_triage_level is not None, it MUST be used instead of LLM output
        """
        red_flags = []
        override_level = None
        
        symptoms_lower = [s.lower() for s in patient.symptoms]
        symptoms_text = " ".join(symptoms_lower)
        
        # FR-3(a): Cardiac event detection
        has_chest_pain = any(term in symptoms_text for term in ["chest pain", "chest discomfort", "crushing chest"])
        has_shortness_breath = any(term in symptoms_text for term in ["shortness of breath", "difficulty breathing", "can't breathe", "breathing problem"])
        
        if has_chest_pain and has_shortness_breath:
            red_flags.append(RedFlag.CARDIAC_EVENT_RISK)
            override_level = TriageLevel.EMERGENCY
        
        # FR-3(b): FAST stroke indicators
        has_face_drooping = any(term in symptoms_text for term in ["face drooping", "facial droop", "face weakness", "facial paralysis"])
        has_arm_weakness = any(term in symptoms_text for term in ["arm weakness", "arm numbness", "can't lift arm", "weak arm"])
        has_speech_difficulty = any(term in symptoms_text for term in ["speech difficulty", "slurred speech", "can't speak", "speech problem", "trouble speaking"])
        
        if any([has_face_drooping, has_arm_weakness, has_speech_difficulty]):
            red_flags.append(RedFlag.STROKE_RISK)
            override_level = TriageLevel.EMERGENCY
        
        # FR-3(c): Pediatric high fever
        if patient.age < 12:
            has_high_fever = any(term in symptoms_text for term in ["fever", "high temperature"])
            # Check for explicit temperature mentions > 39C (102.2F)
            has_critical_fever = any(term in symptoms_text for term in ["39", "40", "41", "102", "103", "104", "105"])
            
            if has_high_fever and has_critical_fever:
                red_flags.append(RedFlag.PEDIATRIC_HIGH_FEVER)
                # Override to URGENT (not EMERGENCY per FR-3c)
                if override_level != TriageLevel.EMERGENCY:  # Don't downgrade from EMERGENCY
                    override_level = TriageLevel.URGENT
        
        return override_level, red_flags

# ==================== LLM TRIAGE ASSESSMENT ====================

class LLMTriageAssessor:
    """Uses Claude API for intelligent triage assessment"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = genai.Client(api_key=api_key or os.environ.get("GOOGLE_API_KEY"))
    
    def assess_patient(self, patient: PatientInput) -> tuple[TriageLevel, float, str]:
        """
        Returns: (triage_level, confidence_score, reasoning)
        """
        
        prompt = f"""You are a medical triage AI assistant. Analyze the following patient information and provide a triage assessment.

Patient Information:
- Name: {patient.patient_name}
- Age: {patient.age}
- Gender: {patient.gender}
- Symptoms: {', '.join(patient.symptoms)}
- Medical History: {patient.medical_history_notes or 'None provided'}

Your task:
1. Assess the severity of the patient's condition
2. Classify into one of these triage levels:
   - EMERGENCY: Life-threatening, needs immediate attention (< 5 min)
   - URGENT: Serious but not immediately life-threatening (< 30 min)
   - STANDARD: Non-urgent medical attention needed (< 2 hours)
   - SELF_CARE: Minor issues that may not need professional care

3. Provide a confidence score (0.0 to 1.0) for your assessment
4. Give brief reasoning (2-3 sentences)

Respond in this EXACT format:
TRIAGE_LEVEL: [one of: EMERGENCY, URGENT, STANDARD, SELF_CARE]
CONFIDENCE: [0.0 to 1.0]
REASONING: [your explanation]"""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            
            # Parse the response
            triage_level = None
            confidence = 0.5  # default
            reasoning = ""
            
            for line in response_text.split('\n'):
                line = line.strip()
                if line.startswith("TRIAGE_LEVEL:"):
                    level_str = line.split(":", 1)[1].strip()
                    try:
                        triage_level = TriageLevel(level_str)
                    except ValueError:
                        triage_level = TriageLevel.STANDARD
                
                elif line.startswith("CONFIDENCE:"):
                    try:
                        confidence = float(line.split(":", 1)[1].strip())
                        confidence = max(0.0, min(1.0, confidence))  # Clamp to 0-1
                    except (ValueError, IndexError):
                        confidence = 0.5
                
                elif line.startswith("REASONING:"):
                    reasoning = line.split(":", 1)[1].strip()
            
            if not triage_level:
                triage_level = TriageLevel.STANDARD
            
            if not reasoning:
                reasoning = "Assessment based on presented symptoms and patient demographics."
            
            return triage_level, confidence, reasoning
            
        except Exception as e:
            # Fallback to conservative assessment if LLM fails
            print(f"LLM Error: {e}")
            return TriageLevel.URGENT, 0.3, f"LLM assessment unavailable. Conservative triage recommended. Error: {str(e)[:100]}"

# ==================== DEPARTMENT MATCHER ====================

class DepartmentMatcher:
    """Matches triage level to available departments"""
    
    @staticmethod
    def find_department(triage_level: TriageLevel, departments: List[Department]) -> tuple[Optional[Department], bool]:
        """
        Returns: (matched_department, capacity_flag)
        capacity_flag = True if first choice has no slots
        """
        # Find departments that accept this triage level
        matching_depts = [d for d in departments if triage_level in d.accepts_triage_levels]
        
        # Sort by priority: available slots (descending), then wait time (ascending)
        matching_depts.sort(key=lambda d: (-d.available_slots, d.estimated_wait_minutes))
        
        if not matching_depts:
            return None, True
        
        # Check if first choice has availability
        best_dept = matching_depts[0]
        capacity_flag = best_dept.available_slots == 0
        
        if capacity_flag and len(matching_depts) > 1:
            # Find next best with available slots
            for dept in matching_depts[1:]:
                if dept.available_slots > 0:
                    return dept, True
        
        return best_dept, capacity_flag

# ==================== TRIAGE AGENT ====================

class TriageAgent:
    """Main triage orchestrator"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.red_flag_detector = RedFlagDetector()
        self.llm_assessor = LLMTriageAssessor(api_key)
        self.department_matcher = DepartmentMatcher()
    
    def process_patient(self, patient: PatientInput) -> TriageReport:
        """
        Main triage workflow:
        1. Red-flag detection (safety override)
        2. LLM triage assessment
        3. Department matching
        4. Report generation
        """
        
        # Step 1: Red-flag detection
        override_level, red_flags = self.red_flag_detector.detect_red_flags(patient)
        
        # Step 2: LLM assessment (unless overridden)
        if override_level:
            triage_level = override_level
            confidence = 1.0  # Safety overrides are 100% confident
            reasoning = f"SAFETY OVERRIDE: Critical red flags detected - {', '.join([f.value for f in red_flags])}"
        else:
            triage_level, confidence, reasoning = self.llm_assessor.assess_patient(patient)
        
        # Step 3: Department matching
        matched_dept, capacity_flag = self.department_matcher.find_department(triage_level, MOCK_DEPARTMENTS)
        
        # Step 4: Generate recommended action
        recommended_action = self._generate_recommendation(triage_level, matched_dept, capacity_flag, red_flags)
        
        # Step 5: Build report
        report = TriageReport(
            patient_id=f"PT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{patient.patient_name[:3].upper()}",
            patient_name=patient.patient_name,
            triage_level=triage_level,
            confidence_score=round(confidence, 2),
            reasoning=reasoning,
            red_flags=red_flags,
            matched_department=matched_dept.name if matched_dept else None,
            recommended_action=recommended_action,
            estimated_wait_minutes=matched_dept.estimated_wait_minutes if matched_dept else None,
            capacity_flag=capacity_flag,
            timestamp=datetime.now().isoformat()
        )
        
        return report
    
    def _generate_recommendation(self, level: TriageLevel, dept: Optional[Department], 
                                 capacity_flag: bool, red_flags: List[RedFlag]) -> str:
        """Generate human-readable action recommendation"""
        
        if red_flags:
            if RedFlag.CARDIAC_EVENT_RISK in red_flags or RedFlag.STROKE_RISK in red_flags:
                return "🚨 CRITICAL: Call 911 immediately or proceed to nearest Emergency Room. Do not drive yourself."
        
        if level == TriageLevel.EMERGENCY:
            if dept and not capacity_flag:
                return f"Proceed immediately to {dept.name}. Alert staff of arrival."
            else:
                return "Proceed to nearest Emergency Room immediately or call 911."
        
        elif level == TriageLevel.URGENT:
            if dept and not capacity_flag:
                return f"Proceed to {dept.name} within 30 minutes. Estimated wait: {dept.estimated_wait_minutes} min."
            elif capacity_flag:
                return f"Proceed to {dept.name} (currently at capacity) or consider nearby urgent care facility."
            else:
                return "Seek urgent medical attention within 30 minutes."
        
        elif level == TriageLevel.STANDARD:
            if dept:
                return f"Schedule appointment at {dept.name}. Estimated wait: {dept.estimated_wait_minutes} min."
            else:
                return "Schedule appointment with general practitioner within 24 hours."
        
        else:  # SELF_CARE
            return "Monitor symptoms at home. Seek medical attention if symptoms worsen. Consider over-the-counter remedies."

# ==================== FASTAPI APPLICATION ====================

app = FastAPI(
    title="AI-Powered Patient Triage Agent",
    description="Healthcare MedTech System with LLM Integration",
    version="1.0.0"
)

# Initialize the triage agent
triage_agent = TriageAgent()

@app.post("/triage", response_model=TriageReport)
async def triage_patient(patient: PatientInput):
    """
    Main endpoint for patient triage assessment
    
    Accepts patient data and returns comprehensive triage report with:
    - Triage level classification
    - Red-flag detection
    - Department matching
    - Recommended actions
    """
    try:
        report = triage_agent.process_patient(patient)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Triage processing error: {str(e)}")

@app.get("/departments")
async def list_departments():
    """List all available departments and their current capacity"""
    return MOCK_DEPARTMENTS

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Patient Triage Agent",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)