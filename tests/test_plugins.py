import asyncio
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from main import create_bot, selected_plugins
from utils.storage import KVStore, store
from cogs.cores import ColorPanelView
from cogs.painel_interativo import build_public_panel


class ConfigurationTests(unittest.TestCase):
    def test_selection(self):
        with patch.dict(os.environ, {'BOT_PLUGINS': 'cores,cores'}):
            self.assertEqual(selected_plugins(), ['cogs.cores'])
        for invalid in ('', 'other', '../secret'):
            with patch.dict(os.environ, {'BOT_PLUGINS': invalid}):
                with self.assertRaises(ValueError):
                    selected_plugins()


class PluginTests(unittest.IsolatedAsyncioTestCase):
    async def test_load_and_permissions(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {'DATABASE_URL': ''}), patch.object(store, '_path', Path(directory) / 'data.json'):
                async with create_bot() as bot:
                    await store.init()
                    await bot.load_extension('cogs.cores')
                    await bot.load_extension('cogs.painel_interativo')
                    groups = {group.name: group for group in bot.tree.get_commands()}
                    self.assertEqual(set(groups), {'cores', 'painel'})
                    self.assertEqual(len(groups['cores'].commands), 7)
                    self.assertEqual(len(groups['painel'].commands), 9)
                    for group in groups.values():
                        for command in group.commands:
                            self.assertTrue(command.checks, command.name)
                            self.assertTrue(command.default_permissions.administrator)
                    self.assertEqual(len(bot.persistent_views), 2)

    async def test_persistent_color_buttons(self):
        ids = []
        for gradient, count in ((False, 9), (True, 8)):
            view = ColorPanelView(gradient=gradient, title='Cores', description='Escolha', accent=0x5865F2)
            self.assertTrue(view.is_persistent())
            buttons = [item for item in view.walk_children() if hasattr(item, 'custom_id')]
            self.assertEqual(len(buttons), count)
            self.assertTrue(all(button.label for button in buttons))
            self.assertTrue(all(button.emoji.id is None for button in buttons))
            ids.extend(button.custom_id for button in buttons)
            self.assertTrue(view.to_components())
        self.assertEqual(len(ids), len(set(ids)))

    async def test_maximum_panel(self):
        pages = [{'id': f'{i:06x}', 'label': f'Página {i}', 'content': 'Conteúdo'} for i in range(20)]
        panel = {'id': '0123abcd', 'title': 'Guia', 'description': 'Escolha', 'pages': pages}
        view = build_public_panel(panel)
        self.assertTrue(view.is_persistent())
        buttons = [item for item in view.walk_children() if hasattr(item, 'custom_id')]
        self.assertEqual(len(buttons), 20)
        self.assertEqual(len({button.custom_id for button in buttons}), 20)
        self.assertTrue(view.to_components())

    async def test_json_survives_restart_and_isolates_guilds(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {'DATA_DIR': directory, 'DATABASE_URL': ''}):
                first = KVStore()
                await first.set(1, 'cores', 'config', {'roles': {'vermelho': 123}})
                await first.set(2, 'cores', 'config', {'roles': {'azul': 456}})
                await first.close()
                second = KVStore()
                self.assertEqual(await second.get(1, 'cores', 'config'), {'roles': {'vermelho': 123}})
                self.assertEqual(await second.get(2, 'cores', 'config'), {'roles': {'azul': 456}})
                await second.delete(1, 'cores', 'config')
                self.assertIsNone(await second.get(1, 'cores', 'config'))
                self.assertIsNotNone(await second.get(2, 'cores', 'config'))
                await second.close()


if __name__ == '__main__':
    unittest.main()
