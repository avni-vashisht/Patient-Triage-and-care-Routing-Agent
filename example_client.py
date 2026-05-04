"""
Simple Python client for AI-Powered Patient Triage Agent
Demonstrates how to interact with the API programmatically
"""

import requests
from typing import List, Optional

class TriageClient:
    """Client for interacting with Patient Triage API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def triage_patient(
        self,
        patient_name: str,
        age: int,
        gender: str,
        symptoms: List[str],
        medical_history_notes: Optional[str] = None
    ):
        """
        Submit patient for triage assessment
        
        Args:
            patient_name: Full name of patient
            age: Patient age in years
            gender: Patient gender
            symptoms: List of symptom descriptions
            medical_history_notes: Optional medical history
            
        Returns:
            Triage report dict or None if error
        """
        payload = {
            "patient_name": patient_name,
            "age": age,
            "gender": gender,
            "symptoms": symptoms,
            "medical_history_notes": medical_history_notes
        }
        
        try:
            response = requests.post(f"{self.base_url}/triage", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None
    
    def get_departments(self):
        """Get list of available departments"""
        try:
            response = requests.get(f"{self.base_url}/departments")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None
    
    def health_check(self):
        """Check API health status"""
        try:
            response = requests.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

# ==================== EXAMPLE USAGE ====================

def example_1_standard_patient():
    """Example 1: Standard patient with mild symptoms"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Standard Patient Assessment")
    print("="*60)
    
    client = TriageClient()
    
    report = client.triage_patient(
        patient_name="Alice Johnson",
        age=28,
        gender="Female",
        symptoms=["sore throat", "mild cough", "runny nose"],
        medical_history_notes="No chronic conditions"
    )
    
    if report:
        print(f"\n✓ Triage Complete")
        print(f"  Patient: {report['patient_name']}")
        print(f"  Level: {report['triage_level']}")
        print(f"  Department: {report['matched_department']}")
        print(f"  Action: {report['recommended_action']}")
        print(f"  Wait Time: {report['estimated_wait_minutes']} minutes")

def example_2_cardiac_emergency():
    """Example 2: Cardiac emergency with red flag detection"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Cardiac Emergency (Red Flag)")
    print("="*60)
    
    client = TriageClient()
    
    report = client.triage_patient(
        patient_name="Robert Smith",
        age=62,
        gender="Male",
        symptoms=[
            "severe chest pain",
            "shortness of breath",
            "radiating pain to left arm",
            "sweating"
        ],
        medical_history_notes="History of high blood pressure, takes medication"
    )
    
    if report:
        print(f"\n🚨 EMERGENCY DETECTED")
        print(f"  Red Flags: {', '.join(report['red_flags'])}")
        print(f"  Level: {report['triage_level']} (Confidence: {report['confidence_score']})")
        print(f"  Department: {report['matched_department']}")
        print(f"  🚑 Action: {report['recommended_action']}")

def example_3_pediatric_fever():
    """Example 3: Pediatric high fever"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Pediatric High Fever")
    print("="*60)
    
    client = TriageClient()
    
    report = client.triage_patient(
        patient_name="Emma Wilson",
        age=6,
        gender="Female",
        symptoms=[
            "high fever 40 degrees celsius",
            "headache",
            "irritability",
            "won't eat"
        ],
        medical_history_notes="Generally healthy, vaccinations up to date"
    )
    
    if report:
        print(f"\n⚠️  PEDIATRIC CASE")
        print(f"  Red Flags: {', '.join(report['red_flags'])}")
        print(f"  Level: {report['triage_level']}")
        print(f"  Reasoning: {report['reasoning']}")
        print(f"  Action: {report['recommended_action']}")

def example_4_stroke_indicators():
    """Example 4: Stroke with FAST indicators"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Stroke Indicators (FAST)")
    print("="*60)
    
    client = TriageClient()
    
    report = client.triage_patient(
        patient_name="Mary Chen",
        age=71,
        gender="Female",
        symptoms=[
            "face drooping on right side",
            "arm weakness",
            "trouble speaking clearly",
            "confusion"
        ],
        medical_history_notes="Diabetes, hypertension"
    )
    
    if report:
        print(f"\n🚨 STROKE RISK DETECTED")
        print(f"  Red Flags: {', '.join(report['red_flags'])}")
        print(f"  Level: {report['triage_level']}")
        print(f"  Department: {report['matched_department']}")
        print(f"  🚑 IMMEDIATE ACTION: {report['recommended_action']}")

def example_5_check_departments():
    """Example 5: Check available departments"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Check Available Departments")
    print("="*60)
    
    client = TriageClient()
    
    departments = client.get_departments()
    
    if departments:
        print(f"\n📍 Found {len(departments)} departments:")
        for dept in departments:
            print(f"\n  {dept['name']}")
            print(f"    - Accepts: {', '.join(dept['accepts_triage_levels'])}")
            print(f"    - Available Slots: {dept['available_slots']}")
            print(f"    - Wait Time: ~{dept['estimated_wait_minutes']} minutes")

def example_6_batch_triage():
    """Example 6: Process multiple patients"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Batch Patient Processing")
    print("="*60)
    
    client = TriageClient()
    
    patients = [
        {
            "patient_name": "Patient A",
            "age": 45,
            "gender": "Male",
            "symptoms": ["headache", "mild fever"],
            "medical_history_notes": None
        },
        {
            "patient_name": "Patient B",
            "age": 55,
            "gender": "Female",
            "symptoms": ["severe abdominal pain", "vomiting"],
            "medical_history_notes": "Previous appendectomy"
        },
        {
            "patient_name": "Patient C",
            "age": 8,
            "gender": "Male",
            "symptoms": ["sprained ankle", "swelling"],
            "medical_history_notes": "Sports injury"
        }
    ]
    
    results = []
    for patient in patients:
        report = client.triage_patient(**patient)
        if report:
            results.append(report)
    
    print(f"\n✓ Processed {len(results)} patients:")
    for report in results:
        print(f"\n  {report['patient_name']}:")
        print(f"    - Level: {report['triage_level']}")
        print(f"    - Department: {report['matched_department']}")
        print(f"    - Wait: {report['estimated_wait_minutes']} min")

if __name__ == "__main__":
    print("\n" + "🏥"*30)
    print("  PATIENT TRIAGE CLIENT - EXAMPLES")
    print("🏥"*30)
    
    # Check if server is running
    client = TriageClient()
    health = client.health_check()
    
    if not health:
        print("\n❌ ERROR: Cannot connect to API server")
        print("Please start the server first:")
        print("  python triage_agent.py")
        exit(1)
    
    print(f"\n✓ Server Status: {health['status']}")
    
    # Run all examples
    example_1_standard_patient()
    example_2_cardiac_emergency()
    example_3_pediatric_fever()
    example_4_stroke_indicators()
    example_5_check_departments()
    example_6_batch_triage()
    
    print("\n" + "="*60)
    print("  ALL EXAMPLES COMPLETED")
    print("="*60 + "\n")
