from pedalboard import Pedalboard, Reverb, load_plugin, Chorus
from pedalboard.io import AudioFile
import matplotlib.pyplot as plt
import librosa.display
import librosa
import soundfile as sf
import os, json

print(os.getcwd())
vst3_path = ".\\python\\data\\vst3"
data = {}
for file in os.listdir(vst3_path):
    print(file)
    if file.endswith(".vst3"):
        data[file] = {}
        vst = load_plugin(os.path.join(vst3_path, file))
        for param in vst.parameters:
            print(param)
            
            data[file][param] = {}
            data[file][param]['min'] = vst.parameters[param].min_value
            data[file][param]['max'] = vst.parameters[param].max_value
            default_value = str(getattr(vst, param))
            data[file][param]['default'] = default_value
            data[file][param]['valid_value'] = vst.parameters[param].valid_values
            
with open('.\\python\\data.json', 'w') as outfile:
    json.dump(data, outfile, indent=4)
