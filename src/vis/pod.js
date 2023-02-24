const getLinks = async (pod_url, owner_key, database_key, external_id) => {
    const response = await fetch(`${pod_url}/v4/${owner_key}/search`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            "auth": {
                "type": "ClientAuth",
                "databaseKey": database_key
            },
            "payload": {
                "externalId": external_id,
                "type": "LinkedInAccount",
                "deleted": false,
                "[[edges]]": {},
                "~[[edges]]": {}
            }
        }),
    });

    const podData = await response.json();

    return podData[0];
};