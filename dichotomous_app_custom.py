from pylsl import StreamInlet, resolve_stream
from flask import Flask, render_template, send_file,request
import base64

app = Flask(__name__)
inlet = None
left_img = None
right_img = None

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
	return render_template('setup.html')#,left=left,right=right)

@app.route('/finish_setup')
def finish_setup():
	global left_img
	global right_img
	left_img = request.args.get('leftImg')
	right_img = request.args.get('rightImg')
	#print(bool(left_img)	,bool(right_img)	)

	if left_img: write_file(left_img,'experiment/left.png')
	if right_img: write_file(right_img,'experiment/right.png')

	return 'success'

def write_file(img,path):
	starter = img.find(',')
	image_data = img[starter+1:]
	image_data = bytes(image_data, encoding="ascii")
	with open(path, "wb") as fh:
		fh.write(base64.decodebytes(image_data))
	
@app.route('/experiment/')
def experiment():
	sample = inlet.pull_sample()[0]
	left=(sample[0]+1.0)/2*100
	right=(sample[1]+1.0)/2*100
	print(left,right)
	if left_img and not right_img:
		print('One file found.')
		return render_template('single.html',left=left)
	elif left_img and right_img:
		print('Two files found.')
		return render_template('double.html',left=left,right=right)
	else:
		return 'Wrong number of files inputted. Refresh and try again.'

@app.route('/images/<name>.<ext>')
def return_image(name, ext):
	return send_file('images/'+name+'.'+ext, mimetype='image/gif')

@app.route('/experiment/<name>.<ext>')
def return_exp_image(name, ext):
	return send_file('experiment/'+name+'.'+ext, mimetype='image/gif')

@app.route('/<name>.css')
@app.route('/experiment/<name>.css')
def return_css(name):
	return send_file('css/'+name+'.css', mimetype='text/css')

if __name__ == '__main__':
	app.run()	