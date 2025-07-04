import json
import sys
from pathlib import Path

def compare_results():
    try:
        baseline = json.load(open('pbt/logs/training_summary_baseline.json'))
        current = json.load(open('pbt/logs/training_summary.json'))
        
        baseline_best = baseline['best_score_achieved']
        current_best = current['best_score_achieved']
        
        baseline_final_mean = baseline['generation_stats'][-1]['summary']['mean_score']
        current_final_mean = current['generation_stats'][-1]['summary']['mean_score']
        
        baseline_std = baseline['generation_stats'][-1]['summary']['std_score']
        current_std = current['generation_stats'][-1]['summary']['std_score']
        
        print('🔍 Performance Comparison:')
        print('=' * 40)
        print(f'Best Score:   {baseline_best:.3f} → {current_best:.3f} ({((current_best/baseline_best)-1)*100:+.1f}%)')
        print(f'Final Mean:   {baseline_final_mean:.3f} → {current_final_mean:.3f} ({((current_final_mean/baseline_final_mean)-1)*100:+.1f}%)')
        print(f'Std Dev:      {baseline_std:.3f} → {current_std:.3f} ({((current_std/baseline_std)-1)*100:+.1f}%)')
        
        # Calculate grades
        def calculate_grade(best, mean, std, pop_size, max_targets):
            peak_score = min(100, (best / 30.0) * 25)
            convergence_score = min(100, (mean / 20.0) * 25)  
            stability_score = min(25, max(0, 25 - (std - 5.0) * 2))
            consistency_score = (max_targets / pop_size) * 25
            return int(peak_score + convergence_score + stability_score + consistency_score)
        
        baseline_grade = calculate_grade(
            baseline_best, baseline_final_mean, baseline_std,
            baseline['generation_stats'][0]['population_size'],
            baseline['max_targets_met']
        )
        
        current_grade = calculate_grade(
            current_best, current_final_mean, current_std,
            current['generation_stats'][0]['population_size'], 
            current['max_targets_met']
        )
        
        print(f'\\nPerformance Grade: {baseline_grade}/100 → {current_grade}/100 ({current_grade-baseline_grade:+d} points)')
        
        if current_grade > baseline_grade:
            print('✅ Enhancement successful!')
        else:
            print('⚠️  Consider additional optimizations')
            
    except FileNotFoundError as e:
        print(f'Error: {e}')
        print('Make sure you have both baseline and current training summaries')
    except Exception as e:
        print(f'Error analyzing results: {e}')

if __name__ == '__main__':
    compare_results()
