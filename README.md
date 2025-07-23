# Purchase Order Durable Function

This project implements an automated Purchase Order (PO) approval workflow using Azure Durable Functions in Python. It demonstrates how to orchestrate multi-step business processes, such as validating and approving purchase orders, with robust state management, error handling, and human-in-the-loop approval.

## Features
- HTTP-triggered workflow initiation
- Validation and approval logic based on PO amount
- Human-in-the-loop approval (waits for user action)
- Status updates and (mock) email notification
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
├── LICENSE                 #, updates the status in the backend, and completes the workflow.

## Power Automate Integration
Trigger the workflow from Power Automate using an HTTP action. See `SETUP_GUIDE.md` for details.

## License
MIT License. See [LICENSE](LICENSE) for details.
