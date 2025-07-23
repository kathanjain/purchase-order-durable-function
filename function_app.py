import azure.functions as func
import azure.durable_functions as df
import logging
import json
from datetime import datetime

app = func.FunctionApp()

# 1. Client Function (HTTP Trigger)
@app.function_name(name="StartPurchaseOrderWorkflow")
@app.route(route="start-po-workflow", methods=["POST"])
@app.durable_client_input(client_name="client")
async def start_workflow(req: func.HttpRequest, client: df.DurableOrchestrationClient):
    try:
        request_data = req.get_json()
        # Validation: Required fields
        required_fields = ["DurableInstanceId", "OrderID", "Status"]
        missing = [f for f in required_fields if not request_data.get(f)]
        if missing:
            return func.HttpResponse(
                json.dumps({"error": f"Missing required fields: {', '.join(missing)}"}),
                status_code=400,
                mimetype="application/json"
            )
        if request_data.get("Status") != "Draft":
            return func.HttpResponse(
                json.dumps({"error": "Order status must be 'Draft' to start workflow"}),
                status_code=400,
                mimetype="application/json"
            )
        # Start orchestration
        instance_id = await client.start_new(
            orchestration_function_name="PurchaseOrderOrchestrator",
            instance_id=request_data["DurableInstanceId"],
            client_input=request_data
        )
        return func.HttpResponse(
            json.dumps({
                "message": "Started Purchase Order approval workflow",
                "instanceId": instance_id,
                "orderID": request_data["OrderID"],
                "status": "Workflow Started"
            }),
            status_code=202,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error in start_workflow: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

# 2. Orchestrator Function
@app.function_name(name="PurchaseOrderOrchestrator")
@app.orchestration_trigger(context_name="context")
def orchestrator(context: df.DurableOrchestrationContext):
    input_data = context.get_input()
    validation_result = yield context.call_activity("ValidateOrderActivity", input_data)
    approval_result = yield context.call_activity("ApproveOrderActivity", input_data)
    # Optionally, add a call to update status in Dataverse here if needed
    return {
        "OrderID": input_data.get("OrderID"),
        "ValidationResult": validation_result,
        "ApprovalResult": approval_result
    }

# 3. Activity Functions
@app.function_name(name="ValidateOrderActivity")
@app.activity_trigger(input_name="input_data")
def validate_order(input_data: dict):
    # Required: OrderID, Status, Details
    if not input_data.get("OrderID"):
        raise Exception("OrderID is required")
    if not input_data.get("Status"):
        raise Exception("Status is required")
    if not input_data.get("Details"):
        raise Exception("Details field must not be empty")
    if input_data.get("Status") != "Draft":
        raise Exception("Order status must be 'Draft'")
    return "Validated"

@app.function_name(name="ApproveOrderActivity")
@app.activity_trigger(input_name="input_data")
def approve_order(input_data: dict):
    amount = input_data.get("Amount", 0)
    try:
        amount = float(amount)
    except Exception:
        amount = 0
    if amount <= 1000:
        return "Auto-Approved"
    elif amount <= 10000:
        return "Manager Approval (Auto-Approved for demo)"
    else:
        return "Executive Approval Required"
        
# 4. Health Check Function
@app.function_name(name="HealthCheck")
@app.route(route="health", methods=["GET"])
def health_check(req: func.HttpRequest):
    return func.HttpResponse(
        json.dumps({
            "status": "healthy",
            "service": "Purchase Order Durable Function",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }),
        status_code=200,
        mimetype="application/json"
    )
