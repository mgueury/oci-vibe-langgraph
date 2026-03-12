#!/usr/bin/env bash
export SRC_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
export ROOT_DIR=${SRC_DIR%/*}
cd $ROOT_DIR

. ./starter.sh env

# Upload Sample Files
sleep 5
echo "https://${APIGW_HOSTNAME}/${TF_VAR_prefix}/index.html" > src/sample_files/website.crawler
oci os object bulk-upload -ns $OBJECT_STORAGE_NAMESPACE -bn ${TF_VAR_prefix}-public-bucket --src-dir src/sample_files --overwrite --content-type auto

# AGENT TOOLS
## RAG-TOOL
title "Creating RAG-TOOL"
oci generative-ai-agent tool create-tool-rag-tool-config \
  --agent-id $TF_VAR_agent_ocid \
  --compartment-id $TF_VAR_compartment_ocid \
  --display-name rag-tool \
  --description "Use for generic questions that other tools can not answer" \
  --tool-config-knowledge-base-configs "[{
    \"knowledgeBaseId\": \"${TF_VAR_agent_kb_ocid}\"
  }]" \
  --wait-for-state SUCCEEDED --wait-for-state FAILED


title "INSTALLATION DONE"
echo
# echo "(experimental) Cohere with Tools and GenAI Agent:"
# echo "http://${BASTION_IP}:8081/"
# echo "-----------------------------------------------------------------------"

echo "URLs" > $FILE_DONE
append_done "-----------------------------------------------------------------------"
append_done "APEX login:"
append_done
append_done "APEX Workspace"
append_done "${ORDS_EXTERNAL_URL}/_/landing"
append_done "  Workspace: APEX_APP"
append_done "  User: APEX_APP"
append_done "  Password: $TF_VAR_db_password"
append_done
append_done "APEX APP"
append_done "${ORDS_EXTERNAL_URL}/r/apex_app/ai_agent_rag/"
append_done "  User: APEX_APP / $TF_VAR_db_password"
append_done 
append_done "-----------------------------------------------------------------------"
append_done "Streamlit:"
append_done "http://${NLB_IP}:8080/"
append_done
append_done "-----------------------------------------------------------------------"
append_done "LangGraph Agent Chat:"
append_done "${BASE_URL}/chat.html"
append_done
if [ "$TF_VAR_openid" == "true" ]; then
    append_done "-----------------------------------------------------------------------"
    append_done "LangGraph OpenID Chat:"
    append_done "https://${APIGW_HOSTNAME}/openid/chat.html"
    append_done
fi
if [ "$TF_VAR_kubernetes" == "true" ]; then
    append_done "-----------------------------------------------------------------------"
    append_done "Kubernetes Chat: http://${TF_VAR_ingress_ip}/oke/chat.html"
    append_done
fi
