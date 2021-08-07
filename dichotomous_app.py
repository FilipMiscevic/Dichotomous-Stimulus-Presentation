from pylsl import StreamInlet, resolve_stream
from flask import Flask, render_template, send_file
app = Flask(__name__)
inlet=None

@app.before_first_request
def start_inlet(name='pearson'):
	# first resolve an EEG stream on the lab network
	print("looking for stream '{}'...".format(name))
	streams = resolve_stream('type', name)

	# create a new inlet to read from the stream
	global inlet
	inlet = StreamInlet(streams[0])
	print("...found!")

@app.route('/')
def root():
	sample = inlet.pull_sample()[0]
	left=(sample[0]+1.0)/2*100
	right=(sample[1]+1.0)/2*100
	print(left,right)
	return render_template('index.html',left=left,right=right)

@app.route('/_get_sizes')
def get_sizes():
	sample, timestamp = inlet.pull_sample()
	print(sample)
	return sample

@app.route('/images/<name>.<ext>')
def return_image(name, ext):
	return send_file('images/'+name+'.'+ext, mimetype='image/gif')

@app.route('/<name>.css')
def return_css(name):
	return send_file('css/'+name+'.css', mimetype='text/css')

if __name__ == '__main__':
	app.run()	