#!/usr/bin/env bash

function vault-config {
    if ! sudo snap list vault; then
        sudo snap install vault
    fi
    if ! sudo snap list yq; then
        sudo snap install yq
    fi

    # Set vault token
    vault_initialization_secret=$(juju secrets --format=yaml | yq '. | with_entries(select(.*.label == "vault-initialization")) | keys | .[]')
    VAULT_TOKEN="$(juju show-secret ${vault_initialization_secret} --reveal | yq '.[].content.roottoken')"
    export VAULT_TOKEN

    # Extract the vault CA cert and set the path
    vault_ca_certificate_secret=$(juju secrets --format=yaml | yq '. | with_entries(select(.*.label == "vault-ca-certificate")) | keys | .[]')
    juju show-secret ${vault_ca_certificate_secret} --reveal | yq '.[].content.certificate' > vault_ca.pem
    export VAULT_CAPATH="$PWD/vault_ca.pem"

    # Set the address of vault
    VAULT_ADDR="https://$(juju status vault-k8s --format=yaml | yq '.applications.vault-k8s.address'):8200"
    export VAULT_ADDR
}
