
# Trading Bot CI/CD Deployment Guide

This guide explains how to automatically deploy a Python trading bot to Google Cloud Virtual Machines using Google Cloud Build, Terraform, and gcloud commands.

## Prerequisites

- A Google Cloud project with billing enabled
- Google Cloud SDK installed locally
- Terraform installed locally
- A custom Google Cloud image for your VM
- A GitHub repository with your bot code and configuration

## Step 1: Set Up Google Cloud Build Trigger

1. Go to the [Google Cloud Build Console](https://console.cloud.google.com/cloud-build/triggers).
2. Create a new trigger linked to your GitHub repository.
3. Configure the trigger to build whenever a specific branch is updated (e.g., `bot_01_branch`).
4. Select the `cloudbuild.yaml` configuration file for the build steps.

## Step 2: Terraform Infrastructure Setup

We use **Terraform** to create the virtual machine (VM) with a custom image.

- The `infra/main.tf` file contains the Terraform configuration to create the VM.
- To apply the infrastructure:

```bash
cd infra
terraform init
terraform apply -auto-approve
```

- This creates a Windows VM using the custom image specified in `main.tf`.

## Step 3: Deploy the Bot to the VM

After the VM is created, the bot code is copied to the VM using the following commands:

```bash
gcloud compute scp --recurse ./path/to/bot/* trading-bot-vm:/path/to/deployment --zone=YOUR_ZONE
```

## Step 4: Set Up Python Environment on the VM

Once the code is on the VM, install the necessary Python dependencies and run pre-checks:

```bash
gcloud compute ssh trading-bot-vm --zone=YOUR_ZONE --command "cd /path/to/deployment && pip install -r requirements.txt && python pre_check.py"
```

## Step 5: Run the Bot

Finally, run the bot using:

```bash
gcloud compute ssh trading-bot-vm --zone=YOUR_ZONE --command "cd /path/to/deployment && python main.py"
```

## Cloudbuild.yaml File

The CI/CD process is automated using **Google Cloud Build**. Below is the `cloudbuild.yaml` file used in this deployment:

```yaml
steps:
- name: 'hashicorp/terraform:light'
  entrypoint: 'sh'
  args:
    - '-c'
    - |
      cd infra
      terraform init
      terraform apply -auto-approve

- name: 'gcr.io/cloud-builders/gcloud'
  entrypoint: 'bash'
  args:
    - '-c'
    - |
      echo "Copying bot code to VM"
      gcloud compute scp --recurse ./path/to/bot/* trading-bot-vm:/path/to/deployment --zone=YOUR_ZONE

- name: 'gcr.io/cloud-builders/gcloud'
  entrypoint: 'bash'
  args:
    - '-c'
    - |
      echo "Setting up Python environment on the VM"
      gcloud compute ssh trading-bot-vm --zone=YOUR_ZONE --command "cd /path/to/deployment && pip install -r requirements.txt && python pre_check.py"

- name: 'gcr.io/cloud-builders/gcloud'
  entrypoint: 'bash'
  args:
    - '-c'
    - |
      echo "Starting the trading bot"
      gcloud compute ssh trading-bot-vm --zone=YOUR_ZONE --command "cd /path/to/deployment && python main.py"
```

## Troubleshooting

1. **SSH Access Issues**:
   Ensure the correct SSH keys are installed on the VM and accessible in the Google Cloud Console.

2. **Terraform Errors**:
   If Terraform fails to apply changes, ensure that your custom image path is correct and that you have sufficient permissions to create resources.

## Further Resources

- [Google Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Terraform Google Cloud Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
