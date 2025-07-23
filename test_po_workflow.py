import json
import requests
import time

# Configuration
FUNCTION_URL = "http://localhost:7072/api/start-po-workflow"  # Update with your deployed function URL
HEALTH_CHECK_URL = "http://localhost:7072/api/health"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing Health Check...")
    try:
        response = requests.get(HEALTH_CHECK_URL)
        print(f"Health Check Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_purchase_order_workflow(test_data):
    """Test the purchase order workflow with given data"""
    print(f"\nTesting Purchase Order Workflow with OrderID: {test_data.get('OrderID')}")
    print(f"Test Data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            FUNCTION_URL,
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code in [200, 202]:
            response_data = response.json()
            if 'instanceId' in response_data:
                print(f"Workflow started successfully with Instance ID: {response_data['instanceId']}")
            return True
        else:
            print(f"Workflow failed to start: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error testing workflow: {e}")
        return False

def run_all_tests():
    """Run all test scenarios"""
    print("=== Purchase Order Durable Function Tests ===\n")
    
    # Test 1: Health Check
    health_ok = test_health_check()
    
    if not health_ok:
        print("Health check failed. Make sure the function is running locally.")
        return
    
    # Test 2: Valid Draft Order (Small Amount - Auto Approve)
    test_data_1 = {
        "DurableInstanceId": "TEST001",
        "OrderID": "ORD001",
        "Details": "Office supplies - pens, paper, notebooks",
        "Status": "Draft",
        "Amount": 500
    }
    test_purchase_order_workflow(test_data_1)
    
    # Test 3: Valid Draft Order (Medium Amount - Manager Approval)
    test_data_2 = {
        "DurableInstanceId": "TEST002",
        "OrderID": "ORD002",
        "Details": "Computer equipment - laptop, monitor, keyboard",
        "Status": "Draft",
        "Amount": 5000
    }
    test_purchase_order_workflow(test_data_2)
    
    # Test 4: Valid Draft Order (Large Amount - Executive Approval)
    test_data_3 = {
        "DurableInstanceId": "TEST003",
        "OrderID": "ORD003",
        "Details": "Server infrastructure upgrade",
        "Status": "Draft",
        "Amount": 25000
    }
    test_purchase_order_workflow(test_data_3)
    
    # Test 5: Invalid Order (Missing Details)
    test_data_4 = {
        "DurableInstanceId": "TEST004",
        "OrderID": "ORD004",
        "Status": "Draft",
        "Amount": 1000
        # Missing "Details" field
    }
    test_purchase_order_workflow(test_data_4)
    
    # Test 6: Order with Non-Draft Status
    test_data_5 = {
        "DurableInstanceId": "TEST005",
        "OrderID": "ORD005",
        "Details": "Marketing materials",
        "Status": "Approved",  # Not Draft
        "Amount": 800
    }
    test_purchase_order_workflow(test_data_5)
    
    # Test 7: Missing Required Fields
    test_data_6 = {
        "DurableInstanceId": "TEST006",
        "Details": "Test order without OrderID",
        "Status": "Draft",
        "Amount": 300
        # Missing "OrderID" field
    }
    test_purchase_order_workflow(test_data_6)
    
    # Test 8: Empty Request Body
    print("\nTesting Empty Request Body...")
    try:
        response = requests.post(FUNCTION_URL, json=None)
        print(f"Empty Body Response Status: {response.status_code}")
        print(f"Empty Body Response: {response.text}")
    except Exception as e:
        print(f"Error testing empty body: {e}")

def create_power_automate_sample():
    """Create a sample JSON for Power Automate HTTP action"""
    sample_data = {
        "DurableInstanceId": "@{guid()}",  # Power Automate expression for unique ID
        "OrderID": "@{triggerOutputs()?['body/cr123_orderid']}",  # Replace with your Dataverse field
        "Details": "@{triggerOutputs()?['body/cr123_details']}",  # Replace with your Dataverse field
        "Status": "@{triggerOutputs()?['body/cr123_status']}",    # Replace with your Dataverse field
        "Amount": "@{triggerOutputs()?['body/cr123_amount']}"     # Replace with your Dataverse field
    }
    
    print("\n=== Power Automate HTTP Action Configuration ===")
    print("Method: POST")
    print(f"URI: {FUNCTION_URL}")
    print("Headers:")
    print("  Content-Type: application/json")
    print("\nBody (replace field names with your actual Dataverse fields):")
    print(json.dumps(sample_data, indent=2))
    
    # Also create a static example for testing
    static_sample = {
        "DurableInstanceId": "PA_TEST_001",
        "OrderID": "PO_2025_001",
        "Details": "Office furniture - desk, chair, filing cabinet",
        "Status": "Draft",
        "Amount": 1500
    }
    
    print("\nStatic Test Example:")
    print(json.dumps(static_sample, indent=2))

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Run all tests")
    print("2. Show Power Automate configuration")
    print("3. Both")
    
    choice = input("Enter your choice (1, 2, or 3): ").strip()
    
    if choice in ["1", "3"]:
        run_all_tests()
    
    if choice in ["2", "3"]:
        create_power_automate_sample()
    
    print("\n=== Test Complete ===")
