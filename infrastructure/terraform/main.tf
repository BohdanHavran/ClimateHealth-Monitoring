# Infrastructure scaffold: this configuration creates billable resources when applied.
# It has not been applied. Services, OS hardening and database are separate work.
resource "digitalocean_vpc" "network" {
  name     = "${var.project}-${var.environment}-vpc"
  region   = var.region
  ip_range = var.vpc_cidr
}

resource "digitalocean_droplet" "application" {
  name       = "${var.project}-${var.environment}-application"
  region     = var.region
  size       = var.application_size
  image      = var.image
  vpc_uuid   = digitalocean_vpc.network.id
  ssh_keys   = var.ssh_key_fingerprints
  monitoring = true
  backups    = var.enable_weekly_backups

  dynamic "backup_policy" {
    for_each = var.enable_weekly_backups ? [1] : []
    content {
      plan    = "weekly"
      weekday = "SUN"
      hour    = 4
    }
  }
}

resource "digitalocean_droplet" "ml" {
  name       = "${var.project}-${var.environment}-ml"
  region     = var.region
  size       = var.ml_size
  image      = var.image
  vpc_uuid   = digitalocean_vpc.network.id
  ssh_keys   = var.ssh_key_fingerprints
  monitoring = true
  backups    = var.enable_weekly_backups

  dynamic "backup_policy" {
    for_each = var.enable_weekly_backups ? [1] : []
    content {
      plan    = "weekly"
      weekday = "SUN"
      hour    = 4
    }
  }
}

resource "digitalocean_firewall" "application" {
  name        = "${var.project}-${var.environment}-application"
  droplet_ids = [digitalocean_droplet.application.id]

  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = var.admin_cidrs
  }
  # Public reverse proxy must enforce HTTPS; 80 is necessary for redirect/ACME.
  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0"]
  }
  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0"]
  }
  # Egress for HTTPS dependencies and private ML traffic; narrow after observation.
  outbound_rule {
    protocol              = "tcp"
    port_range            = "443"
    destination_addresses = ["0.0.0.0/0"]
  }
  outbound_rule {
    protocol                = "tcp"
    port_range              = tostring(var.ml_port)
    destination_droplet_ids = [digitalocean_droplet.ml.id]
  }
  outbound_rule {
    protocol              = "udp"
    port_range            = "53"
    destination_addresses = ["0.0.0.0/0"]
  }
  outbound_rule {
    protocol              = "tcp"
    port_range            = "53"
    destination_addresses = ["0.0.0.0/0"]
  }
  outbound_rule {
    protocol              = "udp"
    port_range            = "123"
    destination_addresses = ["0.0.0.0/0"]
  }
}

resource "digitalocean_firewall" "ml" {
  name        = "${var.project}-${var.environment}-ml"
  droplet_ids = [digitalocean_droplet.ml.id]

  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = var.admin_cidrs
  }
  # Source droplet identity narrows network access; it is not authentication.
  inbound_rule {
    protocol           = "tcp"
    port_range         = tostring(var.ml_port)
    source_droplet_ids = [digitalocean_droplet.application.id]
  }
  outbound_rule {
    protocol              = "tcp"
    port_range            = "443"
    destination_addresses = ["0.0.0.0/0"]
  }
  outbound_rule {
    protocol              = "udp"
    port_range            = "53"
    destination_addresses = ["0.0.0.0/0"]
  }
  outbound_rule {
    protocol              = "tcp"
    port_range            = "53"
    destination_addresses = ["0.0.0.0/0"]
  }
  outbound_rule {
    protocol              = "udp"
    port_range            = "123"
    destination_addresses = ["0.0.0.0/0"]
  }
}
