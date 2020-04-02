using System;
using System.Threading.Tasks;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;
using System.Runtime.Serialization;
using System.Runtime.Serialization.Json;
using Discord;
using Discord.WebSocket;

namespace KahootDiscord.Modules
{
    class GameModule
    {
        public List<Game> Games = new List<Game>();
        public List<Game> ArchivedGames = new List<Game>();

        private DataContractJsonSerializer serializer = new DataContractJsonSerializer(typeof(Config));
        public Config Config;

        private Emoji[] numberreacts = new Emoji[]
        {
            new Emoji("1️⃣"),
            new Emoji("2️⃣"),
            new Emoji("3️⃣"),
            new Emoji("4️⃣"),
            new Emoji("5️⃣"),
            new Emoji("6️⃣"),
            new Emoji("7️⃣"),
            new Emoji("8️⃣"),
            new Emoji("9️⃣"),
            new Emoji("🔟")
        };

        public GameModule()
        {
            Load();
        }
        private bool Load()
        {
            MemoryStream ms = new MemoryStream();
            using (FileStream file = new FileStream("game.json", FileMode.Open, FileAccess.Read))
            {
                file.CopyTo(ms);
                // Deserialization from JSON
                Config = (Config)serializer.ReadObject(ms);
            }
            return true;
        }
        private bool Save()
        {
            MemoryStream ms = new MemoryStream();
            using (FileStream file = new FileStream("game.json", FileMode.OpenOrCreate, FileAccess.Write))
            {
                // Serialization to JSON
                serializer.WriteObject(ms, Config);
                ms.WriteTo(file);
            }
            return true;
        }

        public async Task NewGame(ISocketMessageChannel channel, int countdown = 60)
        {
            // Start game with default settings
            var game = new Game
            {
                Party = new List<User>(),
                State = GameStates.lobbyopen,
                Timer = countdown,
                Channel = (IGuildChannel) channel
            };

            Games.Add(game);

            Task runcountdown = Task.Run(async () =>
            {
                var msg = await channel.SendMessageAsync("A game of KahootDiscord is starting soon!");
                while (game.Timer > 0)
                {
                    await msg.ModifyAsync(msg => msg.Content = $"A game of Kahoot is starting in {game.Timer} seconds...");
                    game.Timer--;
                    await Task.Delay(1000);
                }
            });
            Task promptforcollection = Task.Run(async () =>
            {
                var msg = await channel.SendMessageAsync(
                    $"Please choose a collection...", embed: new EmbedBuilder()
                    {
                        Title = "Available collections",
                        Description = "React with the matching emoji to vote for a collection.",
                        Fields = new List<EmbedFieldBuilder>()
                        {
                            new EmbedFieldBuilder()
                            {
                                IsInline = false,
                                Name = "0: Random",
                                Value = "A sampler of all the user-submitted questions on KahootDiscord."
                            }
                        }.Concat(Config.Collections.Select(e => new EmbedFieldBuilder() { IsInline = false, Name = e.Name, Value = e.Description })).ToList(),
                        Color = new Color(247, 183, 49)
                    }.Build()
                );
                await msg.AddReactionsAsync(numberreacts);
            });

            Task.WaitAll(runcountdown, promptforcollection);
        }
    }

    [DataContract]
    struct Config
    {
        [DataMember]
        public List<Question> Questions;
        [DataMember]
        public List<Collection> Collections;
    }

    public enum GameStates { lobbyopen, needmoreplayers, needcollection, question, questionresult, summary, error };
    struct Game
    {
        public List<User> Party;
        public GameStates State;
        public int Timer;
        public List<Question> Questions;
        public int? CurrentQuestion;
        public IGuildChannel Channel;
    }
    struct Question
    {
        public int Id;
        public string Title;
        public string[] Answers;
        public bool[] Correct;
        public int Timer;
        public User? Author;
        public List<Voter> Voters;
        public int Upvotes
        {
            get
            {
                return Voters.Where(i => i.vote == true).Count();
            }
        }
        public int Downvotes
        {
            get
            {
                return Voters.Where(i => i.vote == false).Count();
            }
        }
    }
    struct User
    {
        public int Discordid;
        public string Username;
        public int Discriminator;
        public int Score;
        public string Token;

        public static implicit operator User(int i) => new User() { Discordid = i };
        public static implicit operator int(User u) => u.Discordid;
    }
    struct Collection
    {
        public int Id;
        public string Name;
        public string Description;
        public List<Voter> Voters;
        public int Upvotes {
            get
            {
                return Voters.Where(i => i.vote == true).Count();
            }
        }
        public int Downvotes
        {
            get
            {
                return Voters.Where(i => i.vote == false).Count();
            }
        }
        public List<Question> Questions;
    }
    struct Voter
    {
        public User user;
        public bool vote;
    }
}
