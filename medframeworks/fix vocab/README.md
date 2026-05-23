# Vocal Rehabilitation System with Neurostimulation

A comprehensive system for vocal rehabilitation that combines audio analysis with adaptive neurostimulation for speech therapy and vocal training.

## Features

- **Audio Analysis**: Advanced acoustic feature extraction for vocal assessment
- **Neurostimulation**: USB-controlled electrical stimulation for brain and vocal tract
- **Adaptive Training**: Machine learning-based weight adjustment for personalized therapy
- **Multi-modal Feedback**: Tactile, auditory, and visual feedback integration

## System Architecture

### Core Components

1. **Audio Analysis Module** (`audio_utils.py`)
   - Dysarthria feature extraction (jitter, shimmer, tremor indices)
   - Audio classification and quality assessment
   - Real-time frequency analysis

2. **USB Neurostimulation** (`usb_neuro_stimulator.py`)
   - USB HID device control for stimulation hardware
   - Brain region targeting (Broca's area, dLMC)
   - Vocal tract stimulation (thyroid ligaments, vocal folds)
   - Adaptive parameter control

3. **Training System** (`vocal_rehabilitation_trainer.py`)
   - Performance-based adaptive stimulation
   - Real-time weight adjustment
   - Progress tracking and session management

## Installation

1. **Create Virtual Environment**
   ```bash
   setup_venv.bat
   ```

2. **Install Additional Dependencies**
   ```bash
   pip install -r requirements_additional.txt
   ```

3. **Activate Environment**
   ```bash
   call venv\Scripts\activate.bat
   ```

## Usage

### Basic Audio Analysis
```bash
python -m src.main --audio path/to/audio.wav --mode analyze
```

### Training Mode
```bash
python -m src.main --audio path/to/baseline.wav --mode train --target-freq 180
```

### Stimulation Test
```bash
python -m src.main --mode test
```

## Hardware Requirements

### USB Stimulation Device
- Vendor ID: `0x1234` (configurable)
- Product ID: `0x5678` (configurable)
- HID-compatible stimulation hardware
- Safe current levels (micro-ampere range)

### Safety Features
- Current limiting circuitry
- Isolation protection
- Emergency stop capability
- Real-time monitoring

## API Documentation

### USBNeuroStimulator Class
```python
stimulator = USBNeuroStimulator(vendor_id=0x1234, product_id=0x5678)
stimulator.connect()
stimulator.stimulate_brain_region('broca', intensity=0.5)
stimulator.stimulate_vocal_tract('thyroid', intensity=0.3)
```

### VocalRehabilitationTrainer Class
```python
trainer = VocalRehabilitationTrainer()
trainer.start_training_session(audio_path, target_frequency=180.0)
results = trainer.run_training_cycle(current_audio_path)
```

## Safety Guidelines

1. **Medical Supervision**: Always use under professional supervision
2. **Current Limits**: Never exceed safe stimulation levels
3. **Electrode Placement**: Follow anatomical guidelines
4. **Monitoring**: Continuously monitor patient response
5. **Emergency Stop**: Implement hardware emergency stop

## Development

### Adding New Features
1. Extend `USBNeuroStimulator` for new stimulation patterns
2. Add feature extractors to `audio_utils.py`
3. Implement new training algorithms in `vocal_rehabilitation_trainer.py`

### Testing
```bash
# Run basic tests
python -m src.usb_neuro_stimulator
python -m src.vocal_rehabilitation_trainer
```

## License

Medical Device - For research and development use only

## Support

For technical support and medical guidance, contact the development team.

---

**Warning**: This system is for research purposes only. Always follow medical guidelines and regulations when using neurostimulation devices.