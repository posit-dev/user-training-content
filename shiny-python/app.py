from shiny import App, ui, render, reactive
import random
import time

# Define the UI
app_ui = ui.page_fluid(
    ui.h1("🧮 Speed Math Challenge", style="text-align: center; color: #2c3e50;"),
    ui.br(),
    
    ui.row(
        ui.column(6,
            ui.div(
                ui.h3("Solve the Problem!", style="text-align: center;"),
                ui.div(
                    ui.output_ui("problem_display"),
                    style="text-align: center; background-color: #ecf0f1; padding: 30px; border-radius: 10px; margin: 20px 0;"
                ),
                ui.input_numeric("answer", "Your Answer:", value=None, min=-1000, max=1000),
                ui.br(),
                ui.input_action_button("submit_answer", "Submit Answer", class_="btn-primary"),
                ui.input_action_button("skip_problem", "Skip Problem", class_="btn-warning"),
                ui.br(),
                ui.br(),
                ui.div(
                    ui.input_select("difficulty", "Difficulty:", 
                                  choices={"easy": "Easy (1-12)", "medium": "Medium (1-25)", "hard": "Hard (1-50)"},
                                  selected="easy"),
                    ui.input_action_button("new_game", "New Game", class_="btn-success"),
                    style="text-align: center;"
                )
            )
        ),
        ui.column(6,
            ui.div(
                ui.h3("Game Stats", style="text-align: center;"),
                ui.output_ui("timer_display"),
                ui.br(),
                ui.output_ui("score_display"),
                ui.br(),
                ui.output_ui("feedback"),
                ui.br(),
                ui.output_ui("streak_display"),
                ui.br(),
                ui.output_ui("high_score_display"),
            )
        )
    )
)

# Define the server logic
def server(input, output, session):
    # Reactive values for game state
    current_problem = reactive.Value({"num1": 0, "num2": 0, "operation": "+", "answer": 0})
    score = reactive.Value(0)
    total_problems = reactive.Value(0)
    streak = reactive.Value(0)
    best_streak = reactive.Value(0)
    feedback_message = reactive.Value("Ready to start? Click 'New Game'!")
    game_active = reactive.Value(False)
    start_time = reactive.Value(time.time())
    time_left = reactive.Value(60)  # 60 second games
    high_score = reactive.Value(0)
    
    def generate_problem(difficulty):
        """Generate a math problem based on difficulty level"""
        if difficulty == "easy":
            num1 = random.randint(1, 12)
            num2 = random.randint(1, 12)
        elif difficulty == "medium":
            num1 = random.randint(1, 25)
            num2 = random.randint(1, 25)
        else:  # hard
            num1 = random.randint(1, 50)
            num2 = random.randint(1, 50)
        
        operations = ["+", "-", "×"]
        operation = random.choice(operations)
        
        if operation == "+":
            answer = num1 + num2
        elif operation == "-":
            # Ensure positive results for subtraction
            if num1 < num2:
                num1, num2 = num2, num1
            answer = num1 - num2
        else:  # multiplication
            # Keep multiplication smaller for easier mental math
            if difficulty == "easy":
                num1 = random.randint(1, 8)
                num2 = random.randint(1, 8)
            elif difficulty == "medium":
                num1 = random.randint(1, 12)
                num2 = random.randint(1, 12)
            else:
                num1 = random.randint(1, 15)
                num2 = random.randint(1, 15)
            answer = num1 * num2
        
        return {"num1": num1, "num2": num2, "operation": operation, "answer": answer}
    
    @output
    @render.ui
    def problem_display():
        if game_active():
            prob = current_problem()
            return ui.h2(f"{prob['num1']} {prob['operation']} {prob['num2']} = ?", 
                        style="font-size: 36px; font-weight: bold; color: #2c3e50;")
        else:
            return ui.h3("Click 'New Game' to start!", style="color: #7f8c8d;")
    
    @output
    @render.ui
    def timer_display():
        if game_active():
            color = "red" if time_left() <= 10 else "orange" if time_left() <= 20 else "green"
            return ui.div(
                ui.h4(f"⏰ Time: {time_left()}s", style=f"color: {color}; font-weight: bold;"),
                style="text-align: center; background-color: #f8f9fa; padding: 15px; border-radius: 8px;"
            )
        else:
            return ui.div(
                ui.h4("⏰ Ready to play!", style="color: #28a745;"),
                style="text-align: center; background-color: #f8f9fa; padding: 15px; border-radius: 8px;"
            )
    
    @output
    @render.ui
    def score_display():
        accuracy = (score() / max(total_problems(), 1)) * 100 if total_problems() > 0 else 0
        return ui.div(
            ui.p(f"Score: {score()}", style="font-size: 20px; font-weight: bold;"),
            ui.p(f"Problems: {total_problems()}", style="font-size: 16px;"),
            ui.p(f"Accuracy: {accuracy:.1f}%", style="font-size: 16px;"),
            style="text-align: center; background-color: #e8f5e8; padding: 15px; border-radius: 8px;"
        )
    
    @output
    @render.ui  
    def feedback():
        color = "#28a745" if "Correct" in feedback_message() else "#dc3545" if "Wrong" in feedback_message() else "#007bff"
        return ui.div(
            ui.p(feedback_message(), style=f"font-size: 16px; font-weight: bold; color: {color}; text-align: center;"),
            style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin: 10px 0;"
        )
    
    @output
    @render.ui
    def streak_display():
        emoji = "🔥" if streak() >= 5 else "⭐" if streak() >= 3 else "✨" if streak() >= 1 else ""
        return ui.div(
            ui.p(f"Current Streak: {streak()} {emoji}", style="font-size: 16px; font-weight: bold;"),
            ui.p(f"Best Streak: {best_streak()}", style="font-size: 14px;"),
            style="text-align: center; background-color: #fff3cd; padding: 10px; border-radius: 5px;"
        )
    
    @output
    @render.ui
    def high_score_display():
        return ui.div(
            ui.p(f"🏆 High Score: {high_score()}", style="font-size: 18px; font-weight: bold; color: #ffc107;"),
            style="text-align: center; background-color: #f8f9fa; padding: 10px; border-radius: 5px;"
        )
    
    # Timer effect
    @reactive.Effect
    def update_timer():
        if game_active():
            reactive.invalidate_later(1)  # Update every second
            elapsed = time.time() - start_time()
            remaining = max(0, 60 - int(elapsed))
            time_left.set(remaining)
            
            if remaining == 0:
                # Game over
                game_active.set(False)
                if score() > high_score():
                    high_score.set(score())
                feedback_message.set(f"⏰ Time's up! Final score: {score()} points!")
    
    # Handle answer submission
    @reactive.Effect
    @reactive.event(input.submit_answer)
    def handle_answer():
        if game_active() and input.answer() is not None:
            total_problems.set(total_problems() + 1)
            
            if input.answer() == current_problem()["answer"]:
                score.set(score() + 1)
                streak.set(streak() + 1)
                if streak() > best_streak():
                    best_streak.set(streak())
                feedback_message.set(f"✅ Correct! +1 point")
            else:
                streak.set(0)
                feedback_message.set(f"❌ Wrong! Answer was {current_problem()['answer']}")
            
            # Generate new problem
            current_problem.set(generate_problem(input.difficulty()))
            ui.update_numeric("answer", value=None)
    
    # Handle skip
    @reactive.Effect
    @reactive.event(input.skip_problem)
    def handle_skip():
        if game_active():
            streak.set(0)
            total_problems.set(total_problems() + 1)
            feedback_message.set(f"⏭️ Skipped! Answer was {current_problem()['answer']}")
            current_problem.set(generate_problem(input.difficulty()))
            ui.update_numeric("answer", value=None)
    
    # Handle new game
    @reactive.Effect
    @reactive.event(input.new_game)
    def start_new_game():
        game_active.set(True)
        score.set(0)
        total_problems.set(0)
        streak.set(0)
        start_time.set(time.time())
        time_left.set(60)
        feedback_message.set("Game started! Solve as many as you can!")
        current_problem.set(generate_problem(input.difficulty()))
        ui.update_numeric("answer", value=None)

# Create the app
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()