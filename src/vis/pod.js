export const getOwnerProfile = async (pod_url, owner_key, database_key, include_links) => {
    const payload = {
        "isMe": true,
        "type": "LinkedInAccount",
        "deleted": false,
    };

    if (include_links) {
        payload["[[edges]]"] = {};
        payload["~[[edges]]"] = {};
    }

    const response = await fetch(`${pod_url}/v4/${owner_key}/search`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            auth: {
                type: "ClientAuth",
                databaseKey: database_key
            },
            payload: payload
        }),
    });

    const podData = await response.json();

    return podData[0];
};