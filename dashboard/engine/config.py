"""Study settings shared by the analysis engine and its result explorer."""
MODELS = [f"M{i}" for i in range(1, 17)]
DISTRICTS = ["Ahmedabad", "Amreli", "Okha"]
LATITUDE = {"Ahmedabad": 23 + 4/60, "Amreli": 21 + 36/60, "Okha": 22 + 29/60}
PERIODS = ["Annual", "Winter", "Pre-Monsoon", "Monsoon", "Post-Monsoon"]
SEASON_OF_MONTH = {1: "Winter", 2: "Winter", 3: "Pre-Monsoon", 4: "Pre-Monsoon", 5: "Pre-Monsoon",
                   6: "Monsoon", 7: "Monsoon", 8: "Monsoon", 9: "Monsoon",
                   10: "Post-Monsoon", 11: "Post-Monsoon", 12: "Post-Monsoon"}
GSC = 0.0820
A_AP, B_AP = 0.25, 0.50
MIN_DAYS = 30
