from random import choice

class defaultStart:
    default_list = ['It was a dark and stormy night.',

                    '\"How many demons have you slain?\" the man said to Balendro. \"Just one, but it was a big one.\"',

                    '\"Fight the state.\" These were the words that have echoed in my mind for years.',

                    'It was an abnormally bright day in November when we parted ways.',

                    'I had heard this story from various people, and as generally happens in situations such as this, every person told a different tale.',

                    'It wasn\'t until he was on the firing squad that the Major thought about this day.',

                    '\"Where am I?!\" Nathaniel screamed into the darkness.',

                    'The park was empty, considering the weather.',

                    'My story begins on the happiest day of my life.',

                    'I remember thinking, \"I can still win this.\"',

                    'As soon as she entered the room, I could tell she would be nothing but trouble.',

                    'In the dark, damp cell, he began scribbling on the walls.',

                    'I really should have known when to give up.',

                    'There was no possibility of taking a walk that day.',

                    'I remember her well.',

                    'It was the afternoon of his forty-eighth birthday when Charles\' life was turned upside down.',

                    'For the longest time, I used to go to bed early.',

                    '\"That was a mistake.\"',

                    'He was a man named John Slattery, and he almost deserved it.',

                    'We were halfway out of town when the drugs started to kick in.',

                    '\"Why don\'t you start at the beginning? It\'s always the easiest,\" she said as we both put back another shot.',

                    'People always ask me \"Do you consider your book to be autobiographical?\"',

                    '\"Who are you?\"',

                    'She waited impatiently for the bus to pick up the kids.',

                    '\"Sorry I\'ve been gone so long. I won\'t let you down again.\"',

                    'They called him the Code Warrior. He lives now, but only in our memories.',

                    'I\'ve always loved this town.',

                    'I would rather have not known.'

                    'I couldn\'t help but overhear the women in the corner'

                    'We were scheduled to leave exactly at noon.'

                    'No one could believe they were back together.'

                    'She was crazy.'

                    'The whole idea didn\'t really appeal to him.'
                                    ]

    @staticmethod
    def getRandomDefault():
        return choice(defaultStart.default_list)

