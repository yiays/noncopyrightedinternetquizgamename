using System;
using System.Collections.Generic;
using Microsoft.Extensions.Configuration;
using System.Linq;
using System.Text;

namespace KahootDiscord.Modules
{
    class GameModule
    {
        public List<Game> Games = new List<Game>();
        public List<Game> ArchivedGames = new List<Game>();
        public List<Question> QuestionPool = new List<Question>();

        private IConfiguration _config;
        public Dictionary<string, Object> Config;

        public GameModule()
        {
            _config = new ConfigurationBuilder().AddJsonFile("game.js").Build();
            ConfigurationBinder.Bind(_config, Config);
        }

        public Game NewGame(Discord.IGuildChannel channel, int countdown = 60)
        {
            // Start game with default settings
            var game = new Game
            {
                Party = new List<User>(),
                State = GameStates.lobbyopen,
                Timer = countdown,
                Channel = channel
            };

            Games.Add(game);

            return game;
        }
    }
    public enum GameStates { lobbyopen, needmoreplayers, needcollection, question, questionresult, summary, error };
    struct Game
    {
        public List<User> Party;
        public GameStates State;
        public int Timer;
        public List<Question> Questions;
        public int? CurrentQuestion;
        public Discord.IGuildChannel Channel;
    }
    struct Question
    {
        public int Id;
        public string Title;
        public string[] Answers;
        public bool[] Correct;
        public int Timer;
        public User? Author;
    }
    struct User
    {
        public int Discordid;
        public string Username;
        public int Discriminator;
        public int Score;
        public string Token;
    }
    struct Collection
    {
        public int Id;
        public string Name;
        public string Description;
        private IList<Voter> voters;
        public int Upvotes {
            get
            {
                return voters.Where(i => i.vote == true).Count();
            }
        }
        public int Downvotes
        {
            get
            {
                return voters.Where(i => i.vote == false).Count();
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
