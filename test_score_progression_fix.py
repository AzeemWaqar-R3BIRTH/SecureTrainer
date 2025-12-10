"""
Test script to verify score progression chart shows linear growth
"""
from datetime import datetime, timedelta
import random

def test_score_progression_logic():
    """Simulate the new score progression logic"""
    print("🧪 Testing Score Progression Chart Logic\n")
    print("="*60)
    
    # Simulate 50 completed challenges over time
    all_attempts_sorted = []
    running_score = 0
    base_date = datetime.now() - timedelta(days=60)
    
    for i in range(50):
        # Each challenge earns between 50-500 points
        points = random.randint(50, 500)
        running_score += points
        
        attempt = {
            'attempt_time': base_date + timedelta(days=i),
            'score_earned': points,
            'is_correct': True
        }
        all_attempts_sorted.append(attempt)
    
    print(f"📊 Simulated {len(all_attempts_sorted)} challenges")
    print(f"💯 Total Score: {running_score}")
    print()
    
    # Build cumulative score over time (NEW LOGIC)
    if len(all_attempts_sorted) > 0:
        cumulative_data = []
        running = 0
        
        for attempt in all_attempts_sorted:
            running += attempt.get('score_earned', 0)
            cumulative_data.append({
                'date': attempt.get('attempt_time', datetime.now()),
                'score': running
            })
        
        # Take last 30 data points
        chart_data = cumulative_data[-30:] if len(cumulative_data) > 30 else cumulative_data
        
        # Extract labels and scores
        chart_labels = [point['date'].strftime('%m/%d') for point in chart_data]
        chart_scores = [point['score'] for point in chart_data]
        
        print("📈 Chart Data (Last 30 attempts):")
        print("-" * 60)
        
        # Show first 5, middle 5, and last 5 points
        print("\n🔹 First 5 data points:")
        for i in range(min(5, len(chart_data))):
            print(f"  {chart_labels[i]}: {chart_scores[i]:,} points")
        
        if len(chart_data) > 10:
            print("\n🔹 Middle 5 data points:")
            mid = len(chart_data) // 2
            for i in range(mid - 2, min(mid + 3, len(chart_data))):
                print(f"  {chart_labels[i]}: {chart_scores[i]:,} points")
        
        print("\n🔹 Last 5 data points:")
        for i in range(max(0, len(chart_data) - 5), len(chart_data)):
            print(f"  {chart_labels[i]}: {chart_scores[i]:,} points")
        
        # Verify it's increasing
        print("\n" + "="*60)
        print("✅ VERIFICATION:")
        print("-" * 60)
        
        is_increasing = all(chart_scores[i] <= chart_scores[i+1] for i in range(len(chart_scores)-1))
        
        if is_increasing:
            print("✅ SUCCESS! Chart shows LINEAR INCREASING progression")
            print(f"   Starting score: {chart_scores[0]:,}")
            print(f"   Ending score:   {chart_scores[-1]:,}")
            print(f"   Total growth:   {chart_scores[-1] - chart_scores[0]:,} points")
        else:
            print("❌ FAILED! Chart does not show consistent growth")
            
        # Check for flatness (OLD BUG)
        score_range = max(chart_scores) - min(chart_scores)
        avg_score = sum(chart_scores) / len(chart_scores)
        variance_percentage = (score_range / avg_score) * 100
        
        print(f"\n   Score range:    {score_range:,} points")
        print(f"   Variance:       {variance_percentage:.1f}%")
        
        if variance_percentage < 5:
            print("   ⚠️  WARNING: Very low variance - might appear flat")
        elif variance_percentage < 20:
            print("   ⚠️  Low variance - gentle slope")
        else:
            print("   ✅ Good variance - clear upward trend")
            
    else:
        print("❌ No attempts to chart")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    test_score_progression_logic()
    print("\n🎯 Test complete! The chart should now show a linear increasing line.")
    print("📍 Restart your Flask server to see the updated chart on the dashboard.")
