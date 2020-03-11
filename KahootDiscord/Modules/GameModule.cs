using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace KahootDiscord.Modules
{
    class GameModule
    {
        public List<Game> Games = new List<Game>();
        public List<Question> QuestionPool = new List<Question>();

        public GameModule()
        {
            
        }

        public Game NewGame()
        {
            // Start game with default settings
            var game = new Game
            {
                Party = new List<User>(),
                State = GameStates.lobbyopen,
                Timer = 60
            };

            return game;
        }
    }
    public enum GameStates { lobbyopen, needmoreplayers, needcollection, question, questionresult, summary, error };
    struct Game
    {
        public List<User> Party;
        public GameStates State;
        public int Timer;
        public Question? Question;
    }
    struct Question
    {
        public int Id;
        public string Title;
        public string[] Questions;
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
