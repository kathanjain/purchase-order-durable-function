# Purchase Order Durable Function

This project implements an automated Purchase Order (PO) approval workflow using Azure Durable Functions in Python. It demonstrates how to orchestrate multi-step business processes, such as validating and approving purchase orders, with robust state management and error handling.

## Features
- HTTP-triggered workflow initiation
- Validation and approval logic based on PO amount
- Health check endpoint
- Automated local testing script
- Ready for Power Automate integration

## Project Structure
```
DurablePOApproval/
│
├── function_app.py         # Main Azure Functions app with all triggers and activities
├── test_po_workflow.py     # Python script for automated endpoint testing
├── local.settings.json     # Local settings for Azure Functions runtime
├── SETUP_GUIDE.md          # Detailed setup and usage guide
├── LICENSE                 # MIT License
└─�� README.md               # Project overview (this file)
```

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Azure Functions Core Tools v4
- [Azurite](https://docs.microsoft.com/en-us/azure/storage/common/storage-use-azurite) (for local storage emulation)

### Local Setup
1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Start Azurite:
   ```sh
   azurite
   ```
3. Start the function app:
   ```sh
   func start
   ```
4. Run tests:
   ```sh
   python test_po_workflow.py
   ```

### Endpoints
- **Start Workflow:** `POST /api/start-po-workflow`
- **Health Check:** `GET /api/health`

## Power Automate Integration
Trigger the workflow from Power Automate using an HTTP action. See `SETUP_GUIDE.md` for details.

## License
MIT License. See [LICENSE](LICENSE) for details.
