from random import choice

class defaultStart:
    default_list = ['This is the saddest story I have ever heard.',

                    '\"How many demons have you slain?\" the man said to Balendro. \"Just one, but it was a big one.\"',

                    'It was a dark and stormy night.',

                    'It was always a pleasure to kill.',

                    '\"You don\'t remember me?\" he said to his detainee. \"Let me remind you of how our histories interweave...\"',

                    'Mykal stood on the edge of the cliff, ready to jump, ready to end his sea of troubles.',

                    '\"Fight the state.\" These were the words that have echoed in my mind for years.',

                    'It was an abnormally bright day in November when I lost her.',

                    'A wise man once said, \"Happy families are all alike; every unhappy family is unhappy in its own way.\"',

                    'I had heard the story from various people, and as generally happens in situations such as this, every person told a different tale.',

                    'It wasn\'t until he was on the firing squad that the Major thought about this day.',

                    '\"Where am I?!\" Nathaniel screamed into the darkness.',

                    'I remember vividly the day of the assassination and how our lives changed thereafter.',

                    'My story begins on the happiest day of my life.',

                    'I remember thinking, \"I can still win this.\"',

                    'As soon as she entered the room, I could tell she would be nothing but trouble.',

                    'In the dark, damp cell, he began scribbling on the walls.',

                    'My brothers always said it would be a cold day in hell when I found true love.',

                    'There was no possibility of taking a walk that day.',

                    'I remember her well.',

                    'It was the afternoon of his forty-eighth birthday when Charles\' life was turned upside down.',

                    'For the longest time, I used to go to bed early.',

                    '\"That was a mistake.\"',

                    'Our final run was just a little too interesting.',

                    'I am a sick man, a spiteful man.',

                    'They shot her first.',

                    'He was a man named John Slattery, and he almost deserved it.',

                    'I died the morning of December 12th, 1992.',

                    'We were halfway out of town when the drugs started to kick in.',

                    '\"Why don\'t you start at the beginning? It\'s always the easiest,\" she said as we both put back another shot.',

                    'People always ask me \"Do you consider your book to be autobiographical?\"',

                    '\"Who are you?\"',

                    'I never gave much thought into how I would die...',

                    '\"Sorry I\'ve been gone so long. I won\'t let you down again.\"',

                    'They called him the Code Warrior. He lives now, but only in our memories.',

                    'I love this town.',

                    'I fought on the losing side of the New Great War.'
                                    ]

    @staticmethod
    def getRandomDefault():
        return choice(defaultStart.default_list)
