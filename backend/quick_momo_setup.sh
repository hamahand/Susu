#!/bin/bash
# Quick MTN MoMo Setup Script

echo "======================================================================"
echo "MTN MoMo Quick Setup for SusuSave"
echo "======================================================================"
echo ""
echo "This will set up MTN MoMo for automated susu transactions."
echo ""
echo "Prerequisites:"
echo "  1. Subscription Key from https://momodeveloper.mtn.com/"
echo "  2. Subscribed to Collection + Disbursement APIs"
echo ""
echo "Press Enter to continue or Ctrl+C to cancel..."
read

# Activate virtual environment
source venv/bin/activate

# Run setup
python setup_mtn_momo.py

# Test setup
echo ""
echo "======================================================================"
echo "Testing your setup..."
echo "======================================================================"
python test_mtn_integration.py

echo ""
echo "======================================================================"
echo "Setup Complete!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "  1. Start backend: python -m app.main"
echo "  2. Start ngrok: ngrok http 8000"
echo "  3. Test payments with your phone number"
echo ""

