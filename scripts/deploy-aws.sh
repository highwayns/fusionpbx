#!/bin/bash
#
# FusionPBX AWS Deployment Script
#
# Usage: ./deploy-aws.sh [dev|staging|prod] [create|update|delete]
#
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENV_NAME="${1:-dev}"
ACTION="${2:-create}"
AWS_REGION="${AWS_REGION:-ap-northeast-1}"
PROJECT_NAME="fusionpbx"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CFN_DIR="$PROJECT_ROOT/cloudformation"

# Stack names
NETWORK_STACK="${ENV_NAME}-${PROJECT_NAME}-network"
COMPUTE_STACK="${ENV_NAME}-${PROJECT_NAME}-compute"

# Instance types by environment
declare -A INSTANCE_TYPES=(
  ["dev"]="t3.small"
  ["staging"]="t3.medium"
  ["prod"]="t3.large"
)

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check prerequisites
check_prerequisites() {
  log_info "Checking prerequisites..."

  # Check AWS CLI
  if ! command -v aws &> /dev/null; then
    log_error "AWS CLI is not installed. Please install it first."
    exit 1
  fi

  # Check AWS credentials
  if ! aws sts get-caller-identity &> /dev/null; then
    log_error "AWS credentials not configured. Run 'aws configure' first."
    exit 1
  fi

  log_success "Prerequisites check passed"

  # Show current AWS identity
  ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
  USER_ARN=$(aws sts get-caller-identity --query Arn --output text)
  log_info "AWS Account: $ACCOUNT_ID"
  log_info "AWS User: $USER_ARN"
}

# Create or check EC2 key pair
ensure_key_pair() {
  KEY_PAIR_NAME="${ENV_NAME}-${PROJECT_NAME}-key"
  KEY_FILE="$PROJECT_ROOT/keys/${KEY_PAIR_NAME}.pem"

  log_info "Checking EC2 key pair: $KEY_PAIR_NAME"

  if aws ec2 describe-key-pairs --key-names "$KEY_PAIR_NAME" --region "$AWS_REGION" &> /dev/null; then
    log_info "Key pair '$KEY_PAIR_NAME' already exists"
    if [ ! -f "$KEY_FILE" ]; then
      log_warn "Key file not found locally. You may need to use existing key."
    fi
  else
    log_info "Creating new key pair: $KEY_PAIR_NAME"
    mkdir -p "$PROJECT_ROOT/keys"
    aws ec2 create-key-pair \
      --key-name "$KEY_PAIR_NAME" \
      --region "$AWS_REGION" \
      --query 'KeyMaterial' \
      --output text > "$KEY_FILE"
    chmod 400 "$KEY_FILE"
    log_success "Key pair created and saved to: $KEY_FILE"
    log_warn "IMPORTANT: Back up this key file securely!"
  fi
}

# Deploy network stack
deploy_network() {
  log_info "Deploying network stack: $NETWORK_STACK"

  local stack_action="create-stack"
  if aws cloudformation describe-stacks --stack-name "$NETWORK_STACK" --region "$AWS_REGION" &> /dev/null; then
    stack_action="update-stack"
    log_info "Stack exists, updating..."
  fi

  aws cloudformation $stack_action \
    --stack-name "$NETWORK_STACK" \
    --template-body "file://$CFN_DIR/network.yaml" \
    --parameters "file://$CFN_DIR/parameters/${ENV_NAME}.json" \
    --region "$AWS_REGION" \
    --capabilities CAPABILITY_NAMED_IAM \
    2>&1 || {
      if [[ $? -eq 255 && "$stack_action" == "update-stack" ]]; then
        log_info "No updates needed for network stack"
        return 0
      fi
      return 1
    }

  log_info "Waiting for network stack to complete..."
  aws cloudformation wait stack-${stack_action//-stack/}-complete \
    --stack-name "$NETWORK_STACK" \
    --region "$AWS_REGION"

  log_success "Network stack deployed successfully"
}

# Get network stack outputs
get_network_outputs() {
  log_info "Retrieving network stack outputs..."

  VPC_ID=$(aws cloudformation describe-stacks \
    --stack-name "$NETWORK_STACK" \
    --region "$AWS_REGION" \
    --query "Stacks[0].Outputs[?OutputKey=='VpcId'].OutputValue" \
    --output text)

  SUBNET_ID=$(aws cloudformation describe-stacks \
    --stack-name "$NETWORK_STACK" \
    --region "$AWS_REGION" \
    --query "Stacks[0].Outputs[?OutputKey=='PublicSubnetId'].OutputValue" \
    --output text)

  SG_ID=$(aws cloudformation describe-stacks \
    --stack-name "$NETWORK_STACK" \
    --region "$AWS_REGION" \
    --query "Stacks[0].Outputs[?OutputKey=='SecurityGroupId'].OutputValue" \
    --output text)

  log_info "VPC ID: $VPC_ID"
  log_info "Subnet ID: $SUBNET_ID"
  log_info "Security Group ID: $SG_ID"
}

# Deploy compute stack
deploy_compute() {
  log_info "Deploying compute stack: $COMPUTE_STACK"

  get_network_outputs

  local instance_type="${INSTANCE_TYPES[$ENV_NAME]}"
  KEY_PAIR_NAME="${ENV_NAME}-${PROJECT_NAME}-key"

  local stack_action="create-stack"
  if aws cloudformation describe-stacks --stack-name "$COMPUTE_STACK" --region "$AWS_REGION" &> /dev/null; then
    stack_action="update-stack"
    log_info "Stack exists, updating..."
  fi

  aws cloudformation $stack_action \
    --stack-name "$COMPUTE_STACK" \
    --template-body "file://$CFN_DIR/compute.yaml" \
    --parameters \
      ParameterKey=EnvironmentName,ParameterValue="$ENV_NAME" \
      ParameterKey=InstanceType,ParameterValue="$instance_type" \
      ParameterKey=KeyPairName,ParameterValue="$KEY_PAIR_NAME" \
      ParameterKey=VpcId,ParameterValue="$VPC_ID" \
      ParameterKey=SubnetId,ParameterValue="$SUBNET_ID" \
      ParameterKey=SecurityGroupId,ParameterValue="$SG_ID" \
    --region "$AWS_REGION" \
    --capabilities CAPABILITY_NAMED_IAM \
    2>&1 || {
      if [[ $? -eq 255 && "$stack_action" == "update-stack" ]]; then
        log_info "No updates needed for compute stack"
        return 0
      fi
      return 1
    }

  log_info "Waiting for compute stack to complete (this may take several minutes)..."
  aws cloudformation wait stack-${stack_action//-stack/}-complete \
    --stack-name "$COMPUTE_STACK" \
    --region "$AWS_REGION"

  log_success "Compute stack deployed successfully"
}

# Get compute stack outputs
get_compute_outputs() {
  log_info "Retrieving compute stack outputs..."

  INSTANCE_ID=$(aws cloudformation describe-stacks \
    --stack-name "$COMPUTE_STACK" \
    --region "$AWS_REGION" \
    --query "Stacks[0].Outputs[?OutputKey=='InstanceId'].OutputValue" \
    --output text)

  PUBLIC_IP=$(aws cloudformation describe-stacks \
    --stack-name "$COMPUTE_STACK" \
    --region "$AWS_REGION" \
    --query "Stacks[0].Outputs[?OutputKey=='PublicIP'].OutputValue" \
    --output text)

  log_info "Instance ID: $INSTANCE_ID"
  log_info "Public IP: $PUBLIC_IP"
}

# Deploy FusionPBX application
deploy_application() {
  get_compute_outputs

  KEY_PAIR_NAME="${ENV_NAME}-${PROJECT_NAME}-key"
  KEY_FILE="$PROJECT_ROOT/keys/${KEY_PAIR_NAME}.pem"

  log_info "Deploying FusionPBX application to $PUBLIC_IP"

  # Wait for SSH to be available
  log_info "Waiting for SSH to be available..."
  local max_attempts=30
  local attempt=0
  while [ $attempt -lt $max_attempts ]; do
    if ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -i "$KEY_FILE" ec2-user@"$PUBLIC_IP" "echo 'SSH ready'" &> /dev/null; then
      break
    fi
    attempt=$((attempt + 1))
    sleep 10
  done

  if [ $attempt -eq $max_attempts ]; then
    log_error "SSH connection timed out"
    exit 1
  fi

  log_success "SSH connection established"

  # Create .env file for deployment
  log_info "Creating deployment environment file..."
  cat > "$PROJECT_ROOT/.env.deploy" << EOF
# Environment
ENV_NAME=$ENV_NAME
AWS_REGION=$AWS_REGION

# External IPs for NAT traversal
EXTERNAL_SIP_IP=$PUBLIC_IP
EXTERNAL_RTP_IP=$PUBLIC_IP

# Database
FUSIONPBX_DB_USER=fusionpbx
FUSIONPBX_DB_PASSWORD=$(openssl rand -base64 24 | tr -d '=/+')
FUSIONPBX_DB_NAME=fusionpbx
FUSIONPBX_DOMAIN=$PUBLIC_IP

# FreeSWITCH
ESL_PASSWORD=$(openssl rand -base64 16 | tr -d '=/+')

# voice-gateway (leave empty to use IAM role)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

# SignalWire PAT (required for FreeSWITCH packages)
SIGNALWIRE_PAT=${SIGNALWIRE_PAT:-}
EOF

  # Transfer project files
  log_info "Transferring project files..."
  rsync -avz --progress \
    -e "ssh -o StrictHostKeyChecking=no -i $KEY_FILE" \
    --exclude '.git' \
    --exclude 'keys' \
    --exclude 'cloudformation' \
    --exclude 'scripts' \
    --exclude '.env.deploy' \
    "$PROJECT_ROOT/" ec2-user@"$PUBLIC_IP":/opt/fusionpbx/

  # Transfer .env file
  scp -o StrictHostKeyChecking=no -i "$KEY_FILE" \
    "$PROJECT_ROOT/.env.deploy" ec2-user@"$PUBLIC_IP":/opt/fusionpbx/.env

  # Start Docker Compose
  log_info "Starting Docker Compose..."
  ssh -o StrictHostKeyChecking=no -i "$KEY_FILE" ec2-user@"$PUBLIC_IP" << 'REMOTE_SCRIPT'
    cd /opt/fusionpbx

    # Pull and start containers
    sudo docker compose pull
    sudo docker compose up -d

    # Wait for services to start
    sleep 30

    # Check container status
    sudo docker compose ps
REMOTE_SCRIPT

  log_success "FusionPBX application deployed!"
}

# Show deployment summary
show_summary() {
  get_compute_outputs

  echo ""
  echo "============================================"
  echo -e "${GREEN}FusionPBX Deployment Summary${NC}"
  echo "============================================"
  echo ""
  echo "Environment: $ENV_NAME"
  echo "Region: $AWS_REGION"
  echo ""
  echo "Instance ID: $INSTANCE_ID"
  echo "Public IP: $PUBLIC_IP"
  echo ""
  echo "URLs:"
  echo "  FusionPBX Web GUI: http://$PUBLIC_IP:8081"
  echo "  HTTPS (self-signed): https://$PUBLIC_IP:8443"
  echo ""
  echo "VoIP Endpoints:"
  echo "  SIP: sip:$PUBLIC_IP:5060"
  echo "  SIP External: sip:$PUBLIC_IP:5080"
  echo ""
  echo "SSH Access:"
  echo "  ssh -i keys/${ENV_NAME}-${PROJECT_NAME}-key.pem ec2-user@$PUBLIC_IP"
  echo ""
  echo "Next Steps:"
  echo "  1. Access FusionPBX at http://$PUBLIC_IP:8081"
  echo "  2. Complete the installation wizard"
  echo "  3. Configure SIP trunks and extensions"
  echo ""
  echo "============================================"
}

# Delete stacks
delete_stacks() {
  log_warn "Deleting FusionPBX stacks..."

  # Delete compute stack first
  if aws cloudformation describe-stacks --stack-name "$COMPUTE_STACK" --region "$AWS_REGION" &> /dev/null; then
    log_info "Deleting compute stack: $COMPUTE_STACK"
    aws cloudformation delete-stack --stack-name "$COMPUTE_STACK" --region "$AWS_REGION"
    aws cloudformation wait stack-delete-complete --stack-name "$COMPUTE_STACK" --region "$AWS_REGION"
    log_success "Compute stack deleted"
  fi

  # Delete network stack
  if aws cloudformation describe-stacks --stack-name "$NETWORK_STACK" --region "$AWS_REGION" &> /dev/null; then
    log_info "Deleting network stack: $NETWORK_STACK"
    aws cloudformation delete-stack --stack-name "$NETWORK_STACK" --region "$AWS_REGION"
    aws cloudformation wait stack-delete-complete --stack-name "$NETWORK_STACK" --region "$AWS_REGION"
    log_success "Network stack deleted"
  fi

  log_success "All stacks deleted"
}

# Main execution
main() {
  echo ""
  echo "============================================"
  echo "FusionPBX AWS Deployment"
  echo "============================================"
  echo "Environment: $ENV_NAME"
  echo "Action: $ACTION"
  echo "Region: $AWS_REGION"
  echo "============================================"
  echo ""

  case "$ACTION" in
    create|update)
      check_prerequisites
      ensure_key_pair
      deploy_network
      deploy_compute
      deploy_application
      show_summary
      ;;
    delete)
      check_prerequisites
      delete_stacks
      ;;
    status)
      check_prerequisites
      show_summary
      ;;
    *)
      echo "Usage: $0 [dev|staging|prod] [create|update|delete|status]"
      exit 1
      ;;
  esac
}

main "$@"
