% opens a JSON file and plot Length vs Signal Strength

function plot_signal_strength(filename)

	data = loadjson(filename)

	length = data.length_0x28_cm_0x29_
	signal = data.Signal_0x28_dBm_0x29_

	plot(length, signal)
	xlabel('Length (cm)')
	ylabel('Signal Strength (dBm)')
	grid minor

endfunction