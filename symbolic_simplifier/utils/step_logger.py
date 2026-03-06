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
        counter: Current step number
    """
    
    def __init__(self):
        """Initialize the step logger."""
        self.steps = []
        self.counter = 1
    
    def log(self, description: str) -> None:
        """Log a step with automatic numbering.
        
        Args:
            description: Description of the step to log
        """
        self.steps.append(f"Step {self.counter}: {description}")
        self.counter += 1
    
    def get_steps(self):
        """Get all logged steps.
        
        Returns:
            List of step strings
        """
        return self.steps
    
    def get_step_count(self) -> int:
        """Get the number of steps logged.
        
        Returns:
            Number of steps
        """
        return len(self.steps)
