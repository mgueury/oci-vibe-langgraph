#!/usr/bin/env bash
export SRC_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
export ROOT_DIR=${SRC_DIR%/*}
cd $ROOT_DIR

. ./starter.sh env

title "INSTALLATION DONE"
echo

echo "URLs" > $FILE_DONE
append_done "-----------------------------------------------------------------------"
append_done "LangGraph Agent Chat:"
append_done "${BASE_URL}index.html"
append_done
if [ "$TF_VAR_openid" == "true" ]; then
    append_done "-----------------------------------------------------------------------"
    append_done "LangGraph OpenID Chat:"
    append_done "https://${APIGW_HOSTNAME}/openid/index.html"
    append_done
fi
if [ "$TF_VAR_kubernetes" == "true" ]; then
    append_done "-----------------------------------------------------------------------"
    append_done "Kubernetes Chat: http://${TF_VAR_ingress_ip}/oke/index.html"
    append_done
fi
