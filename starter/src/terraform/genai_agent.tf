
# -- Object Storage ---------------------------------------------------------

resource "oci_objectstorage_bucket" "starter_bucket" {
  compartment_id = local.lz_serv_cmp_ocid
  namespace      = local.local_object_storage_namespace
  name           = "${var.prefix}-public-bucket"
  access_type    = "ObjectReadWithoutList"
  object_events_enabled = true

  freeform_tags = local.freeform_tags
}

resource "oci_objectstorage_bucket" "starter_agent_bucket" {
  compartment_id = local.lz_serv_cmp_ocid
  namespace      = local.local_object_storage_namespace
  name           = "${var.prefix}-agent-bucket"
  object_events_enabled = true

  freeform_tags = local.freeform_tags
}

locals {
  local_bucket_url = "https://objectstorage.${var.region}.oraclecloud.com/n/${local.local_object_storage_namespace}/b/${var.prefix}-public-bucket/o/"
}  

# -- Agent ------------------------------------------------------------------

resource "oci_generative_ai_agent_agent" "starter_agent" {
  compartment_id                 = local.lz_serv_cmp_ocid
  display_name                   = "${var.prefix}-agent"
  description                    = "${var.prefix}-agent"
  welcome_message                = "How can I help you ?"
  # Added in after_build.sh
  # knowledge_base_ids = [
  #   oci_generative_ai_agent_knowledge_base.starter_agent_kb.id
  # ]  
  freeform_tags = local.freeform_tags
}

# -- Agent Endpoint ---------------------------------------------------------

resource "oci_generative_ai_agent_agent_endpoint" "starter_agent_endpoint" {
  compartment_id                 = local.lz_serv_cmp_ocid
  agent_id                       = oci_generative_ai_agent_agent.starter_agent.id
  display_name                  = "${var.prefix}-agent-endpoint"
  description                   = "${var.prefix}-agent-endpoint"
  should_enable_citation        = "true"
  should_enable_session         = "true"
  should_enable_trace           = "true"
  content_moderation_config  {
    should_enable_on_input = "false"
    should_enable_on_output = "false"
  }
  session_config              {
    idle_timeout_in_seconds = 3600
  }
  freeform_tags = local.freeform_tags  
}

