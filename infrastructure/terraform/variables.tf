variable "project" {
  description = "Назва проєкту для хмарних ресурсів."
  type        = string
  default     = "climate-health"
  validation {
    condition     = can(regex("^[a-z0-9-]{1,30}$", var.project))
    error_message = "project має містити лише малі латинські літери, цифри та дефіс."
  }
}
variable "environment" {
  description = "Ізольоване середовище dev або production."
  type        = string
  validation {
    condition     = contains(["dev", "production"], var.environment)
    error_message = "environment має бути dev або production."
  }
}
variable "region" {
  description = "DigitalOcean region slug, обраний за доступністю."
  type        = string
  default     = "fra1"
}
variable "vpc_cidr" {
  description = "Непересічна приватна CIDR-мережа VPC /16–/24."
  type        = string
  validation {
    condition     = can(cidrnetmask(var.vpc_cidr)) && can(regex("^10\\.", var.vpc_cidr)) && try(tonumber(split("/", var.vpc_cidr)[1]) >= 16 && tonumber(split("/", var.vpc_cidr)[1]) <= 24, false)
    error_message = "Вкажіть мережу 10.0.0.0/8 з префіксом /16–/24."
  }
}
variable "admin_cidrs" {
  description = "Довірені вузькі IPv4 CIDR для SSH; публічний 0.0.0.0/0 заборонено."
  type        = list(string)
  validation {
    condition     = length(var.admin_cidrs) > 0 && alltrue([for cidr in var.admin_cidrs : can(cidrnetmask(cidr)) && can(regex("/(2[4-9]|3[0-2])$", cidr))])
    error_message = "SSH CIDR має бути IPv4 /24–/32 та список не може бути порожнім."
  }
}
variable "ssh_key_fingerprints" {
  description = "Ідентифікатори або fingerprint вже зареєстрованих SSH public keys у DigitalOcean."
  type        = list(string)
  validation {
    condition     = length(var.ssh_key_fingerprints) > 0 && alltrue([for x in var.ssh_key_fingerprints : length(trimspace(x)) > 0])
    error_message = "Вкажіть щонайменше один зареєстрований SSH ключ."
  }
}
variable "application_size" {
  description = "Розмір Application Droplet."
  type        = string
  default     = "s-1vcpu-2gb"
}
variable "ml_size" {
  description = "Розмір CPU Droplet для інференсу; перевірити фактичну RAM моделі."
  type        = string
  default     = "s-1vcpu-2gb"
}
variable "image" {
  description = "Офіційний image slug, який слід перевірити для вибраного регіону."
  type        = string
  default     = "ubuntu-24-04-x64"
}
variable "ml_port" {
  description = "Порт внутрішнього ML API; сервіс має слухати приватну адресу та автентифікувати запити."
  type        = number
  default     = 8001
  validation {
    condition     = var.ml_port >= 1024 && var.ml_port <= 65535 && floor(var.ml_port) == var.ml_port
    error_message = "ml_port має бути цілим числом у діапазоні 1024–65535."
  }
}
variable "enable_weekly_backups" {
  description = "Увімкнути платні щотижневі резервні образи обох Droplets."
  type        = bool
  default     = false
}
