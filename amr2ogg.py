#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division

import os
import sys
import glob
import shutil

from subprocess import Popen, PIPE, STDOUT
import threading

import wave
import time

try:
	CWD = os.path.abspath(os.path.dirname(__file__))
except:
	CWD = os.path.abspath(os.path.dirname(sys.executable))


# CWD = os.path.abspath(os.path.dirname(sys.argv[0]))


def path2sys():
	binpath = []
	binpath.append(CWD)
	binpath.append(os.environ['PATH'])
	os.environ['PATH'] = os.path.pathsep.join(binpath)


def run(cmd):
	p = Popen(cmd, stdout=PIPE, stderr=PIPE)
	stdout_s, stderr_s = p.communicate()
	p.wait()
	return p.returncode, stdout_s, stderr_s


def aud2fix(audfile):
	if not os.path.isfile(audfile):
		return

	magic = '#!AMR\n'
	with open(audfile, 'r+b') as fi:
		auddata = fi.read()
		if auddata[:len(magic)] != magic:
			fi.seek(0)
			fi.write(magic)
			fi.write(auddata)
	return audfile


def is_regular_amrfile(amrfile):
	magic_amr = b'#!AMR'
	with open(amrfile, 'rb') as fi:
		data = fi.read()
		return data[:len(magic_amr)] == magic_amr


def silk2pcm(silkfile):
	if not os.path.isfile(silkfile):
		return

	magic_silk = b'#!SILK_V3'
	with open(silkfile, 'r+b') as fi:
		data = fi.read()
		if data[1:len(magic_silk) + 1] == magic_silk:
			fi.seek(0)
			fi.write(data[1:])
			fi.truncate(len(data) - 1)

	cmd = os.path.join(CWD, 'decoder.exe')

	options = []
	options.append('-Fs_API 8000')

	basename = os.path.splitext(silkfile)
	pcmfile = basename[0] + '.pcm'

	cmdline = '"%s" "%s" "%s" %s' % (cmd, silkfile, pcmfile, ' '.join(options))

	# print(cmdline)
	ret = run(cmdline)
	return dict(pcmfile=pcmfile, retcode=ret[0], stdout=ret[1], stderr=ret[2])


def pcm2wav(pcmfile):
	if not os.path.isfile(pcmfile):
		return

	with open(pcmfile, 'rb') as fi:
		pcmdata = fi.read()
		# wavfile.setparams((2, 2, 44100, 0, 'NONE', 'NONE'))
		# wavfile.setparams((2, 1, 8000, 242, 'NONE', 'NONE'))

		# Wave_write.setnchannels(n)
		# Set the number of channels.
		#
		# Wave_write.setsampwidth(n)
		# Set the sample width to n bytes.
		#
		# Wave_write.setframerate(n)
		# Set the frame rate to n.
		#
		# Wave_write.setnframes(n)
		# Set the number of frames to n. This will be changed later if more frames are written.
		#
		# Wave_write.setcomptype(type, name)
		# Set the compression type and description. At the moment, only compression type NONE is supported, meaning no compression.
		#
		# Wave_write.setparams(tuple)
		# The tuple should be (nchannels, sampwidth, framerate, nframes, comptype, compname), with values valid for the set*() methods. Sets all parameters.
		#
		basename = os.path.splitext(pcmfile)
		wavfile = basename[0] + '.wav'
		fo = wave.open(wavfile, 'wb')

		fo.setnchannels(1)
		fo.setsampwidth(2)
		fo.setframerate(8000)
		fo.setnframes(0)

		fo.writeframes(pcmdata)

		fo.close()

		return wavfile


def silk2wav(silkfile, destdir=None):
	ret = silk2pcm(silkfile)
	if ret['retcode'] != 0:
		print ret['stderr']
		print ret['stdout']
		return

	pcmfile = ret['pcmfile']
	if not pcmfile:
		return

	if not os.path.isfile(pcmfile):
		print ret['stderr']
		print ret['stdout']
		return

	wavfile = pcm2wav(pcmfile)
	if not wavfile:
		return

	os.remove(pcmfile)
	if destdir:
		basefile = os.path.basename(wavfile)
		sour, dest = wavfile, os.path.join(destdir, basefile)
		shutil.move(sour, dest)
		wavfile = dest
	return wavfile


def wavconvert(wav, codec):
	from pydub import AudioSegment
	song = AudioSegment.from_wav(wav)

	fn = os.path.splitext(wav)
	out = fn[0] + '.' + codec

	tags = {
		'artist': 'Various Artists',
		'album': 'WeChat Voice',
		'year': time.strftime('%Y-%m-%d'),
		'comments': 'This album is awesome!'
	}

	parameters = ['-q:a', '0']
	if codec.lower() == 'ogg':
		parameters = ['-q:a', '0']
	elif codec.lower() in ['mp3', 'mp2', 'mpa']:
		parameters = ['-q:a', '6']
	elif codec.lower() in ['aac', 'mp4', 'm4a']:
		parameters = ['-q:a', '0']
		codec = 'mp4'

	song.export(out, format=codec, parameters=parameters, tags=tags)
	return out
	pass


def clean(pcmfile, wavfile):
	if os.path.isfile(pcmfile):
		os.remove(pcmfile)
	if os.path.isfile(wavfile):
		os.remove(wavfile)


if __name__ == '__main__':
	fin = None
	fout = None
	codec = 'ogg'
	argc = len(sys.argv)
	if argc == 1:
		print('usage: amr2ogg.py <*.amr|input.amr> [ogg|mp3|mp4|m4a]')
		exit

	if argc > 1:
		fin = sys.argv[1]
	if argc > 2:
		# fn = os.path.splitext(sys.argv[2])
		# codec = fn[1][1:]
		codec = sys.argv[2]

	if fin and codec in ['ogg', 'mp3', 'mp4', 'm4a', 'aac']:
		path2sys()

		files = glob.glob(fin)
		for amr in files:
			fn = os.path.splitext(amr)
			ext = fn[1].lower()
			if ext in ['.amr']:
				pcm = silk2pcm(amr)
				wav = pcm2wav(pcm)
				fout = wavconvert(wav, codec)
				clean(pcm, wav)
			elif ext in ['aud']:
				aud = aud2fix(amr)
				fout = wavconvert(aud, codec)
			print('%s has converted to %s.\n' % (amr, fout))
