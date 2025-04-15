/* 
import * as db from '$lib/server/database';

export async function load({ params }) {
    return {
        // conversations: await db.getHistory(params.user)
        // Call the utility function that gets user history from userID
        conversation: await db.getHistory("gaming")
    };
}
*/