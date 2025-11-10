#!/bin/bash
# Generate FERNET_KEY for Airflow encryption
# Usage: ./scripts/generate-fernet-key.sh

# Check if venv is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Warning: Virtual environment not activated. Activating venv..."
    source venv/bin/activate 2>/dev/null || {
        echo "Error: venv not found. Please activate virtual environment first."
        echo "Run: source venv/bin/activate"
        exit 1
    }
fi

# Check if cryptography is installed
python -c "import cryptography" 2>/dev/null || {
    echo "Installing cryptography package..."
    pip install cryptography
}

# Generate FERNET_KEY
echo "Generating FERNET_KEY..."
FERNET_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

echo ""
echo "FERNET_KEY generated successfully!"
echo ""
echo "Add this to your .env file:"
echo "FERNET_KEY=${FERNET_KEY}"
echo ""

