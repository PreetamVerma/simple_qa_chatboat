# Makefile to set up and run the project with venv

.PHONY: install_dependencies set_env start_server start_api test clean venv

# Step 1: Clone the GitHub repository
clone_repo:
	@echo "Cloning the GitHub repository..."
	# Add your repo URL below
	git clone git@github.com:PreetamVerma/simple_qa_chatboat.git

# Step 2: Create a virtual environment (venv)
venv:
	@echo "Creating virtual environment..."
	python3 -m venv venv

# Step 3: Activate the virtual environment and install dependencies
install_dependencies: venv
	@echo "Installing dependencies from requirements.txt..."
	. venv/bin/activate && pip install -r requirements.txt

# Step 4: Set up environment variables
set_env:
	@echo "Setting up environment variables..."
	cp src/sample.env src/.env

# Step 5: Start the HTTP server (static frontend)
start_server:
	@echo "Starting the HTTP server..."
	cd html/static && python3 -m http.server 8000

# Step 6: Run the REST API backend (User Auth and Interaction)
start_api:
	@echo "Starting the API backend..."
	cd src && unicorn driver:app --reload

# Step 7: Test the system (via Postman or UI)
test:
	@echo "You can now test the system via Postman or UI."

# Default task to install everything and start the server
setup: install_dependencies set_env start_server start_api
	@echo "Setup complete. The system is now ready to use."

# Clean up (deactivate venv and remove files if needed)
clean:
	@echo "Cleaning up..."
	rm -rf venv
