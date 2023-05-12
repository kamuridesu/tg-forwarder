"""Parses the messages to check for the following:
- Public chat messages
- Private chat messages
- Private chat links"""


async def get_group_hash(message: str) -> dict:
    params = {"hash": message.split("/")[-1], "private": False}
    if "https://t.me/+" in message:
        params["hash"] = message
        params["private"] = True
    elif "https://t.me/joinchat/" in message:
        params["hash"] = message
        params["private"] = True
    return params


async def parse_message(message: str) -> dict:
    return_dict = {"type": "unknown"}
    origin: str = ""
    target: str = ""
    splitted_message = message.split(" ")
    if len(splitted_message) < 2:
        return_dict["type"] = "error"
        return_dict[
            "message"
        ] = "Error! I need the origin and target chats!\n\nEx: https://t.me/origin https://t.me/target"
    else:
        origin = splitted_message[0]
        target = splitted_message[1]
        origin_data = await get_group_hash(origin)
        target_data = await get_group_hash(target)
        return_dict["type"] = "forward"
        return_dict["origin"] = origin_data
        return_dict["target"] = target_data
    return return_dict
