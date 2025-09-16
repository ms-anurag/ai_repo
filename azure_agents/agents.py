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

    def fetch_security_flaws(self, selected_file, code):
        """Perform a security review of the provided code file and return structured findings."""
        chatAgent = AssistantAgent(
            name="AI_Security_Reviewer",
            system_message=(
                "You are a seasoned application security engineer performing a focused secure code review. "
                "Only analyze the provided code content (do not invent unseen files). Be precise, actionable, and concise."
            ),
            llm_config={
                "config_list": self.config_list,
            }
        )

        training_prompt = f"""
                    You are a security code reviewer. I will give you a code. Follow these rules when analyzing only the provided code:

                    Identify all relevant security issues and classify each into one of these categories: Authentication, Authorization, Input Validation, Injection (SQL/LDAP/OS), XSS, CSRF, Remote Code Execution (RCE), Insecure Deserialization, Insecure Configuration, Cryptography, Secrets Management, File/Path Traversal, Unsafe File Upload/Download, SSRF, Race Condition/TOCTOU, Denial of Service, Dependency Vulnerabilities, Business Logic, Logging/Errors, Memory Safety, or Other.

                    For each finding provide:

                    Title (short)

                    Category (one of the list above)

                    Severity (Critical / High / Medium / Low) with one-sentence justification

                    Location (file + approximate line numbers or function name). If exact lines aren’t given, give a best guess.

                    Why it’s vulnerable (concise technical explanation)

                    Exploitability (steps an attacker would take; if possible include a short PoC request/ payload)

                    Fix / Remediation: exact, actionable steps. Provide a minimal code patch or diff showing the fix (only the changed lines or a full corrected function if small).

                    Mitigations/defense-in-depth suggestions (config/runtime/hardening).

                    References: CWE number, and 1–2 authoritative references (CWE, OWASP, or docs).

                    If no vulnerabilities of a given category are present, say “No issues found in <category>”.

                    At the end provide a prioritized checklist (top 3-5 fixes to do first) and a single-line summary of overall risk.

                    Explicitly do not change application logic unless required for security; prefer minimal, well-commented fixes.

                    Now review the following file:

                    File: {selected_file}

                    Code:
                    ```
                    {code}
                    ```
                    """

        response = chatAgent.generate_reply(
            messages=[{"role": "user", "content": training_prompt}],
        )

        return response

    def fetch_security_flaws_by_category(self, selected_file, code, overall_findings=None):
        """Category-structured security assessment with one section per category and prioritized wrap-up.

        overall_findings: optional string of previously generated holistic findings to give additional context.
        """
        chatAgent = AssistantAgent(
            name="AI_Security_Category_Reviewer",
            system_message=(
                "You are a senior application security engineer. Output ONLY structured, category-organized findings. "
                "If a category has no issues, write exactly: 'No issues found in <Category>'."
            ),
            llm_config={
                "config_list": self.config_list,
            }
        )

        prompt = f"""
                    Perform a category-focused security review of the single file below.

                    File: {selected_file}

                    Code:
                    ```
                    {code}
                    ```

                    Categories (in this exact order; use headings):
                    1. Injection — SQL/OS Command
                    2. XSS
                    3. CSRF
                    4. Authentication
                    5. Authorization
                    6. Insecure Deserialization
                    7. Cryptography
                    8. Secrets Management
                    9. Insecure Configuration
                    10. File Upload / Path Traversal
                    11. SSRF
                    12. Dependency Vulnerabilities
                    13. Business Logic
                    14. Denial of Service / Rate Limiting
                    15. Memory Safety
                    16. Logging / Errors

                    For each category WITH issues:
                    - Findings (numbered)
                    - Title
                    - Risk: <Severity (Critical/High/Medium/Low)> - <justification>
                    - Location (best-effort line or function)
                    - Root Cause
                    - Exploit Sketch / PoC (payload or steps if applicable)
                    - Remediation (minimal diff or replacement snippet)
                    - References (CWE + 1 authoritative link)

                    If no issues: do not include the category in the output.

                    Finish with:
                    ### Top 5 Remediation Priorities
                    - (ranked list)

                    ### Overall Risk Summary
                    <one line>

                    Do NOT invent code outside this file. Do NOT repeat the full source.
                    """
        if overall_findings:
            prompt += "\n\nContext (previous holistic findings summary provided earlier; do NOT repeat verbatim, only refine):\n" + overall_findings[:6000]

        response = chatAgent.generate_reply(messages=[{"role": "user", "content": prompt}])
        return response

    def compute_security_score(self, selected_file, code, overall_findings, category_findings):
        """Derive an overall security score (0-100) and concise summary based on earlier agent outputs."""
        chatAgent = AssistantAgent(
            name="AI_Security_Scorer",
            system_message=(
                "You are an impartial security risk scoring engine. Produce ONLY a short structured result."
            ),
            llm_config={
                "config_list": self.config_list,
            }
        )

        scoring_prompt = f"""
You will compute a security risk score for a single file based on prior analyses.

File: {selected_file}

Code (reference excerpt – do not re-audit raw code fully, rely on findings):
---
{code[:4000]}
---

Holistic Findings (truncated if long):
---
{overall_findings[:8000]}
---

Category Findings (truncated if long):
---
{category_findings[:8000]}
---

Instructions:
1. Parse severities and counts. Treat Critical=4, High=3, Medium=2, Low=1 for weighting.
2. Consider breadth of categories impacted, exploitability indications, presence of systemic issues (auth gaps, injection, secrets).
3. Output strictly in this JSON-like markdown block:

```json
{{
  "score": <integer 0-100 (100 best)>,
  "risk_level": "Low|Moderate|High|Critical",
  "primary_drivers": ["short phrase", "short phrase"],
  "immediate_actions": ["top fix 1", "top fix 2", "top fix 3"],
  "summary": "single concise sentence"
}}
```

Rules:
- Never exceed one sentence in summary.
- Score bands suggestion: 0-39 Critical, 40-59 High, 60-79 Moderate, 80-100 Low (override if justified).
- Do NOT invent new findings; base only on provided findings.
"""

        response = chatAgent.generate_reply(messages=[{"role": "user", "content": scoring_prompt}])
        return response