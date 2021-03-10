from pyrogram import Client, filters
import asyncio
from datetime import datetime
from ...noxx import Noxx
from ..constants import HANDLING_KEY, TG_MAX_SELECT_LEN


async def fast_purge(app,message,chat_id):
    message_ids = []
    start_time = datetime.now()
    purge_start_message = message.reply_to_message.message_id
    purge_end_message = message.message_id
    message_ids = []
    for message_id in range(purge_start_message,purge_end_message):
        message_ids.append(message_id)
        if len(message_ids) == TG_MAX_SELECT_LEN:
            await app.delete_messages(
                chat_id=chat_id,
                message_ids=message_ids,
                revoke=False
            )
            message_ids = []
    if len(message_ids) > 0:
        await app.delete_messages(
            chat_id=chat_id,
            message_ids=message_ids,
            revoke=False
        )
    end_time = datetime.now()
    time_taken = (end_time - start_time).microseconds / 1000
    await message.edit(f"`Purge completed in {time_taken}ms.\nMessage will autodelete in 2s`")
    await asyncio.sleep(2)
    await message.delete()

async def slow_purge(app,message,chat_id):
    message_ids = []
    start_time = datetime.now()
    async for i in app.iter_history(chat_id, offset=1):
        if(message.reply_to_message.message_id == i.message_id):
            message_ids.append(i.message_id)
            break
        message_ids.append(i.message_id)
        if len(message_ids) == TG_MAX_SELECT_LEN:
                await app.delete_messages(
                    chat_id=chat_id,
                    message_ids=message_ids,
                    revoke=False
                )
                message_ids = []
    if len(message_ids) > 0:
        await app.delete_messages(
            chat_id=chat_id,
            message_ids=message_ids,
            revoke=False
        )
    end_time = datetime.now()
    time_taken = (end_time - start_time).microseconds / 1000
    await message.edit(f"`Purge completed in {time_taken}ms.\nMessage will autodelete in 5s`")
    await asyncio.sleep(2)
    await message.delete()


@Noxx.on_message(filters.me & filters.command("purge", HANDLING_KEY))
async def purge(app: Noxx, message):
    await message.edit("`Purging`")

    can_delete = True

    chat_id = message.chat.id
    user_id = message.from_user.id
    

    #If the user cannot delete message then skip it :)
    if message.chat.type in ["supergroup", "channel", "group"]:
        check_status = await app.get_chat_member(
            chat_id=chat_id,
            user_id=user_id
        )
        if (check_status.can_delete_messages == None):
            can_delete=False

    if(not can_delete):
        await message.edit("You can't delete messages in this group")
        await asyncio.sleep(2)
        await message.delete()
        return 

    if message.reply_to_message:
        if message.chat.type in ["supergroup", "channel"]:
            await fast_purge(app,message,chat_id)
        else:
            await slow_purge(app,message,chat_id)
    else:
        await message.edit(f"`Reply to a message to delete`")
        await asyncio.sleep(2)
        await message.delete()

