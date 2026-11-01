from __future__ import annotations

import asyncio
import logging
import os

import discord
from discord import app_commands
from discord.ext import commands

from utils.storage import store

AVAILABLE_PLUGINS = {
    'cores': 'cogs.cores',
    'painel_interativo': 'cogs.painel_interativo',
}


def selected_plugins() -> list[str]:
    names = list(dict.fromkeys(
        name.strip() for name in os.environ.get(
            'BOT_PLUGINS', 'cores,painel_interativo'
        ).split(',') if name.strip()
    ))
    unknown = set(names) - AVAILABLE_PLUGINS.keys()
    if unknown or not names:
        raise ValueError('BOT_PLUGINS deve conter cores e/ou painel_interativo.')
    return [AVAILABLE_PLUGINS[name] for name in names]


class PluginBot(commands.Bot):
    async def setup_hook(self) -> None:
        await store.init()
        for extension in selected_plugins():
            await self.load_extension(extension)
        await self.tree.sync()

    async def close(self) -> None:
        await store.close()
        await super().close()


def create_bot() -> PluginBot:
    intents = discord.Intents.default()
    intents.members = True
    bot = PluginBot(command_prefix=commands.when_mentioned, intents=intents, help_command=None)

    @bot.tree.error
    async def on_error(interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.MissingPermissions):
            message = 'Você não tem permissão para usar este comando.'
        elif isinstance(error, app_commands.NoPrivateMessage):
            message = 'Este comando só funciona em servidores.'
        else:
            logging.getLogger('bot').error('Erro em comando', exc_info=error)
            message = 'Não foi possível concluir a ação. Confira as permissões e tente novamente.'
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)

    return bot


async def main() -> None:
    token = os.environ.get('DISCORD_TOKEN', '').strip()
    if not token:
        raise SystemExit('Defina DISCORD_TOKEN no ambiente antes de iniciar.')
    selected_plugins()
    async with create_bot() as bot:
        await bot.start(token)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
