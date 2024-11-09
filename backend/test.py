from datetime import datetime, timedelta

# Get today's date
today = datetime.today()

# Calculate the date 10 days ago
ten_days_ago = today - timedelta(days=10)

# Format the dates in string format (e.g., "YYYY-MM-DD")
time_interval = (ten_days_ago.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))

print(time_interval)
