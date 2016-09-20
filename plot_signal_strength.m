% opens a JSON file and plot Length vs Signal Strength

[FileName,PathName] = uigetfile('*.json')
data = loadjson(strcat(PathName,FileName))

length = data.length_0x28_cm_0x29_
signal = data.Signal_0x28_dBm_0x29_

plot(length, signal)
xlabel('Length (cm)')
ylabel('Signal Strength (dBm)')
grid minor