This repo provisions a serverless solution that ensures every EC2 instance with an application' tag has a corresponding Alert Policy in New Relic.

## What It Provisions

- IAM role and policies for Lambda execution
- A Lambda function to sync EC2 application tags with New Relic alert policies
- An EventBridge rule for real-time EC2 state change events
- A scheduled EventBridge rule (every 5 minutes) for reconciliation

## Tech stack used

- Terraform for infrastructure  
- AWS Lambda (Python 3.11) for sync logic  
- New Relic NerdGraph API (GraphQL)  
- EventBridge for event-driven + scheduled triggers  

## Repository Structure

lambda/  
app.py                # Lambda handler (event-driven + scheduled sync)  
ec2_client.py        # EC2 helper functions  
newrelic_client.py   # New Relic API client  
requirements.txt     # Python dependencies  

terraform/  
main.tf              # Core infrastructure  
variables.tf         # Input variables  
outputs.tf           # Outputs  
versions.tf          # Provider/version constraints  

scripts/  
build.sh             # Packages Lambda code  

## Infrastructure-as-Code

## Prerequisites

- Install Terraform and AWS CLI  
- Run 'aws configure' to set credentials and region  
- New Relic account with API key  

### Deployment

# Clone the repository
git clone <repo-url>
cd terraform

# Build Lambda package
../scripts/build.sh

# Initialize Terraform
terraform init

# Plan with variables
terraform plan \
  -var="new_relic_api_key=XXX" \
  -var="new_relic_account_id=XXX" \
  -out=tfplan

# Apply the plan
terraform apply tfplan

## How It Works

- When an EC2 instance enters 'running' state:
  - EventBridge triggers Lambda
  - Lambda reads the 'application' tag
  - Creates a matching New Relic alert policy if it does not exist

- Every 5 minutes:
  - Scheduled EventBridge rule triggers Lambda
  - Lambda scans all EC2 instances
  - Ensures all application tags have corresponding policies

## Scheduling

- Real-time trigger: EC2 state change → EventBridge  
- Scheduled sync: 'rate(5 minutes)' 
- Frequency can be adjusted in 'main.tf'

## Monitoring

- Logs are available in CloudWatch Logs:
  '/aws/lambda/nr-policy-sync'
- Logs include:
  - Policy creation events
  - Skipped resources
  - API failures


