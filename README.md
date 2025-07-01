# AI Codebase Analyzer

## Introduction

The AI Codebase Analyzer is a powerful Streamlit-based application that helps developers analyze, understand, and learn from codebases using AI-powered insights. This tool scans your local code repositories and provides intelligent analysis, learning resources, and interactive chat capabilities to help you ramp up on new projects or better understand existing code.

### Key Features

- **📁 Smart Codebase Scanning**: Recursively scan folders and analyze code files with customizable file extensions
- **🧠 AI-Powered Code Analysis**: Get detailed insights and explanations about your code using Azure OpenAI
- **📚 Learning Resources**: Receive personalized learning recommendations based on your codebase
- **💬 Interactive AI Chat**: Ask questions about your code and get context-aware responses
- **🔍 File Filtering & Navigation**: Easy-to-use interface for browsing and selecting files
- **📊 Progress Tracking**: Real-time progress indicators during folder scanning

## Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- Azure OpenAI access (Azure AI Foundry account required)

## Installation

### 1. Install uv (if not already installed)

```bash
# On Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone or download the project

```bash
git clone <your-repository-url>
cd AI_repo
```

### 3. Install dependencies using uv

```bash
uv sync
```

This will automatically create a virtual environment and install all required dependencies as specified in `pyproject.toml`:

- `ag2[openai]>=0.9.3`
- `autogen>=0.9.3`
- `azure-cli>=2.0.67`
- `azure-identity>=1.23.0`
- `streamlit>=1.46.0`

## Configuration

### Setting up Azure OpenAI Configuration

Before running the application, you need to configure your Azure OpenAI credentials:

#### Step 1: Create Configuration File

- Create a `config.ini` file in the project root directory
- Copy the template from `configDev.ini` file

#### Step 2: Generate Azure AI Foundry Credentials

1. **Go to Azure AI Foundry** (https://ai.azure.com/)
2. **Create or select a project**:
   - Sign in with your Azure account
   - Create a new project or select an existing one
3. **Deploy a model**:
   - Navigate to "Deployments" in your project
   - Click "Deploy model" and select `gpt-4o-mini` (or your preferred model)
   - Note down the deployment name
4. **Get your credentials**:
   - Go to the "Overview" section of your deployment
   - Copy the **Endpoint URL**
   - Copy the **API Key**

#### Step 3: Update config.ini

Open your `config.ini` file and update the following values:

```ini
[azure_openai]
# Azure OpenAI Configuration
endpoint = YOUR_AZURE_OPENAI_ENDPOINT_HERE
deployment_name = gpt-4o-mini
api_version = 2024-02-01
api_key = YOUR_API_KEY_HERE

[settings]
# Application settings
timeout = 30
max_retries = 3
```

**Example:**

```ini
[azure_openai]
endpoint = https://your-resource.openai.azure.com/
deployment_name = gpt-4o-mini
api_version = 2024-02-01
api_key = abcd1234567890efghijklmnopqrstuvwxyz
```

#### Step 4: Secure Your Configuration

- **Important**: Never commit your `config.ini` file with real credentials to version control
- The `config.ini` file should be added to `.gitignore`
- For production, consider using environment variables or Azure Key Vault

### Alternative: Environment Variables

You can also set your API key as an environment variable:

```powershell
# Windows PowerShell
$env:AZURE_OPENAI_API_KEY="your-api-key-here"

# Windows Command Prompt
set AZURE_OPENAI_API_KEY=your-api-key-here
```

The application will prioritize environment variables over the config file for the API key.

## Running the Project

### Start the Streamlit Application

```bash
uv run streamlit run main.py
```

The application will start and be available at `http://localhost:8501` in your web browser.

### Using the Application

1. **Configure Folder Settings**:

   - Enter the full path to your local codebase folder
   - Specify file extensions you want to analyze (e.g., `.py, .js, .ts, .html, .css`)

2. **Scan Your Codebase**:

   - Click "🔍 Scan Folder" to analyze your project
   - The app will create a repository summary and train the AI agent

3. **Explore Your Code**:
   - Use the sidebar to filter and select files
   - Navigate through different tabs for various analysis options:
     - **📄 File Content**: View the raw code
     - **🧠 Code Analysis**: Get AI-powered insights
     - **📚 Learning Resources**: Receive educational recommendations
     - **💬 AI Chat**: Interactive Q&A about your code

## Project Structure

```
AI_repo/
├── main.py                 # Main Streamlit application
├── pyproject.toml          # Project dependencies and metadata
├── README.md              # This file
├── config.ini             # Azure OpenAI configuration (create from configDev.ini)
├── configDev.ini          # Configuration template
├── uv.lock               # Dependency lock file
├── azure_agents/         # AI agent implementation
│   ├── __init__.py
│   └── agents.py         # RampUpAgent class with Azure OpenAI integration
└── utility/              # Utility functions
    ├── __init__.py
    └── create_json.py    # JSON creation utilities
```

## Features in Detail

### Smart File Scanning

- Automatically ignores common non-code directories (`venv`, `__pycache__`, `.git`, etc.)
- Customizable file extension filtering
- Progress tracking during scan operations
- Caches scan results for improved performance

### AI Analysis

- Context-aware code analysis using Azure OpenAI
- Generates detailed explanations and insights
- Provides learning recommendations based on code patterns
- Interactive chat interface for code-related questions

### User Interface

- Clean, intuitive Streamlit interface
- Responsive design with tabbed navigation
- Real-time file filtering and search
- Session state management for seamless user experience

## Troubleshooting

### Common Issues

1. **Configuration File Not Found**:

   - Ensure `config.ini` exists in the project root directory
   - Copy from `configDev.ini` template if needed
   - Verify the file path is correct

2. **Azure OpenAI Authentication Errors**:

   - Verify your API key is correct and active
   - Check that your Azure OpenAI endpoint URL is properly formatted
   - Ensure your Azure subscription has access to the OpenAI service
   - Confirm the deployment name matches your Azure AI Foundry deployment

3. **File Scanning Issues**:

   - Verify the folder path exists and is accessible
   - Check file permissions for the target directory
   - Ensure you have read access to all files in the directory

4. **Performance Issues**:
   - For large codebases, consider filtering to specific file types
   - The initial scan may take time for large repositories
   - Subsequent operations use cached data for better performance

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Add your license information here]

## Support

For issues, questions, or contributions, please [create an issue](link-to-your-repository-issues) in the project repository.
