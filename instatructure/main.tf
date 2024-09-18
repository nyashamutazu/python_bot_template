provider "google" {
  project = "YOUR_PROJECT_ID"
  region  = "YOUR_REGION"
  zone    = "YOUR_ZONE"
}

resource "google_compute_instance" "trading_bot_vm" {
  name         = "trading-bot-vm"
  machine_type = "n1-standard-1"
  zone         = "YOUR_ZONE"

  boot_disk {
    initialize_params {
      image = "projects/YOUR_PROJECT_ID/global/images/YOUR_CUSTOM_IMAGE"  # Reference your custom image
    }
  }

  network_interface {
    network = "default"
    access_config {}
  }

  metadata_startup_script = <<-EOT
    #!/bin/bash
    echo "Setting up trading bot VM..."
    # This script runs when the VM boots. Add any additional setup commands here.
  EOT
}
