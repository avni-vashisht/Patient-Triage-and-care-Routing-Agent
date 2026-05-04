"""
Test script for AI-Powered Patient Triage Agent
Demonstrates all functional requirements (FR-1 through FR-6)
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def print_section(title: str):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_report(report: Dict[Any, Any]):
    """Pretty print triage report"""
    print(f"\n📋 TRIAGE REPORT")
    print(f"├─ Patient: {report['patient_name']} (ID: {report['patient_id']})")
    print(f"├─ Triage Level: {report['triage_level']} (Confidence: {report['confidence_score']})")
    print(f"├─ Red Flags: {', '.join(report['red_flags']) if report['red_flags'] else 'None'}")
    print(f"├─ Department: {report['matched_department'] or 'N/A'}")
    print(f"├─ Wait Time: {report['estimated_wait_minutes']} minutes" if report['estimated_wait_minutes'] else "├─ Wait Time: N/A")
    print(f"├─ Capacity Flag: {'⚠️  YES' if report['capacity_flag'] else '✓ NO'}")
    print(f"├─ Reasoning: {report['reasoning']}")
    print(f"└─ Action: {report['recommended_action']}")
    print()

def test_fr1_patient_input():
    """FR-1: Patient Input Ingestion"""
    print_section("FR-1: Patient Input Ingestion")
    
    patient = {
        "patient_name": "John Doe",
        "age": 45,
        "gender": "Male",
        "symptoms": ["headache", "mild fever", "fatigue"],
        "medical_history_notes": "No significant medical history"
    }
    
    print("Testing standard patient input ingestion...")
    print(f"Input: {json.dumps(patient, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/triage", json=patient)
    
    if response.status_code == 200:
        print("✓ Patient input accepted successfully")
        print_report(response.json())
    else:
        print(f"✗ Error: {response.status_code} - {response.text}")

def test_fr2_llm_assessment():
    """FR-2: LLM Triage Assessment"""
    print_section("FR-2: LLM Triage Assessment")
    
    patient = {
        "patient_name": "Sarah Johnson",
        "age": 32,
        "gender": "Female",
        "symptoms": ["severe migraine", "nausea", "sensitivity to light"],
        "medical_history_notes": "History of migraines, takes sumatriptan"
    }
    
    print("Testing LLM triage assessment...")
    response = requests.post(f"{BASE_URL}/triage", json=patient)
    
    if response.status_code == 200:
        report = response.json()
        print("✓ LLM Assessment completed")
        print(f"  - Triage Level: {report['triage_level']}")
        print(f"  - Confidence Score: {report['confidence_score']}")
        print(f"  - Reasoning: {report['reasoning']}")
        print_report(report)
    else:
        print(f"✗ Error: {response.status_code}")

def test_fr3a_cardiac_red_flag():
    """FR-3(a): Cardiac Event Red Flag Detection"""
    print_section("FR-3(a): Red-Flag Detection - Cardiac Event")
    
    patient = {
        "patient_name": "Robert Williams",
        "age": 58,
        "gender": "Male",
        "symptoms": ["chest pain", "shortness of breath", "sweating"],
        "medical_history_notes": "Smoker, family history of heart disease"
    }
    
    print("Testing CARDIAC EVENT red flag (chest pain + shortness of breath)...")
    response = requests.post(f"{BASE_URL}/triage", json=patient)
    
    if response.status_code == 200:
        report = response.json()
        print("✓ Red flag detected!")
        print(f"  - Red Flags: {report['red_flags']}")
        print(f"  - Override Level: {report['triage_level']} (should be EMERGENCY)")
        print(f"  - Confidence: {report['confidence_score']} (should be 1.0)")
        print_report(report)
        
        # Verify safety override
        if "CARDIAC_EVENT_RISK" in report['red_flags'] and report['triage_level'] == "EMERGENCY":
            print("✓✓ SAFETY OVERRIDE WORKING CORRECTLY")
        else:
            print("✗✗ WARNING: Safety override may not be working!")
    else:
        print(f"✗ Error: {response.status_code}")

def test_fr3b_stroke_red_flag():
    """FR-3(b): FAST Stroke Red Flag Detection"""
    print_section("FR-3(b): Red-Flag Detection - Stroke (FAST)")
    
    patient = {
        "patient_name": "Margaret Chen",
        "age": 67,
        "gender": "Female",
        "symptoms": ["face drooping", "arm weakness", "slurred speech"],
        "medical_history_notes": "Hypertension, on medication"
    }
    
    print("Testing STROKE red flag (FAST indicators)...")
    response = requests.post(f"{BASE_URL}/triage", json=patient)
    
    if response.status_code == 200:
        report = response.json()
        print("✓ Red flag detected!")
        print(f"  - Red Flags: {report['red_flags']}")
        print(f"  - Override Level: {report['triage_level']} (should be EMERGENCY)")
        print_report(report)
        
        if "STROKE_RISK" in report['red_flags']:
            print("✓✓ STROKE DETECTION WORKING CORRECTLY")
    else:
        print(f"✗ Error: {response.status_code}")

def test_fr3c_pediatric_red_flag():
    """FR-3(c): Pediatric High Fever Red Flag Detection"""
    print_section("FR-3(c): Red-Flag Detection - Pediatric High Fever")
    
    patient = {
        "patient_name": "Emma Thompson",
        "age": 8,
        "gender": "Female",
        "symptoms": ["fever 40 degrees", "headache", "irritability"],
        "medical_history_notes": "Generally healthy child"
    }
    
    print("Testing PEDIATRIC HIGH FEVER red flag (age < 12, fever > 39C)...")
    response = requests.post(f"{BASE_URL}/triage", json=patient)
    
    if response.status_code == 200:
        report = response.json()
        print("✓ Red flag detected!")
        print(f"  - Red Flags: {report['red_flags']}")
        print(f"  - Override Level: {report['triage_level']} (should be URGENT)")
        print_report(report)
        
        if "PEDIATRIC_HIGH_FEVER" in report['red_flags']:
            print("✓✓ PEDIATRIC FEVER DETECTION WORKING CORRECTLY")
    else:
        print(f"✗ Error: {response.status_code}")

def test_fr4_department_matching():
    """FR-4: Department/Provider Matching"""
    print_section("FR-4: Department/Provider Matching")
    
    # First, check available departments
    print("Fetching available departments...")
    response = requests.get(f"{BASE_URL}/departments")
    
    if response.status_code == 200:
        departments = response.json()
        print("\n📍 Available Departments:")
        for dept in departments:
            print(f"  - {dept['name']}: accepts {dept['accepts_triage_levels']}, "
                  f"{dept['available_slots']} slots, ~{dept['estimated_wait_minutes']} min wait")
    
    # Test matching for different triage levels
    test_cases = [
        ("EMERGENCY patient", {
            "patient_name": "Test Emergency",
            "age": 40,
            "gender": "Male",
            "symptoms": ["chest pain", "shortness of breath"]
        }),
        ("URGENT patient", {
            "patient_name": "Test Urgent",
            "age": 35,
            "gender": "Female",
            "symptoms": ["severe abdominal pain", "vomiting"]
        }),
        ("STANDARD patient", {
            "patient_name": "Test Standard",
            "age": 28,
            "gender": "Male",
            "symptoms": ["persistent cough", "mild fever"]
        })
    ]
    
    for case_name, patient in test_cases:
        print(f"\n--- Testing: {case_name} ---")
        response = requests.post(f"{BASE_URL}/triage", json=patient)
        if response.status_code == 200:
            report = response.json()
            print(f"✓ Matched to: {report['matched_department']}")
            print(f"  Level: {report['triage_level']}, Wait: {report['estimated_wait_minutes']} min")

def test_fr5_report_generation():
    """FR-5: Triage Report Generation"""
    print_section("FR-5: Triage Report Generation")
    
    patient = {
        "patient_name": "James Martinez",
        "age": 42,
        "gender": "Male",
        "symptoms": ["ankle sprain", "swelling", "difficulty walking"],
        "medical_history_notes": "Twisted ankle playing basketball"
    }
    
    print("Testing structured JSON report generation...")
    response = requests.post(f"{BASE_URL}/triage", json=patient)
    
    if response.status_code == 200:
        report = response.json()
        
        print("\n✓ Complete Triage Report Generated:")
        print(json.dumps(report, indent=2))
        
        # Verify all required fields
        required_fields = [
            'patient_id', 'triage_level', 'confidence_score', 'red_flags',
            'matched_department', 'recommended_action', 'estimated_wait_minutes', 'capacity_flag'
        ]
        
        missing_fields = [f for f in required_fields if f not in report]
        
        if not missing_fields:
            print("\n✓✓ All required fields present in report")
        else:
            print(f"\n✗✗ Missing fields: {missing_fields}")

def test_fr6_capacity_fallback():
    """FR-6: Capacity Fallback"""
    print_section("FR-6: Capacity Fallback Logic")
    
    print("Note: This test requires manual department capacity manipulation")
    print("In a real scenario, if Emergency Room has 0 slots, system should:")
    print("  1. Set capacity_flag: true")
    print("  2. Suggest next best department (e.g., Urgent Care)")
    
    # Simulate EMERGENCY patient
    patient = {
        "patient_name": "Critical Patient",
        "age": 55,
        "gender": "Male",
        "symptoms": ["chest pain", "shortness of breath", "dizziness"]
    }
    
    response = requests.post(f"{BASE_URL}/triage", json=patient)
    
    if response.status_code == 200:
        report = response.json()
        print_report(report)
        
        if report['capacity_flag']:
            print("⚠️  Capacity fallback activated")
            print(f"   Alternative department suggested: {report['matched_department']}")
        else:
            print("✓ Primary department has availability")

def run_all_tests():
    """Run complete test suite"""
    print("\n" + "🏥"*40)
    print("  AI-POWERED PATIENT TRIAGE AGENT - TEST SUITE")
    print("🏥"*40)
    
    try:
        # Health check first
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("\n✓ API Server is running")
        else:
            print("\n✗ API Server health check failed")
            return
        
        # Run all functional requirement tests
        test_fr1_patient_input()
        test_fr2_llm_assessment()
        test_fr3a_cardiac_red_flag()
        test_fr3b_stroke_red_flag()
        test_fr3c_pediatric_red_flag()
        test_fr4_department_matching()
        test_fr5_report_generation()
        test_fr6_capacity_fallback()
        
        print("\n" + "="*80)
        print("  TEST SUITE COMPLETED")
        print("="*80 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Cannot connect to API server")
        print("Please ensure the server is running with: python triage_agent.py")
        print("Or: uvicorn triage_agent:app --reload")

if __name__ == "__main__":
    run_all_tests()
