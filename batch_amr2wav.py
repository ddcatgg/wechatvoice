import os
import glob
import shutil
import argparse
from amr2ogg import silk2wav, is_regular_amrfile


def main():
	dest_dir = opts.dest_dir or os.path.split(amrfile)[0]
	if not os.path.isdir(dest_dir):
		try:
			os.makedirs(dest_dir)
		except:
			print 'can not create directory: %s' % dest_dir
			return

	amrfiles = glob.glob('%s/*.amr' % opts.sour_dir)
	for amrfile in amrfiles:
		if is_regular_amrfile(amrfile):
			print '%s is a regluar amr file.' % amrfile
			sour = amrfile
			dest = os.path.join(dest_dir, os.path.basename(amrfile))
			print '%s -> %s' % (sour, dest)
			shutil.copy(sour, dest)
		else:
			wavfile = silk2wav(amrfile, opts.dest_dir)
			print '%s -> %s' % (amrfile, wavfile)


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-s", "--sour-dir", dest="sour_dir",
					  help="source directory", metavar="SOUR_DIR")
	parser.add_argument("-d", "--dest-dir", dest="dest_dir",
					  help="destination directory", metavar="DEST_DIR")
	parser.add_argument('args', nargs=argparse.REMAINDER, help='SOUR_DIR [DEST_DIR]')

	opts = parser.parse_args()

	if not opts.sour_dir:
		if len(opts.args):
			opts.sour_dir = opts.args[0]
	if not opts.dest_dir:
		if len(opts.args) > 1:
			opts.dest_dir = opts.args[1]

	if opts.sour_dir:
		main()
	else:
		parser.print_help()
		exit(1)

