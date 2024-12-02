import streamlit as st
import random
import itertools
import math
import pandas as pd
import plotly.express as px
from streamlit_echarts import st_echarts  # Import the ECharts library
import numpy as np
from sympy.stats.rv import probability


# Function to start a new game
def start_new_game():
    st.session_state.secret_number = ''.join(random.sample('0123456789', 4))  # Random 4-digit number
    st.session_state.history = []  # Reset history
    st.session_state.attempts = 0  # Reset attempts counter
    st.session_state.possibilities = [''.join(p) for p in
                                      itertools.permutations('0123456789', 4)]  # All 4-digit possibilities
    st.session_state.game_over = False  # Game status flag
    st.session_state.entropy_values = []  # Track entropy values for plotting


# Function to calculate bulls and cows
def calculate_bulls_and_cows(secret, guess):
    bulls = sum(1 for i in range(4) if secret[i] == guess[i])
    cows = sum(1 for i in range(4) if secret[i] != guess[i] and guess[i] in secret)
    return bulls, cows


# Function to filter possibilities based on the guess and result (bulls, cows)
# Function to filter possibilities based on the guess and result (bulls, cows)
# def filter_possibilities(possibilities, guess, bulls, cows, randomness_factor=0.2):
#     """
#     Filter out possibilities based on bulls and cows feedback, with a randomness factor to
#     allow some wrong guesses to retain more possibilities.
#     """
#     # Filter possibilities based on the bulls and cows feedback
#     valid_possibilities = [p for p in possibilities if calculate_bulls_and_cows(p, guess) == (bulls, cows)]
#
#     # If the guess is wrong (i.e., bulls < 4), allow some randomness
#     if bulls < 4:
#         # Introduce randomness: only keep a percentage of the filtered possibilities
#         num_to_keep = int(len(valid_possibilities) * (1 + randomness_factor))
#         # Ensure that we don't keep more than the total possibilities
#         num_to_keep = min(num_to_keep, len(possibilities))
#         selected_possibilities = random.sample(possibilities, num_to_keep)
#     else:
#         selected_possibilities = valid_possibilities
#
#     return selected_possibilities
# Function to filter possibilities based on the guess and result (bulls, cows)
# Function to filter possibilities based on the guess and result (bulls, cows)
def filter_possibilities(possibilities, guess, bulls, cows):
    """
    Filters out the possibilities based on bulls and cows feedback.
    The function only keeps those possibilities which match the bulls and cows
    feedback from the guess.
    """
    return [p for p in possibilities if calculate_bulls_and_cows(p, guess) == (bulls, cows)]


# Function to calculate entropy based on remaining possibilities
# def calculate_entropy(possibilities):
#     total = len(possibilities)
#     if total == 0:
#         return 0
#     probabilities = [possibilities.count(p) / total for p in set(possibilities)]
#     return -sum(p * math.log2(p) for p in probabilities if p > 0)  # Use math.log2() for log2 calculation
def calculate_entropy(possibilities, guess, bulls, cows):
    """
    Calculate entropy based on the number of remaining possibilities,
    adjusted by the proximity of the guess to the secret number.
    """
    total_possibilities = len(possibilities)
    if total_possibilities == 0:
        return 0

    # Proximity score adjustment
    bulls_weight = 1.0  # Full weight for bulls
    cows_weight = 0.5   # Half weight for cows
    proximity_score = (bulls_weight * bulls) + (cows_weight * cows)

    # Base entropy calculation
    probabilities = [1 / total_possibilities for _ in possibilities]
    base_entropy = -sum(p * math.log2(p) for p in probabilities if p > 0)

    # Adjust entropy based on proximity
    adjusted_entropy = base_entropy - proximity_score
    return max(0, adjusted_entropy)  # Ensure entropy is non-negative



# Function to display the entropy and information gain graph with ECharts
import streamlit as st
from streamlit_echarts import st_echarts
from math import isnan


# Function to handle the display of the entropy graph with information gain
def display_graph():
    # Ensure entropy_values and information_gain are stored in session state
    if "entropy_values" not in st.session_state:
        st.session_state.entropy_values = []

    if "information_gain_values" not in st.session_state:
        st.session_state.information_gain_values = []

    # Check if the entropy and information gain values are valid
    if any(isnan(x) for x in st.session_state.entropy_values + st.session_state.information_gain_values):
        st.error("Error: NaN values found in the entropy or information gain data!")
        return

    # Create x-axis data for each guess attempt
    x_data = [f"Guess {i}" for i in range(1, len(st.session_state.entropy_values) + 1)]

    # Chart options for entropy and information gain
    options = {
        "title": {"text": "Entropy and Information Gain Over Time"},
        "tooltip": {"trigger": "axis"},
        "legend": {
            "data": ["Entropy", "Information Gain"],
            "top": "10%",
            # Adjust the top position of the legend (you can set it to a percentage of the height or a fixed value)
            "right": "5%",  # You can set the right position to move it further from the left side
            "left": "auto",  # This will allow the right positioning to work automatically
            "orient": "horizontal",  # If you want the legend to be horizontal, you can use "horizontal"
        },
        "grid": {
            "left": "3%", "right": "4%", "bottom": "3%", "containLabel": True
        },
        "toolbox": {"feature": {"saveAsImage": {}}},
        "xAxis": {
            "type": "category",
            "boundaryGap": False,
            "data": x_data,
        },
        "yAxis": {"type": "value"},
        "series": [
            {
                "name": "Entropy",
                "type": "line",
                "data": st.session_state.entropy_values,
                "smooth": True,
                "lineStyle": {"color": "blue"},
            },
            {
                "name": "Information Gain",
                "type": "line",
                "data": st.session_state.information_gain_values,
                "smooth": True,
                "lineStyle": {"color": "green"},
            },
        ],
    }

    # Render the graph
    st_echarts(options=options, height="400px")


# Function to display bulls and cows using LiquidFill chart (side by side)
def display_bulls_and_cows(bulls, cows):
    bulls_water_level = bulls / 4  # Max bulls = 4
    cows_water_level = cows / 4  # Max cows = 4

    # ECharts LiquidFill chart for Bulls
    bulls_option = {
        "series": [{
            "type": "liquidFill",
            "data": [bulls_water_level],
            "color": ["#28a745"],  # Green color for bulls
            "label": {
                "show": True,
                "position": "inside",
                "fontSize": 24,
                "color": "#fff",
                "formatter": f"Bulls: {bulls}",
            }
        }]
    }

    # ECharts LiquidFill chart for Cows
    cows_option = {
        "series": [{
            "type": "liquidFill",
            "data": [cows_water_level],
            "color": ["#ffc107"],  # Yellow color for cows
            "label": {
                "show": True,
                "position": "inside",
                "fontSize": 24,
                "color": "#fff",
                "formatter": f"Cows: {cows}",
            }
        }]
    }

    # Display the liquid fill charts for bulls and cows side by side
    col1, col2 = st.columns(2)
    with col1:
        st_echarts(options=bulls_option, height="300px")
    with col2:
        st_echarts(options=cows_option, height="300px")


# Function to display attempt history with images as headers
def display_attempt_history():
    with st.sidebar:
        st.subheader("Attempt History:")

        # Display images as headers with counts below them
        bulls_image = r"C:\Users\csain\Downloads\bull.png"
        cows_image = r"C:\Users\csain\Downloads\cow.png"
        col1, col2 = st.columns(2)
        with col1:
            st.image(bulls_image, use_container_width=True)
        with col2:
            st.image(cows_image, use_container_width=True)
        # Loop through history to display each attempt
        for attempt, bulls, cows in st.session_state.history:
            col1, col2 = st.columns(2)
            with col1:
                #st.image(bulls_image, use_container_width=True)
                st.markdown(f"**{attempt}:** {bulls} Bulls")
            with col2:
                #st.image(cows_image, use_container_width=True)
                st.markdown(f"**{attempt}:** {cows} Cows")

def play_game():
    # If the game is not started, initialize the session state
    if "secret_number" not in st.session_state:
        start_new_game()

    # Initialize session state variables if not already initialized
    if "entropy_values" not in st.session_state:
        st.session_state.entropy_values = []

    if "information_gain_values" not in st.session_state:
        st.session_state.information_gain_values = []

    st.title('BULLS AND COWS GAME')

    # Main Game UI
    guess = st.text_input("Enter your guess: ", max_chars=4)

    if guess:
        # Validate the guess
        if len(guess) == 4 and guess.isdigit() and len(set(guess)) == 4:
            bulls, cows = calculate_bulls_and_cows(st.session_state.secret_number, guess)
            st.session_state.attempts += 1

            # Check if the guess already exists in history
            guess_exists = any(existing_attempt[0] == guess for existing_attempt in st.session_state.history)

            # Add the guess to the history only if it doesn't exist already
            if not guess_exists:
                st.session_state.history.append((guess, bulls, cows))  # Store the guess and the results
            display_attempt_history()
            # Display bulls and cows liquid fill charts
            display_bulls_and_cows(bulls, cows)

            # Filter possibilities and calculate entropy
            # Filter possibilities and calculate entropy
            st.session_state.possibilities = filter_possibilities(st.session_state.possibilities, guess, bulls, cows)

            # Calculate entropy with proximity adjustment
            entropy = calculate_entropy(st.session_state.possibilities, guess, bulls, cows)

            # Track entropy values for plotting and entropy change
            if len(st.session_state.entropy_values) > 0:
                previous_entropy = st.session_state.entropy_values[-1]
                entropy_change = entropy - previous_entropy  # Change from the last guess
            else:
                entropy_change = 0  # For the first guess, there's no change

            # Store current entropy value
            st.session_state.entropy_values.append(entropy)

            initial_entropy = calculate_entropy(
                [''.join(p) for p in itertools.permutations('0123456789', 4)], guess, 0, 0
            )
            information_gain = initial_entropy - entropy
            st.session_state.information_gain_values.append(information_gain)

            # Display the graph with entropy and information gain
            display_graph()

            # Display additional calculations
            initial_possibilities_count = 5040  # Total number of 4-digit permutations without repetitions (10P4)

            # Check if possibilities are available (non-empty) before calculating the probability
            if len(st.session_state.possibilities) > 0:
                # Calculate probability of finding the secret number
                probability_of_finding = 1 / len(st.session_state.possibilities)
                probability_percentage = probability_of_finding
            else:
                # If no possibilities left, it's the correct guess
                probability_percentage = 1.00 if bulls == 4 else 0.0
            intial_probability=0
            st.write(f"Probability of Finding the Secret Number: {probability_percentage:.6f}")
            current_probability=probability_percentage
            probability_change=current_probability-intial_probability
            # Use columns for displaying metrics
            col1, col2, col3 = st.columns(3)

            with col2:
                # Show entropy change in delta format (Green for Gain, Red for Loss)
                if entropy_change < 0:  # Entropy has decreased (information gained)
                    st.metric(label="Entropy", value=f"{abs(entropy):.2f}",
                              delta=f"-{abs(entropy_change):.2f}", delta_color="normal")
                elif entropy_change > 0:  # Entropy has increased (information lost)
                    st.metric(label="Entropy", value=f"{abs(entropy):.2f}",
                              delta=f"+{abs(entropy_change):.2f}", delta_color="normal")
                else:  # No change in entropy
                    st.metric(label="Entropy", value=f"{abs(entropy):.2f}", delta="0.00", delta_color="off")

            with col3:
                # Show probability of finding the secret number as a metric
                st.metric(label="Probability of Finding Secret", value=f"{probability_percentage:.6f}", delta=f"+{abs(probability_change):.2f}",
                          delta_color="normal")

            # Additional metrics as before
            st.write(f"Information Gain: {information_gain:.2f}")

            avg_bulls = sum(bulls for _, bulls, _ in st.session_state.history) / len(st.session_state.history) if len(
                st.session_state.history) > 0 else 0
            avg_cows = sum(cows for _, _, cows in st.session_state.history) / len(st.session_state.history) if len(
                st.session_state.history) > 0 else 0
            st.write(f"Average Bulls per Attempt: {avg_bulls:.2f}")
            st.write(f"Average Cows per Attempt: {avg_cows:.2f}")

            # Check if the user guessed the correct number
            if bulls == 4:
                st.balloons()
                st.success(f"Congratulations! You guessed the number in {st.session_state.attempts} attempts.")
                st.session_state.game_over = True
        else:
            st.error("Invalid guess. Please enter a 4-digit number with no duplicate digits.")


# Start a new game when the app is first loaded
if 'game_over' not in st.session_state:
    st.session_state.game_over = False

# Start the game
if not st.session_state.game_over:
    play_game()
else:
    st.button("Start New Game", on_click=start_new_game)
