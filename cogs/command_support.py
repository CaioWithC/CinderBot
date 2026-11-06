"""Let prefix and slash commands use the same Nextcord invocation pipeline."""
import os
from types import SimpleNamespace

import nextcord
from nextcord.ext import commands
import nextcord.ext.commands.core as _commands_core
from nextcord.ext.commands.view import StringView

OWNER_ID = int(os.getenv("OWNER_ID", "1241118323287261257"))


def is_bot_owner(user):
    user_id = getattr(user, "id", user)
    return user_id == OWNER_ID


def _owner_has_permissions(**perms: bool):
    invalid = set(perms) - set(nextcord.Permissions.VALID_FLAGS)
    if invalid:
        raise TypeError(f"Invalid permission(s): {', '.join(invalid)}")

    def predicate(ctx: commands.Context) -> bool:
        if getattr(ctx.author, "id", None) == OWNER_ID:
            return True
        ch = ctx.channel
        permissions = ch.permissions_for(ctx.author)

        missing = [perm for perm, value in perms.items() if getattr(permissions, perm) != value]

        if not missing:
            return True

        raise commands.MissingPermissions(missing)

    return _commands_core._permission_check_wrapper(predicate, "__required_permissions", perms)


def _owner_has_guild_permissions(**perms: bool):
    invalid = set(perms) - set(nextcord.Permissions.VALID_FLAGS)
    if invalid:
        raise TypeError(f"Invalid permission(s): {', '.join(invalid)}")

    def predicate(ctx: commands.Context) -> bool:
        if not ctx.guild:
            raise commands.NoPrivateMessage()

        if getattr(ctx.author, "id", None) == OWNER_ID:
            return True

        permissions = ctx.author.guild_permissions
        missing = [perm for perm, value in perms.items() if getattr(permissions, perm) != value]

        if not missing:
            return True

        raise commands.MissingPermissions(missing)

    return _commands_core._permission_check_wrapper(predicate, "__required_guild_permissions", perms)


commands.has_permissions = _owner_has_permissions
_commands_core.has_permissions = _owner_has_permissions
commands.has_guild_permissions = _owner_has_guild_permissions
_commands_core.has_guild_permissions = _owner_has_guild_permissions

_orig_command_can_run = commands.Command.can_run


async def _command_can_run(self, ctx: commands.Context) -> bool:
    try:
        return await _orig_command_can_run(self, ctx)
    except commands.MissingPermissions:
        if getattr(ctx.author, "id", None) == OWNER_ID:
            return True
        raise


commands.Command.can_run = _command_can_run


class ModerationError(commands.CheckFailure):
    """An actionable moderation error safe to show to the moderator."""


class CommandDisabledError(commands.CheckFailure):
    """Raised when a command has been disabled by server administrators in the dashboard."""
    def __init__(self, command_name):
        self.command_name = command_name
        super().__init__(f"O comando `{command_name}` está desativado neste servidor.")


class InteractionContext(commands.Context):
    def __init__(self, bot, interaction, command, options, attachments=()):
        # Prefix checks, cooldowns and existing upload handlers expect a message.
        message = SimpleNamespace(
            id=interaction.id, author=interaction.user, guild=interaction.guild,
            channel=interaction.channel, attachments=list(attachments), content="",
            created_at=interaction.created_at, edited_at=None, _state=bot._connection,
        )
        super().__init__(message=message, bot=bot, view=StringView(""), prefix="/",
                         command=command, invoked_with=command.name)
        self.interaction = interaction
        self.options = options

    async def send(self, content=None, **kwargs):
        # The slash entry point defers first. wait=True returns an editable message
        # for game buttons and automatic settlements on timeout.
        return await self.interaction.followup.send(content=content, wait=True, **kwargs)


class _DualArguments:
    async def _parse_arguments(self, ctx):
        if not isinstance(ctx, InteractionContext):
            return await super()._parse_arguments(ctx)

        ctx.args = [ctx] if self.cog is None else [self.cog, ctx]
        ctx.kwargs = {}
        for name, param in self.clean_params.items():
            ctx.current_parameter = param
            if name in ctx.options:
                value = ctx.options[name]
                # Discord resolves users, attachments and numeric options. Text
                # still uses the prefix converters (including BetAmount and int).
                if isinstance(value, str):
                    converter = param.annotation if param.annotation is not param.empty else str
                    value = await commands.run_converters(ctx, converter, value, param)
            elif param.default is not param.empty:
                value = param.default
            else:
                raise commands.MissingRequiredArgument(param)
            if param.kind == param.KEYWORD_ONLY:
                ctx.kwargs[name] = value
            else:
                ctx.args.append(value)


class DualCommand(_DualArguments, commands.Command):
    """Keep checks, cooldowns, converters, hooks and errors shared across inputs."""

    async def can_run(self, ctx):
        try:
            return await super().can_run(ctx)
        except commands.MissingPermissions:
            if getattr(ctx.author, "id", None) == OWNER_ID:
                return True
            raise


class DualGroup(_DualArguments, commands.Group):
    """A prefix group whose base callback also accepts resolved slash options."""

    async def can_run(self, ctx):
        try:
            return await super().can_run(ctx)
        except commands.MissingPermissions:
            if getattr(ctx.author, "id", None) == OWNER_ID:
                return True
            raise


def slash_name(command):
    return {"profile": "profile view", "six": "six iniciar"}.get(command.qualified_name, command.qualified_name)
