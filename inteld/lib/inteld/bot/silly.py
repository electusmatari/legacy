import random

QUOTES = [
    "Merchandising, merchandising, where the real money is made. "
    "Electus Matari-the T-shirt, Electus Matari-the Coloring Book, "
    "Electus Matari-the Lunch box, Electus Matari-the Breakfast Cereal, "
    "Electus Matari-the Flame Thrower.",

    "That's the stupidest combination I've ever heard in my life. "
    "The kind of thing an idiot would have on his hangar door.",
    
    "I'm a dot: half daemon, half bot. I'm my own best friend!",

    "What's the matter, what's all that churning and bubbling? You call "
    "that intel?",

    "I always have my coffee when I watch intel, you know that.",

    "Raspberry. There's only one man who would dare give me the raspberry.",

    "Now you see that evil will always triumph because good is dumb.",

    "I am your father's brother's nephew's cousin's former roommate.",

    "Are we being too literal?",

    "We're gonna have to go right to ludicrous speed.",

    "Shall I have Snotty beam you down, sir?",

    "Hey! I don't have to put up with this! I'm rich!",

    "I've lost the bleeps, I've lost the sweeps, and I've lost the creeps.",

    ]

def generate_reply(text):
    return random.choice(QUOTES)
