import os
import asyncio
import logging

import discord
from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", "0"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
MESSAGE_ID = int(os.getenv("MESSAGE_ID", "0"))
ROLE_ID = int(os.getenv("ROLE_ID", "0"))
ACTION = os.getenv("ACTION", "ADD").upper()


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)


def validate_config():
    if not TOKEN:
        raise ValueError("DISCORD_TOKEN is missing")

    if not GUILD_ID:
        raise ValueError("GUILD_ID is missing")

    if not CHANNEL_ID:
        raise ValueError("CHANNEL_ID is missing")

    if not MESSAGE_ID:
        raise ValueError("MESSAGE_ID is missing")

    if not ROLE_ID:
        raise ValueError("ROLE_ID is missing")

    if ACTION not in ("ADD", "REMOVE"):
        raise ValueError("ACTION must be ADD or REMOVE")


async def get_reaction_users(message):
    users = {}

    for reaction in message.reactions:
        async for user in reaction.users():
            if not user.bot:
                users[user.id] = user

    return list(users.values())


async def process_message(client):
    guild = client.get_guild(GUILD_ID)

    if guild is None:
        raise ValueError("Server not found. Check GUILD_ID.")

    channel = guild.get_channel(CHANNEL_ID)

    if channel is None:
        channel = await client.fetch_channel(CHANNEL_ID)

    message = await channel.fetch_message(MESSAGE_ID)

    role = guild.get_role(ROLE_ID)

    if role is None:
        raise ValueError("Role not found. Check ROLE_ID.")

    logging.info("Message found: %s", message.id)
    logging.info("Action: %s", ACTION)

    users = await get_reaction_users(message)

    logging.info("Found %d unique reacting users.", len(users))

    for user in users:
        try:
            member = guild.get_member(user.id)

            if member is None:
                member = await guild.fetch_member(user.id)

            if ACTION == "ADD":
                if role in member.roles:
                    logging.info(
                        "SKIPPED - %s already has %s",
                        member,
                        role.name
                    )
                    continue

                await member.add_roles(
                    role,
                    reason="Reaction role manager"
                )

                logging.info(
                    "ADDED - %s -> %s",
                    member,
                    role.name
                )

            else:
                if role not in member.roles:
                    logging.info(
                        "SKIPPED - %s does not have %s",
                        member,
                        role.name
                    )
                    continue

                await member.remove_roles(
                    role,
                    reason="Reaction role manager"
                )

                logging.info(
                    "REMOVED - %s -> %s",
                    member,
                    role.name
                )

        except discord.Forbidden:
            logging.error(
                "Permission denied while processing %s",
                user
            )

        except discord.NotFound:
            logging.warning(
                "User %s is no longer in the server",
                user
            )

        except discord.HTTPException as error:
            logging.error(
                "Discord API error for %s: %s",
                user,
                error
            )

    logging.info("Finished processing users.")


class RoleManagerClient(discord.Client):

    async def on_ready(self):
        logging.info("Logged in as %s", self.user)

        try:
            await process_message(self)

        except Exception as error:
            logging.error("ERROR: %s", error)

        finally:
            logging.info("Script finished. Closing connection.")
            await self.close()


async def main():
    validate_config()

    intents = discord.Intents.default()
    intents.members = True
    intents.reactions = True
    intents.message_content = True
    intents.polls = True

    client = RoleManagerClient(intents=intents)

    await client.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
