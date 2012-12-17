from random import choice

class defaultEnd:
    default_list = ['The end. Or is it?',
                                    'It couldn\'t have been more perfect.',
                                    'Tomorrow, I\'ll think of some way to get him back. After all, tomorrow is another day.',
                                    'She smiled.',
                                    'She lowered the sword and noticed that the twitch had stopped.',
                                    '\"Wow, I can\'t believe that actually worked!\"',
                                    'At this point, what difference could it possibly have made?',
                                    '\"Isn\'t this where we began?\"',
                                    '\"They\'re never going to believe this back home.\"',
                                    'The prophecy was fulfilled.',
                                    'You just can\'t make this stuff up.',
                                    '\"But I can\'t leave. Everything I hate is right here...\"',
                                    'And they all lived happily ever after.',
                                    'He never knew my name, and still doesn\'t. I\'d prefer to keep it that way.',
                                    '\"Stand still. It\'ll all be over soon.\"',
                                    '\"All right, folks, you\'ve seen enough. Move along now.\"',
                                    'She had a feeling that this one would leave a scar.',
                                    '\"You\'ll have to wait for me. I still have work to do.\"',
                                    '\"Today you...tomorrow me.\"',
                                    '\"Goodbye, my friend.\"',
                                    'He rode off into the sunset.',
                                    'He drove off, filled with hope for the first time in years.',
                                    'And, with that, the attack began at 6:23 AM, just as they said it would.',
                                    'I was right.',
                                    'She was right.',
                                    'He spoke with almost robotic intonation. \"The decision rests with you. We\'ll be waiting for your answer.\"',
                                    'And there was nothing we could do to stop it.',
                                    'It was flawless.',
                                    'After all, what\'s the worst that could happen?',
                                    'She knew it to be true, for it was written.',
                                    'And that\'s why you always leave a note.',
                                    'I never said it\'d be a happy ending, did I?',
                                    'I suppose everything worked out in the end.',
                                    'It was all a dream.'
                                    ]

    @staticmethod
    def getRandomDefault():
        return choice(defaultEnd.default_list)
