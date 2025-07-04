# PBT System Troubleshooting Guide

## Quick Diagnostic Checklist

Before diving into specific issues, run this quick diagnostic:

```bash
# 1. Check Python version
python --version  # Should be 3.8+

# 2. Check PyTorch installation
python -c "import torch; print(f'PyTorch: {torch.__version__}')"

# 3. Check dependencies
python -c "import numpy, pandas, matplotlib, seaborn, sklearn, yaml, tqdm, colorama; print('All dependencies OK')"

# 4. Test basic PBT functionality
python pbt/test_pbt_simple.py

# 5. Check baseline data
python scripts/analyze_agent_dump.py --consistency --dir data
```

## Common Installation Issues

### 1. PyTorch Installation Problems

#### Problem: `ModuleNotFoundError: No module named 'torch'`
**Solution:**
```bash
# For CPU-only (recommended for most users)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# For CUDA (if you have compatible GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### Problem: PyTorch installation hangs or fails
**Solutions:**
1. **Clear pip cache:**
   ```bash
   pip cache purge
   pip install --no-cache-dir torch
   ```

2. **Use conda instead:**
   ```bash
   conda install pytorch torchvision torchaudio cpuonly -c pytorch
   ```

### 2. Memory Problems

#### Problem: `RuntimeError: out of memory`
**Solutions:**
1. **Reduce population size:**
   ```python
   population_size = 4  # Instead of 8
   ```

2. **Use CPU instead of GPU:**
   ```python
   device = torch.device('cpu')
   ```

### 3. Data Loading Issues

#### Problem: `FileNotFoundError: No such file or directory`
**Solutions:**
1. **Check data directory structure:**
   ```bash
   ls -la data/
   # Should show: agent_0/, agent_1/, agent_2/, agent_3/, agent_4/
   ```

2. **Verify JSON format:**
   ```python
   import json
   with open('data/agent_0/agent_0_full_dump.json') as f:
       data = json.load(f)
       print(f"Data type: {type(data)}, Length: {len(data)}")
   ```

## Performance Issues

### Problem: Training is very slow
**Solutions:**
1. **Enable mock mode for testing:**
   ```bash
   python pbt/pbt_runner.py --mock --generations 5
   ```

2. **Reduce episode length:**
   ```python
   config['max_episodes'] = 1000  # Instead of 100000
   ```

### Problem: No improvement in metrics
**Solutions:**
1. **Check baseline metrics:**
   ```bash
   python scripts/analyze_agent_dump.py --consistency --dir data
   ```

2. **Verify target values are realistic:**
   ```python
   targets = {
       'zero_rate': 0.10,  # Start with modest improvement
       'success_rate': 0.13,
       'excellence_rate': 0.07,
       'mean_value': 0.32
   }
   ```

## Visualization Issues

### Problem: Plots are empty or incorrect
**Solutions:**
1. **Check data format:**
   ```python
   print(f"Data shape: {data.shape}")
   print(f"Data range: {data.min()} to {data.max()}")
   ```

2. **Use non-interactive backend:**
   ```python
   import matplotlib
   matplotlib.use('Agg')
   import matplotlib.pyplot as plt
   ```

## Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

runner = PBTRunner()
runner.run(debug=True)
```

## Recovery Procedures

### Complete Reset
```bash
# Reset to clean state
rm -rf pbt/logs/
rm -rf pbt/analysis/
rm -rf pbt/visualizations/

# Regenerate directories
mkdir -p pbt/{logs,analysis,visualizations}

# Test basic functionality
python pbt/test_pbt_simple.py
```

## Getting Help

### Collect Debug Information
```bash
python -c "
import sys, torch, numpy, pandas, matplotlib
print(f'Python: {sys.version}')
print(f'PyTorch: {torch.__version__}')
print(f'NumPy: {numpy.__version__}')
print(f'Pandas: {pandas.__version__}')
print(f'Matplotlib: {matplotlib.__version__}')
" > debug_info.txt
```

### Support Checklist
- [ ] Baseline analysis completed
- [ ] Targets are realistic (within 50% of baseline)
- [ ] Sufficient generations (>20)
- [ ] Agent diversity enabled
- [ ] Debug logging enabled
