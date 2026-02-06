import random

def random_house_thinking_reply() -> str:
    quotes = [
        "Hmm. Let me think. Be quiet. I'm navigating the vast, empty chasm of your contribution to find an actual idea. Don't startle it.",
        "I need to think. Stop talking. You've already reached your syllable quota for the day. I need the silence to filter out the useless parts of that sentence.",
        "I'm busy checking the back of my brain for the answer. It's a large warehouse; you're standing in the doorway blocking the light. Move.",
        "Let me think. Don't worry. The silence is called 'thought.' Try not to let the secondary smoke from my neurons give you a contact high."
    ]
    
    response = random.choice(quotes)
    return response
