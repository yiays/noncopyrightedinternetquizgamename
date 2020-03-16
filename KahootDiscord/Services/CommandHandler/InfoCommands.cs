using System.Threading.Tasks;
using System.Collections.Generic;
using Discord.Commands;
using Discord;

namespace DiscordBot.Modules.CommandHandler
{
    public class InfoCommands : ModuleBase<SocketCommandContext>
    {
        public readonly Dictionary<string, string> Docs = new Dictionary<string, string>()
        {
            {"info", "*k!info* - Dhows basic information about this bot."},
            {"help", "*k!help [cmd]* - Lists an overview of all commands, help followed by a command shows instructions on how to use that specific command."},
            {"play", "*k!play [time]* - Starts a game of discord kahoot, optionally with a custom timer (default is 60 seconds) before the game starts. You will be the admin of this game."}
        };

        [Command("info")]
        public Task Info()
        {
            /// info - shows basic information about this bot.
            return ReplyAsync(
                embed: new EmbedBuilder()
                {
                    Title = "info",
                    Url = "https://kahoot.yiays.com/",
                    Description = "Kahoot clone but on discord.",
                    ImageUrl = "https://cdn.discordapp.com/attachments/532699822214348810/550562868458946571/PkIeN4J.png",
                    Color = new Color(247, 183, 49)
                }.Build());
        }

        [Command("help")]
        public Task Help(string cmd = "")
        {
            /// help [cmd] - lists an overview of all commands, help followed by a command shows instructions on how to use that specific command.
            if (cmd != "")
            {
                if (Docs.ContainsKey(cmd.ToLower()))
                {
                    return ReplyAsync(
                    embed: new EmbedBuilder()
                    {
                        Title = "help",
                        Url = "https://kahoot.yiays.com/",
                        Description = Docs[cmd]
                    }.Build());
                }
                else
                {
                    return ReplyAsync(
                    embed: new EmbedBuilder()
                    {
                        Title = "help",
                        Url = "https://kahoot.yiays.com/",
                        Description = $"Command `{cmd.ToLower()}` not found!"
                    }.Build());
                }
            }
            else
            {
                return ReplyAsync(
                embed: new EmbedBuilder()
                {
                    Title = "help",
                    Url = "https://kahoot.yiays.com/",
                    Description = "For more details, use `k!help [command]`.",
                    Fields = new List<EmbedFieldBuilder>() {
                        new EmbedFieldBuilder()
                        {
                            IsInline = false,
                            
                            Name = "Help",
                            Value = "```help, info```"
                        },
                        new EmbedFieldBuilder()
                        {
                            IsInline = false,

                            Name = "Play",
                            Value = "```play```"
                        }
                    }
                }.Build());
            }
        }
    }
}
