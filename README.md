# Tunable Piano Synth & Rhythm Sequencer (Streamlit Prototype)

## Features
- **Tunable on-screen piano:** Each key displays its frequency (Hz) and is tuned from a user-settable base frequency (0.0–2000.00000 Hz).
- **Synth playback:** Play notes with a click/tap.
- **Rhythm layers:** Mix up to 5 drum/percussion tracks, with instrument and rhythm pattern selection.
- **Real-time rhythm playback:** Play/stop drum sequences at your chosen BPM.

## Requirements

Install these Python packages:
- `streamlit`
- `numpy`
- `sounddevice`

**Quick install:**
```sh
pip install streamlit numpy sounddevice
```

(If `sounddevice` fails, you may need portaudio:  
- On Ubuntu: `sudo apt-get install libportaudio2`
- On macOS: Use Homebrew, if needed: `brew install portaudio`
)

## Running the App

1. Save `app.py` and `README.md` to a folder.
2. Open a terminal in that folder.
3. Run:
   ```sh
   streamlit run app.py
   ```
   
Your browser will open at [http://localhost:8501](http://localhost:8501)

## Notes

- **Works best on desktop:** Sound playback uses your computer’s audio hardware.
- **Layered rhythm:** See grid preview and play/stop controls; tap keys to play notes as you wish.
- **All sound is synthesized in Python:** No samples required.

---

**Prototype only**—expand, remix, or deploy as you like!
