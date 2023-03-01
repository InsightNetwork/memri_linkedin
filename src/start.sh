#!/bin/bash

target_item='{"type":"Person","id":"38583224e56e6d2385d36e05af9caa5e","dateCreated":1623241923508,"dateModified":1623241923508,"dateServerModified":1623241923508,"deleted":false}'
pod_auth_json='{"data":{"nonce":"909382870d9df58935c9924f260fb38276ffe97fbaa76f09","encryptedPermissions":"74136e27e5537e0f594c394cd723eceb"}}'

export POD_VERSION=dev-fd1e8bdd
export POD_TARGET_ITEM="$target_item"
export POD_AUTH_JSON="$pod_auth_json"

docker-compose up