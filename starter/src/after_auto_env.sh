if grep -q 'GENERATIVE AI MODEL' $TARGET_DIR/tf_env.sh; then
    echo "tf_env.sh already modified"
else 
    ## Set env variables needed for env.sh
    append_tf_env "# GENERATIVE AI MODEL"
    oci generative-ai model-collection list-models --compartment-id $TF_VAR_compartment_ocid --all > $TARGET_DIR/genai_models.json 
    export TF_VAR_genai_meta_model=$(jq -r '.data.items[]|select(.vendor=="meta" and (.capabilities|index("CHAT")))|.["display-name"]' $TARGET_DIR/genai_models.json | head -n 1)
    append_tf_env "export TF_VAR_genai_meta_model=\"$TF_VAR_genai_meta_model\""

    export TF_VAR_genai_cohere_model=$(jq -r '.data.items[]|select(.vendor=="cohere" and (.capabilities|index("CHAT")))|.["display-name"]' $TARGET_DIR/genai_models.json | head -n 1)
    append_tf_env "export TF_VAR_genai_cohere_model=\"$TF_VAR_genai_cohere_model\""

    export TF_VAR_genai_embed_model="cohere.embed-multilingual-v3.0"
    # export TF_VAR_genai_embed_model=$(jq -r '.data.items[]|select(.vendor=="cohere" and (.capabilities|index("TEXT_EMBEDDINGS")) and ."time-on-demand-retired"==null)|.["display-name"]' $TARGET_DIR/genai_models.json | head -n 1)
    append_tf_env "export TF_VAR_genai_embed_model=\"$TF_VAR_genai_embed_model\""
    append_tf_env "export TF_VAR_genai_api_key=\"$TF_VAR_genai_api_key\""
    append_tf_env "export TF_VAR_project_ocid=\"$TF_VAR_project_ocid\""

    append_tf_env

    # Self-Signed Certificate for the IP address
    export BASE_URL="https://${BASTION_IP}/"
    append_tf_env "export BASE_URL=\"$BASE_URL\""

    # Kubernetes
    if [ "$TF_VAR_deploy_type" == "kubernetes" ]; then
        append_tf_env "export LANGGRAPH_URL=\"http://langgraph-service:8080\""
        append_tf_env "export MCP_SERVER_URL=\"http://mcp-server-service:2025/mcp\""
    else 
        append_tf_env "export LANGGRAPH_URL=\"http://127.0.0.1:8080\""
        append_tf_env "export MCP_SERVER_URL=\"http://localhost:2025/mcp\""
    fi
    export LANGGRAPH_APIKEY="##TF_VAR_db_password##"
fi
