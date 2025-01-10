# Makefile to set up and run the project

.PHONY: install_dependencies set_env start_server start_api test

# Step 1: Clone the GitHub repository
clone_repo:
	@echo "Cloning the GitHub repository..."
	# Add your repo URL below
	git clone git@github.com:PreetamVerma/simple_qa_chatboat.git

# Step 2: Install system dependencies via pip3
install_dependencies:
	@echo "Installing dependencies from requirements.txt..."
	pip3 install -r requirements.txt

# Step 3: Set up environment variables
set_env:
	@echo "Setting up environment variables..."
	cp src/sample.env src/.env

# Step 4: Start the HTTP server (static frontend)
start_server:
	@echo "Starting the HTTP server..."
	cd html/static && python3 -m http.server 8000

# Step 5: Run the REST API backend (User Auth and Interaction)
start_api:
	@echo "Starting the API backend..."
	cd src && unicorn driver:app --reload

# Step 6: Test the system (via Postman or UI)
test:
	@echo "You can now test the system via Postman or UI."

# Default task to install everything and start the server
setup: install_dependencies set_env start_server start_api
	@echo "Setup complete. The system is now ready to use."
