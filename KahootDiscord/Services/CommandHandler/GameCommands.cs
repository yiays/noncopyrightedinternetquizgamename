using System.Threading.Tasks;
using System.Collections.Generic;
using Discord.Commands;
using Discord;
using KahootDiscord.Modules;

namespace KahootDiscord.Services.CommandHandler
{
    public class GameCommands : ModuleBase<SocketCommandContext>
    {
        private GameModule gm = new GameModule();

        [Command("play")]
        public async Task Play(int _countdown = 60)
        {
            gm.NewGame((IGuildChannel)Context.Channel, _countdown);
            await Context.Channel.SendMessageAsync("time to play kahoot dude");
        }
    }
}
