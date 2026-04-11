"""
Step Logger Module

Manages logging and tracking of algebraic simplification steps.
Maintains step counter and provides helper functions for step recording.

Classes:
    - StepLogger: Manages step tracking and logging

Functions:
    - log_step(): Record a single simplification step
"""


class StepLogger:
    """Manages step tracking during symbolic simplification.
    
    Attributes:
        steps: List of step descriptions
        solution_trail: Ordered list of all output entries, including warnings
        counter: Current step number
    """
    
    def __init__(self):
        """Initialize the step logger."""
        self.steps = []
        self.solution_trail = []
        self.counter = 1
    
    def log(self, description: str) -> None:
        """Log a step with automatic numbering.
        
        Args:
            description: Description of the step to log
        """
        step_text = f"Step {self.counter}: {description}"
        self.steps.append(step_text)
        self.solution_trail.append(step_text)
        self.counter += 1
    
    def log_robustness_warning(self, message: str) -> None:
        """Log a robustness warning as a distinct solution trail entry.
        
        Args:
            message: Warning message to record
        """
        warning_text = f"⚠️ WARNING: {message}"
        self.solution_trail.append(warning_text)

    def log_recommended_warning(self, message: str) -> None:
        """Log a recommended next step warning at the top of the solution trail.
        
        Args:
            message: Recommendation message to record
        """
        warning_text = message if message.startswith("⚠️") else f"⚠️ RECOMMENDED: {message}"
        self.solution_trail.insert(0, warning_text)
        # also add to the beginning of step records so it is visible first
        self.steps.insert(0, warning_text)

    def get_steps(self):
        """Get all logged steps.
        
        Returns:
            List of step strings
        """
        return self.steps
    
    def get_solution_trail(self):
        """Get the ordered solution trail, including warnings.
        
        Returns:
            List of solution trail strings
        """
        return self.solution_trail
    
    def get_step_count(self) -> int:
        """Get the number of steps logged.
        
        Returns:
            Number of steps
        """
        return len(self.steps)
