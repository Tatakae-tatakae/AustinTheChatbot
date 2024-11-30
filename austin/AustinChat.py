# File: kindergarten_game_with_emojis.py
import pygame
import random
from google.cloud import dialogflow_v2 as dialogflow  # Ensure you install google-cloud-dialogflow
import uuid
from google.api_core.exceptions import InvalidArgument
import os
import emoji

# Set up the service account JSON for Dialogflow authentication
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\Andre\OneDrive\Documents\austin\robotic-aviary-441720-p4-954c84373a72.json"  # Replace with your JSON path

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Kindergarten Educational Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

# Fonts
font = pygame.font.Font(None, 40)
small_font = pygame.font.Font(None, 30)

# Levels and Progress
progress = {"Math": 0, "Reading": 0}  # Tracks levels completed
stars_collected = {"Math": 0, "Reading": 0}  # Tracks stars earned

# Emojis
star_emoji = emoji.emojize(":star:")
math_emojis = [emoji.emojize(":apple:"), emoji.emojize(":banana:"),
               emoji.emojize(":grapes:"), emoji.emojize(":watermelon:"),
               emoji.emojize(":cherries:")]
animal_emojis = [emoji.emojize(e) for e in
                 [":dog:", ":cat:", ":mouse:", ":rabbit:", ":bear:", ":panda_face:", ":koala:", ":tiger:", ":lion:", ":frog:", ":monkey_face:", ":pig:"]]

# Dialogflow Setup (Replace with your project credentials)
DIALOGFLOW_PROJECT_ID = 'robotic-aviary-441720-p4'
DIALOGFLOW_LANGUAGE_CODE = 'en'
SESSION_CLIENT = dialogflow.SessionsClient()


def dialogflow_query(text_input):
    """Send a text input to Dialogflow and return the response."""
    try:
        text_input = dialogflow.TextInput(text=text_input, language_code=DIALOGFLOW_LANGUAGE_CODE)
        query_input = dialogflow.QueryInput(text=text_input)
        session_id = str(uuid.uuid4())
        session = SESSION_CLIENT.session_path(DIALOGFLOW_PROJECT_ID, session_id)
        response = SESSION_CLIENT.detect_intent(request={"session": session, "query_input": query_input})
        return response.query_result.fulfillment_text
    except InvalidArgument as e:
        print(f"Dialogflow error: {e}")
        return "Sorry, I couldn't understand that."


def show_message(message, x, y, color=BLACK, size="medium"):
    """Utility to display messages on the screen."""
    if size == "small":
        text = small_font.render(message, True, color)
    else:
        text = font.render(message, True, color)
    screen.blit(text, (x, y))


def math_question(level):
    """Generate a math question with emoji examples based on level difficulty."""
    num1 = random.randint(1, 10 * level)
    num2 = random.randint(1, 10 * level)
    operation = random.choice(["+", "-", "*"])
    emoji_symbol = random.choice(math_emojis)
    question = f"{num1} {emoji_symbol} {operation} {num2} {emoji_symbol}"
    answer = eval(f"{num1} {operation} {num2}")
    return question, answer


def reading_question(level):
    """Generate a reading question with animal emojis based on level difficulty."""
    words = ["cat", "dog", "bat", "apple", "orange", "grape", "house"]
    sentence = " ".join(random.choices(words, k=3 + level))
    animal = random.choice(animal_emojis)
    question = f"Recreate this sentence: {sentence} {animal}"
    answer = sentence
    return question, answer


def render_emoji_text(text, x, y, color=BLACK):
    """Utility to render text containing emojis on the screen."""
    rendered_text = font.render(text, True, color)
    screen.blit(rendered_text, (x, y))


def run_level(subject, level):
    """Run a single level for a chosen subject."""
    global progress, stars_collected
    running = True
    question_count = 0
    correct_answers = 0

    while running and question_count < 5:
        screen.fill(WHITE)
        if subject == "Math":
            question, answer = math_question(level)
        else:
            question, answer = reading_question(level)

        # Show level details and question
        render_emoji_text(f"Level {level} - {subject}", 20, 20, BLUE)
        render_emoji_text(f"Question: {question}", 20, 100, BLACK)
        show_message("Type your answer and press ENTER.", 20, 300, GREEN)
        pygame.display.flip()

        user_input = ""
        answered = False
        while not answered:  # Wait for user to answer
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # Submit answer
                        if subject == "Math":
                            try:
                                user_answer = int(user_input)  # Convert input to number
                                if user_answer == answer:
                                    correct_answers += 1
                                question_count += 1
                                answered = True
                            except ValueError:
                                user_input = ""  # Reset on invalid input
                        elif subject == "Reading":
                            # For Reading, check string equality
                            if user_input.strip().lower() == answer.lower():
                                correct_answers += 1
                            question_count += 1
                            answered = True
                    elif event.key == pygame.K_BACKSPACE:  # Remove last character
                        user_input = user_input[:-1]
                    else:  # Add to input string
                        user_input += event.unicode

            # Display user input
            screen.fill(WHITE)
            render_emoji_text(f"Level {level} - {subject}", 20, 20, BLUE)
            render_emoji_text(f"Question: {question}", 20, 100, BLACK)
            show_message("Type your answer and press ENTER.", 20, 300, GREEN)
            show_message(f"Your Answer: {user_input}", 20, 400, RED)
            pygame.display.flip()

    # End of level
    stars_collected[subject] += correct_answers
    progress[subject] += 1

    screen.fill(WHITE)
    earned_stars = star_emoji * correct_answers
    show_message(f"Level Complete!", 20, 200, BLUE)
    show_message(f"Stars earned: {earned_stars}", 20, 300, YELLOW)

    if correct_answers >= 4:
        show_message("Congratulations! You passed the level!", 20, 400, GREEN)
    else:
        show_message("Try again to improve your score.", 20, 400, RED)

    pygame.display.flip()
    pygame.time.wait(3000)


def main():
    """Main game loop."""
    running = True
    dialogflow_greeting = dialogflow_query("Hello")
    print(dialogflow_greeting)

    while running:
        screen.fill(WHITE)
        show_message("Kindergarten Educational Game", 200, 50, BLUE)
        show_message("Choose a Subject:", 300, 150, BLACK)
        show_message("1. Math", 300, 200, BLACK)
        show_message("2. Reading", 300, 250, BLACK)
        show_message("Press [ESC] to quit", 300, 300, GREEN)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    run_level("Math", 1)
                elif event.key == pygame.K_2:
                    run_level("Reading", 1)
                elif event.key == pygame.K_ESCAPE:
                    running = False

    pygame.quit()


if __name__ == "__main__":
    main()
