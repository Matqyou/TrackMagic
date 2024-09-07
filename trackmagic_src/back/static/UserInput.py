class UserInput:
    @staticmethod
    def choice_lowercase(choices: list, prompt: str = ''):
        while True:
            user_input = input(prompt).lower()

            if user_input.lower() in choices:
                return user_input
