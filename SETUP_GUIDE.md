# Purchase Order Durable Function Setup Guide

## Overview
This Azure Durable Function implements an automated Purchase Order approval workflow that can be triggered from Power Automate when a new Purchase Order is created with Status = "Draft".

## Architecture

### Functions Overview
1. **StartPurchaseOrderWorkflow** (HTTP Trigger) - Entry point for Power Automate
2. **PurchaseOrderOrchestrator** - Orchestrates the approval workflow
3. **ValidateOrderActivity** - Validates order data
4. **ApproveOrderActivity** - Handles approval logic
5. **UpdateOrderStatusActivity** - (Placeholder for Dataverse integration, not implemented by default)
6. **HealthCheck** - Health monitoring endpoint

### Workflow Steps
1. Receive Purchase Order data from Power Automate
2. Validate required fields and business rules
3. Apply approval logic based on order amount
4. (Optional) Update order status in Dataverse (requires custom implementation)
5. Return workflow results

## Local Development Setup

### Prerequisites
- Python 3.8 or higher
- Azure Functions Core Tools v4
- Visual Studio Code with Azure Functions extension

### Installation Steps

1. **Install Azure Functions Core Tools**
   ```bash
   npm install -g azure-functions-core-tools@4 --unsafe-perm true
   ```

2. **Install Python Dependencies**
   ```bash
   cd DurablePOApproval
   pip install -r requirements.txt
   ```

3. **Run Locally**
   ```bash
   func start
   ```

4. **Test the Function**
   ```bash
   python test_po_workflow.py
   ```

## Power Automate Integration

### HTTP Action Configuration

**Method:** POST  
**URI:** `https://your-function-app.azurewebsites.net/api/start-po-workflow`  
**Headers:**
```json
{
  "Content-Type": "application/json"
}
```

**Body:**
```json
{
  "DurableInstanceId": "@{guid()}",
  "OrderID": "@{triggerOutputs()?['body/your_orderid_field']}",
  "Details": "@{triggerOutputs()?['body/your_details_field']}",
  "Status": "@{triggerOutputs()?['body/your_status_field']}",
  "Amount": "@{triggerOutputs()?['body/your_amount_field']}"
}
```

### Power Automate Flow Setup

1. **Trigger:** When a row is added or modified (Dataverse)
   - Table: Your Purchase Order table
   - Filter: Status equals "Draft"

2. **HTTP Action:** Call the Azure Function
   - Use the configuration above
   - Replace field names with your actual Dataverse column names

3. **Email Action (Optional):** Send notification based on workflow result
   - Use the HTTP response to determine email content

## Approval Logic

The function implements a tiered approval system:

- **≤ $1,000:** Auto-approved
- **$1,001 - $10,000:** Manager approval (currently auto-approved for demo)
- **> $10,000:** Executive approval required

You can customize this logic in the `ApproveOrderActivity` function.

## Testing

### Local Testing
```bash
# Run all tests
python test_po_workflow.py

# Choose option 1 for comprehensive testing
# Choose option 2 for Power Automate configuration examples
# Choose option 3 for both
```

### Manual Testing with curl
```bash
curl -X POST http://localhost:7072/api/start-po-workflow \
  -H "Content-Type: application/json" \
  -d '{
    "DurableInstanceId": "TEST001",
    "OrderID": "ORD001",
    "Details": "Test order",
    "Status": "Draft",
    "Amount": 500
  }'
```

### Health Check
```bash
curl http://localhost:7072/api/health
```

## Deployment to Azure

### Using Azure CLI
```bash
# Create resource group
az group create --name rg-po-approval --location eastus

# Create storage account
az storage account create --name stpoapproval --resource-group rg-po-approval --location eastus --sku Standard_LRS

# Create function app
az functionapp create --resource-group rg-po-approval --consumption-plan-location eastus --runtime python --runtime-version 3.9 --functions-version 4 --name func-po-approval --storage-account stpoapproval

# Deploy function
func azure functionapp publish func-po-approval
```

### Using VS Code
1. Install Azure Functions extension
2. Sign in to Azure
3. Right-click on the function folder
4. Select "Deploy to Function App"
5. Follow the prompts

## Configuration

### Environment Variables
Add these to your Function App settings:

- `DATAVERSE_URL`: Your Dataverse environment URL
- `DATAVERSE_CLIENT_ID`: Service principal client ID
- `DATAVERSE_CLIENT_SECRET`: Service principal secret
- `DATAVERSE_TENANT_ID`: Azure AD tenant ID

### Dataverse Integration
**Note:** The `UpdateOrderStatusActivity` function is provided as a template for Dataverse integration and is not included in the default codebase.

To implement actual Dataverse updates, modify the `UpdateOrderStatusActivity` function:

```python
import requests
from azure.identity import ClientSecretCredential

def update_order_status(input_data: dict):
    # Get credentials from environment
    tenant_id = os.environ["DATAVERSE_TENANT_ID"]
    client_id = os.environ["DATAVERSE_CLIENT_ID"]
    client_secret = os.environ["DATAVERSE_CLIENT_SECRET"]
    dataverse_url = os.environ["DATAVERSE_URL"]
    
    # Authenticate
    credential = ClientSecretCredential(tenant_id, client_id, client_secret)
    token = credential.get_token("https://your-org.crm.dynamics.com/.default")
    
    # Update record
    headers = {
        "Authorization": f"Bearer {token.token}",
        "Content-Type": "application/json"
    }
    
    update_data = {
        "your_status_field": input_data.get('NewStatus'),
        "your_approval_field": input_data.get('ApprovalResult')
    }
    
    response = requests.patch(
        f"{dataverse_url}/api/data/v9.2/your_table_name({input_data['OrderID']})",
        json=update_data,
        headers=headers
    )
    
    return f"Status updated: {response.status_code}"
```

## Monitoring and Logging

### Application Insights
The function automatically logs to Application Insights when deployed to Azure. Key metrics to monitor:

- Function execution count
- Success/failure rates
- Execution duration
- Custom events for approval decisions

### Log Queries (KQL)
```kql
// Function execution summary
requests
| where name contains "StartPurchaseOrderWorkflow"
| summarize count() by resultCode, bin(timestamp, 1h)

// Approval decisions
traces
| where message contains "approval"
| project timestamp, message, severityLevel
```

## Troubleshooting

### Common Issues

1. **Function not starting locally**
   - Ensure Azure Functions Core Tools are installed
   - Check Python version compatibility
   - Verify all dependencies are installed

2. **Power Automate connection fails**
   - Check function URL and authentication
   - Verify JSON payload format
   - Check function app CORS settings

3. **Dataverse updates failing**
   - Verify service principal permissions
   - Check environment variables
   - Validate Dataverse API endpoints

### Debug Mode
Enable debug logging by adding to `host.json`:
```json
{
  "logging": {
    "logLevel": {
      "default": "Debug"
    }
  }
}
```

## Security Considerations

1. **Authentication:** Implement function-level authentication for production
2. **CORS:** Configure appropriate CORS settings
3. **Secrets:** Use Azure Key Vault for sensitive configuration
4. **Network:** Consider VNet integration for enhanced security

## Customization

### Adding New Approval Rules
Modify the `ApproveOrderActivity` function to add custom business logic:

```python
def approve_order(input_data: dict):
    # Custom approval logic
    department = input_data.get("Department")
    amount = input_data.get("Amount", 0)
    
    if department == "IT" and amount > 5000:
        return "Requires IT Manager Approval"
    elif department == "Marketing" and amount > 2000:
        return "Requires Marketing Director Approval"
    
    # Default logic...
```

### Adding New Activity Functions
```python
@app.function_name(name="NotifyApproverActivity")
@app.activity_trigger(input_name="input_data")
def notify_approver(input_data: dict):
    # Send notification to approver
    # Implementation here
    return "Notification sent"
```

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review Azure Functions documentation
3. Check Power Automate connector documentation
4. Review Dataverse API documentation

## Version History

- **v1.0:** Initial implementation with basic approval workflow
- **v1.1:** Added comprehensive error handling and logging
- **v1.2:** Enhanced Power Automate integration
