using System;
using System.Collections.Generic;
using System.Text;

namespace KahootDiscord.Modules
{
    class GameModule
    {

    }
    enum GameStates { lobbyopen, needmoreplayers, needcollection, question, questionresult, summary, closed };
    struct Game
    {
        public List<User> Party;
        public GameStates State;
        public int timer;
        public int question;
    }
    struct Question
    {
        public int Id;
        public string Title;
        public string[] Questions;
        public bool[] Correct;
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
        private Dictionary<User, bool> voters;
        public int Upvotes { get; }
        public int Downvotes { get; }
        public List<Question> Questions;
    }
}
