using System.Threading.Tasks;
using System.Collections.Generic;
using Discord.Commands;
using Discord;

namespace KahootDiscord.Services.CommandHandler
{
    public class GameCommands : ModuleBase<SocketCommandContext>
    {
        [Command("play")]
        public Task Play(int _countdown = 60)
        {
            return ReplyAsync("time to play kahoot dude");
        }
    }
}
