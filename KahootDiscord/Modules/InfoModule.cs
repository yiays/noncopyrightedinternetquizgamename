using System.Threading.Tasks;
using System.Collections.Generic;
using Discord.Commands;
using Discord;

namespace DiscordBot.Modules
{
    public class InfoModule : ModuleBase<SocketCommandContext>
    {
        [Command("info")]
        public Task Info()
            => ReplyAsync(
                embed: new EmbedBuilder() {
                    Title = "info",
                    Url = "https://kahoot.yiays.com/",
                    Description = "Kahoot clone but on discord.",
                    ImageUrl = "https://cdn.discordapp.com/attachments/532699822214348810/550562868458946571/PkIeN4J.png",
                    Color = new Color(247,183,49)
                }.Build());

        [Command("help")]
        public Task Help(string? cmd)
            => ReplyAsync(
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
                        }
                    }
                }.Build());
    }
}
