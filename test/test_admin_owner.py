"""Unit tests verifying that the bot owner can execute all administration commands."""
import asyncio
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock
import unittest

# Stub PIL if C-extension is not compiled for this Python version
for mod in ["PIL", "PIL.Image", "PIL.ImageDraw", "PIL.ImageFont", "PIL.ImageOps"]:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

import nextcord
from nextcord.ext import commands

from cogs.command_support import OWNER_ID, DualCommand
from cogs.moderation import check_target, ModerationError
from cogs.uno import staff


class AdminOwnerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.bot = commands.Bot(command_prefix="r.", intents=nextcord.Intents.none())
        self.bot.owner_id = OWNER_ID

        @self.bot.command(cls=DualCommand)
        @commands.has_permissions(administrator=True)
        async def admin_perm(ctx):
            return "ok"

        @self.bot.command(cls=DualCommand)
        @commands.has_guild_permissions(administrator=True)
        async def admin_guild_perm(ctx):
            return "ok"

        @self.bot.command(cls=DualCommand)
        @commands.has_guild_permissions(ban_members=True)
        async def mod_ban(ctx):
            return "ok"

        self.cmd_perm = admin_perm
        self.cmd_guild_perm = admin_guild_perm
        self.cmd_ban = mod_ban

        self.guild = SimpleNamespace(id=100, owner_id=1, me=SimpleNamespace(id=999, top_role=10))

    def create_context(self, user_id, is_admin=False):
        perms = nextcord.Permissions(administrator=is_admin)
        author = SimpleNamespace(id=user_id, guild_permissions=perms, top_role=1)
        channel = SimpleNamespace(
            permissions_for=lambda member: member.guild_permissions,
            guild=self.guild
        )
        ctx = SimpleNamespace(
            bot=self.bot,
            author=author,
            guild=self.guild,
            channel=channel,
            command=None
        )
        return ctx

    async def test_owner_can_run_admin_commands_without_permissions(self):
        ctx_owner = self.create_context(OWNER_ID, is_admin=False)
        self.assertTrue(await self.cmd_perm.can_run(ctx_owner))
        self.assertTrue(await self.cmd_guild_perm.can_run(ctx_owner))
        self.assertTrue(await self.cmd_ban.can_run(ctx_owner))

    async def test_non_owner_without_permissions_is_rejected(self):
        ctx_user = self.create_context(999999, is_admin=False)
        with self.assertRaises(commands.MissingPermissions):
            await self.cmd_perm.can_run(ctx_user)
        with self.assertRaises(commands.MissingPermissions):
            await self.cmd_guild_perm.can_run(ctx_user)
        with self.assertRaises(commands.MissingPermissions):
            await self.cmd_ban.can_run(ctx_user)

    async def test_non_owner_with_permissions_can_run(self):
        ctx_admin = self.create_context(999999, is_admin=True)
        self.assertTrue(await self.cmd_perm.can_run(ctx_admin))
        self.assertTrue(await self.cmd_guild_perm.can_run(ctx_admin))

    def test_uno_staff_allows_owner(self):
        owner_member = SimpleNamespace(id=OWNER_ID, guild_permissions=nextcord.Permissions.none())
        user_member = SimpleNamespace(id=999999, guild_permissions=nextcord.Permissions.none())
        admin_member = SimpleNamespace(id=999999, guild_permissions=nextcord.Permissions(administrator=True))

        self.assertTrue(staff(owner_member))
        self.assertFalse(staff(user_member))
        self.assertTrue(staff(admin_member))

    def test_moderation_check_target_allows_owner_role_hierarchy(self):
        ctx_owner = self.create_context(OWNER_ID, is_admin=False)
        ctx_user = self.create_context(999999, is_admin=False)

        # Target has top_role=5, author has top_role=1, bot has top_role=10
        target = SimpleNamespace(id=555, guild=self.guild, top_role=5, bot=False, guild_permissions=nextcord.Permissions.none())

        # Non-owner fails role check
        with self.assertRaises(ModerationError):
            check_target(ctx_user, target)

        # Owner passes role check
        check_target(ctx_owner, target)

    async def test_moderation_text_channel_allows_owner_without_channel_perms(self):
        from cogs.moderation import Moderation
        mod = Moderation(self.bot, storage=None)

        channel = MagicMock(spec=nextcord.TextChannel)
        channel.guild = self.guild
        channel.permissions_for = MagicMock(side_effect=lambda m: nextcord.Permissions.all() if m == self.guild.me else nextcord.Permissions.none())

        ctx_owner = self.create_context(OWNER_ID, is_admin=False)
        ctx_user = self.create_context(999999, is_admin=False)

        # Owner should bypass channel permission requirement
        result = await mod.text_channel(ctx_owner, channel, "manage_channels")
        self.assertEqual(result, channel)

        # Non-owner should fail with MissingPermissions
        with self.assertRaises(commands.MissingPermissions):
            await mod.text_channel(ctx_user, channel, "manage_channels")


if __name__ == "__main__":
    unittest.main()
