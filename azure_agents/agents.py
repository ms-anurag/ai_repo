from autogen import AssistantAgent
from azure.identity import AzureCliCredential
import json
import os
import configparser
from pathlib import Path

# Load configuration from config.ini
def load_config():
    config = configparser.ConfigParser()
    # Get the path to config.ini (assuming it's in the project root)
    config_path = Path(__file__).parent.parent / "config.ini"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    config.read(config_path)
    return config

# Load configuration
config = load_config()

# Get Azure OpenAI configuration from config.ini
AZURE_OPENAI_ENDPOINT = config.get('azure_openai', 'endpoint')
DEPLOYMENT_NAME = config.get('azure_openai', 'deployment_name')
API_VERSION = config.get('azure_openai', 'api_version')

# Try to get API key from environment variable first, then fall back to config file
API_KEY = os.getenv('AZURE_OPENAI_API_KEY') or config.get('azure_openai', 'api_key')

# Optional: Get Azure CLI credential as fallback
credential = AzureCliCredential()
# Uncomment the line below if you want to use Azure CLI credentials instead
# token = credential.get_token("https://cognitiveservices.azure.com/.default").token

# Define the AI Agent using AutoGen

class RampUpAgent:
    def __init__(self):
        self.config_list = [
                {
                    "model": DEPLOYMENT_NAME,
                    "api_key": API_KEY,  
                    "base_url": f"{AZURE_OPENAI_ENDPOINT}",
                    "api_type": "azure",
                    "api_version": API_VERSION,
                }
            ]
    
    def train_on_repo_summary(self, repo_summary_path):
        """
        Load and process the repo_summary.json file to train the agent on repository context.
        
        Args:
            repo_summary_path (str): Path to the repo_summary.json file
        
        Returns:
            dict: Processed repository summary data
        """
        
        try:
            if not os.path.exists(repo_summary_path):
                raise FileNotFoundError(f"Repository summary file not found: {repo_summary_path}")
            
            with open(repo_summary_path, 'r', encoding='utf-8') as file:
                repo_data = json.load(file)
            
            # Send training content to Azure using AutoGen AssistantAgent
            
            # Create an AssistantAgent with Azure OpenAI configuration
            assistant = AssistantAgent(
                name="ramp_up_assistant",
                llm_config={
                    "config_list": self.config_list,
                }
            )
            
            # Prepare training prompt with repository context
            training_prompt = f"""
            You are being trained on the following repository context:
            
            Repository Structure: {json.dumps(repo_data, indent=2)}
            
            Please acknowledge that you have processed this repository context and are ready to assist with questions about this codebase.
            """
            # Send training content to the assistant
            response = assistant.generate_reply(messages=[{
                "role": "user",
                "content": training_prompt
            }])
            print(f"Training acknowledgment: {response}")
            
            # Store the assistant for later use
            return assistant
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON file: {e}")
            return None

    def analyze_code(self, selected_file, code):
        chatAgent = AssistantAgent(
            name="AI_Agent",
            system_message= "You are an assistant agent that helps developer to understand the given code and explain the flow in briefly.",
            llm_config={
                    "config_list": self.config_list,
                }
        )

        training_prompt = f"""
            Based on the complete repository details I shared earlier, please analyze the following specific file and its content:

            **File:** {selected_file}
            
            **Code Content:**
            ```
            {code}
            ```

            Please provide a comprehensive analysis that includes:
            
            1. **Purpose & Functionality**: What does this code do within the context of the overall repository?
            2. **Code Flow**: Explain the execution flow and key logic steps.
            3. **Dependencies**: How does this file relate to other components in the repository?
            4. **Key Components**: Identify important classes, functions, variables, and their roles
            5. **Potential Issues**: Highlight any code smells, potential bugs, or areas for improvement
            6. **Best Practices**: Comment on code quality and adherence to best security practices
            
            Keep the explanation clear and concise, suitable for a developer who needs to understand this code quickly.
        """

        explanations = chatAgent.generate_reply(
            messages= [{"role": "user", "content": training_prompt}],
        )

        return explanations

    def fetch_learning_resorces(self, selected_file, code):
        chatAgent = AssistantAgent(
            name="AI_Agent",
            system_message= "You are an assistant agent that helps developer to understand the given code explanation and choose important tech topics and suggest hands on tutorails for clear understanding for the concept.",
            llm_config={
                    "config_list": self.config_list,
                }
        )

        training_prompt = f"""
            Based on the complete repository details I shared earlier and the following specific file analysis:

            **File:** {selected_file}
            
            **Code Content:**
            ```
            {code}
            ```

            Please identify the key technical concepts, frameworks, and technologies used in this code and throughout the repository, then provide comprehensive learning resources for each:

            For each identified concept, please provide:
            
            1. **Concept Identification**: List the main technologies, frameworks, patterns, and concepts used
            2. **Learning Priority**: Rank concepts by importance for understanding this codebase (High/Medium/Low)
            3. **Reference Materials**: 
               - Official documentation links
               - Best practice guides
               - API references
            4. **Video Tutorials**: 
               - Beginner-friendly video courses
               - Specific implementation tutorials
               - Conference talks or deep dives
            5. **Hands-on Experience**: 
               - Step-by-step tutorials
               - Code-along projects
               - Interactive coding exercises
               - Sample projects to practice
            6. **Code Examples**: 
               - GitHub repositories with similar implementations
               - Code snippets demonstrating key patterns
               - Working examples to study

            Focus on practical, actionable learning resources that will help a developer quickly understand and work with this specific codebase and its underlying technologies.
            
            Organize the response by concept/technology for easy reference.
        """

        tutorials = chatAgent.generate_reply(
            messages= [{"role": "user", "content": training_prompt}],
        )

        return tutorials
    
    def chat_with_context(self, prompt, selected_file, code):
        chatAgent = AssistantAgent(
            name="AI_Agent",
            system_message= "You are an assistant agent that helps developer to answer there queries. Context of the query is the code and repository details shared earlier.",
            llm_config={
                    "config_list": self.config_list,
                }
        )

        training_prompt = f"""
            Based on the complete repository details I shared earlier, please analyze the following specific file and its content:

            **File:** {selected_file}
            
            **Code Content:**
            ```
            {code}
            ```

            {prompt}
        """

        response = chatAgent.generate_reply(
            messages= [{"role": "user", "content": training_prompt}],
        )

        return response