# Store the docker image in the Container Registry of LZ_APP Compartment
# Avoid container's name conflict by adding a random prefix
resource "random_string" "container_prefix" {
  length  = 8
  numeric  = false
  special = false
  upper = false
}

# Pre-create the repository in the LZ_APP compartment
resource "oci_artifacts_container_repository" "starter_repo_fn" {
  compartment_id = local.lz_app_cmp_ocid  
  display_name   = "${random_string.container_prefix.result}/fn-java-oracle"
  freeform_tags = local.freeform_tags    
}

locals  {
  local_container_prefix = random_string.container_prefix.result
}