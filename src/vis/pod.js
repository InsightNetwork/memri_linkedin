export const getOwnerProfile = async (podUrl, ownerKey, databaseKey, includeLinks) => {
    const payload = {
        isMe: true,
        type: "LinkedInAccount",
        deleted: false,
    };

    if (includeLinks) {
        payload["[[edges]]"] = {};
        payload["~[[edges]]"] = {};
    }

    const response = await fetch(`${podUrl}/v4/${ownerKey}/search`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            auth: {
                type: "ClientAuth",
                databaseKey,
            },
            payload,
        }),
    });

    const podData = await response.json();

    return podData[0];
};

export const getOwnerGraph = async (podUrl, ownerKey, databaseKey) => {
    let nodes = [];
    let links = [];

    const ownerData = await getOwnerProfile(podUrl, ownerKey, databaseKey, true);

    if (ownerData) {
        const edges = ownerData["[[edges]]"] || [];
        const owner = { ...ownerData };
        delete owner["[[edges]]"];
        delete owner["~[[edges]]"];

        nodes = [
            owner,
            ...edges.map(v => v._item),
        ];

        links = edges.map(v => ({
            source: owner.id,
            target: v._item.id,
            type: v._edge,
        }));
    }

    return {
        links,
        nodes,
    }
};
