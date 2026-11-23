output "application_public_ipv4" {
  description = "Публічна IPv4 адреса вебсервера."
  value       = digitalocean_droplet.application.ipv4_address
}
output "application_private_ipv4" {
  description = "Приватна IPv4 адреса сервера застосунку у VPC."
  value       = digitalocean_droplet.application.ipv4_address_private
}
output "ml_private_ipv4" {
  description = "Приватна IPv4 адреса ML-сервера у VPC."
  value       = digitalocean_droplet.ml.ipv4_address_private
}
output "vpc_id" {
  description = "Ідентифікатор приватної мережі."
  value       = digitalocean_vpc.network.id
}
