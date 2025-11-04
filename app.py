import streamlit as st
import numpy as np
import sounddevice as sd
import time

# --- Piano key logic ---
def get_key_freqs(base_freq, num_keys=24):
    # Generate 24 frequencies for keys, using base_freq and 12-TET formula
    return [base_freq * 2**(i/12) for i in range(num_keys)]

def play_sine(freq, duration=0.4, fs=44100, volume=0.15):
    t = np.linspace(0, duration, int(fs * duration), False)
    wave = volume * np.sin(2 * np.pi * freq * t)
    sd.stop()
    sd.play(wave, fs)

# --- Drum synthesis (simple drum sounds via waveform) ---
def drum_synth(kind, duration=0.15, fs=44100, volume=0.18):
    t = np.linspace(0, duration, int(fs * duration), False)
    if kind == "Bass Drum":
        wave = volume * np.sin(2*np.pi * 60 * t) * np.exp(-20 * t)
    elif kind == "Snare":
        noise = np.random.uniform(-1, 1, t.shape)
        wave = volume * noise * np.exp(-12 * t)
    elif kind == "HiHat":
        noise = np.random.uniform(-1, 1, t.shape)
        wave = volume * noise * np.exp(-45 * t)
    elif kind == "Shaker":
        noise = np.random.uniform(-1, 1, t.shape)
        wave = volume*0.5 * noise * np.exp(-30 * t)
    elif kind == "Djembe":
        wave = volume * np.sin(2*np.pi*100 * t) * np.exp(-16 * t)
        wave += 0.3*volume * np.sin(2*np.pi*330 * t) * np.exp(-30 * t)
    else:  # fallback
        wave = volume * np.sin(2*np.pi * 220 * t) * np.exp(-13 * t)
    return wave

def play_drum(kind, duration=0.15):
    fs = 44100
    wave = drum_synth(kind, duration=duration, fs=fs)
    sd.stop()
    sd.play(wave, fs)

# --- Rhythm Patterns ---
default_patterns = {
    "Four-on-the-Floor": [1,0,1,0,1,0,1,0],
    "Backbeat":          [1,0,0,1,1,0,0,1],
    "Shuffle":           [1,0,1,1,0,1,1,0],
    "Sparse":            [1,0,0,1,0,0,1,0],
    "Custom":            [1,0,0,0,1,0,0,1]
}
# --- App Layout ---
st.title("Tunable Piano Synth & Rhythm Sequencer (Streamlit Prototype)")
st.markdown(
    """
    - Click or tap a piano key to play a synthesized note, tuned by your chosen base frequency.
    - All Hz values are computed and shown for each key.
    - Add, layer, and edit drum rhythm tracks. Play all rhythms at once!
    - Choose BPM, instrument types, and rhythm patterns.
    """
)

# --- Piano Controls ---
base_freq = st.number_input("Piano base frequency (Hz)", min_value=0.0, max_value=2000.0, value=440.0, step=0.00001, format="%.5f")
st.caption(f"All keys tune up from this base (shown Hz per key, using equal-tempered formula).")

# Piano keys display
freqs = get_key_freqs(base_freq)
cols = st.columns(12)
key_clicked = None
for i, freq in enumerate(freqs):
    col = cols[i % 12]
    if col.button(f"{freq:.5f} Hz", key=f"key_{i}"):
        key_clicked = freq
        play_sine(freq)

# --- Rhythm Layering ---
st.header("Rhythm Tracks & Sequencer")
bpm = st.number_input("Rhythm BPM", min_value=30, max_value=300, value=120)
interval_sec = 60.0 / bpm / 2.0  # 8 steps per measure

if 'layers' not in st.session_state:
    st.session_state.layers = [
        {'instrument': "Bass Drum", 'pattern': "Four-on-the-Floor"}
    ]

max_layers = 5
def new_layer():
    if len(st.session_state.layers) < max_layers:
        st.session_state.layers.append({
            'instrument': "Snare",
            'pattern': "Backbeat"
        })

def del_layer(idx):
    if len(st.session_state.layers) > 1:
        st.session_state.layers.pop(idx)

with st.expander("Edit Rhythm Layers", expanded=True):
    for idx, layer in enumerate(st.session_state.layers):
        col1, col2, col3 = st.columns([2,2,1])
        layer['instrument'] = col1.selectbox(
            f"Instrument #{idx+1}",
            ["Bass Drum", "Snare", "HiHat", "Shaker", "Djembe"],
            index=["Bass Drum", "Snare", "HiHat", "Shaker", "Djembe"].index(layer['instrument']),
            key=f"inst_{idx}",
        )
        layer['pattern'] = col2.selectbox(
            "Pattern",
            list(default_patterns.keys()),
            index=list(default_patterns.keys()).index(layer['pattern']),
            key=f"pat_{idx}",
        )
        if col3.button("Remove", key=f"del_{idx}", disabled=len(st.session_state.layers)==1):
            del_layer(idx)
    st.button("Add Layer", on_click=new_layer, disabled=len(st.session_state.layers)>=max_layers)

# Preview rhythm pattern grid
st.subheader("Rhythm Layer Preview")
layer_labels = [f"{l['instrument'][:8]} ({l['pattern']})" for l in st.session_state.layers]
steps = 8
grid = np.zeros((len(st.session_state.layers), steps), dtype=int)
for i, layer in enumerate(st.session_state.layers):
    patt = default_patterns[layer['pattern']]
    grid[i,:] = patt

for row, label in zip(grid, layer_labels):
    st.write(label+": "+(" ".join(['█' if x else ' ' for x in row])))

# --- Play Rhythm Engine ---
st.markdown("### Play/Stop Drum Sequence")
play_rhythm = st.button("Play Rhythm", key="play_rhythm")
stop_rhythm = st.button("Stop", key="stop_rhythm")

if 'playing' not in st.session_state:
    st.session_state.playing = False

def rhythm_thread(layers, bpm):
    interval = 60.0 / bpm / 2.0
    steps = 8
    while st.session_state.playing:
        for step in range(steps):
            t_start = time.time()
            for lid, layer in enumerate(layers):
                patt = default_patterns[layer['pattern']]
                if patt[step]:
                    play_drum(layer['instrument'])
            t_elapsed = time.time() - t_start
            interval_left = interval - t_elapsed
            if interval_left > 0:
                time.sleep(interval_left)

if play_rhythm:
    st.session_state.playing = True
    st.success("Playing rhythm! Click Stop to end.")
    import threading
    thr = threading.Thread(target=rhythm_thread, args=(st.session_state.layers,bpm), daemon=True)
    thr.start()

if stop_rhythm:
    st.session_state.playing = False
    sd.stop()
    st.info("Rhythm stopped.")

st.markdown("---")
st.markdown("""
**Prototype built with Python, Streamlit, numpy, and sounddevice.  
All synthesis performed locally: piano and rhythm patterns use numerically generated sound waves.**  
""")
