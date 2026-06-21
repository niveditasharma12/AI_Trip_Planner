from typing import Any

class Calculator:
    @staticmethod
    def multiply(a: Any, b: Any) -> int:
        """
        Multiply two values safely by casting them to integers.

        Args:
            a: The first value (int, float, or numeric string).
            b: The second value (int, float, or numeric string).

        Returns:
            int: The product of a and b.
        """
        try:
            return int(float(str(a).strip())) * int(float(str(b).strip()))
        except (ValueError, TypeError):
            return 0
    
    @staticmethod
    def calculate_total(*x: Any) -> float:
        """
        Calculate sum of the given list of numbers, casting string inputs safely.

        Args:
            x: Arguments of numbers or numeric strings.

        Returns:
            float: The sum of numbers in the list x
        """
        clean_list = []
        for item in x:
            try:
                # Strip spaces and convert each item to a float
                clean_list.append(float(str(item).strip()))
            except (ValueError, TypeError):
                continue  # Skip items that cannot be converted
        return sum(clean_list)
    
    @staticmethod
    def calculate_daily_budget(total: Any, days: Any) -> float:
        """
        Calculate daily budget safely handling string types.

        Args:
            total: Total cost (numeric or string).
            days: Total number of days (numeric or string).

        Returns:
            float: Expense for a single day
        """
        try:
            clean_total = float(str(total).strip())
            clean_days = int(float(str(days).strip()))
            
            return clean_total / clean_days if clean_days > 0 else 0.0
        except (ValueError, TypeError, ZeroDivisionError):
            return 0.0